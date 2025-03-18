import os
import cv2
import requests
import numpy as np
import pytesseract

# Access token from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# API Endpoints
PROBLEM_URL = f"https://hackattic.com/challenges/visual_basic_math/problem?access_token={ACCESS_TOKEN}"
SUBMIT_URL = f"https://hackattic.com/challenges/visual_basic_math/solve?access_token={ACCESS_TOKEN}"

def fetch_image_url():
    """Fetch the image URL from the problem endpoint."""
    print("[INFO] Fetching image URL from problem endpoint...")
    response = requests.get(PROBLEM_URL)
    print(f"[DEBUG] Response Status Code: {response.status_code}")
    print(f"[DEBUG] Response JSON: {response.json()}")
    response.raise_for_status()
    return response.json()["image_url"]

def download_image(image_url):
    """Download the image and return it as an OpenCV format."""
    print(f"[INFO] Downloading image from: {image_url}")
    response = requests.get(image_url)
    print(f"[DEBUG] Image Response Status Code: {response.status_code}")
    response.raise_for_status()
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
    print("[INFO] Image downloaded and decoded successfully.")
    return image

def extract_text(image):
    """Extract text from image using Tesseract OCR."""
    print("[INFO] Extracting text from image using OCR...")
    custom_config = "--psm 6 -c tessedit_char_whitelist=0123456789+-x÷"
    text = pytesseract.image_to_string(image, config=custom_config)
    print(f"[DEBUG] Extracted Text:\n{text}")
    return text.strip()

def compute_result(math_operations):
    """Computes the final result based on parsed math operations."""
    print("[INFO] Computing result from extracted math operations...")
    result = 0
    for line in math_operations.split("\n"):
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        op, num = parts[0], int(parts[1])
        print(f"[DEBUG] Processing: {op} {num}")
        if op == '+':
            result += num
        elif op == '-':
            result -= num
        elif op == '×':  # Multiplication
            result *= num
        elif op == '÷':  # Floor Division
            result //= num
    print(f"[INFO] Computed Result: {result}")
    return result

def submit_solution(result):
    """Submit the computed result."""
    print(f"[INFO] Submitting result: {result}")
    payload = {"result": result}
    response = requests.post(SUBMIT_URL, json=payload)
    print(f"[DEBUG] Submission Response Status Code: {response.status_code}")
    print(f"[DEBUG] Submission Response JSON: {response.json()}")
    response.raise_for_status()
    return response.json()

def main():
    try:
        print("\n=== Starting Visual Basic Math Challenge ===")
        image_url = fetch_image_url()
        image = download_image(image_url)
        extracted_text = extract_text(image)
        # result = compute_result(extracted_text)
        # response = submit_solution(result)
        # print("[SUCCESS] Challenge Completed:", response)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
