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