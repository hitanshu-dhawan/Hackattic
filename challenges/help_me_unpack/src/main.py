import os
import requests
import base64
from struct import unpack

# Get access token from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# API endpoints
PROBLEM_URL = f"https://hackattic.com/challenges/help_me_unpack/problem?access_token={ACCESS_TOKEN}"
SOLVE_URL = f"https://hackattic.com/challenges/help_me_unpack/solve?access_token={ACCESS_TOKEN}" + "&playground=1"

# Fetch the problem statement
response = requests.get(PROBLEM_URL)
data = response.json()

# Decode base64-encoded bytes
encoded_bytes = data["bytes"]
byte_data = base64.b64decode(encoded_bytes)

# Print the byte data
print("Byte data:", byte_data)

# Unpacking the values
signed_int = unpack("<i", byte_data[:4])[0]           # 4 bytes (little-endian, signed int)
unsigned_int = unpack("<I", byte_data[4:8])[0]        # 4 bytes (little-endian, unsigned int)
signed_short = unpack("<h", byte_data[8:10])[0]       # 2 bytes (little-endian, signed short)
float_value = unpack("<f", byte_data[12:16])[0]       # 4 bytes (little-endian, float)
double_value = unpack("<d", byte_data[16:24])[0]      # 8 bytes (little-endian, double)
big_endian_double = unpack(">d", byte_data[24:32])[0] # 8 bytes (big-endian, double)

# Prepare solution payload
solution_payload = {
    "int": signed_int,
    "uint": unsigned_int,
    "short": signed_short,
    "float": float_value,
    "double": double_value,
    "big_endian_double": big_endian_double
}

# Print the unpacked values
print("Unpacked values:")
print("Signed int (4 bytes, little-endian):", signed_int)
print("Unsigned int (4 bytes, little-endian):", unsigned_int)
print("Signed short (2 bytes, little-endian):", signed_short)
print("Float (4 bytes, little-endian):", float_value)
print("Double (8 bytes, little-endian):", double_value)
print("Big-endian double (8 bytes, big-endian):", big_endian_double)

# Submit the solution
solve_response = requests.post(SOLVE_URL, json=solution_payload)
result = solve_response.json()

# Print the result
print("Solution submitted. Response:", result)
