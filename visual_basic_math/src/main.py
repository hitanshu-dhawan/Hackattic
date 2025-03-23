import os
import requests
import webbrowser
from openai import OpenAI

# Access token from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# API Endpoints
PROBLEM_URL = f"https://hackattic.com/challenges/visual_basic_math/problem?access_token={ACCESS_TOKEN}"
SUBMIT_URL = f"https://hackattic.com/challenges/visual_basic_math/solve?access_token={ACCESS_TOKEN}" + "&playground=1"

def fetch_image_url():
    """Fetch the image URL from the problem endpoint."""
    print("[INFO] Fetching image URL from problem endpoint...")
    response = requests.get(PROBLEM_URL)
    print(f"[DEBUG] Response Status Code: {response.status_code}")
    response.raise_for_status()
    response_json = response.json()
    print(f"[DEBUG] Response JSON: {response_json}")
    return response_json["image_url"]

def extract_text_using_gpt(image_url):
    """Extract text from the given image URL using OpenAI's GPT."""
    # https://platform.openai.com/docs/guides/images?api-mode=chat&format=url
    
    print("[INFO] Sending image to GPT for text extraction...")

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Ensure the extracted text consists only of the characters '0123456789+-×÷' while preserving the original formatting. The first character must be one of '+', '-', '×', or '÷', followed by a space, and then a number without any spaces."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": "auto",
                    }
                },
            ],
        }],
    )
    
    extracted_text = response.choices[0].message.content
    print("[DEBUG] Extracted Text:")
    print(extracted_text)
    return extracted_text

def compute_result(math_operations):
    """Computes the final result based on parsed math operations."""
    print("[INFO] Computing result from extracted math operations...")
    result = 0
    for line in math_operations.split("\n"):
        parts = line.strip().split()
        if len(parts) != 2:
            print(f"[WARNING] Skipping invalid line: {line}")
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
        else:
            print(f"[WARNING] Unknown operator encountered: {op}")
    
    print(f"[INFO] Computed Result: {result}")
    return result

def submit_solution(result):
    """Submit the computed result."""
    print(f"[INFO] Submitting result: {result}")
    payload = {"result": result}
    response = requests.post(SUBMIT_URL, json=payload)
    print(f"[DEBUG] Submission Response Status Code: {response.status_code}")
    response.raise_for_status()
    response_json = response.json()
    print(f"[DEBUG] Submission Response JSON: {response_json}")
    return response_json

def main():
    """Main function to execute the challenge."""
    try:
        print("\n=== Starting Visual Basic Math Challenge ===")

        # Fetch image URL from the challenge API
        image_url = fetch_image_url()

        # Open the image URL in browser
        print("[INFO] Opening Image URL in Browser...")
        webbrowser.open(image_url)
        
        # Extract text using GPT model
        extracted_text = extract_text_using_gpt(image_url)
        
        # Compute the mathematical result
        result = compute_result(extracted_text)
        
        # Submit the computed result
        response = submit_solution(result)
        print("[SUCCESS] Challenge Completed:", response)
    
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
