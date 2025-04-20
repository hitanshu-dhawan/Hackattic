import os
import requests
import json
import hashlib


# 1. Get Access Token and Set up URLs
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

BASE_URL = "https://hackattic.com/challenges/mini_miner"
PROBLEM_URL = f"{BASE_URL}/problem?access_token={ACCESS_TOKEN}"
SOLUTION_URL = f"{BASE_URL}/solve?access_token={ACCESS_TOKEN}" + "&playground=1"

# 2. Fetch the Problem Data
print("\nFetching problem...")
response = requests.get(PROBLEM_URL)
problem_data = response.json()
difficulty = int(problem_data['difficulty'])
block = problem_data['block']
print(f"Successfully fetched problem.")
print(f"Difficulty: {difficulty} bits")

# 3. Mine the Nonce
print("\nStarting mining process...")
nonce = 0
while True:
    # Update the nonce in the block dictionary
    block['nonce'] = nonce

    # Serialize the block to JSON string:
    # - Keys must be sorted alphabetically.
    # - No extra whitespace (most compact representation).
    block_string = json.dumps(block, sort_keys=True, separators=(',', ':'))
    block_bytes = block_string.encode('utf-8')

    # Calculate the SHA256 hash
    hash_object = hashlib.sha256(block_bytes)
    hex_hash = hash_object.hexdigest()

    # Convert the hex hash to an integer
    hash_int = int(hex_hash, 16)

    # Calculate Target
    # The hash, interpreted as a 256-bit integer, must be less than the target value.
    # Target = 2**(256 - difficulty)
    # We use bit shifting (1 << n is equivalent to 2**n for integers)
    target_value = 1 << (256 - difficulty)

    # Check if the hash integer is less than the target value
    if hash_int < target_value:
        break # Exit the loop, we found the nonce

    # Increment nonce
    nonce += 1

# We have exited the loop, nonce is found
print(f"\n--- Nonce Found! ---")
print(f"Nonce: {nonce}")
print(f"Hash:  {hex_hash}")
print(f"Block: {block_string}")

# 4. Submit the Solution
print("\nSubmitting solution...")
solution_payload = {"nonce": nonce}
print(f"Solution payload: {solution_payload}")
solve_response = requests.post(SOLUTION_URL, json=solution_payload)
result = solve_response.json()
print("\n--- Submission Result ---")
print(json.dumps(result, indent=2))  # Pretty-print the JSON response
