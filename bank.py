import pygame
import json
import os

class Bank:
    def __init__(self, initial_amount=1000, font=None, save_file="bank.json"):
        self.save_file = save_file
        self.amount = initial_amount
        self.bet = 10
        self.min_bet = 1
        self.max_bet = self.amount
        self.font = font or pygame.font.SysFont("serif", 20, bold=True)

        # Input box setup
        self.input_active = False
        self.input_text = ""
        self.input_rect = pygame.Rect(0, 0, 120, 30)
        self.input_color_inactive = (150, 150, 150)
        self.input_color_active = (255, 255, 0)
        self.input_color = self.input_color_inactive

        # Load saved data (if exists)
        self.load_from_json()

    def save_to_json(self):
        data = {
            "amount": self.amount,
            "bet": self.bet,
            "min_bet": self.min_bet
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_json(self):
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
        x, y = position
        self.max_bet = max(self.min_bet, self.amount)

        # Draw text labels
        amt_text = self.font.render(f"Bank: ${self.amount}", True, (255, 255, 255))
        screen.blit(amt_text, (x, y))
        bet_text = self.font.render(f"Current Bet: ${self.bet}", True, (255, 255, 255))
        screen.blit(bet_text, (x - 50, y + 30))  # shift 10 pixels left

        # Draw input box
        self.input_rect.topleft = (x, y + 60)
        pygame.draw.rect(screen, self.input_color, self.input_rect, 2)

        # Render input text
        text_surface = self.font.render(self.input_text, True, (255, 255, 255))
        screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

        # Instructions
        instr_text = self.font.render("Click box, type bet, press Enter", True, (200, 200, 200))
        screen.blit(instr_text, (x - 175, y + 100))

    def handle_event(self, event):
        # Detect clicking on the input box
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.input_color = self.input_color_active
            else:
                self.input_active = False
                self.input_color = self.input_color_inactive

        # Handle typing when box is active
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                # Confirm bet
                try:
                    new_bet = int(self.input_text)
                    if self.min_bet <= new_bet <= self.max_bet:
                        self.bet = new_bet
                        print(f"Bet set to ${self.bet}")
                    else:
                        print(f"Invalid bet (must be ${self.min_bet}–${self.max_bet})")
                except ValueError:
                    print("Invalid input: must be a number")

                # Reset input after pressing Enter
                self.input_text = ""
                self.input_active = False
                self.input_color = self.input_color_inactive

            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                # Only allow digits
                if event.unicode.isdigit():
                    self.input_text += event.unicode

    def place_bet(self):
        if self.bet > self.amount:
            return False
        self.amount -= self.bet
        self.save_to_json()
        return True

    def payout(self, multiplier=2):
        self.amount += int(self.bet * multiplier)
        self.save_to_json()
