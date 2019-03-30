from socket import socket
from Server import Server
from threading import Thread

class Client:
    def __init__(self, bufsize=1024, port=6642, chat_port=6643):
        self.bufsize = bufsize
        self.port = port
        self.chat_port = chat_port
        self.sock = socket()
        self.chat_sock = socket()

    def chat_loop(self, gui):
        while True:
            msg = self.receive_chat()
            if not msg:
                break
            else:
                gui.add_to_queue(msg)

    def connect(self, username, host_ip):
        self.sock.connect((host_ip, self.port))
        self.chat_sock.connect((host_ip, self.chat_port))
        self.send(username)
        print('Connected.')

    def loop(self, gui):
        while True:
            msg = self.receive()
            if not msg:
                print('Disconnected.')
                break
            else:
                gui.add_to_queue(msg)

    def receive(self):
        return self.sock.recv(self.bufsize).decode('utf-8')

    def receive_chat(self):
        return self.chat_sock.recv(self.bufsize).decode('utf-8')

    def send(self, msg):
        self.sock.sendall(msg.encode('utf-8'))

    def send_chat(self, msg):
        self.chat_sock.sendall(msg.encode('utf-8'))

    def start_server(self):
        server = Server()
        Thread(target=server.start_game).start()
