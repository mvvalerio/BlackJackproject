class Bank:
    def __init__(self, starting_balance=1000):
        self.balance = starting_balance
        self.current_bet = 0

    def can_bet(self, amount):
        return 0 < amount <= self.balance

    def place_bet(self, amount):
        if self.can_bet(amount):
            self.current_bet = amount
            self.balance -= amount
            return True
        return False

    def win(self):
        self.balance += self.current_bet * 2
        self.current_bet = 0

    def push(self):
        self.balance += self.current_bet
        self.current_bet = 0

    def lose(self):
        self.current_bet = 0

    def is_broke(self):
        return self.balance <= 0
