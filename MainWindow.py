import asyncio
import os
import sys

import qasync
import websockets
from PySide6.QtCore import Qt
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGroupBox, QPushButton, QListWidget, QLabel, QCheckBox, \
    QMessageBox, QFileDialog, QApplication, QListWidgetItem, QComboBox, QDoubleSpinBox
from bleak import BleakScanner
import mss
import DeviceBLE as ble_module
from ConfigMapper import ConfigMapper
from DeviceBLE import DeviceBLE, INPUT_SERVICE_UUID
from GPXManager import GPXManager
from MapBridge import MapBridge
from UIBuilder import LayoutBuilder


class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_mapper = None
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

        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #888888;
                background-color: #2a2a2a;
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;            
            }
        """)
        layout.addWidget(self.status_label)

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

        trail_group = QGroupBox("Trail")
        trail_layout = QVBoxLayout()

        self._map_bridge = MapBridge()
        self._map_bridge.set_callback(self._on_pin_placed)

        self.map_view = QWebEngineView()
        self.map_view.setFixedHeight(350)
        channel = QWebChannel(self.map_view.page())
        channel.registerObject("bridge", self._map_bridge)
        self.map_view.page().setWebChannel(channel)
        self.map_view.setHtml(self._find_map())
        trail_layout.addWidget(self.map_view)

        self.pin_label = QLabel("No pin placed")
        self.pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trail_layout.addWidget(self.pin_label)

        self.start_trail_button = QPushButton("Start Trail")
        self.start_trail_button.clicked.connect(self.on_start_trail_clicked)
        self.start_trail_button.setEnabled(False)

        self.stop_trail_button = QPushButton("Stop & Save Trail")
        self.stop_trail_button.clicked.connect(self.on_stop_trail_clicked)
        self.stop_trail_button.setEnabled(False)

        trail_layout.addWidget(self.start_trail_button)
        trail_layout.addWidget(self.stop_trail_button)
        trail_group.setLayout(trail_layout)
        layout.addWidget(trail_group)

        #Settings Section
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()

        self.emulation_toggle = QCheckBox("Enable Xbox Controller Emulation")
        self.emulation_toggle.setChecked(ble_module.EMULATION)
        self.emulation_toggle.stateChanged.connect(self.on_emulation_toggled)

        self.config_mapper_button = QPushButton("Open Config Mapper")
        self.config_mapper_button.clicked.connect(self.on_config_mapper_clicked)

        self.monitor_dropdown = QComboBox()
        self.populate_monitors()
        self.monitor_dropdown.currentIndexChanged.connect(self.on_monitor_changed)

        settings_layout.addWidget(self.emulation_toggle)
        settings_layout.addWidget(self.config_mapper_button)
        settings_layout.addWidget((QLabel("Select Monitor to Screenshot:")))
        settings_layout.addWidget(self.monitor_dropdown)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

    def _on_pin_placed(self,lat,lon):
        self.pin_label.setText(f"Pin: {lat:.6f}, {lon:.6f}")
        if self.connected_device:
            self.start_trail_button.setEnabled(True)

    def _find_map(self):
        map_html_path = os.path.join(os.path.dirname(__file__), "map.html")
        with open(map_html_path, "r", encoding="utf-8") as f:
            map_html = f.read()
        return map_html

    def set_status(self, text, state = "idle"):
        colors = {
            "idle": (text, "#888888", "#2a2a2a"),
            "busy": (text, "#f0c040", "#2a2200"),
            "ok": (text, "#50d070", "#002a10"),
            "error": (text, "#e05050", "#2a0000"),
        }
        label, fg, bg = colors.get(state, colors["idle"])
        self.status_label.setText(label)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background-color: {bg};
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }}
        """)

    def on_device_disconnected(self):
        if self._is_shutting_down:
            return
        self.connected_device = None
        self.send_file_button.setEnabled(False)
        self.start_trail_button.setEnabled(False)
        self.stop_trail_button.setEnabled(False)
        self.scan_button.setEnabled(True)
        self.connect_button.setEnabled(False)
        self.set_status("Device Disconnected", "error")
        QMessageBox.critical(self, "Disconnected", "The BLE device disconnected unexpectedly.")


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
        device.on_disconnect = self.on_device_disconnected
        try:

            await device.connect()
            await device.notify()
            await device.start_heartbeat_loop()
            self.connected_device = device
            asyncio.create_task(self.run_websocket_server(device))

            self.status_label.setText("Status: Connected")
            self.send_file_button.setEnabled(True)
            if self._map_bridge.position()[0] is not None:
                self.start_trail_button.setEnabled(True)
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


    def on_config_mapper_clicked(self):
        self.config_mapper = ConfigMapper()
        self.config_mapper.show()

    def on_builder_button_clicked(self):
        self.builder_window = LayoutBuilder()
        self.builder_window.show()

    def on_emulation_toggled(self, state):
        is_enabled = (state == 2)
        ble_module.EMULATION = is_enabled
        state_str = "Enabled" if is_enabled else "Disabled"
        self.status_label.setText(f"Status: Emulation {state_str}")

    def populate_monitors(self):
        with mss.MSS() as sct:
            for i, monitor in enumerate(sct.monitors):
                if i == 0:
                    self.monitor_dropdown.addItem("All Monitors Combined", i)
                else:
                    text = f"Monitor {i} ({monitor['width']} x {monitor['height']}"
                    self.monitor_dropdown.addItem(text,i)

        if self.monitor_dropdown.count() > 1:
            self.monitor_dropdown.setCurrentIndex(1)

    def on_monitor_changed(self,index):
        selected_monitor_index = self.monitor_dropdown.itemData(index)
        if self.connected_device:
            self.connected_device.monitor_index = selected_monitor_index

    def on_start_trail_clicked(self):
        if not self.connected_device:
            return
        lat, lon = self._map_bridge.position()
        if lat is None:
            return
        self.connected_device.gpx_manager = GPXManager(lat, lon)
        self.start_trail_button.setEnabled(False)
        self.stop_trail_button.setEnabled(True)
        self.set_status("Trail started", "ok")

    def on_stop_trail_clicked(self):
        if not self.connected_device or not self.connected_device.gpx_manager:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Trail", "", "GPX files (*.gpx)")
        if path:
            self.connected_device.gpx_manager.save(path)
            self.set_status("Trail saved", "ok")
        self.connected_device.gpx_manager = None
        self.stop_trail_button.setEnabled(False)
        self.start_trail_button.setEnabled(True)



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