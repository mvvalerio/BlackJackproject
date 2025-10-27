import pygame
import random
import sys
import os

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
RANKS = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
SUITS = {'♠': "Spades", '♥': "Hearts", '♦': "Diamonds", '♣': "Clubs"}
VALUES = {'ace':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'jack':10, 'queen':10, 'king':10}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        return VALUES[self.rank]

    def is_ace(self):
        return self.rank == 'ace'

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
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.is_ace())
        totals = {total}
        for _ in range(aces):
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

class Player:
    def __init__(self):
        self.hands = [Hand()]  # suporte para split, lista de mãos
        self.current_hand = 0

    def reset(self):
        self.hands = [Hand()]
        self.current_hand = 0

    def add_card(self, card):
        self.hands[self.current_hand].add(card)

    def can_split(self):
        if len(self.hands) > 1:
            return False  # só permite split uma vez (pode adaptar depois)
        hand = self.hands[0]
        if len(hand.cards) != 2:
            return False
        c1, c2 = hand.cards[0], hand.cards[1]
        # split se cartas forem exatamente iguais (rank e suit)
        return c1.rank == c2.rank

    def split(self):
        hand = self.hands[0]
        if self.can_split():
            c1 = hand.cards[0]
            c2 = hand.cards[1]
            self.hands = [Hand(), Hand()]
            self.hands[0].add(c1)
            self.hands[1].add(c2)
            self.current_hand = 0
            return True
        return False

class Dealer(Player):
    def __init__(self):
        super().__init__()

    def should_hit(self):
        best = self.hands[0].best_value()
        return best < 17

