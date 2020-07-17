import cv2
import sys
import threading
import numpy as np
import socket
import pickle
import struct ## new

def Message_Server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)   

    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = s.accept() 

    while True:
        #try:
            # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16).decode('utf-8')
            print('received'+data)
            if data:
                print('sending data back to the client')
                connection.sendall(data.encode('utf-8'))
            else:
                print('no more data from' + client_address)
                break
                
        #finally:
        #    # Clean up the connection
        #    connection.close()         

def Video_Server(host,port):
    print(host)
    print(port)

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Socket created')

    s.bind((host, port))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    conn,addr=s.accept()

    data = b""
    payload_size = struct.calcsize(">L")
    print("payload_size: {}".format(payload_size))


    while True:
        while len(data) < payload_size:
            print("Recv: {}".format(len(data)))
            data += conn.recv(4096)

        print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
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
        Video_Server(host,port)

    def sensor_stream(self, host, port):
        print("thread called")        
        Message_Server(host,port)  


    def start(self):
        video_thread = threading.Thread(target=self.video_stream, args=(self.host, self.port1))
    #    video_thread.daemon = True
        video_thread.start()

        #mesaj işlemi ayrı bir threadde çalışsın
        sensor_thread = threading.Thread(target=self.sensor_stream, args=(self.host, self.port2))
        #sensor_thread.daemon = True
        sensor_thread.start()

        #self.video_stream(self.host, self.port1)        


if __name__ == '__main__':
    h, p1, p2 = "localhost", 8000, 8002

    ts = Server(h, p1, p2)
    ts.start()