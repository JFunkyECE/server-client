import requests
import os

raspberry_pi_ip = '10.0.0.49'  # Replace with your Raspberry Pi's IP address
port = 8000
url = f'http://{raspberry_pi_ip}:{port}'
image_url = f'{url}/image'

desktop_path = os.path.expanduser('~/Desktop')  # Expands the ~ to the full path of the user's home directory
image_path = os.path.join(desktop_path, 'downloaded_image.jpg')

# Requesting and saving the image
try:
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved as '{image_path}'")
    else:
        print("Failed to retrieve image")
except Exception as e:
    print(f"Error connecting to server: {e}")