class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.enabled = True

    def draw(self, surf, mouse_pos):
        color = BUTTON_HIGHLIGHT if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        if not self.enabled:
            color = (120, 120, 120)
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, CARD_BORDER, self.rect, 2, border_radius=6)
        txt = self.font.render(self.text, True, TEXT_COLOR if self.enabled else (100, 100, 100))
        txt_r = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_r)

    def clicked(self, event):
        return self.enabled and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class Game:
    def __init__(self, screen):
        self.card_images = self.load_card_images("png-cards")
        self.screen = screen
        self.deck = Deck(num_decks=4)
        self.player = Player()
        self.dealer = Dealer()
        self.font = pygame.font.SysFont("serif", 22, bold=True)
        self.big_font = pygame.font.SysFont("serif", 36, bold=True)
        self.state = 'idle'  # idle, playing, player_stand, round_over
        self.message = 'Click DEAL to start'

        self.fullscreen = False
        self.base_width = SCREEN_WIDTH
        self.base_height = SCREEN_HEIGHT
        self.base_surface = pygame.Surface((self.base_width, self.base_height))

        # UI Buttons
        self.btn_deal = Button((20, self.base_height - 60, 100, 40), 'DEAL', self.font)
        self.btn_hit = Button((140, self.base_height - 60, 100, 40), 'HIT', self.font)
        self.btn_stand = Button((260, self.base_height - 60, 100, 40), 'STAND', self.font)
        self.btn_split = Button((380, self.base_height - 60, 100, 40), 'SPLIT', self.font)
        self.btn_quit = Button((self.base_width - 120, self.base_height - 60, 100, 40), 'QUIT', self.font)

    def start_round(self):
        self.player.reset()
        self.dealer.reset()
        # mão inicial de 2 cartas
        self.player.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
        self.player.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
        self.state = 'playing'
        self.message = ''
        # Desabilita botão DEAL enquanto jogar
        self.btn_deal.enabled = False
        self.btn_split.enabled = self.player.can_split()
        self.btn_hit.enabled = True
        self.btn_stand.enabled = True

        # verifica Blackjack
        if self.player.hands[0].is_blackjack():
            if self.dealer.hands[0].is_blackjack():
                self.message = 'Push: both have Blackjack'
            else:
                self.message = 'Blackjack! You win!'
            self.state = 'round_over'
            self.btn_deal.enabled = True
            self.btn_hit.enabled = False
            self.btn_stand.enabled = False
            self.btn_split.enabled = False

    def player_hit(self):
        if self.state != 'playing':
            return
        hand = self.player.hands[self.player.current_hand]
        hand.add(self.deck.draw())
        self.btn_split.enabled = False  # após hit, split desabilita

        if hand.is_bust():
            self.message = f'Hand {self.player.current_hand + 1} busted!'

            # Avança para próxima mão, se houver
            if self.player.current_hand + 1 < len(self.player.hands):
                self.player.current_hand += 1
                self.message += f' Playing hand {self.player.current_hand + 1}.'
            else:
                self.message += ' All hands played.'
                self.state = 'player_stand'
                self.btn_hit.enabled = False
                self.btn_stand.enabled = False
                self.btn_split.enabled = False
                self.dealer_play()

        elif 21 in hand.values():
            self.player_stand()

    def player_stand(self):
        if self.state != 'playing':
            return
        # Avança para próxima mão, se houver
        if self.player.current_hand + 1 < len(self.player.hands):
            self.player.current_hand += 1
            self.message = f'Playing hand {self.player.current_hand + 1} of {len(self.player.hands)}'
            self.btn_split.enabled = False  # split só na primeira mão
        else:
            self.state = 'player_stand'
            self.btn_hit.enabled = False
            self.btn_stand.enabled = False
            self.btn_split.enabled = False
            self.dealer_play()


    def player_split(self):
        if self.player.split():
            # adiciona uma carta para cada mão
            self.player.hands[0].add(self.deck.draw())
            self.player.hands[1].add(self.deck.draw())
            self.message = 'Split done: playing first hand'
            self.btn_split.enabled = self.player.can_split()
            # continua jogando na primeira mão
        else:
            self.message = 'Cannot split these cards.'

    def dealer_play(self):
        while not self.dealer.hands[0].is_bust() and self.dealer.should_hit():
            self.dealer.hands[0].add(self.deck.draw())
        self.end_round()

    def end_round(self):
        self.state = 'round_over'
        self.btn_deal.enabled = True
        self.btn_hit.enabled = False
        self.btn_stand.enabled = False
        self.btn_split.enabled = False
        self.message = self.determine_winner()

    def determine_winner(self):
        results = []
        dealer_hand = self.dealer.hands[0]
        d_best = dealer_hand.best_value()
        dealer_bust = dealer_hand.is_bust()

        # avalia cada mão do jogador
        for i, hand in enumerate(self.player.hands):
            p_best = hand.best_value()
            label = f"Hand {i+1}"

            if hand.is_bust():
                results.append(f"{label}: Busted! Dealer wins.")
            elif dealer_bust:
                results.append(f"{label}: Dealer busted! Player wins!")
            elif hand.is_blackjack() and not dealer_hand.is_blackjack():
                results.append(f"{label}: Blackjack! Player wins!")
            elif dealer_hand.is_blackjack() and not hand.is_blackjack():
                results.append(f"{label}: Dealer has Blackjack! You lose.")
            elif p_best > d_best:
                results.append(f"{label}: Player wins!")
            elif p_best < d_best:
                results.append(f"{label}: Dealer wins.")
            else:
                results.append(f"{label}: Push (tie).")

        # Junta mensagens em linhas
        return " | ".join(results)

    def load_card_images(self, folder):
        images = {}
        # Supondo que a pasta tem arquivos no formato "ace_of_spades.png", etc
        for rank in RANKS:
            for suit in SUITS:
                filename = f"{rank}_of_{SUITS[suit].lower()}.png"
                path = os.path.join(folder, filename)
                if os.path.isfile(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (CARD_WIDTH, CARD_HEIGHT))
                    images[(rank, suit)] = img
                else:
                    # placeholder se arquivo não existir (retângulo)
                    img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                    img.fill(CARD_COLOR)
                    pygame.draw.rect(img, CARD_BORDER, img.get_rect(), 2)
                    # Desenha rank e suit texto
                    font = pygame.font.SysFont("serif", 20, bold=True)
                    text1 = font.render(rank[0].upper(), True, TEXT_COLOR)
                    text2 = font.render(suit, True, TEXT_COLOR)
                    img.blit(text1, (5, 5))
                    img.blit(text2, (5, 25))
                    images[(rank, suit)] = img
        # Card back
        back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        back.fill((100, 20, 20))
        pygame.draw.rect(back, (0,0,0), back.get_rect(), 2)
        images['back'] = back
        return images

    def draw_card(self, surf, card, pos):
        img = self.card_images.get((card.rank, card.suit), None)
        if img:
            surf.blit(img, pos)

    def draw_back_card(self, surf, pos):
        surf.blit(self.card_images['back'], pos)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def render(self):
        surf = self.base_surface  # desenhamos na superfície fixa 900x600

        # Fundo mesa
        surf.fill(TABLE_COLOR)
        for y in range(0, self.base_height, 20):
            for x in range(0, self.base_width, 20):
                pygame.draw.circle(surf, (20, 120, 50), (x+10, y+10), 2)

        # Título
        title = self.big_font.render("Casino Clássico - Blackjack", True, (255, 255, 255))
        surf.blit(title, (self.base_width // 2 - title.get_width() // 2, 10))

        # Desenha dealer
        dealer_x = 50
        dealer_y = 80
        surf.blit(self.font.render("Dealer", True, (255,255,255)), (dealer_x, dealer_y - 30))
        for i, card in enumerate(self.dealer.hands[0].cards):
            pos = (dealer_x + i*(CARD_WIDTH+CARD_GAP), dealer_y)
            if self.state == 'playing' and i == 0:
                self.draw_back_card(surf, pos)
            else:
                self.draw_card(surf, card, pos)
        
        dealer_hand = self.dealer.hands[0]
        if self.state == 'playing':
            # Oculta primeira carta enquanto rodada está em andamento
            visible_cards = dealer_hand.cards[1:]
            temp_hand = Hand()
            for c in visible_cards:
                temp_hand.add(c)
            val = temp_hand.best_value() if visible_cards else 0
            val_text = f"Value: {val if val > 0 else '?'}"
        else:
            # Mostra valor total ao final
            val = dealer_hand.best_value()
            val_text = f"Value: {val}" if not dealer_hand.is_bust() else "Bust!"
        
        color = (255,0,0) if dealer_hand.is_bust() else (255,255,255)
        surf.blit(self.font.render(val_text, True, color), (dealer_x, dealer_y + CARD_HEIGHT + 5))

        # Desenha jogador (uma ou duas mãos)
        base_y = self.base_height - CARD_HEIGHT - 120
        for idx, hand in enumerate(self.player.hands):
            hand_x = 50 + idx * (CARD_WIDTH + CARD_GAP) * 5
            label = "Player" + (f" (Hand {idx+1})" if len(self.player.hands) > 1 else "")
            surf.blit(self.font.render(label, True, (255,255,255)), (hand_x, base_y - 30))

            for i, card in enumerate(hand.cards):
                pos = (hand_x + i*(CARD_WIDTH + CARD_GAP), base_y)
                self.draw_card(surf, card, pos)

            # Valor da mão
            val = hand.best_value()
            val_text = f"Value: {val}" if not hand.is_bust() else "Bust!"
            color = (255,0,0) if hand.is_bust() else (255,255,255)
            surf.blit(self.font.render(val_text, True, color), (hand_x, base_y + CARD_HEIGHT + 5))

            # Destacar a mão atual
            if idx == self.player.current_hand:
                pygame.draw.rect(surf, (255, 255, 0), (hand_x - 5, base_y - 5, (CARD_WIDTH + CARD_GAP)*len(hand.cards), CARD_HEIGHT + 10), 3)

        # Mensagem centralizada
        msg_surf = self.font.render(self.message, True, (255, 255, 0))
        surf.blit(msg_surf, (self.base_width // 2 - msg_surf.get_width() // 2, self.base_height - 90))

        # ESCALONAR para tela real
        if self.fullscreen:
            screen_w, screen_h = self.screen.get_size()

            scale_w = screen_w / self.base_width
            scale_h = screen_h / self.base_height
            scale = min(scale_w, scale_h)

            new_w = int(self.base_width * scale)
            new_h = int(self.base_height * scale)

            scaled_surface = pygame.transform.smoothscale(self.base_surface, (new_w, new_h))

            pos_x = (screen_w - new_w) // 2
            pos_y = (screen_h - new_h) // 2

            self.screen.fill((0, 0, 0))  # barras pretas
            self.screen.blit(scaled_surface, (pos_x, pos_y))
        else:
            self.screen.blit(self.base_surface, (0, 0))
            pos_x = 0
            pos_y = 0
            scale = 1

        # Ajusta mouse_pos para os botões no fullscreen
        real_mouse_pos = pygame.mouse.get_pos()
        if self.fullscreen:
            mx, my = real_mouse_pos
            mx = int((mx - pos_x) / scale)
            my = int((my - pos_y) / scale)
            mouse_pos = (mx, my)
        else:
            mouse_pos = real_mouse_pos

        # Botões desenhados na tela real, mas posição fixa, ok
        self.btn_deal.draw(self.screen, mouse_pos)
        self.btn_hit.draw(self.screen, mouse_pos)
        self.btn_stand.draw(self.screen, mouse_pos)
        self.btn_split.draw(self.screen, mouse_pos)
        self.btn_quit.draw(self.screen, mouse_pos)

        pygame.display.flip()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.toggle_fullscreen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_deal.clicked(event):
                    self.start_round()
                elif self.btn_hit.clicked(event):
                    self.player_hit()
                elif self.btn_stand.clicked(event):
                    self.player_stand()
                elif self.btn_split.clicked(event):
                    self.player_split()
                elif self.btn_quit.clicked(event):
                    pygame.quit()
                    sys.exit()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Casino Clássico - Blackjack")
    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        events = pygame.event.get()
        game.handle_events(events)
        game.render()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
