import requests
import os
import time

raspberry_pi_ip = '10.42.0.1'  # Raspberry Pi's IP address
port = 8000
base_url = f'http://{raspberry_pi_ip}:{port}'
counter_url = f'{base_url}/counter'  # For counter requests
image_url = f'{base_url}/image'
csv_url = f'{base_url}/csv'
take_picture_url = f'{base_url}/take-picture'

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

def request_take_picture():
    try:
        response = requests.get(take_picture_url)
        print("Taking Photo")
        if response.status_code == 200:
            print("Photo taken success")
    except Exception as e:
        print(f"Error taking photo: {e}")

def main():

    request_take_picture()

    time.sleep(1)

    # Request image
    request_image()
    time.sleep(1)


    # Request CSV file
    request_csv()


    time.sleep(10)

if __name__ == "__main__":
    main()
