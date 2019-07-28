from Game import Game
import socket
from sys import stdin, stdout
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
        self.setup_sockets()

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
            msg = 'u:' + ' '.join([self.usernames[(k+i) % 4]
                                   for k in range(4)])
            self.send(i, msg)
            Thread(target=self.chat_loop, args=(i,)).start()
        Thread(target=self.terminal_loop).start()
        print('Starting game.')
        self.game = Game(self)
        self.game.play()

    def broadcast(self, msg):
        for i in range(len(self.conns)):
            self.send(i, msg)

    def chat_loop(self, player_num, delay_sec=0.05):
        while True:
            msg = self.chat_conns[player_num].recv(self.bufsize).decode('utf-8')
            broadcast_msg = ('z:' + self.usernames[player_num] + ' ' + msg
                             + '\x03')
            for i in range(len(self.chat_conns)):
                self.chat_conns[i].sendall(broadcast_msg.encode('utf-8'))
                sleep(delay_sec)

    def recv_from_conn(self, conn):
        r = conn.recv(self.bufsize).decode('utf-8')
        # print('<-*', r)
        return r

    def request(self, player_num, msg):
        self.send(player_num, msg)
        return self.recv_from_conn(self.conns[player_num])

    def send(self, player_num, msg, delay_sec=0.05):
        self.send_to_conn(self.conns[player_num], msg)
        # print(msg, '*->', player_num)
        # Delay may be unnecessary with the '\x03' message separator
        sleep(delay_sec)

    def send_to_conn(self, conn, msg):
        conn.sendall((msg + '\x03').encode('utf-8'))

    def setup_sockets(self):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.sock.listen()
        self.chat_sock = socket.socket()
        self.chat_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.chat_sock.bind(('', self.chat_port))
        self.chat_sock.listen()

    def terminal_loop(self):
        while True:
            cmd = stdin.readline().split()
            try:
                if cmd[0] == 'set':
                    if cmd[1] == 'score':
                        player_num = self.usernames.index(cmd[2])
                        self.game.set_score(player_num, int(cmd[3]))
                    elif cmd[1] == 'pass':
                        self.game.set_pass_dir(cmd[2])
                    else:
                        print('Invalid command.')
                else:
                    print('Invalid command.')
            except (ValueError, IndexError):
                print('Invalid command.')
