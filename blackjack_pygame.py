import pygame
import random
import sys

# --------- Constantes ---------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 30
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_GAP = 20
TABLE_COLOR = (18, 100, 41)
CARD_COLOR = (245, 245, 245)
CARD_BORDER = (20, 20, 20)
TEXT_COLOR = (10, 10, 10)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HIGHLIGHT = (170, 170, 170)

# --------- Classes de Deck, Mão e Cartas ---------
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['♠', '♥', '♦', '♣']
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':10, 'Q':10, 'K':10}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        return VALUES[self.rank]

    def is_ace(self):
        return self.rank == 'A'

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
        # returns possible totals (accounting for Aces)
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.is_ace())
        totals = {total}
        for _ in range(aces):
            # Each ace can add +10 (since counted as 1 already, 11 instead gives +10)
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

# --------- Classe do Player e do Dealer ---------
class Player:
    def __init__(self):
        self.hand = Hand()

class Dealer(Player):
    def __init__(self):
        super().__init__()

    def should_hit(self):
        # dealer hits until 17 or higher (soft 17 stands here)
        best = self.hand.best_value()
        return best < 17

# --------- Botões ---------
class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font

    def draw(self, surf, mouse_pos):
        color = BUTTON_HIGHLIGHT if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, CARD_BORDER, self.rect, 2, border_radius=6)
        txt = self.font.render(self.text, True, TEXT_COLOR)
        txt_r = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_r)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --------- Classe do jogo ---------
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.deck = Deck(num_decks=4)
        self.player = Player()
        self.dealer = Dealer()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 32)
        self.state = 'idle'  # idle, playing, player_stand, round_over
        self.message = 'Click DEAL to start'

        # UI Buttons
        self.btn_deal = Button((20, SCREEN_HEIGHT - 60, 100, 40), 'DEAL', self.font)
        self.btn_hit = Button((140, SCREEN_HEIGHT - 60, 100, 40), 'HIT', self.font)
        self.btn_stand = Button((260, SCREEN_HEIGHT - 60, 100, 40), 'STAND', self.font)
        self.btn_quit = Button((SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 40), 'QUIT', self.font)

    def start_round(self):
        self.player.hand.clear()
        self.dealer.hand.clear()
        # mão inicial de 2 cartas
        self.player.hand.add(self.deck.draw())
        self.dealer.hand.add(self.deck.draw())
        self.player.hand.add(self.deck.draw())
        self.dealer.hand.add(self.deck.draw())
        self.state = 'playing'
        self.message = 'Your move: HIT or STAND'
        # verifica o Blackjack
        if self.player.hand.is_blackjack():
            if self.dealer.hand.is_blackjack():
                self.message = 'Push: both have Blackjack'
            else:
                self.message = 'Blackjack! You win!'
            self.state = 'round_over'

    def player_hit(self):
        if self.state != 'playing':
            return
        self.player.hand.add(self.deck.draw())
        if self.player.hand.is_bust():
            self.message = 'You busted! Dealer wins.'
            self.state = 'round_over'

    def player_stand(self):
        if self.state != 'playing':
            return
        self.state = 'player_stand'
        self.dealer_play()

    def dealer_play(self):
        # dealer joga automaticamente
        while not self.dealer.hand.is_bust() and self.dealer.should_hit():
            self.dealer.hand.add(self.deck.draw())
        # decide
        self.resolve_round()

    def resolve_round(self):
        if self.dealer.hand.is_bust():
            self.message = 'Dealer busted — you win!'
        else:
            p_val = self.player.hand.best_value()
            d_val = self.dealer.hand.best_value()
            if p_val > 21:
                self.message = 'You busted — dealer wins.'
            elif p_val > d_val:
                self.message = f'You win! {p_val} vs {d_val}'
            elif p_val < d_val:
                self.message = f'Dealer wins: {d_val} vs {p_val}'
            else:
                self.message = f'Push: {p_val}'
        self.state = 'round_over'

    def draw_card(self, surf, card, pos):
        x, y = pos
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surf, CARD_COLOR, rect, border_radius=8)
        pygame.draw.rect(surf, CARD_BORDER, rect, 2, border_radius=8)
        # cor da carta
        suit_color = (200, 0, 0) if card.suit in ('♥', '♦') else TEXT_COLOR
        r1 = self.font.render(card.rank, True, suit_color)
        r2 = self.font.render(card.suit, True, suit_color)
        surf.blit(r1, (x + 6, y + 6))
        surf.blit(r2, (x + 6, y + 26))
        # ficar no centro
        big = self.big_font.render(f'{card.rank}{card.suit}', True, suit_color)
        bc = big.get_rect(center=rect.center)
        surf.blit(big, bc)

    def draw_back_card(self, surf, pos):
        x, y = pos
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surf, (20, 60, 120), rect, border_radius=8)
        pygame.draw.rect(surf, CARD_BORDER, rect, 2, border_radius=8)
        txt = self.big_font.render('🂠', True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=rect.center))

    def render(self):
        surf = self.screen
        surf.fill(TABLE_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        # Area do Dealter
        dealer_txt = self.big_font.render('Dealer', True, (255, 255, 255))
        surf.blit(dealer_txt, (20, 20))
        # Desenha as cartas dele
        dx = 20
        dy = 60
        for i, c in enumerate(self.dealer.hand.cards):
            x = dx + i * (CARD_WIDTH + CARD_GAP)
            if i == 0 and self.state == 'playing':
                # esconde a mão do dealer até o fim do jogo
                self.draw_back_card(surf, (x, dy))
            else:
                self.draw_card(surf, c, (x, dy))

        # area do Player
        player_txt = self.big_font.render('Player', True, (255, 255, 255))
        surf.blit(player_txt, (20, 240))
        px = 20
        py = 280
        for i, c in enumerate(self.player.hand.cards):
            x = px + i * (CARD_WIDTH + CARD_GAP)
            self.draw_card(surf, c, (x, py))

        # Valores
        val_y = py + CARD_HEIGHT + 10
        if self.state == 'playing':
            player_val = ', '.join(str(v) for v in self.player.hand.values())
            val_surf = self.font.render(f'Player value(s): {player_val}', True, (255, 255, 255))
            surf.blit(val_surf, (20, val_y))
        else:
            # mostra o resultado final do dealer
            p_val = ', '.join(str(v) for v in self.player.hand.values())
            d_val = ', '.join(str(v) for v in self.dealer.hand.values())
            surf.blit(self.font.render(f'Player value(s): {p_val}', True, (255,255,255)), (20, val_y))
            surf.blit(self.font.render(f'Dealer value(s): {d_val}', True, (255,255,255)), (20, val_y + 22))

        # Mensagem
        msg_surf = self.big_font.render(self.message, True, (255, 255, 0))
        surf.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, SCREEN_HEIGHT - 120))

        # Butões
        self.btn_deal.draw(surf, mouse_pos)
        self.btn_hit.draw(surf, mouse_pos)
        self.btn_stand.draw(surf, mouse_pos)
        self.btn_quit.draw(surf, mouse_pos)

    def handle_event(self, event):
        if self.btn_quit.clicked(event):
            pygame.quit()
            sys.exit()
        if self.btn_deal.clicked(event):
            self.start_round()
        if self.btn_hit.clicked(event):
            self.player_hit()
        if self.btn_stand.clicked(event):
            self.player_stand()

# --------- Pygame loop ---------

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Blackjack - OOP Pygame Example')
    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.render()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
