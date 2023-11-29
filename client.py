import requests

raspberry_pi_ip = '10.0.0.49'  # Replace with your Raspberry Pi's IP address
port = 8000
url = f'http://{raspberry_pi_ip}:{port}'
image_url = f'{url}/image'

# Requesting and saving the image
try:
    response = requests.get(image_url)
    if response.status_code == 200:
        with open('downloaded_image.jpg', 'wb') as file:
            file.write(response.content)
        print("Image saved as 'downloaded_image.jpg'")
    else:
        print("Failed to retrieve image")
except Exception as e:
    print(f"Error connecting to server: {e}")
