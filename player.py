from cartas import Hand

class Player:
    def __init__(self):
        self.hands = [Hand()]  # suporte para split, lista de mãos
        self.current_hand = 0

    def reset(self):
        self.hands = [Hand()]
        self.current_hand = 0

    def add_card(self, card):
        self.hands[self.current_hand].add(card)

    def can_split(self):
        if len(self.hands) > 1:
            return False  # só permite split uma vez (pode adaptar depois)
        hand = self.hands[0]
        if len(hand.cards) != 2:
            return False
        c1, c2 = hand.cards[0], hand.cards[1]
        # split se cartas forem exatamente iguais (rank e suit)
        return c1.rank == c2.rank

    def split(self):
        hand = self.hands[0]
        if self.can_split():
            c1 = hand.cards[0]
            c2 = hand.cards[1]
            self.hands = [Hand(), Hand()]
            self.hands[0].add(c1)
            self.hands[1].add(c2)
            self.current_hand = 0
            return True
        return False

class Dealer(Player):
    def __init__(self):
        super().__init__()

    def should_hit(self):
        best = self.hands[0].best_value()
        return best < 17
