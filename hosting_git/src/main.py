#!/usr/bin/env python3
import requests
import os
import sys
import subprocess
import argparse

# Your access token
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_URL = "https://hackattic.com"

def get_problem_data():
    """Fetch the problem data from the endpoint"""

    url = f"{BASE_URL}/challenges/hosting_git/problem?access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to get problem data: {response.status_code}")
        sys.exit(1)
    return response.json()

def run_command(command, as_user=None):
    """Run a command with subprocess, optionally as another user"""

    if as_user:
        command = f"sudo -u {as_user} bash -c \"{command}\""
    
    print(f"Running: {command}")
    proc = subprocess.run(command, capture_output=True, text=True, shell=True)
    
    if proc.returncode != 0:
        print(f"Command failed with exit code {proc.returncode}")
        print(f"STDOUT: {proc.stdout}")
        print(f"STDERR: {proc.stderr}")
        sys.exit(1)
    
    return proc.stdout.strip()

def setup_user_and_repo(username, ssh_key, repo_path):
    """
    Set up the user and git repository

    Setting Up the Server: https://git-scm.com/book/en/v2/Git-on-the-Server-Setting-Up-the-Server
    """

    # Check if user already exists
    try:
        subprocess.run(f"id {username}", capture_output=True, text=True, check=True, shell=True)
        print(f"User {username} already exists")
    except:
        # Create the user if it doesn't exist
        print(f"Creating user {username}")
        run_command(f"sudo adduser --disabled-password --gecos '' {username}")
    
    # Create .ssh directory and authorized_keys file
    run_command(f"mkdir -p /home/{username}/.ssh", as_user=username)
    run_command(f"chmod 700 /home/{username}/.ssh", as_user=username)
    run_command(f"touch /home/{username}/.ssh/authorized_keys", as_user=username)
    run_command(f"chmod 600 /home/{username}/.ssh/authorized_keys", as_user=username)
    
    # Add the SSH key to authorized_keys
    ssh_key_path = f"/home/{username}/.ssh/authorized_keys"
    run_command(f"echo '{ssh_key}' > {ssh_key_path}", as_user=username)
    # run_command(f"sudo chown -R {username}:{username} /home/{username}/.ssh")
    
    # Create repository directory
    repo_full_path = f"/home/{username}/{repo_path}"
    # repo_dir = os.path.dirname(repo_full_path)
    run_command(f"mkdir -p {repo_full_path}", as_user=username)
    # run_command(f"sudo chown -R {username}:{username} {repo_dir}")
    
    # Initialize bare git repository
    run_command(f"mkdir -p {repo_full_path}", as_user=username)
    # run_command(f"sudo chown -R {username}:{username} {repo_full_path}")
    run_command(f"cd {repo_full_path} && git init --bare", as_user=username)
    
    return repo_full_path

def trigger_push(push_token, repo_host):
    """Trigger a push from the hackattic server"""

    url = f"{BASE_URL}/_/git/{push_token}"
    data = {"repo_host": repo_host}

    print(f"Triggering push with data: {data}")
    
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to trigger push: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    print("Push triggered successfully")
    return response.json()

def submit_solution(secret):
    """Submit the solution to hackattic"""
    url = f"{BASE_URL}/challenges/hosting_git/solve?access_token={ACCESS_TOKEN}"
    data = {"secret": secret}
    
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to submit solution: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    print("Solution submitted successfully!")
    return response.json()

def extract_secret(username, repo_path):
    """Clone the repository and extract the secret from solution.txt"""
    temp_dir = "/tmp/git_challenge"
    run_command(f"rm -rf {temp_dir}")
    run_command(f"mkdir -p {temp_dir}")
    
    # Clone the repo locally
    repo_dir = os.path.dirname(repo_path)
    repo_name = os.path.basename(repo_path)
    
    run_command(f"cd {temp_dir} && git clone /home/{username}/{repo_path} cloned_repo")
    
    # Extract the secret from solution.txt
    secret = run_command(f"cat {temp_dir}/cloned_repo/solution.txt")
    return secret

def main():

    parser = argparse.ArgumentParser(description="Hosting Git")
    parser.add_argument("--public-ip", required=True, help="Public IPv4 address to submit the solution")

    args = parser.parse_args()
    public_ip = args.public_ip
    
    # Get problem data
    print("Fetching problem data...")
    data = get_problem_data()
    
    username = data["username"]
    ssh_key = data["ssh_key"]
    repo_path = data["repo_path"]
    push_token = data["push_token"]
    
    print(f"Username: {username}")
    print(f"Repo path: {repo_path}")
    print(f"SSH Key: {ssh_key}")
    print(f"Push token: {push_token}")
    
    # Setup user and repo
    print("Setting up user and repository...")
    setup_user_and_repo(username, ssh_key, repo_path)
    
    # Trigger push
    print("Triggering push...")
    push_result = trigger_push(push_token, public_ip)
    print(f"Push result: {push_result}")
    
    # Extract secret
    # print("Extracting secret...")
    # secret = extract_secret(username, repo_path)
    # print(f"Secret found: {secret}")
    
    # Submit solution
    # print("Submitting solution...")
    # solution_result = submit_solution(secret)
    # print(f"Solution result: {solution_result}")
    
    print("Challenge completed successfully!")

if __name__ == "__main__":
    main()