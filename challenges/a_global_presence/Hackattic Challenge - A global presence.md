---
url: https://hackattic.com/challenges/a_global_presence
code_url: https://github.com/hitanshu-dhawan/Hackattic
---

# A global presence

Connect to the problem endpoint, write down your `presence_token`.

You now have 30 seconds to perform at least 7 requests to the URL `https://hackattic.com/_/presence/$presence_token`.

Here's the catch: every request has to come from a different country.

For every request, the response will return a list of countries that have checked in so far, in the form of a simple string, like so: `PL,NL,DE,CA,RU`. After you've accumulated at least 7, send an empty JSON to the solution endpoint to mark the challenge as solved.

Go!

##### Getting the problem set

`GET /challenges/a_global_presence/problem?access_token=<access_token>`

JSON structure:

- `presence_token`: your token, use with `https://hackattic.com/_/presence/$presence_token`

##### Submitting a solution

`POST /challenges/a_global_presence/solve?access_token=<access_token>`

Send an empty JSON (`{}`) when you're done going around the world.

---
# Solution

## **What is a Proxy?**

- **Definition**: A proxy server is a machine or service that forwards your requests to another server and sends the response back to you.
- **Purpose**: It hides your original IP address and makes the destination server see the request as coming from the proxy, not you.
- **Types of proxies**:
    - **HTTP Proxy** – works at the HTTP request/response level (good for web browsing).
    - **HTTPS Proxy** – same as HTTP proxy, but supports encrypted connections.
    - **SOCKS Proxy** – lower-level protocol that can handle any kind of traffic (not just web).
    - **Transparent proxy** – forwards your request without changing headers (still reveals your IP).
    - **Anonymous or Elite proxy** – hides your IP completely.

---

## **How does it help to hit URLs from different countries?**

Every internet request carries an IP address that reveals the approximate location of the device. If you use a proxy server located in another country:

1. **You send your request to the proxy server.**
2. **The proxy server forwards the request to the destination website.**
3. **The website only sees the proxy’s IP (its country), not yours.**
4. **The proxy then sends the response back to you.**

This allows you to:
- Access region-restricted content.
- Test how websites behave for users in different countries (e.g., QA/testing).
- Scrape web data while appearing to be from different regions.
- Avoid IP bans or throttling when making lots of requests.

---

## **Example**

Let’s say you are in India, but you want to access a website as if you are in the US.

### **Without proxy:**

```plaintext
You → (Your Indian IP) → example.com
```

The website sees your IP as **123.45.67.89 (India)**. If the site only allows US visitors, you’re blocked.

### **With proxy:**

```plaintext
You → (Proxy in US: 50.100.200.10) → example.com
```

The website sees your IP as **50.100.200.10 (US)** — it thinks you're in the US.

---

### **Code Example using Python `requests`**

```python
import requests

# Proxy in US (for demonstration)
proxies = {
    "http": "http://username:password@us-proxy.example.com:8080",
    "https": "http://username:password@us-proxy.example.com:8080"
}

url = "https://api.ipify.org?format=json"  # Returns your public IP

response = requests.get(url, proxies=proxies)
print(response.json())
```

**What happens here?**

- If you run this without a proxy → it will print your actual IP (e.g., an Indian IP).
- If you run it with a US proxy → it will print the proxy’s IP (e.g., 50.100.200.10, which is in the US).

---

## **Key points about proxies**

1. **Speed vs. anonymity trade-off** – Free proxies are usually slow and overloaded; paid proxies are faster and more reliable.
2. **Residential vs. datacenter proxies**
    - Residential proxies use IPs from real devices (harder to block).
    - Datacenter proxies use IPs from cloud servers (faster but easier to detect).
3. **Rotating proxies** – Services that automatically switch IP addresses, useful for web scraping or large-scale testing.

---


#Hackattic 

