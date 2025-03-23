import asyncio
import websockets

async def send_messages():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        for i in range(5):  # Send 5 pings
            message = f"Ping {i + 1}"
            await websocket.send(message)
            print(f"Sent: {message}")
            
            response = await websocket.recv()
            print(f"Server response: {response}")
            
            await asyncio.sleep(2)  # Wait 2 seconds between pings

asyncio.run(send_messages())
