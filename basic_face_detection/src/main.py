import os
import cv2
import requests
import numpy as np

# Load the OpenCV pre-trained face detector
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Access token from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# API Endpoints
PROBLEM_URL = f"https://hackattic.com/challenges/basic_face_detection/problem?access_token={ACCESS_TOKEN}"
SUBMIT_URL = f"https://hackattic.com/challenges/basic_face_detection/solve?access_token={ACCESS_TOKEN}" + "&playground=1"

def fetch_image_url():
    """Fetch the image URL from the problem endpoint."""
    print("[INFO] Fetching image URL...")
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
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    print("[INFO] Image downloaded and decoded successfully.")
    return image

def detect_faces(image):
    """Detect faces in the 8x8 grid and return their coordinates."""
    print("[INFO] Detecting faces in the 8x8 grid...")
    h, w, _ = image.shape
    tile_h, tile_w = h // 8, w // 8
    face_tiles = []
    
    for i in range(8):
        for j in range(8):
            tile = image[i * tile_h: (i + 1) * tile_h, j * tile_w: (j + 1) * tile_w]
            gray_tile = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(gray_tile, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) > 0:
                print(f"[DEBUG] Face detected at tile: ({i}, {j})")
                face_tiles.append([i, j])
    
    print(f"[INFO] Total faces detected: {len(face_tiles)}")
    return face_tiles

def submit_solution(face_tiles):
    """Submit the detected face tiles."""
    print(f"[INFO] Submitting detected faces: {face_tiles}")
    payload = {"face_tiles": face_tiles}
    response = requests.post(SUBMIT_URL, json=payload)
    print(f"[DEBUG] Submission Response Status Code: {response.status_code}")
    print(f"[DEBUG] Submission Response JSON: {response.json()}")
    response.raise_for_status()
    return response.json()

def main():
    try:
        print("\n=== Starting Face Detection Challenge ===")
        image_url = fetch_image_url()
        image = download_image(image_url)
        face_tiles = detect_faces(image)
        response = submit_solution(face_tiles)
        print("[SUCCESS] Challenge Completed:", response)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
