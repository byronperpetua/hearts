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
            msg_raw = self.receive_chat()
            if not msg_raw:
                print('Disconnected.')
                break
            else:
                # Handle multiple packets coming at once
                msgs = [m for m in msg_raw.split('\x03') if m]
                for m in msgs:
                    gui.add_to_queue(m)

    def connect(self, username, host_ip):
        self.sock.connect((host_ip, self.port))
        self.chat_sock.connect((host_ip, self.chat_port))
        self.send(username)
        print('Connected.')

    def loop(self, gui):
        while True:
            msg_raw = self.receive()
            if not msg_raw:
                print('Disconnected.')
                break
            else:
                # Handle multiple packets coming at once
                msgs = [m for m in msg_raw.split('\x03') if m]
                for m in msgs:
                    gui.add_to_queue(m)

    def receive(self):
        r = self.sock.recv(self.bufsize).decode('utf-8')
        return r

    def receive_chat(self):
        return self.chat_sock.recv(self.bufsize).decode('utf-8')

    def send(self, msg):
        self.sock.sendall(msg.encode('utf-8'))

    def send_chat(self, msg):
        self.chat_sock.sendall(msg.encode('utf-8'))

