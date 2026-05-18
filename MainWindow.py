import asyncio
import sys

import qasync
import websockets
from PySide6 import QtAsyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGroupBox, QPushButton, QListWidget, QLabel, QCheckBox, \
    QMessageBox, QFileDialog, QApplication, QListWidgetItem
from bleak import BleakScanner

import DeviceBLE as ble_module
from DeviceBLE import DeviceBLE, INPUT_SERVICE_UUID
from PySide import LayoutBuilder


class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self._is_shutting_down = False
        self.setWindowTitle("Server")
        self.setMinimumSize(800, 600)

        self.connected_device = None
        self.scanned_devices = {}

        self.setupUi()

    def setupUi(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        #Device Discovery Section
        scan_group = QGroupBox("Scanning")
        scan_layout = QVBoxLayout()

        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.on_scan_button_clicked)

        self.device_list = QListWidget()

        self.connect_button = QPushButton("Connect to a selected Device")
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.connect_button.setEnabled(False)
        self.device_list.itemSelectionChanged.connect(
            lambda: self.connect_button.setEnabled(bool(self.device_list.selectedItems()))
        )

        scan_layout.addWidget(self.scan_button)
        scan_layout.addWidget(QLabel("Available Devices:"))
        scan_layout.addWidget(self.device_list)
        scan_layout.addWidget(self.connect_button)
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        #Actions Section
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()

        self.send_file_button = QPushButton("Send Layout File to Phone")
        self.send_file_button.clicked.connect(self.on_send_file_button_clicked)
        self.send_file_button.setEnabled(False)

        self.builder_button = QPushButton("Open UI Builder")
        self.builder_button.clicked.connect(self.on_builder_button_clicked)

        actions_layout.addWidget(self.send_file_button)
        actions_layout.addWidget(self.builder_button)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        #Settings Section
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()

        self.emulation_toggle = QCheckBox("Enable Xbox Controller Emulation")
        self.emulation_toggle.setChecked(ble_module.EMULATION)
        self.emulation_toggle.stateChanged.connect(self.on_emulation_toggled)

        settings_layout.addWidget(self.emulation_toggle)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        #Status Bar
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("color: gray; font-weight: bold;")
        layout.addWidget(self.status_label)


    async def scan_for_devices(self):
        self.status_label.setText("Status: Scanning....")
        self.scan_button.setEnabled(False)
        self.device_list.clear()
        self.scanned_devices.clear()

        try:
            devices = await BleakScanner.discover(5.0, return_adv=True)
            for address, (device, adv) in devices.items():
                if INPUT_SERVICE_UUID in adv.service_uuids and adv.rssi > -90:
                    self.scanned_devices[address] = device

                    name = device.name or adv.local_name or "Unknown Device"
                    display_text = f"{name} ({address})"

                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, address)
                    self.device_list.addItem(item)

            count = len(self.scanned_devices)
            self.status_label.setText(f"Status: Scan Complete. Found {count} devices")
        except Exception as e:
            self.status_label.setText(f"Status: Error: {e}")
        finally:
            self.scan_button.setEnabled(True)


    async def connect_and_start(self, address):
        self.status_label.setText("Status: Connecting...")
        self.connect_button.setEnabled(False)

        device = DeviceBLE()
        device.address = address
        try:

            await device.connect()
            await device.notify()
            self.connected_device = device
            asyncio.create_task(self.run_websocket_server(device))

            self.status_label.setText("Status: Connected")
            self.send_file_button.setEnabled(True)
            self.scan_button.setEnabled(False)
        except Exception as e:
            self.status_label.setText(f"Status: Error -{e}")
            self.connect_button.setEnabled(True)

    async def run_websocket_server(self, device):
        try:

            async with websockets.serve(
                    device.socketHandler.handle_websocket,
                    device.socketHandler.url,
                    device.socketHandler.port
            ):
                self.status_label.setText(f"Status: WebSocket Connected")
                await asyncio.Future()
        except Exception as e:
            print(f"WebSocket Error: {e}")


    async def async_send_file(self, filepath):
        self.status_label.setText("Status: Sending File...")
        try:
            await self.connected_device.send_file(filepath)
            self.status_label.setText("Status: File Sent")
        except Exception as e:
            self.status_label.setText(f"Status: Error -{e}")


    def on_scan_button_clicked(self):
        asyncio.create_task(self.scan_for_devices())

    def on_connect_clicked(self):
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            return
        address = selected_items[0].data(Qt.ItemDataRole.UserRole)
        asyncio.create_task(self.connect_and_start(address))

    def on_send_file_button_clicked(self):
        if not self.connected_device:
            QMessageBox.warning(self, "Warning", "No device connected")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Select Layout JSON", "", "JSON files (*.json)")
        if path:
            asyncio.create_task(self.async_send_file(path))

    def on_builder_button_clicked(self):
        self.builder_window = LayoutBuilder()
        self.builder_window.show()

    def on_emulation_toggled(self, state):
        is_enabled = (state == 2)
        ble_module.EMULATION = is_enabled
        state_str = "Enabled" if is_enabled else "Disabled"
        self.status_label.setText(f"Status: Emulation {state_str}")

    def closeEvent(self, event):
        if self._is_shutting_down:
            event.ignore()
            return

        if self.connected_device and self.connected_device.client:
            event.ignore()
            self._is_shutting_down = True
            self.setEnabled(False)
            self.status_label.setText("Status: Disconnecting")

            asyncio.create_task(self.shutdown_routine())
        else:
            event.accept()

    async def shutdown_routine(self):
        try:
            print("Disconnecting BLE to prevent notification crash.")
            await self.connected_device.client.disconnect()
            self.connected_device = None
        except Exception as e:
            print(f"Disconnecting Error: {e}")
        finally:
            QApplication.instance().exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = ServerGUI()
    window.show()

    with loop:
        loop.run_forever()