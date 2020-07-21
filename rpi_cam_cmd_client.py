import io
import socket
import struct
import time
import picamera
import socketserver
import cv2
import sys
import threading
import numpy as np
import pickle

class CommandClientHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

def Picamera_Client(host, port):
    # create socket and bind host
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    connection = client_socket.makefile('wb')  

    try:
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)      # pi camera resolution
            camera.framerate = 15               # 15 frames/sec
            time.sleep(2)                       # give 2 secs for camera to initilize
            start = time.time()
            stream = io.BytesIO()

            # send jpeg format video stream
            for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):
                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
                if time.time() - start > 600:
                    break
                stream.seek(0)
                stream.truncate()
        connection.write(struct.pack('<L', 0))

    finally:
        connection.close()
        client_socket.close()        


class Rpi_Program(object):
    def __init__(self, host1, host2, port1, port2):
        self.host1 = host1
        self.host2 = host2
        self.port1 = port1
        self.port2 = port2

    def PiCamera_stream(self, host, port):
        Picamera_Client(host, port)
   
    def command_data(self, host, port):
        # Create the server, binding to localhost on port 9999
        with socketserver.TCPServer((host, port), CommandClientHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()

    def start(self):
        video_thread = threading.Thread(target=self.PiCamera_stream, args=(self.host2, self.port2))
    #    video_thread.daemon = True
        video_thread.start()

        #mesaj islemi ayri bir threadde calissin
        command_thread = threading.Thread(target=self.command_data, args=(self.host1, self.port1))
        command_thread.start()

if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    h1, h2, p1, p2 = '', '192.168.1.105',8001, 8000
    ts = Rpi_Program(h1, h2, p1, p2)
    ts.start()
