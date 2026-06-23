import asyncio
import base64
import datetime
import json
import os
import tempfile

import websockets

from src.config import emulation_state
from src.GPX.GPXManager import GPXManager
from src.GPX.ScreenshotHelper import save_screenshot_with_exif


class SocketHandler:
    def __init__(self, ble_device):
        self.url = "localhost"
        self.port = 9999
        self.queue = asyncio.Queue()
        self.ble_device = ble_device
        self.on_trail_state_changed = None

    async def handle_websocket(self,websocket):
        async def sender():
            while True:
                message = await self.queue.get()
                await websocket.send(message)

        async def receiver():
            async for message in websocket:
                print(f"[receiver] raw message prefix: {message[:60]}")
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                except(json.JSONDecodeError, AttributeError):
                    msg_type = "layout"
                    data = {"payload": message}

                if msg_type == "layout":
                    self.handle_layout(data, message)

                elif msg_type == "control":
                    command = data.get("command")
                    if command == "DISABLE_EMULATION":
                        emulation_state.enabled = False
                    elif command == "ENABLE_EMULATION":
                        emulation_state.enabled = True


                elif msg_type == "photo_upload":
                    asyncio.create_task(self.handle_photo(data))

                elif msg_type == "gpx_point":
                    self.handle_gpx_point(data)

                elif msg_type == "gpx_start":
                    self.handle_gpx_start(data)

                elif msg_type == "gpx_stop":
                    await self.handle_gpx_stop(data)

                elif msg_type == "gpx_release":
                    self.ble_device.gpx_manager = None

                else:
                    print(f"[receiver] unhandled message type: {msg_type}")

        try:
            await asyncio.gather(sender(),receiver())
        except websockets.ConnectionClosed:
            pass

    def handle_layout(self,data, raw_message):
        payload = data.get("payload", raw_message)
        filename = "layout.layout"
        with open(filename, "w") as f:
            f.write(payload)
        print("Layout file received")
        asyncio.create_task(self.ble_device.layout_received(filename))

    async def handle_photo(self, data):
        print("[handle_photo] entered")
        raw_data = data.get("data", "")
        if not raw_data:
            return

        img_bytes = base64.b64decode(raw_data)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(img_bytes)
            png_path = tmp.name

        jpg_path = png_path.replace(".png", ".jpg")
        jpg_b64 = raw_data
        gpx = self.ble_device.gpx_manager
        if gpx is not None:
            lat, lon = gpx.current_position()
            print(f"[handle_photo] tagging with GPS {lat},{lon}")
            try:
                save_screenshot_with_exif(png_path, jpg_path, lat, lon)
                print("[handle_photo] exif save done")
            except Exception as e:
                print(f"[handle_photo] exif failed: {e}")
                jpg_b64 = raw_data
            else:
                with open(jpg_path, "rb") as f:
                    jpg_b64 = base64.b64encode(f.read()).decode("utf-8")
                os.remove(jpg_path)

        self.addMessage(json.dumps({
            "type": "photo_response",
            "data": jpg_b64,
            "has_gps": gpx is not None
        }))


    def handle_gpx_start(self,data):
        lat = data.get("lat", 0.0)
        lon = data.get("lon", 0.0)

        self.ble_device.gpx_manager = GPXManager(lat, lon)
        self.ble_device.gpx_external_control = True

        self.ble_device.gpx_external_control = True
        if self.on_trail_state_changed:
            self.on_trail_state_changed("engine")

        print("GPX control taken by Game Engine.")

    def handle_gpx_point(self, data):
        if not getattr(self.ble_device, "gpx_external_control", False):
            return
        gpx = self.ble_device.gpx_manager
        if gpx is None:
            return
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is not None and lon is not None:
            gpx.add_point(lat, lon)

    async def handle_gpx_stop(self,data):
        gpx = self.ble_device.gpx_manager
        if gpx is None:
            return

        with tempfile.NamedTemporaryFile(suffix=".gpx", delete=False, mode="w") as f:
            f.write(gpx._gpx.to_xml())
            gpx_path = f.name

        with open(gpx_path, "r") as f:
            gpx_xml = f.read()
        os.remove(gpx_path)

        response = json.dumps({
            "type": "gpx_response",
            "gpx_xml": gpx_xml
        })
        self.addMessage(response)

        self.ble_device.gpx_manager = None
        self.ble_device.gpx_external_control = False
        print("GPX control returned from Godot")


    def addMessage(self,message):
         self.queue.put_nowait(message)