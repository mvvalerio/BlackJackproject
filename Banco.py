try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class Bank:
    def __init__(self, initial_amount=10000):
        self.money = initial_amount
        self.current_bet = 0
        if PYGAME_AVAILABLE:
            try:
                self.image = pygame.image.load('pixel-art-money-pack_preview_rev_1.png')
            except pygame.error as e:
                print(f"Error loading image: {e}")
                self.image = None
        else:
            self.image = None

    def place_bet(self, amount):
        if amount <= self.money:
            self.money -= amount
            self.current_bet = amount
            return True
        return False

    def win_bet(self):
        self.money += self.current_bet * 2
        self.current_bet = 0

    def lose_bet(self):
        self.current_bet = 0

    def push(self):
        self.money += self.current_bet
        self.current_bet = 0

    def get_balance(self):
        return self.money
