import json
import socket
from threading import Thread

#HOST = '24.147.10.71'
HOST = '127.0.0.1'
PORT = 6642

def encode(dict):
    return json.dumps(dict).encode('utf-8')

def decode(msg):
    return json.loads(msg)

def receive_loop(sock, bufsize=1024):
    while True:
        data = sock.recv(bufsize)
        print(decode(data))

def send_loop(sock, user):
    while True:
        msg = input()
        sock.sendall(encode({'message': msg, 'from': user}))

with socket.socket() as sock:
    user = input('Enter username: ')
    sock.connect((HOST, PORT))
    print('Connected to host {}'.format(HOST))
    receive_thread = Thread(target=receive_loop, args=(sock,))
    send_thread = Thread(target=send_loop, args=(sock, user))
    receive_thread.start()
    send_thread.start()
    while True: pass
