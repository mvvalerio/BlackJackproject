import pygame, sys
from configs import *
from cartas import Deck
from player import Player, Dealer
from botao import Button
from bank import Bank

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
        self.bank = Bank()
        self.bet_options = [10, 50, 100, 200, 500]
        self.selected_bet = 50
        self.bet_buttons = [
            Button((400 + i*100, SCREEN_HEIGHT - 60, 80, 40), f"${amt}", self.font)
            for i, amt in enumerate(self.bet_options)
        ]


        # Botões
        self.btn_deal = Button((20, SCREEN_HEIGHT - 60, 100, 40), 'DEAL', self.font)
        self.btn_hit = Button((140, SCREEN_HEIGHT - 60, 100, 40), 'HIT', self.font)
        self.btn_stand = Button((260, SCREEN_HEIGHT - 60, 100, 40), 'STAND', self.font)
        self.btn_quit = Button((SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 40), 'QUIT', self.font)

    # ----- Lógica de jogo -----
    def start_round(self):
        if self.bank.is_broke():
            self.state = 'game_over'
            self.message = 'Você ficou sem dinheiro! Fim de jogo.'
            return

        if not self.bank.place_bet(self.selected_bet):
            self.message = 'Saldo insuficiente para essa aposta.'
            return

        self.player.hand.clear()
        self.dealer.hand.clear()
        for _ in range(2):
            self.player.hand.add(self.deck.draw())
            self.dealer.hand.add(self.deck.draw())
        self.state = 'playing'
        self.message = f'Aposta: ${self.selected_bet} | Saldo: ${self.bank.balance}'

        if self.player.hand.is_blackjack():
            if self.dealer.hand.is_blackjack():
                self.bank.push()
                self.message = 'Push: ambos Blackjack!'
            else:
                self.bank.win()
                self.message = 'Blackjack! Você ganhou!'
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
            self.bank.win()
            self.message = f'Dealer estourou! Você ganhou ${self.selected_bet}'
        else:
            p_val = self.player.hand.best_value()
            d_val = self.dealer.hand.best_value()
            if p_val > 21:
                self.bank.lose()
                self.message = f'Você estourou — perdeu ${self.selected_bet}'
            elif p_val > d_val:
                self.bank.win()
                self.message = f'Você ganhou ${self.selected_bet}!'
            elif p_val < d_val:
                self.bank.lose()
                self.message = f'Dealer ganhou — perdeu ${self.selected_bet}'
            else:
                self.bank.push()
                self.message = f'Empate — aposta devolvida.'
        self.state = 'round_over'


    # ----- Renderização -----
    def draw_card(self, surf, card, pos):
        x, y = pos
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        
        # fundo da carta
        pygame.draw.rect(surf, CARD_COLOR, rect, border_radius=8)
        pygame.draw.rect(surf, CARD_BORDER, rect, 2, border_radius=8)

        # cor depende do naipe
        suit_color = (200, 0, 0) if card.suit in ('heart', 'diamond') else TEXT_COLOR

        # rank pequeno no canto superior esquerdo
        rank_text = self.font.render(card.rank, True, suit_color)
        surf.blit(rank_text, (x + 8, y + 6))

        # rank pequeno no canto inferior direito (espelhado)
        rank_text_rot = pygame.transform.rotate(rank_text, 180)
        surf.blit(rank_text_rot, (x + CARD_WIDTH - rank_text.get_width() - 8, 
                                y + CARD_HEIGHT - rank_text.get_height() - 6))

        # imagem do naipe centralizada
        suit_img = SUITS.get(card.suit)
        if suit_img:
            img_rect = suit_img.get_rect(center=rect.center)
            surf.blit(suit_img, img_rect)
        else:
            # fallback se imagem faltar
            suit_symbol = SUIT_SYMBOLS.get(card.suit, '?')
            big = self.big_font.render(suit_symbol, True, suit_color)
            surf.blit(big, big.get_rect(center=rect.center))


    def draw_back_card(self, surf, pos):
        x, y = pos
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surf, (20, 60, 120), rect, border_radius=8)
        pygame.draw.rect(surf, CARD_BORDER, rect, 2, border_radius=8)
        surf.blit(self.big_font.render('🂠', True, (255,255,255)),
                  self.big_font.render('🂠', True, (255,255,255)).get_rect(center=rect.center))

    def render(self):
        # render em um tamanho fixo
        base_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        base_surface.fill(TABLE_COLOR)

        # computar a escala e o offset
        window_width, window_height = self.screen.get_size()
        aspect_base = SCREEN_WIDTH / SCREEN_HEIGHT
        aspect_window = window_width / window_height

        if aspect_window > aspect_base:
            new_height = window_height
            new_width = int(new_height * aspect_base)
        else:
            new_width = window_width
            new_height = int(new_width / aspect_base)

        x_center = (window_width - new_width) // 2
        y_center = (window_height - new_height) // 2

        # converte a posicao do mouse para as coordenadas base
        mx, my = pygame.mouse.get_pos()
        # na area escalada
        if x_center <= mx <= x_center + new_width and y_center <= my <= y_center + new_height:
            # voltar a escala
            scale_x = SCREEN_WIDTH / new_width
            scale_y = SCREEN_HEIGHT / new_height
            base_mouse = ((mx - x_center) * scale_x, (my - y_center) * scale_y)
        else:
            base_mouse = (-1, -1)  # fora da area

        # Dealer
        base_surface.blit(self.big_font.render('Dealer', True, (255,255,255)), (20, 20))
        for i, c in enumerate(self.dealer.hand.cards):
            x = 20 + i * (CARD_WIDTH + CARD_GAP)
            if i == 0 and self.state == 'playing':
                self.draw_back_card(base_surface, (x, 60))
            else:
                self.draw_card(base_surface, c, (x, 60))

        # Player
        base_surface.blit(self.big_font.render('Player', True, (255,255,255)), (20, 240))
        for i, c in enumerate(self.player.hand.cards):
            self.draw_card(base_surface, c, (20 + i*(CARD_WIDTH+CARD_GAP), 280))

        # mensagem
        msg_surf = self.big_font.render(self.message, True, (255,255,0))
        base_surface.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, SCREEN_HEIGHT - 120))

        # butoes
        for btn in [self.btn_deal, self.btn_hit, self.btn_stand, self.btn_quit]:
            btn.draw(base_surface, base_mouse)

        # informacao de saldo
        info_text = f"Saldo: ${self.bank.balance} | Aposta: ${self.selected_bet}"
        base_surface.blit(self.big_font.render(info_text, True, (255,255,255)), (20, SCREEN_HEIGHT - 160))

        # escala para a tela principal
        scaled_surface = pygame.transform.smoothscale(base_surface, (new_width, new_height))
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_surface, (x_center, y_center))


    def handle_event(self, event):
        # ajustar o mouse para a tela escalada
        window_width, window_height = self.screen.get_size()
        aspect_base = SCREEN_WIDTH / SCREEN_HEIGHT
        aspect_window = window_width / window_height

        if aspect_window > aspect_base:
            new_height = window_height
            new_width = int(new_height * aspect_base)
        else:
            new_width = window_width
            new_height = int(new_width / aspect_base)

        x_center = (window_width - new_width) // 2
        y_center = (window_height - new_height) // 2

        # evento de reescalar a posicao do mouse
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mx, my = event.pos
            if x_center <= mx <= x_center + new_width and y_center <= my <= y_center + new_height:
                scale_x = SCREEN_WIDTH / new_width
                scale_y = SCREEN_HEIGHT / new_height
                event.pos = ((mx - x_center) * scale_x, (my - y_center) * scale_y)
            else:
                return

        # cliques normalmente em coordenadas de base
        if self.btn_quit.clicked(event):
            pygame.quit(); sys.exit()
        if self.btn_deal.clicked(event):
            self.start_round()
        if self.btn_hit.clicked(event):
            self.player_hit()
        if self.btn_stand.clicked(event):
            self.player_stand()

        if self.state in ('idle', 'round_over'):
            for btn, amt in zip(self.bet_buttons, self.bet_options):
                if btn.clicked(event):
                    self.selected_bet = amt
                    self.message = f"Aposta selecionada: ${amt}"