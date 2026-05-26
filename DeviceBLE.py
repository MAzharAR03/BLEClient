import asyncio
import os
from datetime import datetime
import mss
import mss.tools
from bleak import BleakScanner, BleakClient
import crcmod.predefined as crc

from ReadFile import read_file
INPUT_SERVICE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
INPUT_CHAR_UUID = "0000beef-0000-1000-8000-00805f9b34fb"
FILE_TRANSFER_CHAR_UUID = "efcdbf7b-fee2-489b-8f79-b649aa50619b"
CONTROL_MESSAGE_CHAR_UUID = "4a55006e-990a-4737-9634-133466ef8e35"
PAUSE_UUID= "446be5b0-93b7-4911-abbe-e4e18d545640"
SCREENSHOT_UUID = "36d942a6-9e79-4812-8a8f-84a275f6b176"
EMULATION = True
from GamepadManager import GamepadManager
from SocketHandler import SocketHandler
from GetScreenshotsDir import get_screenshots_dir
class DeviceBLE:
    def __init__(self, ):
        self.client = None
        self.device = None
        self.uuid_input_service = INPUT_SERVICE_UUID
        self.uuid_input_characteristic = INPUT_CHAR_UUID
        self.uuid_pause_characteristic = PAUSE_UUID
        self.uuid_screenshot_characteristic = SCREENSHOT_UUID
        self.socketHandler = SocketHandler(self)
        self.gamepadManager = GamepadManager()
        self.buffer = []
        self.expecting_chunks = 0
        self.latest_control_message = None
        self.address = None
        self.loop = None
        self.monitor_index = 1




    async def connect(self):
        self.loop = asyncio.get_event_loop()
        if self.address is not None:
            try:
                print(f"Found device at address:{self.address}")
                print("Attempting to connect")
                self.client = BleakClient(self.address)
                await self.client.connect()
                print("Connected")
            except:
                raise Exception("Failed to connect")
        else:
            raise Exception("Did not find available devices")

    async def disconnect(self):
        try:
            if self.client is not None:
                await self.client.disconnect()
        except:
            raise Exception("Failed to disconnect")


    async def notify(self):
        if self.client and self.client.is_connected:
            characteristic = self.client.services.get_characteristic(self.uuid_input_characteristic)
            if characteristic:
                print(f"Characteristic found: {characteristic.uuid}")
                await self.client.start_notify(self.uuid_input_characteristic, self.input_handler)
                await self.client.start_notify(self.uuid_pause_characteristic, self.pause_handler)
                await self.client.start_notify(self.uuid_screenshot_characteristic, self.screenshot_handler)

                await self.client.start_notify(CONTROL_MESSAGE_CHAR_UUID, self.control_handler)
                print(f"Subscribed to notifications")
            else:
                print(f"Error, characteristic {self.uuid_input_characteristic} not found in discovered services.")

    def screenshot_handler(self, sender, data):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(get_screenshots_dir(), f"screenshot_{timestamp}.png")
        with mss.mss() as sct:
            sct.shot(mon = self.monitor_index, output = path)


    def pause_handler(self, sender, data):
        self.socketHandler.addMessage(data)
        print("Pause triggered")

    def input_handler(self, sender, data):
        value = data.decode('utf-8')

        if value.startswith("START:"):
            parts = value.split(":",2)
            self.expecting_chunks = int(parts[1])
            self.buffer = [parts[2]]
            return
        elif value.startswith("CHUNK:"):
            parts = value.split(":",2)
            self.buffer.append(parts[2])
            return
        elif value.startswith("END:"):
            self.buffer.append(value[4:])
            value = "".join(self.buffer)
            self.buffer = []
            self.expecting_chunks = 0

        self.socketHandler.addMessage(value)

        print(f"Notification from handle {sender}: {value}")
        if EMULATION:
            self.gamepadManager.update_state(value)

    def control_handler(self,sender,data):
        message = data.decode('utf-8')
        self.latest_control_message = message

    async def wait_for_response(self, timeout=5):
        attempts = 0
        while attempts < 3:
            start = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start < timeout:
                if self.latest_control_message in ("OK","RESEND"):
                    return self.latest_control_message
                await asyncio.sleep(0.05)
            attempts += 1
        raise TimeoutError("No ACK from Android device")


    async def send_chunks(self,data, CHUNK_SIZE):
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i:i + CHUNK_SIZE]
            await self.client.write_gatt_char(
                FILE_TRANSFER_CHAR_UUID,
                chunk,
                response=False
            )


    async def send_file(self, filename):

        if self.client and self.client.is_connected:
            import os
            basename = os.path.basename(filename)
            print("File transfer started")
            mtu_size = self.client.mtu_size
            ATT_OVERHEAD = 10
            CHUNK_SIZE = mtu_size - ATT_OVERHEAD
            data = read_file(filename)
            await self.client.write_gatt_char(
                CONTROL_MESSAGE_CHAR_UUID,
                f"START:{basename}".encode('utf-8'),
                response=True
            )
            await self.send_chunks(data, CHUNK_SIZE)

            crc32 = crc.mkPredefinedCrcFun("crc-32")
            checksum = crc32(data)
            await self.client.write_gatt_char(
                CONTROL_MESSAGE_CHAR_UUID,
                f"CHECKSUM:{checksum}".encode('utf-8'),
                response = True
            )
            try:
                result = await self.wait_for_response()
            except TimeoutError:
                print("No ACK from Android device after 3 tries, aborting.")
                return

            while result != "OK":
                print(result)
                await self.send_chunks(data, CHUNK_SIZE)
                await self.client.write_gatt_char(
                    CONTROL_MESSAGE_CHAR_UUID,
                    f"CHECKSUM:{checksum}".encode('utf-8'),
                    response=True
                )
                try:
                    result = await self.wait_for_response()
                except TimeoutError:
                    print("No ACK from Android device after 3 tries, aborting.")
                    return

            await self.client.write_gatt_char(
                CONTROL_MESSAGE_CHAR_UUID,
                f"END".encode('utf-8'),
                response=True
            )
            print(f"File {filename} sent")

    async def layout_received(self,filename):
        await self.send_file(filename)