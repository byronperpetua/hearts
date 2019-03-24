from socket import socket
from Server import Server
from threading import Thread


class Client:
    def __init__(self, bufsize=1024, port=6642):
        self.bufsize = bufsize
        self.port = port
        self.sock = socket()

    def connect(self, username, host_ip):
        self.sock.connect((host_ip, self.port))
        self.send(username)
        print('Connected.')

    def loop(self, gui):
        while True:
            msg = self.receive()
            if not msg:
                print('Disconnected.')
                break
            else:
                gui.set_msg(msg)

    def receive(self):
        return self.sock.recv(self.bufsize).decode('utf-8')

    def send(self, msg):
        self.sock.sendall(msg.encode('utf-8'))

    def start_server(self):
        server = Server()
        Thread(target=server.start_game).start()