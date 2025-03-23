import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(f"Echo: {message}")

async def main():
    server = await websockets.serve(echo, "localhost", 8765)
    await server.wait_closed()

asyncio.run(main())  # Ensures proper event loop management
