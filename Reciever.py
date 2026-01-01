import asyncio
import json
import websockets

from bleak import BleakScanner, BleakClient

from ReadFile import read_file

BUTTON_SERVICE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
BUTTON_CHAR_UUID = "0000beef-0000-1000-8000-00805f9b34fb"
TILT_CHAR_UUID = "446be5b0-93b7-4911-abbe-e4e18d545640"
STEP_CHAR_UUID = "36d942a6-9e79-4812-8a8f-84a275f6b176"
LAYOUT_CHAR_UUID = "efcdbf7b-fee2-489b-8f79-b649aa50619b"

class SocketHandler:
    def __init__(self, ble_device):
        self.url = "localhost"
        self.port = 9999
        self.queue = asyncio.Queue()
        self.ble_device = ble_device


    async def handle_websocket(self,websocket):
        async def sender():
            while True:
                message = await self.queue.get()
                await websocket.send(message)

        async def receiver():
            async for message in websocket:
                filename = "layout.json"
                with open(filename,"w") as f:
                    f.write(message)
                print("JSON file received")
                asyncio.create_task(self.ble_device.layout_received(filename))


        try:
            await asyncio.gather(sender(),receiver())
        except websockets.ConnectionClosed:
            pass

    def addMessage(self,message):
         self.queue.put_nowait(message)

class DeviceBLE:
    def __init__(self):
        self.client = None
        self.device = None
        self.uuid_button_service = BUTTON_SERVICE_UUID
        self.uuid_button_characteristic = BUTTON_CHAR_UUID
        self.uuid_tilt_characteristic = TILT_CHAR_UUID
        self.uuid_step_characteristic = STEP_CHAR_UUID
        self.socketHandler = SocketHandler(self)

    async def discover(self):
        devices = await BleakScanner.discover(5.0, return_adv=True)
        for device in devices:
            advertisement_data = devices[device][1]
            print(advertisement_data)
            if BUTTON_SERVICE_UUID in advertisement_data.service_uuids:
                if advertisement_data.rssi > -90:
                    self.device = devices[device]
                    return device

    async def connect(self):
        address = await self.discover()
        if address is not None:
            try:
                print(f"Found device at address:{address}")
                print("Attempting to connect")
                self.client = BleakClient(address)
                await self.client.connect()
                print("Connected")
            except:
                raise Exception("Failed to connect")
        else:
            raise Exception("Did not find available devices")

    async def disconnect(self):
        try:
            await self.client.disconnect()
        except:
            raise Exception("Failed to disconnect")


    async def notify(self):
        if self.client and self.client.is_connected:
            characteristic = self.client.services.get_characteristic(self.uuid_button_characteristic)


            if characteristic:
                print(f"Characteristic found: {characteristic.uuid}. Attempting to subscribe...")
                print("Descriptors:")
                for descriptor in characteristic.descriptors:
                    print(f"  - UUID: {descriptor.uuid}, Handle: {descriptor.handle}")

                await self.client.start_notify(self.uuid_button_characteristic, self.button_handler)
                await self.client.start_notify(TILT_CHAR_UUID, self.button_handler)
                await self.client.start_notify(STEP_CHAR_UUID, self.button_handler)
                print(f"Subscribed to notifications on {self.uuid_button_characteristic}")
            else:
                print(f"ERROR: Characteristic {self.uuid_button_characteristic} not found in discovered services.")
                print("Please check the UUIDs and ensure the Android device is advertising correctly.")

    def button_handler(self, sender, data):
        value = data.decode('utf-8')
        print(f"Notification from handle {sender}: {value}")

    async def send_file(self, filename, uuid):
        if self.client and self.client.is_connected:
            mtu_size = self.client.mtu_size
            ATT_OVERHEAD = 3
            CHUNK_SIZE = mtu_size - ATT_OVERHEAD
            data = read_file(filename)
            await self.client.write_gatt_char(
                uuid,
                f"START".encode('utf-8'),
                response=True
            )
            for i in range(0,len(data),CHUNK_SIZE):
                chunk = data[i:i+CHUNK_SIZE]
                await self.client.write_gatt_char(
                    uuid,
                    chunk,response=False
                )
            await self.client.write_gatt_char(
                uuid,
                f"END".encode('utf-8'),
                response=True
            )
            print(f"File {filename} sent")

    async def layout_received(self,filename):
        await self.send_file(filename,LAYOUT_CHAR_UUID)

async def main():
    device = DeviceBLE()

    async def runServer():
        async with websockets.serve(device.socketHandler.handle_websocket,device.socketHandler.url, device.socketHandler.port):
            await asyncio.Future()
    try:
        asyncio.create_task(runServer())
        await device.connect()
        await device.notify()
        print("\nListening for button presses... Press Ctrl+C to stop")
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await device.disconnect()


asyncio.run(main())