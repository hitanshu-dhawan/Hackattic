#!/usr/bin/env python3

import os
import requests
import sys
import subprocess
import argparse


# Your Hackattic access token
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
# Base URL for the Hackattic API
BASE_URL = "https://hackattic.com"


def get_problem_data():
    """
    Fetch the problem data from the Hackattic 'hosting_git' challenge endpoint.
    This includes the username, SSH key, repo path, and push token needed for the challenge.
    """

    # Construct the URL for the problem endpoint
    url = f"{BASE_URL}/challenges/hosting_git/problem?access_token={ACCESS_TOKEN}"

    # Make the GET request
    response = requests.get(url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code != 200:
        print(f"Failed to get problem data: {response.status_code}")
        sys.exit(1)
    return response.json()


def run_command(command, as_user=None):
    """
    Run a shell command using subprocess.run.
    Optionally, the command can be run as a specified user using 'sudo -u'.

    Args:
        command (str): The shell command to execute.
        as_user (str, optional): The username to run the command as. Defaults to None (run as current user or root if script uses sudo).

    Returns:
        str: The standard output of the executed command, stripped of leading/trailing whitespace.

    Raises:
        SystemExit: If the command fails (returns a non-zero exit code).
    """

    # If 'as_user' is specified, wrap the command with 'sudo -u <user> bash -c "<command>"'
    # This ensures the command is executed within a shell environment owned by the target user.
    if as_user:
        command = f"sudo -u {as_user} bash -c \"{command}\""
    
    print(f"Running: {command}")

    # Execute the command using subprocess.run
    # capture_output=True: Captures stdout and stderr.
    # text=True: Decodes stdout and stderr as text (UTF-8 by default).
    # shell=True: Executes the command through the shell (necessary for handling pipelines, redirections, and commands like 'cd' if used directly, though 'bash -c' handles this here).
    proc = subprocess.run(command, capture_output=True, text=True, shell=True)
    
    # Check if the command executed successfully (return code 0)
    if proc.returncode != 0:
        print(f"Command failed with exit code {proc.returncode}")
        print(f"STDOUT: {proc.stdout}")
        print(f"STDERR: {proc.stderr}")
        sys.exit(1)
    
    return proc.stdout.strip()


def setup_user_and_repo(username, ssh_key, repo_path):
    """
    Sets up a new system user, configures their SSH access using the provided public key,
    and initializes a bare Git repository in their home directory.

    Follows steps similar to standard Git server setup procedures.
    Ref: https://git-scm.com/book/en/v2/Git-on-the-Server-Setting-Up-the-Server

    Args:
        username (str): The username to create for the challenge.
        ssh_key (str): The public SSH key provided by Hackattic for the user.
        repo_path (str): The relative path within the user's home directory where the Git repo should be created (e.g., 'repo.git').
    """

    # Check if the user already exists using the 'id' command.
    # Using a try-except block to handle the case where 'id' fails (user doesn't exist).
    # `check=True` makes `subprocess.run` raise CalledProcessError if the command fails.
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
    
    # Create repository directory
    repo_full_path = f"/home/{username}/{repo_path}"
    run_command(f"mkdir -p {repo_full_path}", as_user=username)
    
    # Initialize bare git repository
    run_command(f"cd {repo_full_path} && git init --bare", as_user=username)


def trigger_push(push_token, repo_host):
    """
    Sends a request to the Hackattic API to trigger a Git push
    from their server to the repository set up on this machine.

    Args:
        push_token (str): The unique token provided by Hackattic for triggering the push.
        repo_host (str): The public IP address or hostname of this machine where the Git repo is hosted.
    """

    # Construct the URL for the trigger push endpoint
    url = f"{BASE_URL}/_/git/{push_token}"
    # Prepare the data payload for the POST request (the host where the repo is located)
    data = {"repo_host": repo_host}

    print(f"Triggering push with data: {data}")
    
    # Make the POST request with the JSON payload
    response = requests.post(url, json=data)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code != 200:
        print(f"Failed to trigger push: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    print("Push triggered successfully")

    return response.json()


def extract_secret(username, repo_path):
    """
    Extracts the content of the 'solution.txt' file from the HEAD commit
    of the Git repository after Hackattic has pushed to it.

    Args:
        username (str): The user who owns the Git repository.
        repo_path (str): The relative path to the Git repository in the user's home directory.

    Returns:
        str: The content of the 'solution.txt' file (the secret).
    """

    # Construct the full path to the repository    
    repo_full_path = f"/home/{username}/{repo_path}"
    
    # Change directory to repo path and mark it as safe
    # This is needed to avoid "fatal: detected dubious ownership in repository" error
    run_command(f"cd {repo_full_path} && git config --global --add safe.directory {repo_full_path}")
    
    # Extract the secret directly from the HEAD revision of solution.txt
    secret = run_command(f"cd {repo_full_path} && git show HEAD:solution.txt")
    
    return secret


def submit_solution(secret):
    """
    Submits the extracted secret to the Hackattic challenge solve endpoint.

    Args:
        secret (str): The secret content extracted from 'solution.txt'.

    Returns:
        dict: The JSON response from the Hackattic API upon submission.
    """

    # Construct the URL for the solve endpoint
    url = f"{BASE_URL}/challenges/hosting_git/solve?access_token={ACCESS_TOKEN}" + "&playground=1"
    # Prepare the JSON payload containing the secret
    data = {"secret": secret}
    
    # Make the POST request to submit the solution
    response = requests.post(url, json=data)

    # Check if the submission was successful (HTTP status code 200)
    if response.status_code != 200:
        print(f"Failed to submit solution: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    print("Solution submitted successfully!")

    return response.json()


def main():
    """
    Main function to orchestrate the steps for solving the Hackattic 'hosting_git' challenge.
    1. Parses command-line arguments.
    2. Fetches problem data from Hackattic.
    3. Sets up the local user and Git repository.
    4. Triggers Hackattic to push to the repository.
    5. Extracts the secret from the repository.
    6. Submits the secret to Hackattic.
    """

    # Set up argument parser to accept the server's public IP address
    parser = argparse.ArgumentParser(description="Hosting Git")
    parser.add_argument("--public-ip", required=True, help="Public IPv4 address to submit the solution")

    args = parser.parse_args()
    public_ip = args.public_ip
    
    # Get problem data
    print("Fetching problem data...")
    data = get_problem_data()
    
    # Extract necessary details from the problem data
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
    print("Extracting secret...")
    secret = extract_secret(username, repo_path)
    print(f"Secret found: {secret}")
    
    # Submit solution
    print("Submitting solution...")
    solution_result = submit_solution(secret)
    print(f"Solution result: {solution_result}")
    
    print("Challenge completed successfully!")


if __name__ == "__main__":
    main()
