import os
import requests
import zipfile
import subprocess
import time
from io import BytesIO

"""
This script automates a known-plaintext attack on an encrypted ZIP file using pkcrack 
(https://github.com/keyunluo/pkcrack). 

The attack works by leveraging a plaintext file inside the ZIP (dunwich_horror.txt), 
which allows recovering the encryption key and decrypting the archive.
"""

def get_zip_url():
    """Fetch the one-time ZIP file URL from the challenge API."""
    access_token = os.getenv("ACCESS_TOKEN")
    url = f"https://hackattic.com/challenges/brute_force_zip/problem?access_token={access_token}"
    print(f"Fetching ZIP URL from: {url}")
    response = requests.get(url)
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        zip_url = response.json().get("zip_url")
        print(f"ZIP URL received: {zip_url}")
        return zip_url
    print("Failed to fetch ZIP URL")
    return None

def download_zip(zip_url, filename="package.zip"):
    """Download the ZIP file from the given URL."""
    print(f"Downloading ZIP file from: {zip_url}")
    response = requests.get(zip_url)
    print(f"Download response status: {response.status_code}")
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"ZIP file saved as: {filename}")
        return filename
    print("Failed to download ZIP file")
    return None

def run_pkcrack():
    """Run pkcrack to recover the ZIP encryption key and decrypt the ZIP file."""
    command = [
        "../../pkcrack/bin/pkcrack",
        "-C", "package.zip", 
        "-c", "dunwich_horror.txt", 
        "-P", "unprotected.zip", 
        "-p", "dunwich_horror.txt", 
        "-d", "decrypted.zip",
        "-a"
    ]
    print("Running pkcrack with command:", " ".join(command))
    result = subprocess.run(" ".join(command), shell=True, capture_output=True, text=True)
    print("pkcrack output:", result.stdout)
    if result.returncode != 0:
        print("Error running pkcrack:", result.stderr)
    else:
        print("pkcrack completed successfully.")
    return "decrypted.zip" if os.path.exists("decrypted.zip") else None

def extract_secret(zip_filename):
    """Extract the secret.txt file from the decrypted ZIP."""
    print(f"Extracting secret from: {zip_filename}")
    try:
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            with zip_ref.open("secret.txt") as secret_file:
                secret = secret_file.read().decode().strip()
                print("Extracted secret:", secret)
                return secret
    except Exception as e:
        print(f"Error extracting secret: {e}")
    return None

def submit_solution(secret):
    """Submit the extracted secret to the challenge API."""
    access_token = os.getenv("ACCESS_TOKEN")
    url = f"https://hackattic.com/challenges/brute_force_zip/solve?access_token={access_token}" + "&playground=1"
    print(f"Submitting solution to: {url}")
    response = requests.post(url, json={"secret": secret})
    print("Solution submission response status:", response.status_code)
    try:
        response_json = response.json()
        print("Response JSON:", response_json)
    except Exception as e:
        print(f"Error parsing response JSON: {e}")
    return response.status_code == 200

def main():
    start_time = time.time()
    print("Starting process...")
    
    zip_url = get_zip_url()
    if not zip_url:
        print("Failed to get ZIP URL")
        return
    
    zip_filename = download_zip(zip_url)
    if not zip_filename:
        print("Failed to download ZIP file")
        return
    
    print(f"ZIP file downloaded as {zip_filename}")
    
    # Run pkcrack
    decrypted_file = run_pkcrack()
    if not decrypted_file:
        print("pkcrack failed to decrypt ZIP.")
        return
    
    secret = extract_secret("decrypted.zip")
    if secret:
        print(f"Secret extracted: {secret}")
    else:
        print("Failed to extract secret")
        return
    
    if submit_solution(secret):
        print("Solution submitted successfully!")
    else:
        print("Failed to submit solution")

    # Delete the ZIP files
    try:
        os.remove(zip_filename)
        print(f"Deleted {zip_filename}")
    except Exception as e:
        print(f"Failed to delete {zip_filename}: {e}")

    try:
        os.remove(decrypted_file)
        print(f"Deleted {decrypted_file}")
    except Exception as e:
        print(f"Failed to delete {decrypted_file}: {e}")
    
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()