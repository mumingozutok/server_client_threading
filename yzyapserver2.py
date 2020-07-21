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
        stream_bytes = b""
        try:
            # stream video frames one by one
            while True:

                stream_bytes += self.rfile.read(4096)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    #gray = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    cv2.imshow('ImageWindow',image)    
                        
                key = cv2.waitKey(1) & 0xFF
                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break 

        finally:
            print("error")
            cv2.destroyAllWindows()
            sys.exit()                

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
        #command_thread = threading.Thread(target=self.command_data, args=(self.host, self.port2))
        #command_thread.start()

if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    h, p1, p2 = '', 8000, 8001
    ts = Server(h, p1, p2)
    ts.start()
