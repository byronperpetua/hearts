from socket import socket

import sys


class SimpleServer:
    def __init__(self, bufsize=1024, port=6642):
        self.bufsize = bufsize
        self.sock = socket()
        self.sock.bind(('', port))
        self.sock.listen()

    def setup(self):
        self.conn = self.sock.accept()[0]

    def send(self, msg):
        self.conn.sendall(msg.encode('utf-8'))

    def receive(self):
        return self.conn.recv(self.bufsize).decode('utf-8')

    def test_send(self):
        while True:
            self.send(sys.stdin.readline())