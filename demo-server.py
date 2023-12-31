import http.server
import socketserver
import gpsd
import os
import threading
import time
import csv
import cv2 as cv
from picamera2 import Picamera2, Preview
import glob

PORT = 8000
pre_image_path = os.path.expanduser('~/Desktop/server-client/pre-processed-image.jpeg')
post_image_path = os.path.expanduser('~/Desktop/server-client/post-processed-image.jpeg')

modelConfig = os.path.expanduser('~/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
modelWeights = os.path.expanduser('~/Desktop/Object_Detection_Files/frozen_inference_graph.pb')
modelClassList = os.path.expanduser('~/Desktop/Object_Detection_Files/coco_names.txt')

csv_path = os.path.expanduser('~/Desktop/GPS_Data.csv')

gps_polling_active = False
stop_gps_polling = False

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start_preview(Preview.NULL)
picam2.start()

model = cv.dnn_DetectionModel(modelWeights, modelConfig)
model_confidence_threshold = 0.65
model.setInputSize(320, 320)
model.setInputScale(1.0/127.5)
model.setInputMean((127.5, 127.5, 127.5))
model.setInputSwapRB(True)  

#make list of class labels from dataset (only used when drawing box titles)
with open(modelClassList, 'rt') as spt:
    classLabels = spt.read().rstrip('\n').split('\n')
    
temp_base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(temp_base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global gps_polling_active
        if self.path == '/pre-processed-image':
            #edit the image to send back the image either pre or post processing
            self.serve_file(pre_image_path, 'image/jpeg')
        elif self.path =='/post-processed-image':
            self.serve_file(post_image_path, 'image/jpeg')
        elif self.path == '/csv':
            self.serve_file(csv_path, 'text/csv')
        elif self.path == '/take-picture':
            self.take_picture()
        elif self.path =='/gps-poll':
            gps_polling_active = True
            self.serve_gps_poll()
        elif self.path =='/gps-stop':
            self.stop_gps_polling()
        elif self.path == '/computer-vision':
            self.computer_vision()
            #call function to run model on image
            #create image in directory called post-processed-image.jpeg
        elif self.path == '/temp':
            self.read_temp()
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
        picam2.capture_file("pre-processed-image.jpeg")
        self.send_response(200) 
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Photo taken")
    
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
    
    def computer_vision(self):
        img = cv.imread(pre_image_path)
        classIndex, confidence, bbox = model.detect(img, confThreshold=model_confidence_threshold, nmsThreshold=0.2) 
        for classInd, conf, boxes in zip(classIndex, confidence, bbox):
            cv.rectangle(img, boxes, (0, 255, 0), 1)
            cv.putText(img, classLabels[classInd-1], (boxes[0] + 10, boxes[1] + 20), cv.FONT_HERSHEY_PLAIN, fontScale = 1, color=(0, 0, 255), thickness=2)
        cv.imwrite(post_image_path, img)
        self.send_response(200) 
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Computer Vision finished")
        
    def read_temp_raw(self):
        f = open(device_file, 'r')
        Lines = f.readlines()
        f.close()
        return Lines
        
    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            #temp_c = 22.3
        self.send_response(200) 
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        out = "T = " + str(temp_c) + " degrees"
        self.wfile.write(out.encode('utf-8'))
        

        

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Server started at localhost:{PORT}")
    httpd.serve_forever()
