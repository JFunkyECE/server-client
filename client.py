import requests
import os
import time

raspberry_pi_ip = '10.0.0.49'  # Raspberry Pi's IP address
port = 8000
base_url = f'http://{raspberry_pi_ip}:{port}'
counter_url = f'{base_url}/counter'  # For counter requests
image_url = f'{base_url}/image'
csv_url = f'{base_url}/csv'
gps_poll_url = f'{base_url}/gps-poll'  # For GPS polling

desktop_path = os.path.expanduser('~/Desktop')
image_path = os.path.join(desktop_path, 'downloaded_image.jpg')
csv_path = os.path.join(desktop_path, 'downloaded_file.csv')

def request_counter():
    try:
        response = requests.get(counter_url)
        print(f"Counter response: {response.text}")
    except Exception as e:
        print(f"Error requesting counter: {e}")

def request_image():
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, 'wb') as file:
                file.write(response.content)
            print(f"Image saved as '{image_path}'")
        else:
            print("Failed to retrieve image")
    except Exception as e:
        print(f"Error requesting image: {e}")

def request_csv():
    try:
        response = requests.get(csv_url)
        if response.status_code == 200:
            with open(csv_path, 'wb') as file:
                file.write(response.content)
            print(f"CSV file saved as '{csv_path}'")
        else:
            print("Failed to retrieve CSV file")
    except Exception as e:
        print(f"Error requesting CSV file: {e}")

def request_gps_poll():
    try:
        response = requests.get(gps_poll_url)
        print("GPS polling started.")
    except Exception as e:
        print(f"Error starting GPS polling: {e}")

def main():
    # Request counter a few times
    for _ in range(3):
        request_counter()
        time.sleep(1)

    # Start GPS polling
    request_gps_poll()
    time.sleep(1)

    # Request image
    request_image()
    time.sleep(1)

    # Request counter a few more times
    for _ in range(2):
        request_counter()
        time.sleep(1)

    # Request CSV file
    request_csv()

if __name__ == "__main__":
    main()
