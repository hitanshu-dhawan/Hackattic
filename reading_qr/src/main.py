import os
import cv2
import requests
import numpy as np
from pyzbar.pyzbar import decode

# Access token from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# API Endpoints
PROBLEM_URL = f"https://hackattic.com/challenges/reading_qr/problem?access_token={ACCESS_TOKEN}"
SUBMIT_URL = f"https://hackattic.com/challenges/reading_qr/solve?access_token={ACCESS_TOKEN}" + "&playground=1"

def fetch_qr_image():
    """Fetch the QR image URL from the problem endpoint."""
    print("[INFO] Fetching QR image URL...")
    response = requests.get(PROBLEM_URL)
    print(f"[DEBUG] Response Status Code: {response.status_code}")

    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch QR image. Response: {response.text}")
        response.raise_for_status()

    data = response.json()
    print(f"[DEBUG] API Response: {data}")
    return data["image_url"]

def download_image(image_url):
    """Download the image and return it as an OpenCV format."""
    print(f"[INFO] Downloading image from: {image_url}")
    response = requests.get(image_url)
    print(f"[DEBUG] Image Response Status Code: {response.status_code}")

    if response.status_code != 200:
        print(f"[ERROR] Failed to download image. Response: {response.text}")
        response.raise_for_status()

    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        print("[ERROR] Failed to decode image.")
        raise ValueError("Image decoding failed")

    print("[INFO] Image downloaded and decoded successfully.")
    return image

def decode_qr(image):
    """Decode QR code using pyzbar."""
    print("[INFO] Attempting to decode QR code...")
    qr_codes = decode(image)

    if not qr_codes:
        print("[WARNING] No QR Code detected in the image.")
        return None

    qr_data = qr_codes[0].data.decode("utf-8")  # Assuming only one QR code
    print(f"[SUCCESS] QR Code Decoded: {qr_data}")
    return qr_data

def submit_solution(qr_code_data):
    """Submit the extracted QR code data."""
    print(f"[INFO] Submitting QR code data: {qr_code_data}")
    payload = {"code": qr_code_data}

    response = requests.post(SUBMIT_URL, json=payload)
    print(f"[DEBUG] Submission Response Status Code: {response.status_code}")

    if response.status_code != 200:
        print(f"[ERROR] Submission failed. Response: {response.text}")
        response.raise_for_status()

    print(f"[SUCCESS] Submission Response: {response.json()}")

def main():
    try:
        print("\n=== Starting QR Code Reader ===")
        image_url = fetch_qr_image()

        image = download_image(image_url)
        qr_code_data = decode_qr(image)

        if qr_code_data:
            submit_solution(qr_code_data)
        else:
            print("[ERROR] No valid QR Code found. Cannot submit solution.")

    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    main()
