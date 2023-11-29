import http.server
import socketserver
import os
import threading
import gpsd
import time
import csv

PORT = 8000
image_path = os.path.expanduser('~/Desktop/spongebob.jpeg')
csv_path = os.path.expanduser('~/Desktop/GPS_Data.csv')

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/image':
            self.serve_file(image_path, 'image/jpeg')
        elif self.path == '/csv':
            self.serve_file(csv_path, 'text/csv')
        elif self.path == '/gps-poll':
            self.serve_gps_poll()
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
        thread = threading.Thread(target=self.poll_gps)
        thread.start()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"GPS polling started...")

    def poll_gps(self):
        gpsd.connect()

        # Check if the file exists and if not, write the header
        file_exists = os.path.exists(csv_path)

        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(["Latitude", "Longitude", "Time"])

            while True:
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

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Server started at localhost:{PORT}")
    httpd.serve_forever()
