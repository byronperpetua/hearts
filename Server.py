from Game import Game
from socket import socket
from time import sleep


class Server:
    def __init__(self, bufsize=1024, port=6642):
        self.bufsize = bufsize
        self.port = port
        self.conns = []
        self.usernames = []
        self.sock = socket()
        self.sock.bind(('', self.port))
        self.sock.listen()

    def start_game(self, num_players=4):
        print('Awaiting players.')
        while len(self.conns) < num_players:
            conn = self.sock.accept()[0]
            self.conns.append(conn)
            self.usernames.append(conn.recv(self.bufsize).decode('utf-8'))
        for i in range(num_players):
            msg = 'u:' + ' '.join([self.usernames[(k+i) % 4] for k in range(4)])
            self.send(i, msg)
        game = Game(self)
        game.play()

    def broadcast(self, msg):
        for i in range(len(self.conns)):
            self.send(i, msg)

    def request(self, player_num, msg):
        self.send(player_num, msg)
        return self.conns[player_num].recv(self.bufsize).decode('utf-8')

    def send(self, player_num, msg, delay_sec=0.1):
        self.conns[player_num].sendall(msg.encode('utf-8'))
        sleep(delay_sec)
