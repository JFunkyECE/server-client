import http.server
import socketserver
import os
import threading
import time
import csv
#import cv2 as cv
from picamera2 import Picamera2

PORT = 8000
image_path = os.path.expanduser('~/Desktop/spongebob.jpeg')
csv_path = os.path.expanduser('~/Desktop/GPS_Data.csv')

gps_polling_active = False
stop_gps_polling = False

picam2 = Picamera2()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path == '/image':
            #edit the image to send back the image either pre or post processing
            self.serve_file(image_path, 'image/jpeg')
        elif self.path == '/csv':
            self.serve_file(csv_path, 'text/csv')
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
