import http.server
import socketserver
import os
import threading
import gpsd
import time
import csv
import cv2 as cv
from picamera2 import Picamera2

PORT = 8000
image_path = os.path.expanduser('~/Desktop/spongebob.jpeg')
csv_path = os.path.expanduser('~/Desktop/GPS_Data.csv')

gps_polling_active = False
stop_gps_polling = False

picam2 = Picamera2()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global gps_polling_active

        if self.path == '/image':
            #edit the image to send back the image either pre or post processing
            self.serve_file(image_path, 'image/jpeg')
        elif self.path == '/csv':
            self.serve_file(csv_path, 'text/csv')
        elif self.path == '/gps-poll':
            if not gps_polling_active:
                gps_polling_active = True
                self.serve_gps_poll()
            else:
                self.send_response(200) #200 means ok
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"GPS polling is already active.")
        elif self.path == '/gps-stop':
            self.stop_gps_polling()
        elif self.path == '/take-picture':
            self.take_picture()
        #elif self.path == '/computer-vision':
            #call function to run model on image
        else:
            self.serve_not_found()

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.serve_not_found()

    def serve_not_found(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Resource not found.")

    def serve_gps_poll(self):
        global stop_gps_polling
        stop_gps_polling = False
        thread = threading.Thread(target=self.poll_gps)
        thread.start()
        self.send_response(200) 
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"GPS polling started...")

    def stop_gps_polling(self):
        global stop_gps_polling, gps_polling_active
        stop_gps_polling = True
        gps_polling_active = False
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"GPS polling stopped.")
    
    def poll_gps(self):
        global stop_gps_polling
        gpsd.connect()

        # Check if the file exists and if not, write the header
        file_exists = os.path.exists(csv_path)

        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(["Latitude", "Longitude", "Time"])

            while not stop_gps_polling:
                try:
                    packet = gpsd.get_current()
                    if packet.mode >= 2:
                        gps_time = packet.get_time(local_time=False)
                        latitude = packet.lat
                        longitude = packet.lon
                        writer.writerow([latitude, longitude, gps_time])
                        print(f"Written to CSV: Latitude: {latitude}, Longitude: {longitude}, Time: {gps_time}")
                    else:
                        print("Waiting for a valid GPS fix...")
                    time.sleep(1)
                except KeyError:
                    continue
                except Exception as e:
                    print(f"Error in GPS polling: {e}")
                    break

    def take_picture(self):
        picam2.start()
        picam2.capture_file("pre-processed-image.jpg")
        self.send_response(200) 
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Photo taken")

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Server started at localhost:{PORT}")
    httpd.serve_forever()
