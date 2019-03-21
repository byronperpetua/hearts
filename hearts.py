from random import shuffle
from socket import socket
from time import sleep


class Player:
    def __init__(self, conn=None):
        self.conn = conn
        self.username = ''


class Card:
    suits = ['c', 'd', 's', 'h']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 't', 'j', 'q', 'k', 'a']

    def __init__(self, code):
        self.rank = code[0]
        self.suit = code[1]

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        if Card.suits.index(self.suit) < Card.suits.index(other.suit):
            return True
        elif Card.suits.index(self.suit) == Card.suits.index(other.suit):
            return Card.ranks.index(self.rank) < Card.ranks.index(other.rank)
        else:
            return False

    def __repr__(self):
        return self.rank + self.suit


class Hand:
    def __init__(self, cards='', full_deck=False):
        if full_deck:
            self.cards = [Card(r + s) for s in Card.suits for r in Card.ranks]
        else:
            self.cards = [Card(code) for code in cards.split()]

    def __repr__(self):
        s1 = ''
        s2 = '\n'
        for suit in Card.suits:
            in_suit = [c.rank for c in sorted(self.cards) if c.suit == suit]
            s1 += suit + ' ' * max((len(in_suit)), 1)
            s2 += ''.join(in_suit) + ' ' * max(2 - len(in_suit), 1)
        return s1 + s2
    
    def contains(self, card):
        return card in self.cards

    def deal(self, num_players):
        hands = []
        hand_size = int(len(self.cards) / num_players)
        for i in range(num_players):
            hands.append(Hand())
            hands[i].cards = self.cards[i*hand_size:(i+1)*hand_size]
        return hands

    def extend(self, other):
        for c in other.cards:
            self.cards.append(c)

    def get_cards(self):
        return self.cards

    def length(self):
        return len(self.cards)

    def remove_hand(self, other):
        for c in other.cards:
            self.cards.remove(c)

    def short_str(self):
        return ', '.join([str(c) for c in self.cards])

    def shuffle(self):
        shuffle(self.cards)
        
    def subset_of(self, other):
        other_copy = other.cards.copy()
        for c in self.cards:
            if c not in other_copy:
                return False
            other_copy.remove(c)
        return True

class Round:
    def __init__(self, server, pass_dir, num_tricks=13):
        self.num_players = len(server.players)
        self.num_tricks = num_tricks
        self.scores = [0] * self.num_players
        self.hands = []
        self.passes = []
        self.server = server
        self.pass_dir = pass_dir

    def deal(self):
        deck = Hand(full_deck=True)
        deck.shuffle()
        self.hands = deck.deal(self.num_players)

    # TODO: threads
    def get_pass(self):
        msg = 'Choose 3 cards to pass ' + self.pass_dir + ': '
        print(self.hands[0])
        while True:
            h = Hand(input(msg))
            if h.length() == 3 and h.subset_of(self.hands[0]):
                self.passes.append(h)
                break
        for i in range(1, self.num_players):
            self.server.send(self.server.players[i], str(self.hands[i]))
            while True:
                h = Hand(self.server.request(self.server.players[i], msg))
                if h.length() == 3 and h.subset_of(self.hands[i]):
                    self.passes.append(h)
                    break
        for i in range(self.num_players):
            self.hands[i].remove_hand(self.passes[i])

    def distribute_pass(self):
        if self.pass_dir != 'hold':
            for i in range(self.num_players):
                if self.pass_dir == 'left':
                    received = self.passes[(i+1) % self.num_players]
                elif self.pass_dir == 'right':
                    received = self.passes[(i-1) % self.num_players]
                elif self.pass_dir == 'across':
                    received = self.passes[(i+2) % self.num_players]
                self.hands[i].extend(received)
                if i == 0:
                    print('Received: ' + received.short_str())
                    print(self.hands[0])
                else:
                    self.server.send(self.server.players[i],
                                    'Received: ' + received.short_str())
                    self.server.send(self.server.players[i], str(self.hands[i]))

    def play_trick(self):
        pass

    def play(self):
        self.deal()
        self.get_pass()
        self.distribute_pass()
        self.leader = [h.contains(Card('2c')) for h in self.hands].index(True)
        for i in range(self.num_tricks):
            self.play_trick()
        # TODO: fix
        self.scores = [0, 26, 26, 26]


class Game:
    def __init__(self, server, max_score=100,
                 pass_dirs=('left', 'right', 'across', 'hold')):
        self.server = server
        self.num_players = len(server.players)
        self.scores = [0] * self.num_players
        self.max_score = max_score
        self.round_num = 1
        self.pass_dirs = pass_dirs
        self.pass_dir_num = 0

    def get_scores_str(self):
        s = ''
        for i in range(self.num_players):
            s += (self.server.players[i].username + ': ' + str(self.scores[i])
                  + '    ')
        return s

    def play(self):
        while max(self.scores) < self.max_score:
            self.server.broadcast('Starting round ' + str(self.round_num),
                                  print_=True)
            round = Round(self.server, self.pass_dirs[self.pass_dir_num])
            round.play()
            for i in range(self.num_players):
                self.scores[i] += round.scores[i]
            self.server.broadcast(self.get_scores_str(), print_=True)
            self.round_num += 1
            self.pass_dir_num = (self.pass_dir_num + 1) % len(self.pass_dirs)
                

class Server:
    def __init__(self, bufsize=1024, port=6642):
        self.bufsize = bufsize
        self.port = port
        self.players = [Player()]
        self.sock = socket()
        self.sock.bind(('', self.port))
        self.sock.listen()

    def send(self, player, msg):
        player.conn.sendall(msg.encode('utf-8'))
        sleep(0.1)

    def broadcast(self, msg, exclude=(), print_=False):
        for i in range(1, len(self.players)):
            if i not in exclude:
                self.send(self.players[i], msg)
        if print_:
            print(msg)

    def receive(self, player):
        return player.conn.recv(self.bufsize).decode('utf-8')

    def request(self, player, msg):
        self.send(player, msg + '\x05')
        return self.receive(player)

    def start_game(self):
        self.players[0].username = input('Enter username: ')
        print('Waiting for players to join.')
        while len(self.players) < 4:
            new_player = Player(self.sock.accept()[0])
            self.players.append(new_player)
            new_player.username = self.receive(new_player)
            self.broadcast(new_player.username + ' has joined.', print_=True)
        game = Game(self)
        game.play()


class Client:
    def __init__(self, bufsize=1024, port=6642):
        self.bufsize = bufsize
        self.port = port
        self.sock = socket()

    def send(self, msg):
        self.sock.sendall(msg.encode('utf-8'))

    def receive(self):
        return self.sock.recv(self.bufsize).decode('utf-8')

    def connect_to_host(self):
        self.username = input('Enter username: ')
        host = input('Enter server IP address: ')
        self.sock.connect((host, self.port))
        self.send(self.username)
        print('Connected.')

    def loop(self):
        while True:
            msg = self.receive()
            if not msg:
                print('Disconnected.')
                break
            elif msg.endswith('\x05'):
                self.send(input(msg))
            else:
                print(msg)


def main():
    response = None
    while response not in ('s', 'c'):
        response = input('Enter "s" for server mode or "c" for client mode: ')
    if response == 's':
        server = Server()
        server.start_game()
    elif response == 'c':
        client = Client()
        client.connect_to_host()
        client.loop()

if __name__ == '__main__':
    main()
