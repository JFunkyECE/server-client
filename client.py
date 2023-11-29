import requests
import time

raspberry_pi_ip = '10.0.0.49'  # Replace with your Raspberry Pi's IP address
port = 8000
url = f'http://{raspberry_pi_ip}:{port}'

while True:
    try:
        response = requests.get(url)
        print(f"Response from server: {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")
    
    time.sleep(1)  # Wait for 1 second between requests
