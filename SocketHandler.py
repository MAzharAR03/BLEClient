import asyncio
import websockets


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