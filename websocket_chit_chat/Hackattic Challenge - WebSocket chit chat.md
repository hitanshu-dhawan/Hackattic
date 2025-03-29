---
url: https://hackattic.com/challenges/websocket_chit_chat
code_url: https://github.com/hitanshu-dhawan/Hackattic
---

# WebSocket chit chat

Hit the problem endpoint, grab a one-time token. The token expires in 60 minutes, so take your time.

Connect to our WebSocket server by appending your token to `wss://hackattic.com/_/ws/$token`.

Before we explain the challenge, know this: the server will send you `ping!` messages in random intervals of `700`, `1500`, `2000`, `2500` or `3000` milliseconds.

So a short while after connecting you'll receive your first `ping!` message. This is your cue to send back the time after which it was sent. Obviously, due to network latency, the time measured on your end will be slightly different than the intended interval - it's your task to measure time and properly detect which interval was used by the server. Depending on your approach, you may even detect that some messages arrive slightly faster than expected. Something to think about.

Anyway, send back the detected interval (e.g. `700`). You have until the next `ping!` message to do so. If you fail to send back a value before then, the next ping won't be a ping, but a message explaining how sorry the server feels about it, but it has to close the connection. If this happens, you'll have to reconnect and start over.

If you send back the proper interval, the server will confirm your answer immediately with a simple `good!` message. These messages don't influence when the `ping!` messages are sent, so ignore those when measuring intervals. Only look at `ping!` messages.

Keep the conversation up sufficiently long, and the server will reward you with a secret key.

Submit that secret key to the solution endpoint and grab your reward.

##### Getting the problem set

`GET /challenges/websocket_chit_chat/problem?access_token=<access_token>`

Problem JSON format will be in the following format:

- `token`: a token to use when connecting to the websocket server

##### Submitting a solution

`POST /challenges/websocket_chit_chat/solve?access_token=<access_token>`

Solution JSON structure:

- `secret`: the secret phrase you got from the websocket server

---
# Solution

##### `server.py`

```python
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
```

##### `client.py`

```python
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
```


#Hackattic
