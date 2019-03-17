import json
import socket
from threading import Thread

PORT = 6642

def encode(dict):
    return json.dumps(dict).encode('utf-8')

def decode(data):
    return json.loads(data)

def broadcast(conn_list, data):
    for c in conn_list:
        c.sendall(data)

def receive_loop(conn, addr, bufsize=1024):
    while True:
        data = conn.recv(bufsize)
        print(decode(data))

def send_loop(conn_list, user):
    while True:
        msg = input()
        broadcast(conn_list, encode({'message': msg, 'from': user}))

def accept_loop(sock):
    while True:
        conn, addr = sock.accept()
        conn_list.append(conn)
        print('Connected to client {}'.format(addr))
        receive_thread = Thread(target=receive_loop, args=(conn, addr))
        receive_thread.start()

with socket.socket() as sock:
    user = input('Enter username: ')
    sock.bind(('', PORT))
    sock.listen()
    conn_list = []
    send_thread = Thread(target=send_loop, args=(conn_list, user))
    send_thread.start()
    accept_loop(sock)

