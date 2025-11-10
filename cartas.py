import random
from Configs import RANKS, SUITS, VALUES

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        return VALUES[self.rank]

    def is_ace(self):
        return self.rank == 'ace'

    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self, num_decks=1):
        self.cards = []
        for _ in range(num_decks):
            for s in SUITS:
                for r in RANKS:
                    self.cards.append(Card(r, s))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.__init__()
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def values(self):
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.is_ace())
        totals = {total}
        for _ in range(aces):
            new_totals = set()
            for t in totals:
                new_totals.add(t + 10)
            totals |= new_totals
        return sorted([t for t in totals if t <= 21], reverse=True) or [min(totals)]

    def best_value(self):
        return self.values()[0]

    def is_blackjack(self):
        return len(self.cards) == 2 and 21 in self.values()

    def is_bust(self):
        return all(v > 21 for v in self.values())

    def clear(self):
        self.cards = []