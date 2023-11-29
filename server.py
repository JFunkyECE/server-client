import http.server
import socketserver
import os

PORT = 8000
image_path = os.path.expanduser('~/Desktop/spongebob.jpeg')
csv_path = os.path.expanduser('~/Desktop/GPS_Data.csv')  # Replace with your CSV file path

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/image':
            self.serve_file(image_path, 'image/jpeg')
        elif self.path == '/csv':
            self.serve_file(csv_path, 'text/csv')
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

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Server started at localhost:{PORT}")
    httpd.serve_forever()
