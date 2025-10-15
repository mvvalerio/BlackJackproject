import pygame


class Bank:
    def __init__(self, initial_amount=10000):
        self.money = initial_amount
        self.current_bet = 0

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
