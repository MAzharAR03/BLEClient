import asyncio
import time
import hid
from bleak import BleakScanner, BleakClient

BUTTON_SERVICE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
BUTTON_CHAR_UUID = "00002a4d-0000-1000-8000-00805f9b34fb"
TILT_CHAR_UUID = "446be5b0-93b7-4911-abbe-e4e18d545640"
STEP_CHAR_UUID = "36d942a6-9e79-4812-8a8f-84a275f6b176"
MESSAGE_CHAR_UUID = "4a55006e-990a-4737-9634-133466ef8e35"

VENDOR_ID = 0x1234
PRODUCT_ID = 0x5678

class DeviceBLE:
    def __init__(self):
        self.client = None
        self.device = None


    async def discover(self):
        devices = await BleakScanner.discover(5.0, return_adv=True)
        for device in devices:
            advertisement_data = devices[device][1]
            print(device, advertisement_data.local_name, advertisement_data.service_uuids, advertisement_data.rssi)
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
            print("Disconnecting...")
            await self.client.disconnect()
            print("Disconnected!")
        except:
            raise Exception("Failed to disconnect")

#this code is ai generated - change back to my code
    async def notify(self):

        """Starts notification subscription on the button characteristic."""
        if self.client and self.client.is_connected:
            # await asyncio.sleep(1.5)
            # for service in self.client.services:
            #     print(service.uuid + ":")
            #     for characteristic in service.characteristics:
            #         print(characteristic.uuid)

            #print(f"Characteristic found: {characteristic.uuid}. Attempting to subscribe...")


            # Start notifying using the characteristic UUID
            #await self.client.start_notify(BUTTON_CHAR_UUID, self.button_handler)
            #await self.client.start_notify(TILT_CHAR_UUID, self.sensor_handler)
            #await self.client.start_notify(STEP_CHAR_UUID, self.sensor_handler)
            print(f"Subscribed to notifications on {BUTTON_CHAR_UUID}")

    def sensor_handler(self, sender, data):
        """Handler for incoming characteristic notifications."""
        # Convert byte data to integer or string for display
        print(int(round(time.time() * 1000)))
        value = data.decode('utf-8')
        print(f"Notification from handle {sender}: {value}")

    async def button_handler(self, sender, data):
        print("Message recieved, sending back")
        await self.client.write_gatt_char(MESSAGE_CHAR_UUID,b'\x01\x02\x03', response = True)


async def main():
    device = DeviceBLE()
    try:
        await device.connect()
        await device.notify()
        # Keep running indefinitely to receive notifications
        print("\nListening for button presses... Press Ctrl+C to stop")
        while True:
            await asyncio.sleep(1)  # Keep the event loop alive

    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await device.disconnect()


asyncio.run(main())