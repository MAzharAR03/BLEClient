import asyncio

import mss
import websockets
import json
import base64

WS_URL = "ws://localhost:9999"
async def wait_for_type(ws, expected_type, timeout=5.0):
    """Drain incoming messages until we get the expected type or time out."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        remaining = deadline - asyncio.get_event_loop().time()
        raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
        msg = json.loads(raw)
        print(f"  [recv] type={msg.get('type', '(no type)')}")
        if msg.get("type") == expected_type:
            return msg
    raise TimeoutError(f"Never received '{expected_type}'")

async def test_photo():
    """Send a tiny 1x1 red PNG and verify we get a response back."""
    # Minimal valid PNG (1x1 red pixel)
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[1])
        img_bytes = mss.tools.to_png(shot.rgb, shot.size)
    RED_PNG_B64 = base64.b64encode(img_bytes).decode("utf-8")
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"type": "photo_upload", "data": RED_PNG_B64}))
        print("Sent photo, waiting for response...")

        # Loop until we find the photo_response message, ignoring telemetry data
        while True:
            resp = json.loads(await ws.recv())
            if isinstance(resp, dict) and resp.get("type") == "photo_response":
                print("Raw response:", resp)
                print(f"Got photo back. has_gps={resp['has_gps']}, data length={len(resp['data'])}")
                jpg_bytes = base64.b64decode(resp['data'])
                with open("test_photo_result.jpg", "wb") as f:
                    f.write(jpg_bytes)
                print("Saved to test_photo_result.jpg")
                break

async def test_gpx_trail():
    """Simulate Godot doing a 5-step trail."""
    async with websockets.connect(WS_URL) as ws:
        # Take control
        await ws.send(json.dumps({"type": "gpx_start", "lat": 3.1390, "lon": 101.6869}))
        print("GPX started")
        await asyncio.sleep(0.5)

        # Push some points
        points = [
            (3.1391, 101.6870),
            (3.1392, 101.6871),
            (3.1393, 101.6872),
        ]
        for lat, lon in points:
            await ws.send(json.dumps({"type": "gpx_point", "lat": lat, "lon": lon}))
            print(f"Sent point {lat},{lon}")
            await asyncio.sleep(0.2)

        # Stop and get GPX back
        await ws.send(json.dumps({"type": "gpx_stop"}))
        print("Sent stop, waiting for GPX XML...")
        resp = await wait_for_type(ws, "gpx_response", timeout=10.0)
        print(f"Got GPX XML ({len(resp['gpx_xml'])} chars)")
        print(resp["gpx_xml"][:300])  # preview
        with open("test_trail.gpx", "w") as f:
            f.write(resp["gpx_xml"])
        print("Saved to test_trail.gpx")

async def test_emulation_control():
    async with websockets.connect(WS_URL) as ws:
        # Should toggle the checkbox in MainWindow
        await ws.send(json.dumps({"type": "control", "command": "DISABLE_EMULATION"}))
        print("Sent DISABLE_EMULATION — check the checkbox in the server window")
        await asyncio.sleep(2)
        await ws.send(json.dumps({"type": "control", "command": "ENABLE_EMULATION"}))
        print("Sent ENABLE_EMULATION")

# Run one at a time:
asyncio.run(test_photo())
#asyncio.run(test_gpx_trail())
#asyncio.run(test_emulation_control())