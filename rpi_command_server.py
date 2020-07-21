import socketserver
import sys
import threading
import socket

class CommandClientHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())             

class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

   
    def command_data(self, host, port):
        # Create the server, binding to localhost on port 8001
        with socketserver.TCPServer((host, port), CommandClientHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()

    def start(self):
        #mesaj islemi ayri bir threadde calissin
        command_thread = threading.Thread(target=self.command_data, args=(self.host, self.port))
        command_thread.start()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    h, p = '', 8001
    ts = Server(h, p)
    ts.start()
