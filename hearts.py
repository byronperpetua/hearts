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

    def points(self):
        if self.suit == 's' and self.rank == 'q':
            return 13
        elif self.suit == 'h':
            return 1
        else:
            return 0 


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

    def append(self, card):
        self.cards.append(card)
    
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
    
    def has_only_point_cards(self):
        return all([c.points() > 0 for c in self.cards])

    def has_only_suit(self, suit):
        return all([c.suit == suit for c in self.cards])

    def is_void(self, suit):
        return all([c.suit != suit for c in self.cards])

    def length(self):
        return len(self.cards)

    def points(self):
        return sum([c.points() for c in self.cards])

    def remove(self, card):
        self.cards.remove(card)

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
        self.hearts_broken = False
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
        for i in range(self.num_players):
            self.server.send(i, str(self.hands[i]))
            while True:
                try:
                    h = Hand(self.server.request(i, msg))
                except (TypeError, IndexError):
                    continue
                if h.length() == 3 and h.subset_of(self.hands[i]):
                    self.passes.append(h)
                    self.hands[i].remove_hand(self.passes[i])
                    break

    def distribute_pass(self):
        for i in range(self.num_players):
            if self.pass_dir == 'left':
                received = self.passes[(i+1) % self.num_players]
            elif self.pass_dir == 'right':
                received = self.passes[(i-1) % self.num_players]
            elif self.pass_dir == 'across':
                received = self.passes[(i+2) % self.num_players]
            self.hands[i].extend(received)
            self.server.send(i, 'Received: ' + received.short_str())
    
    def validate_play(self, card, hand, suit_led):
        if hand.contains(card):
            if suit_led is None:
                if self.trick_num == 1:
                    return card == Card('2c')
                else:
                    if card.suit == 'h':
                        return self.hearts_broken or hand.has_only_suit('h')
                    else:
                        return True
            else:
                if card.suit == suit_led:
                    return True
                else:
                    if hand.is_void(suit_led):
                        if self.trick_num == 1:
                            return (card.points() == 0
                                    or hand.has_only_point_cards())
                        else:
                            return True
                    else:
                        return False
        else:
            return False

    def play_trick(self):
        trick = Hand()
        suit_led = None
        for i in range(self.num_players):
            self.server.send(i, str(self.hands[i]))
        for k in range(self.num_players):
            i = (self.leader + k) % self.num_players
            while True:
                try:
                    msg = 'Play a card: '
                    c = Card(self.server.request(i, msg))
                except (TypeError, IndexError):
                    continue
                if self.validate_play(c, self.hands[i], suit_led):
                    self.hands[i].remove(c)
                    trick.append(c)
                    msg = self.server.players[i].username + ': ' + str(c)
                    self.server.broadcast(msg, exclude=i)
                    break
            if suit_led is None:
                suit_led = c.suit
                winner = i
                winning_card = c
            if c.suit == suit_led and c > winning_card:
                winner = i
                winning_card = c
            if c.suit == 'h' and not self.hearts_broken:
                self.hearts_broken = True
        msg = self.server.players[winner].username + ' takes the trick.'
        self.server.broadcast(msg)
        self.scores[winner] += trick.points()
        self.leader = winner

    def play(self):
        self.deal()
        if self.pass_dir != 'hold':
            self.get_pass()
            self.distribute_pass()
        self.leader = [h.contains(Card('2c')) for h in self.hands].index(True)
        self.trick_num = 1
        while self.trick_num <= 13:
            self.play_trick()
            self.trick_num += 1
        if max(self.scores) == 26:
            shooter = self.scores.index(26)
            msg = 'Enter "a" to add or "s" to subtract: '
            while True:
                response = self.server.request(shooter, msg)
                if response == 'a':
                    for i in range(self.num_players):
                        if i == shooter:
                            self.scores[i] = 0
                        else:
                            self.scores[i] = 26
                    break
                elif response == 's':
                    self.scores[shooter] = -26
                    break


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

    def get_scores_str(self, scores):
        s = ''
        for i in range(self.num_players):
            s += (self.server.players[i].username + ' ' + str(scores[i])
                  + '    ')
        return s

    def play(self):
        while max(self.scores) < self.max_score:
            self.server.broadcast('Starting round ' + str(self.round_num) + '.')
            round = Round(self.server, self.pass_dirs[self.pass_dir_num])
            round.play()
            self.server.broadcast('Round scores:    '
                                  + self.get_scores_str(round.scores))
            for i in range(self.num_players):
                self.scores[i] += round.scores[i]
            self.server.broadcast('Game scores:    '
                                  + self.get_scores_str(self.scores))
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

    def send(self, player_num, msg):
        if player_num == 0:
            print(msg)
        else:
            self.players[player_num].conn.sendall(msg.encode('utf-8'))
        sleep(0.1)

    def broadcast(self, msg, exclude=None):
        for i in range(len(self.players)):
            if i != exclude:
                self.send(i, msg)

    def receive(self, player):
        return player.conn.recv(self.bufsize).decode('utf-8')

    def request(self, player_num, msg):
        if player_num == 0:
            return input(msg)
        else:
            self.send(player_num, msg + '\x05')
            player = self.players[player_num]
            return player.conn.recv(self.bufsize).decode('utf-8')

    def start_game(self):
        self.players[0].username = input('Enter username: ')
        print('Waiting for players to join.')
        while len(self.players) < 4:
            new_player = Player(self.sock.accept()[0])
            self.players.append(new_player)
            new_player.username = self.receive(new_player)
            self.broadcast(new_player.username + ' has joined.')
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
                while True:
                    response = input(msg)
                    if response:
                        self.send(response)
                        break
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
