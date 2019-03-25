from Card import Card
from random import shuffle

class Hand:
    def __init__(self, cards='', full_deck=False):
        if full_deck:
            self.cards = [Card(r + s) for s in Card.suits for r in Card.ranks]
        else:
            self.cards = [Card(code) for code in cards.split()]

    def __repr__(self):
        return ' '.join([str(c) for c in sorted(self.cards)])

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

    def shuffle(self):
        shuffle(self.cards)
        
    def subset_of(self, other):
        other_copy = other.cards.copy()
        for c in self.cards:
            if c not in other_copy:
                return False
            other_copy.remove(c)
        return True