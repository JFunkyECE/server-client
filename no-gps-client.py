import requests
import os
import time

raspberry_pi_ip = '10.42.0.1'  # Raspberry Pi's IP address
port = 8000
base_url = f'http://{raspberry_pi_ip}:{port}'
counter_url = f'{base_url}/counter'  # For counter requests
pre_processed_image_url = f'{base_url}/pre-processed-image'
post_processed_image_url = f'{base_url}/post-processed-image'

csv_url = f'{base_url}/csv'
take_picture_url = f'{base_url}/take-picture'
gps_poll_url = f'{base_url}/gps-poll'  # For GPS polling
gps_stop_url = f'{base_url}/gps-stop'

cv_url = f'{base_url}/computer-vision'

desktop_path = os.path.expanduser('~/Desktop/demo-files')
pre_image_path = os.path.join(desktop_path, 'pre-processed-image.jpeg')
post_image_path = os.path.join(desktop_path, 'post-processed-image.jpeg')

csv_path = os.path.join(desktop_path, 'GPS_Data.csv')

def request_computer_vision():
    try:
        response = requests.get(cv_url)
        print(f"Running through Model")
        if response.status_code == 200:
            print("Successful running model")
    except Exception as e:
        print(f"Error requesting CV: {e}")

def request_pre_image():
    try:
        response = requests.get(pre_processed_image_url)
        if response.status_code == 200:
            with open(pre_image_path, 'wb') as file:
                file.write(response.content)
            print(f"Image saved as '{pre_image_path}'")
        else:
            print("Failed to retrieve image")
    except Exception as e:
        print(f"Error requesting image: {e}")

def request_post_image():
    try:
        response = requests.get(post_processed_image_url)
        if response.status_code == 200:
            with open(post_image_path, 'wb') as file:
                file.write(response.content)
            print(f"Image saved as '{post_image_path}'")
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
        
def request_gps_poll():
    try:
        response = requests.get(gps_poll_url)
        print("GPS polling started.")
    except Exception as e:
        print(f"Error starting GPS polling: {e}")

def stop_gps_polling():
    try:
        response = requests.get(gps_stop_url)
        print("GPS polling stopped.")
    except Exception as e:
        print(f"Error stopping GPS polling: {e}")

def main():
    #while True:
        #take user input

        #switch statements for each function
    request_take_picture()
    time.sleep(2)
    request_gps_poll()
    # Request image
    request_pre_image()    
    request_computer_vision()
    time.sleep(2)
    request_post_image()

    # Request CSV file
    request_csv()

    time.sleep(10)
    stop_gps_polling()

if __name__ == "__main__":
    main()