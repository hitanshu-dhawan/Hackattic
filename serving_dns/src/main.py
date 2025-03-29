import requests
import subprocess
import re
import socket
import base64
from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, QTYPE, RR, A, AAAA, TXT, RP
import urllib.parse

def fetch_dns_records(access_token):
    """
    Fetch DNS records from the problem endpoint
    """
    problem_url = f"https://hackattic.com/challenges/serving_dns/problem?access_token={access_token}"
    print("Fetching DNS records...")
    
    try:
        response = requests.get(problem_url)
        response.raise_for_status()
        records = response.json()['records']
        
        print("DNS records successfully retrieved:")
        for record in records:
            print(f"- {record['name']} ({record['type']}): {record['data']}")
        
        return records
    except Exception as e:
        print(f"Failed to fetch records: {e}")
        raise

def create_dns_resolver(records):
    """
    Create a custom DNS resolver that handles specific records
    """
    class CustomResolver(BaseResolver):
        def __init__(self):
            super().__init__()
            self.records = records

        def resolve(self, request, handler):
            # Extract query details
            reply = request.reply()
            qname = str(request.q.qname).rstrip('.')
            qtype = request.q.qtype

            # Find matching records
            matching_records = [
                record for record in self.records 
                if (record['name'] == qname or 
                    (record['name'].startswith('*.') and 
                     qname.endswith(record['name'][2:])))
            ]

            # Process matching records
            for record in matching_records:
                try:
                    # Map record types
                    type_map = {
                        'A': (QTYPE.A, A),
                        'AAAA': (QTYPE.AAAA, AAAA),
                        'TXT': (QTYPE.TXT, TXT),
                        'RP': (QTYPE.RP, RP)
                    }

                    if record['type'] in type_map and qtype == type_map[record['type']][0]:
                        rr_class = type_map[record['type']][1]
                        
                        # Special handling for TXT (base64 decoding)
                        data = base64.b64decode(record['data']).decode() if record['type'] == 'TXT' else record['data']

                        # Create appropriate record type
                        rr = RR(
                            rname=qname,
                            rtype=qtype,
                            rdata=rr_class(data)
                        )
                        reply.add_answer(rr)
                except Exception as e:
                    print(f"Error processing record {record}: {e}")

            return reply

    return CustomResolver()

def start_dns_server(records, port=2053):
    """
    Start DNS server using dnslib
    """
    resolver = create_dns_resolver(records)
    
    # Create and start DNS server
    dns_server = DNSServer(resolver, port=port, address='localhost')
    
    print(f"Starting DNS server on localhost:{port}")
    dns_server.start_thread()
    return dns_server

def start_cloudflare_tunnel(dns_port):
    """
    Start Cloudflare tunnel and extract external URL
    """
    try:
        # Start cloudflared tunnel in background
        process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', f'http://localhost:{dns_port}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        tunnel_url = None

        # Read the output line by line
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Print log for debugging

            # Regex to find the tunnel URL
            match = re.search(r"(?P<url>https://[^\s]+\.trycloudflare\.com)", line)
            if match:
                tunnel_url = match.group("url")
                break

        if tunnel_url:
            print(f"\nCloudflare tunnel created: {tunnel_url}")
            return tunnel_url
        else:
            print("\nFailed to extract Cloudflare tunnel URL")
            return None

    except Exception as e:
        print(f"Error starting Cloudflare tunnel: {e}")
        return None

def extract_dns_ip(tunnel_url):
    """
    Robust IP extraction from tunnel URL
    """
    try:
        # Parse the URL
        parsed_url = urllib.parse.urlparse(tunnel_url)
        hostname = parsed_url.hostname

        # Try different methods to resolve IP
        try:
            # First, try direct socket resolution
            ip_address = socket.gethostbyname(hostname)
            print(f"Resolved IP using socket.gethostbyname(): {ip_address}")
            return ip_address
        except socket.gaierror:
            # If that fails, try alternative methods
            try:
                # Try getting all possible addresses
                addrinfo = socket.getaddrinfo(hostname, None)
                ip_address = addrinfo[0][4][0]
                print(f"Resolved IP using socket.getaddrinfo(): {ip_address}")
                return ip_address
            except Exception as e:
                print(f"Failed to resolve IP using getaddrinfo(): {e}")
                
                # Last resort: manual parsing
                match = re.search(r'([^.]+)', hostname)
                if match:
                    fallback_hostname = f"{match.group(1)}.trycloudflare.com"
                    try:
                        fallback_ip = socket.gethostbyname(fallback_hostname)
                        print(f"Resolved IP using fallback method: {fallback_ip}")
                        return fallback_ip
                    except Exception as e:
                        print(f"Fallback IP resolution failed: {e}")

        raise ValueError("Could not resolve tunnel IP")

    except Exception as e:
        print(f"Error extracting DNS IP: {e}")
        raise

def solve_challenge(access_token, dns_ip, dns_port):
    """
    Submit solution to the challenge endpoint
    """
    solve_url = f"https://hackattic.com/challenges/serving_dns/solve?access_token={access_token}"
    solution = {
        "dns_ip": dns_ip,
        "dns_port": dns_port
    }
    
    print("Submitting solution...")
    try:
        response = requests.post(solve_url, json=solution)
        print(f"Solution submission status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error submitting solution: {e}")

def main():
    # Configuration
    access_token = "a606a820e697cfab"
    dns_port = 2053

    try:
        # Fetch DNS records
        records = fetch_dns_records(access_token)

        # Start DNS server
        dns_server = start_dns_server(records, port=dns_port)

        # Start Cloudflare tunnel
        # tunnel_url = start_cloudflare_tunnel(dns_port)
        
        # if tunnel_url:
            # Extract IP from tunnel URL with robust method
            # dns_ip = extract_dns_ip(tunnel_url)
            # print(f"Extracted DNS IP: {dns_ip}")

            # Submit solution
            # solve_challenge(access_token, tunnel_url, dns_port)
        # else:
            # print("Could not complete challenge due to tunnel creation failure")

        while True:
            # Keep the server running
            pass

    except Exception as e:
        print(f"Challenge failed: {e}")

if __name__ == '__main__':
    main()
