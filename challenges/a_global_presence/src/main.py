import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Get Access Token and Problem Data

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PROBLEM_URL = f"https://hackattic.com/challenges/a_global_presence/problem?access_token={ACCESS_TOKEN}"
SOLVE_URL = f"https://hackattic.com/challenges/a_global_presence/solve?access_token={ACCESS_TOKEN}" + "&playground=1"

print("\nFetching problem...")
response = requests.get(PROBLEM_URL)
problem_data = response.json()
presence_token = problem_data["presence_token"]
print(f"Successfully fetched problem. Presence token: {presence_token}")


# 2. Make requests from different countries using a proxy service
# We'll use a hardcoded list of verified working proxies from different countries.

def get_proxies():
	print("[INFO] Using hardcoded proxy list...")

	proxies = [
		{"ip": "8.209.249.89", "port": "3128"},
		{"ip": "181.174.164.221", "port": "80"},
		{"ip": "101.255.69.26", "port": "8080"},
		{"ip": "143.244.143.71", "port": "80"},
		{"ip": "32.223.6.94", "port": "80"},
		{"ip": "193.57.136.40", "port": "80"},
		{"ip": "4.195.16.140", "port": "80"},
		{"ip": "66.36.234.130", "port": "1339"},
		{"ip": "41.33.252.209", "port": "80"},
		{"ip": "4.247.152.147", "port": "3128"},
		{"ip": "50.122.86.118", "port": "80"},
		{"ip": "23.227.39.6", "port": "80"},
		{"ip": "37.187.114.131", "port": "80"},
		{"ip": "57.129.81.201", "port": "8080"},
		{"ip": "138.68.60.8", "port": "80"},
		{"ip": "180.178.109.179", "port": "80"},
		{"ip": "180.211.94.50", "port": "80"},
		{"ip": "126.209.1.14", "port": "80"},
		{"ip": "180.94.80.18", "port": "80"},
		{"ip": "41.223.119.156", "port": "3128"},
		{"ip": "108.141.130.146", "port": "80"},
		{"ip": "147.185.161.94", "port": "80"},
		{"ip": "41.59.90.168", "port": "80"},
		{"ip": "113.160.132.195", "port": "8080"},
		{"ip": "159.69.57.20", "port": "8880"},
		{"ip": "20.54.244.246", "port": "3128"},
		{"ip": "200.174.198.86", "port": "8888"},
	]
	
	print(f"[INFO] Got {len(proxies)} hardcoded proxies.")
	return proxies

def make_request_with_proxy(presence_url, proxy, timeout=5):
	proxy_url = f"http://{proxy['ip']}:{proxy['port']}"
	proxies = {"http": proxy_url, "https": proxy_url}
	try:
		r = requests.get(presence_url, proxies=proxies, timeout=timeout)
		if r.status_code == 200:
			return proxy, r.text.strip()
	except Exception as e:
		pass
	return proxy, None


# 3. Execute the challenge

presence_url = f"https://hackattic.com/_/presence/{presence_token}"
proxies = get_proxies()
checked_in_countries = set()
successful_proxies = []

print("\n[INFO] Starting parallel check-ins from different countries...")

# Use ThreadPoolExecutor to make parallel requests
with ThreadPoolExecutor(max_workers=5) as executor:

	# Submit all proxy requests
	future_to_proxy = {executor.submit(make_request_with_proxy, presence_url, proxy): proxy for proxy in proxies}

	# Process results as they complete
	for future in as_completed(future_to_proxy):
		proxy, result = future.result()
		if result:
			print(f"[SUCCESS] Checked in from {proxy['ip']}:{proxy['port']}. Response: {result}")
			successful_proxies.append(proxy)
			checked_in_countries = set(result.split(","))
			
			# If we have 7+ countries, we can break early
			if len(checked_in_countries) >= 7:
				print(f"[INFO] Got {len(checked_in_countries)} countries : {checked_in_countries}")
				break

print(f"\n[INFO] Countries seen by server: {checked_in_countries}")
if len(checked_in_countries) >= 7:
	print("[INFO] Requirement met. Submitting solution...")
	solve_response = requests.post(SOLVE_URL, json={})
	print("[RESULT]", solve_response.json())
else:
	print("[ERROR] Could not check in from 7 countries.")
	print(f"[INFO] Successfully used {len(successful_proxies)} proxies")
