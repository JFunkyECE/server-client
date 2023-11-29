import http.server
import socketserver

PORT = 8000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/image':
            self.serve_image()
        else:
            self.serve_counter()

    def serve_counter(self):
        global counter
        counter += 1  # Increment the counter with each request
        message = f"Request number: {counter}"

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(message.encode())

    def serve_image(self):
        try:
            with open("path/to/your/image.jpg", "rb") as file:  # Replace with your image path
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "File Not Found")

with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
    print(f"Server started at localhost:{PORT}")
    httpd.serve_forever()
