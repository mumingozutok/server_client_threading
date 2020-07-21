import socketserver
import cv2
import sys
import threading
import numpy as np
import socket
import pickle
import struct ## new

class CommandClientHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

class VideoClientHandler(socketserver.StreamRequestHandler):

    def handle(self):
        data = b""
        payload_size = struct.calcsize(">L")
        print("payload_size: {}".format(payload_size)) 

        while True:
            while len(data) < payload_size:
                print("Recv: {}".format(len(data)))
                data += self.rfile.read(4096)

            print("Done Recv: {}".format(len(data)))
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            print("msg_size: {}".format(msg_size))
            while len(data) < msg_size:
                data += self.rfile.read(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            #edge detection


            cv2.imshow('ImageWindow',frame)    
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break  


class Server(object):
    def __init__(self, host, port1, port2):
        self.host = host
        self.port1 = port1
        self.port2 = port2

    def video_stream(self, host, port):
        # Create the server, binding to localhost on port 9999
        with socketserver.TCPServer((host, port), VideoClientHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
    
    def command_data(self, host, port):
        # Create the server, binding to localhost on port 9999
        with socketserver.TCPServer((host, port), CommandClientHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()



    def start(self):
        video_thread = threading.Thread(target=self.video_stream, args=(self.host, self.port1))
    #    video_thread.daemon = True
        video_thread.start()

        #mesaj islemi ayri bir threadde calissin
        command_thread = threading.Thread(target=self.command_data, args=(self.host, self.port2))
        command_thread.start()

if __name__ == "__main__":

    h, p1, p2 = "localhost", 9001, 9002

    ts = Server(h, p1, p2)
    ts.start()