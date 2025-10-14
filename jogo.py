import pygame, sys
from configs import *
from cartas import Deck
from player import Player, Dealer
from botao import Button

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.deck = Deck(num_decks=4)
        self.player = Player()
        self.dealer = Dealer()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 32)
        self.state = 'idle'
        self.message = 'Click DEAL to start'

        # Botões
        self.btn_deal = Button((20, SCREEN_HEIGHT - 60, 100, 40), 'DEAL', self.font)
        self.btn_hit = Button((140, SCREEN_HEIGHT - 60, 100, 40), 'HIT', self.font)
        self.btn_stand = Button((260, SCREEN_HEIGHT - 60, 100, 40), 'STAND', self.font)
        self.btn_quit = Button((SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 40), 'QUIT', self.font)

    # ----- Lógica de jogo -----
    def start_round(self):
        self.player.hand.clear()
        self.dealer.hand.clear()
        for _ in range(2):
            self.player.hand.add(self.deck.draw())
            self.dealer.hand.add(self.deck.draw())
        self.state = 'playing'
        self.message = 'Your move: HIT or STAND'
        if self.player.hand.is_blackjack():
            if self.dealer.hand.is_blackjack():
                self.message = 'Push: both have Blackjack'
            else:
                self.message = 'Blackjack! You win!'
            self.state = 'round_over'

    def player_hit(self):
        if self.state != 'playing': return
        self.player.hand.add(self.deck.draw())
        if self.player.hand.is_bust():
            self.message = 'You busted! Dealer wins.'
            self.state = 'round_over'

    def player_stand(self):
        if self.state != 'playing': return
        self.state = 'player_stand'
        self.dealer_play()

    def dealer_play(self):
        while not self.dealer.hand.is_bust() and self.dealer.should_hit():
            self.dealer.hand.add(self.deck.draw())
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

    # ----- Renderização -----
    def draw_card(self, surf, card, pos):
        x, y = pos
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surf, CARD_COLOR, rect, border_radius=8)
        pygame.draw.rect(surf, CARD_BORDER, rect, 2, border_radius=8)
        suit_color = (200, 0, 0) if card.suit in ('♥', '♦') else TEXT_COLOR
        surf.blit(self.font.render(card.rank, True, suit_color), (x+6, y+6))
        surf.blit(self.font.render(card.suit, True, suit_color), (x+6, y+26))
        big = self.big_font.render(f'{card.rank}{card.suit}', True, suit_color)
        surf.blit(big, big.get_rect(center=rect.center))

    def draw_back_card(self, surf, pos):
        x, y = pos
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surf, (20, 60, 120), rect, border_radius=8)
        pygame.draw.rect(surf, CARD_BORDER, rect, 2, border_radius=8)
        surf.blit(self.big_font.render('🂠', True, (255,255,255)),
                  self.big_font.render('🂠', True, (255,255,255)).get_rect(center=rect.center))

    def render(self):
        surf = self.screen
        surf.fill(TABLE_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        # Dealer
        surf.blit(self.big_font.render('Dealer', True, (255,255,255)), (20,20))
        for i, c in enumerate(self.dealer.hand.cards):
            x = 20 + i * (CARD_WIDTH + CARD_GAP)
            if i == 0 and self.state == 'playing':
                self.draw_back_card(surf, (x, 60))
            else:
                self.draw_card(surf, c, (x, 60))

        # Player
        surf.blit(self.big_font.render('Player', True, (255,255,255)), (20,240))
        for i, c in enumerate(self.player.hand.cards):
            self.draw_card(surf, c, (20 + i*(CARD_WIDTH+CARD_GAP), 280))

        # Mensagem
        msg_surf = self.big_font.render(self.message, True, (255,255,0))
        surf.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, SCREEN_HEIGHT - 120))

        # Botões
        for btn in [self.btn_deal, self.btn_hit, self.btn_stand, self.btn_quit]:
            btn.draw(surf, mouse_pos)

    def handle_event(self, event):
        if self.btn_quit.clicked(event):
            pygame.quit(); sys.exit()
        if self.btn_deal.clicked(event):
            self.start_round()
        if self.btn_hit.clicked(event):
            self.player_hit()
        if self.btn_stand.clicked(event):
            self.player_stand()
