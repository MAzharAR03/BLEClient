import asyncio
import crcmod.predefined as crc
import websockets

from bleak import BleakScanner, BleakClient

from ReadFile import read_file

BUTTON_SERVICE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
BUTTON_CHAR_UUID = "0000beef-0000-1000-8000-00805f9b34fb"
TILT_CHAR_UUID = "446be5b0-93b7-4911-abbe-e4e18d545640"
STEP_CHAR_UUID = "36d942a6-9e79-4812-8a8f-84a275f6b176"
FILE_TRANSFER_CHAR_UUID = "efcdbf7b-fee2-489b-8f79-b649aa50619b"
CONTROL_MESSAGE_CHAR_UUID = "4a55006e-990a-4737-9634-133466ef8e35"

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

    latest_control_message = ""
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
                print(f"Characteristic found: {characteristic.uuid}")
                await self.client.start_notify(self.uuid_button_characteristic, self.button_handler)
                await self.client.start_notify(TILT_CHAR_UUID, self.button_handler)
                await self.client.start_notify(STEP_CHAR_UUID, self.button_handler)

                await self.client.start_notify(CONTROL_MESSAGE_CHAR_UUID, self.control_handler)
                print(f"Subscribed to notifications")
            else:
                print(f"Error, characteristic {self.uuid_button_characteristic} not found in discovered services.")

    def button_handler(self, sender, data):
        value = data.decode('utf-8')
        print(f"Notification from handle {sender}: {value}")
        self.socketHandler.addMessage(value)

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

    #can probably clean this out somehow
    async def send_file(self, filename):
        if self.client and self.client.is_connected:
            print("File transfer started")
            mtu_size = self.client.mtu_size
            ATT_OVERHEAD = 10
            CHUNK_SIZE = mtu_size - ATT_OVERHEAD
            data = read_file(filename)
            await self.client.write_gatt_char(
                CONTROL_MESSAGE_CHAR_UUID,
                f"START:{filename}".encode('utf-8'),
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

async def main():
    device = DeviceBLE()

    async def runServer():
        async with websockets.serve(device.socketHandler.handle_websocket,device.socketHandler.url, device.socketHandler.port):
            await asyncio.Future()
    try:
        asyncio.create_task(runServer())
        await device.connect()
        await device.notify()
        #await device.send_file("dog.6126.jpg")
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await device.disconnect()


asyncio.run(main())