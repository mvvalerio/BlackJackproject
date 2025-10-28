import pygame
import json
import os

class Bank:
    def __init__(self, initial_amount=1000, font=None, save_file="bank.json"):
        self.save_file = save_file
        self.amount = initial_amount
        self.bet = 10
        self.min_bet = 1
        self.max_bet = self.amount  # max bet starts equal to bank
        self.slider_rect = pygame.Rect(0, 0, 200, 10)
        self.slider_handle_rect = pygame.Rect(0, 0, 20, 20)
        self.dragging = False
        self.font = font or pygame.font.SysFont("serif", 20, bold=True)

        # Load saved data (if available)
        self.load_from_json()

    def save_to_json(self):
        """Automatically saves the current bank data to a JSON file."""
        data = {
            "amount": self.amount,
            "bet": self.bet,
            "min_bet": self.min_bet
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_json(self):
        """Loads bank data from JSON file if it exists."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    self.amount = data.get("amount", self.amount)
                    self.bet = data.get("bet", self.bet)
                    self.min_bet = data.get("min_bet", self.min_bet)
                    self.max_bet = self.amount
            except json.JSONDecodeError:
                print("Warning: bank.json is corrupted. Using default values.")

    def draw(self, screen, position):
        # Always keep max_bet synced with current bank amount
        self.max_bet = max(self.min_bet, self.amount)

        x, y = position
        # Display bank amount
        amt_text = self.font.render(f"Bank: ${self.amount}", True, (255, 255, 255))
        screen.blit(amt_text, (x, y))

        # Slider position
        self.slider_rect.topleft = (x, y + 30)
        pygame.draw.rect(screen, (180, 180, 180), self.slider_rect)

        # Clamp bet to current max_bet if needed
        self.bet = min(self.bet, self.max_bet)

        # Handle position based on bet
        handle_x = x + int(
            (self.bet - self.min_bet)
            / (self.max_bet - self.min_bet)
            * (self.slider_rect.width - self.slider_handle_rect.width)
        ) if self.max_bet > self.min_bet else x
        handle_y = y + 25
        self.slider_handle_rect.topleft = (handle_x, handle_y)
        pygame.draw.rect(screen, (255, 255, 0), self.slider_handle_rect)

        # Display current bet
        bet_text = self.font.render(f"Bet: ${self.bet}", True, (255, 255, 255))
        screen.blit(bet_text, (x, y + 60))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.slider_handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.max_bet = max(self.min_bet, self.amount)
                rel_x = event.pos[0] - self.slider_rect.x
                rel_x = max(0, min(rel_x, self.slider_rect.width - self.slider_handle_rect.width))
                self.bet = self.min_bet + int(
                    rel_x / (self.slider_rect.width - self.slider_handle_rect.width)
                    * (self.max_bet - self.min_bet)
                )

    def place_bet(self):
        """Subtracts the current bet from the bank and auto-saves."""
        if self.bet > self.amount:
            return False  # cannot bet more than available
        self.amount -= self.bet
        self.save_to_json()  # auto-save after betting
        return True

    def payout(self, multiplier=2):
        """Adds winnings to the bank and auto-saves."""
        self.amount += int(self.bet * multiplier)
        self.save_to_json()  # auto-save after payout
