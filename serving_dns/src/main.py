import os
import requests
from dnslib.server import DNSServer
from dnslib import QTYPE, RR, A, AAAA, TXT, RP
import base64


# API Endpoints
BASE_URL = "https://hackattic.com"
PROBLEM_ENDPOINT = "/challenges/serving_dns/problem"
SOLUTION_ENDPOINT = "/challenges/websocket_chit_chat/solve"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


def fetch_dns_records():
    """
    Fetch DNS records from the problem endpoint
    """

    problem_url = f"{BASE_URL}{PROBLEM_ENDPOINT}?access_token={ACCESS_TOKEN}"
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

    class CustomResolver:

        def __init__(self):
            super().__init__()
            self.records = records

        def resolve(self, request, handler):

            # Log the request
            print("Received DNS request:")
            print(request)

            # Extract details
            domain = str(request.q.qname).rstrip('.') # Domain name
            qtype = request.q.qtype # Query type (e.g., A, AAAA, TXT)

            reply = request.reply()

            # Find matching records
            matching_records = []
            for record in self.records:
                record_name = record['name']

                # Check if the record name matches exactly
                if domain == record_name:
                    matching_records.append(record)

                # Check if the record is a wildcard (e.g., "*.example.com")
                elif record_name.startswith('*.'):
                    # Extract the part after "*."
                    wildcard_suffix = record_name[2:]

                    # Check if the queried domain ends with this suffix
                    if domain.endswith(wildcard_suffix):
                        matching_records.append(record)

            print(f"Matching records for {domain}: {len(matching_records)}")

            # Process matching records
            for record in matching_records:
                try:
                    # Extract record type and data
                    record_type = record['type']
                    record_data = record['data']

                    rr_data = None

                    # Handle different DNS record types
                    if record_type == 'A' and qtype == QTYPE.A:
                        rr_data = A(record_data)

                    elif record_type == 'AAAA' and qtype == QTYPE.AAAA:
                        rr_data = AAAA(record_data)

                    elif record_type == 'TXT' and qtype == QTYPE.TXT:
                        # Decode base64 data for TXT records
                        decoded_data = base64.b64decode(record_data).decode()
                        rr_data = TXT(decoded_data)

                    elif record_type == 'RP' and qtype == QTYPE.RP:
                        rr_data = RP(record_data)

                    # If a valid record was created, add it to the response
                    if rr_data:
                        rr = RR(rname=domain, rtype=qtype, rdata=rr_data)
                        reply.add_answer(rr)

                except Exception as e:
                    print(f"Error processing record {record}: {e}")

            return reply

    return CustomResolver()


def start_dns_server(records, address, port):
    """
    Start DNS server using dnslib
    """

    resolver = create_dns_resolver(records)

    # Create and start DNS server
    dns_server = DNSServer(resolver, address=address, port=port)
    
    print(f"Starting DNS server on {address}:{port}")
    dns_server.start_thread()
    return dns_server


def submit_solution(dns_ip, dns_port):
    """
    Submit solution to the challenge endpoint
    """

    solve_url = f"{BASE_URL}{SOLUTION_ENDPOINT}?access_token={ACCESS_TOKEN}"
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
    dns_address = '0.0.0.0' # Listen on all interfaces
    dns_port = 2053

    try:
        # Fetch DNS records
        records = fetch_dns_records()

        # Start DNS server
        dns_server = start_dns_server(records, address=dns_address, port=dns_port)

        while True:
            # Keep the server running
            pass

    except KeyboardInterrupt:
        print("Shutting down server...")
        dns_server.stop()
    except Exception as e:
        print(f"Exception: {e}")


if __name__ == '__main__':
    main()
