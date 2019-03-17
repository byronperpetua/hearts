import json
from socket import socket
from threading import Thread

PORT = 6642
BUFSIZE = 1024

def client_receive_loop(sock):
    while True:
        data = receive(sock)
        if not data:
            break
        print(data)

def client_send_loop(sock, user):
    while True:
        msg = input()
        send(sock, msg)

def send(conn_or_sock, msg):
    conn_or_sock.sendall(msg.encode('utf-8'))

def receive(conn_or_sock):
    return conn_or_sock.recv(BUFSIZE).decode('utf-8')

def broadcast(conn_list, msg):
    for conn in conn_list:
        send(conn, msg)

def launch_server():
    username = input('Enter username: ')
    with socket() as sock:
        sock.bind(('', PORT))
        sock.listen()
        print('Waiting for players to join.')
        conn_list = []
        while len(conn_list) < 3:
            conn, _ = sock.accept()
            conn_list.append(conn)
            new_username = receive(conn)
            msg = new_username + ' has joined.'
            print(msg)
            broadcast(conn_list, msg)
        broadcast(conn_list, "Everyone's here")

def launch_client():
    username = input('Enter username: ')
    host = input('Enter server IP address: ')
    with socket() as sock:
        sock.connect((host, PORT))
        send(sock, username)
        print('Connected.')
        receive_thread = Thread(target=client_receive_loop, args=(sock,))
        send_thread = Thread(target=client_send_loop, args=(sock, username))
        receive_thread.start()
        send_thread.start()
        while True:
            pass

def main():
    response = None
    while response not in ('s', 'c'):
        response = input('Enter "s" for server mode or "c" for client mode: ')
    if response == 's':
        launch_server()
    elif response == 'c':
        launch_client()

if __name__ == '__main__':
    main()
