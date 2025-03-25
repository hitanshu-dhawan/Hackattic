import os
import asyncio
import websockets
import time
import requests
import re

# API Endpoints
BASE_URL = "https://hackattic.com"
PROBLEM_ENDPOINT = "/challenges/websocket_chit_chat/problem"
SOLUTION_ENDPOINT = "/challenges/websocket_chit_chat/solve"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Allowed intervals
ALLOWED_INTERVALS = [700, 1500, 2000, 2500, 3000]

def closest_interval(value):
    """Find the closest allowed interval."""
    return min(ALLOWED_INTERVALS, key=lambda x: abs(x - value))

async def websocket_chit_chat():
    """Main function to retrieve the problem, connect to the WebSocket, and solve the challenge."""
    
    # Get the one-time token
    print("[INFO] Fetching problem token...")
    response = requests.get(f"{BASE_URL}{PROBLEM_ENDPOINT}?access_token={ACCESS_TOKEN}")
    problem_data = response.json()
    token = problem_data.get("token")
    
    if not token:
        print("[ERROR] Failed to retrieve the token.")
        return
    
    websocket_url = f"wss://hackattic.com/_/ws/{token}"
    print(f"[INFO] Connecting to WebSocket: {websocket_url}")

    print("\n")
    
    async with websockets.connect(websocket_url) as websocket:
        last_ping_time = None
        
        try:
            while True:
                message = await websocket.recv()
                print(f"[RECEIVED] {message}")

                current_time = time.time() * 1000  # Convert to milliseconds

                if message.startswith("hello!"):
                    # Initialize last_ping_time when we receive the hello message
                    last_ping_time = current_time
                    print("[INFO] Started counting time from connection open.")
                    continue
                
                if message == "ping!":
                    if last_ping_time is not None:
                        # Calculate the interval based on time difference
                        interval = round(current_time - last_ping_time)  # Already in milliseconds
                        closest = closest_interval(interval)
                        print(f"[DEBUG] Calculated interval: {interval} ms, Closest interval: {closest} ms")
                        
                        # Send the closest detected interval back to the server
                        await websocket.send(str(closest))
                        print(f"[SENT] {closest}")
                    
                    # Update last_ping_time for next calculation
                    last_ping_time = current_time
                    continue
                
                if message == "good!":
                    # Ignore this message, continue listening for the next ping
                    continue

                if message.startswith("congratulations!"):
                    # Extract secret key and submit it
                    print("[INFO] Received secret message!")
                    
                    match = re.search(r'"([^"]*)"', message)
                    secret = match.group(1)
                    print(f"[SUCCESS] Secret received: {secret}")
                    
                    # Submit the solution
                    print("[INFO] Submitting secret to solution endpoint...")
                    submission_response = requests.post(
                        f"{BASE_URL}{SOLUTION_ENDPOINT}?access_token={ACCESS_TOKEN}" + "&playground=1",
                        json={"secret": secret}
                    )
                    print(f"[RESULT] {submission_response.json()}")
                    break
                
        except websockets.exceptions.ConnectionClosed:
            print("[ERROR] Connection closed by server.")
        except Exception as e:
            print(f"[ERROR] {e}")

    print("\n")

# Run the async function
print("[INFO] Starting WebSocket chit chat solver...")
asyncio.run(websocket_chit_chat())
