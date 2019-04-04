from Game import Game
from socket import socket
from time import sleep
from threading import Thread

class Server:
    def __init__(self, bufsize=1024, port=6642, chat_port=6643):
        self.bufsize = bufsize
        self.port = port
        self.chat_port = chat_port
        self.conns = []
        self.chat_conns = []
        self.usernames = []
        self.sock = socket()
        self.sock.bind(('', self.port))
        self.sock.listen()
        self.chat_sock = socket()
        self.chat_sock.bind(('', self.chat_port))
        self.chat_sock.listen()

    def accept_conn(self, sock, return_val_holder):
        # pass an empty list to return_val_holder
        return_val_holder.append(sock.accept()[0])

    def start_game(self, num_players=4):
        while len(self.conns) < num_players:
            conn_holder = []
            chat_conn_holder = []
            t1 = Thread(target=self.accept_conn, args=(self.sock, conn_holder))
            t2 = Thread(target=self.accept_conn,
                        args=(self.chat_sock, chat_conn_holder))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.conns.append(conn_holder[0])
            self.chat_conns.append(chat_conn_holder[0])
            username = conn_holder[0].recv(self.bufsize).decode('utf-8')
            print(username + ' has joined.')
            self.usernames.append(username)
        for i in range(num_players):
            msg = 'u:' + ' '.join([self.usernames[(k+i) % 4] for k in range(4)])
            self.send(i, msg)
            Thread(target=self.chat_loop, args=(i,)).start()
        print('Starting game.')
        game = Game(self)
        game.play()

    def broadcast(self, msg):
        for i in range(len(self.conns)):
            self.send(i, msg)

    def chat_loop(self, player_num, delay_sec=0.05):
        while True:
            msg = self.chat_conns[player_num].recv(self.bufsize).decode('utf-8')
            broadcast_msg = 'z:' + self.usernames[player_num] + ' ' + msg
            for i in range(len(self.chat_conns)):
                self.chat_conns[i].sendall(broadcast_msg.encode('utf-8'))
                sleep(delay_sec)

    def request(self, player_num, msg):
        self.send(player_num, msg)
        r = self.conns[player_num].recv(self.bufsize).decode('utf-8')
        # print('<', player_num, r)
        return r

    def send(self, player_num, msg, delay_sec=0.05):
        self.conns[player_num].sendall(msg.encode('utf-8'))
        # print('>', player_num, msg)
        sleep(delay_sec)
