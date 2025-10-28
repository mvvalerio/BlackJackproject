import pygame

class Bank:
    def __init__(self, initial_amount=1000, font=None):
        self.amount = initial_amount
        self.bet = 10
        self.min_bet = 1
        self.max_bet = self.amount
        self.slider_rect = pygame.Rect(0, 0, 200, 10)
        self.slider_handle_rect = pygame.Rect(0, 0, 20, 20)
        self.dragging = False
        self.font = font or pygame.font.SysFont("serif", 20, bold=True)

    def draw(self, screen, position):
        x, y = position
        # Display bank amount
        amt_text = self.font.render(f"Bank: ${self.amount}", True, (255, 255, 255))
        screen.blit(amt_text, (x, y))

        # Slider position
        self.slider_rect.topleft = (x, y + 30)
        pygame.draw.rect(screen, (180, 180, 180), self.slider_rect)  # slider bar

        # Handle position based on bet
        handle_x = x + int((self.bet - self.min_bet) / (self.max_bet - self.min_bet) * (self.slider_rect.width - self.slider_handle_rect.width))
        handle_y = y + 25
        self.slider_handle_rect.topleft = (handle_x, handle_y)
        pygame.draw.rect(screen, (255, 255, 0), self.slider_handle_rect)  # handle

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
                # Update handle position
                rel_x = event.pos[0] - self.slider_rect.x
                rel_x = max(0, min(rel_x, self.slider_rect.width - self.slider_handle_rect.width))
                # Map to bet amount
                self.bet = self.min_bet + int(rel_x / (self.slider_rect.width - self.slider_handle_rect.width) * (self.max_bet - self.min_bet))

    def place_bet(self):
        if self.bet > self.amount:
            return False  # cannot bet more than available
        self.amount -= self.bet
        return True

    def payout(self, multiplier=2):
        self.amount += int(self.bet * multiplier)
