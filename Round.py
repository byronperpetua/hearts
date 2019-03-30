from Hand import Hand
from Card import Card

class Round:
    def __init__(self, server, pass_dir, num_tricks=13):
        self.num_players = len(server.usernames)
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

    def get_pass(self):
        for i in range(self.num_players):
            self.server.send(i, 'h:' + str(self.hands[i]))
        for i in range(self.num_players):
            h = Hand(self.server.request(i, 'p?'))
            self.passes.append(h)
            self.hands[i].remove_hand(self.passes[i])

    def distribute_pass(self):
        for i in range(self.num_players):
            if self.pass_dir == 'left':
                received = self.passes[(i+1) % self.num_players]
            elif self.pass_dir == 'right':
                received = self.passes[(i-1) % self.num_players]
            elif self.pass_dir == 'across':
                received = self.passes[(i+2) % self.num_players]
            self.hands[i].extend(received)
            self.server.send(i, 'h:' + str(self.hands[i]))
            self.server.send(i, 'p:' + str(received))
    
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
            self.server.send(i, 'h:' + str(self.hands[i]))
        for k in range(self.num_players):
            i = (self.leader + k) % self.num_players
            while True:
                c = Card(self.server.request(i, 'c?'))
                if self.validate_play(c, self.hands[i], suit_led):
                    self.hands[i].remove(c)
                    trick.append(c)
                    self.server.broadcast('c:' + self.server.usernames[i]
                                          + ' ' + str(c))
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
        self.server.broadcast('t:' + self.server.usernames[winner])
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
            while True:
                response = self.server.request(shooter, 'a?')
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