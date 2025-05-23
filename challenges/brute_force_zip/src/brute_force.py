import os
import requests
import zipfile
import itertools
import string
import time
from io import BytesIO

def get_zip_url():
    access_token = os.getenv("ACCESS_TOKEN")
    url = f"https://hackattic.com/challenges/brute_force_zip/problem?access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("zip_url")
    return None

def download_zip(zip_url, filename="package.zip"):
    response = requests.get(zip_url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    return None

def brute_force_zip(zip_filename):
    chars = string.ascii_lowercase + string.digits
    
    with zipfile.ZipFile(zip_filename) as z:
        for length in range(6, 3, -1):  # 6 to 4 characters
            for password in map(''.join, itertools.product(chars, repeat=length)):
                try:
                    print(f"Trying password: {password}")
                    z.setpassword(password.encode())
                    with z.open("secret.txt") as secret_file:
                        return secret_file.read().decode().strip(), password
                except:
                    continue
    
    return None, None

def submit_solution(secret):
    access_token = os.getenv("ACCESS_TOKEN")
    url = f"https://hackattic.com/challenges/brute_force_zip/solve?access_token={access_token}" + "&playground=1"
    response = requests.post(url, json={"secret": secret})
    print("Solution submitted. Response:", response.json())
    return response.status_code == 200

def main():
    start_time = time.time()
    
    zip_url = get_zip_url()
    if not zip_url:
        print("Failed to get ZIP URL")
        return
    
    zip_filename = download_zip(zip_url)
    if not zip_filename:
        print("Failed to download ZIP file")
        return
    
    print(f"ZIP file downloaded as {zip_filename}")
    
    secret, password = brute_force_zip(zip_filename)
    if secret:
        print(f"Success! Password: {password}, Secret: {secret}")
        if submit_solution(secret):
            print("Solution submitted successfully!")
        else:
            print("Failed to submit solution")
    else:
        print("Brute-force failed")
    
    # Delete the ZIP file
    try:
        os.remove(zip_filename)
        print(f"Deleted {zip_filename}")
    except Exception as e:
        print(f"Failed to delete {zip_filename}: {e}")
    
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
