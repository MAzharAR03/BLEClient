import asyncio
import websockets
from bleak import BleakScanner

from DeviceBLE import DeviceBLE
INPUT_SERVICE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
MAX_PITCH = 1.57079633


async def discover():
    devices = await BleakScanner.discover(5.0, return_adv=True)
    results = []
    for device in devices:
        advertisement_data = devices[device][1]
        print(advertisement_data)
        if INPUT_SERVICE_UUID in advertisement_data.service_uuids:
            if advertisement_data.rssi > -90:
                results.append(device)
    return results


async def main():
    scan = await discover()
    connectedDevices = []

    for address in scan:
        d = DeviceBLE()
        d.address = address
        connectedDevices.append(d)


    async def run_device(device):
        # async def runServer():
        #         async with websockets.serve(
        #                 device.socketHandler.handle_websocket,
        #                 device.socketHandler.url,
        #                 device.socketHandler.port
        #         ):
        #             await asyncio.Future()
        #
        # asyncio.create_task(runServer())
        await device.connect()
        await device.notify()
        
        #await device.send_file("Xbox controller.json")


    try:
        await asyncio.gather(*[run_device(d) for d in connectedDevices])
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        for d in connectedDevices:
            await d.disconnect()


asyncio.run(main())