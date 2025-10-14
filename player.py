from cartas import Hand

class Player:
    def __init__(self):
        self.hand = Hand()

class Dealer(Player):
    def __init__(self):
        super().__init__()

    def should_hit(self):
        best = self.hand.best_value()
        return best < 17  # Dealer compra até 17
