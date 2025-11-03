import pygame, sys
from configs import *
from cartas import Deck, Hand
from player import Player, Dealer
from botao import Button
from bank import Bank
from cardSprite import CardSprite

class Game:
    def __init__(self, screen):
        self.base_width = SCREEN_WIDTH
        self.base_height = SCREEN_HEIGHT
        self.base_surface = pygame.Surface((self.base_width, self.base_height))
        self.deck_pos = (self.base_width // 2 - CARD_WIDTH // 2, 50)
        self.card_images = self.load_card_images("imgs")
        self.screen = screen
        self.deck = Deck(num_decks=4)
        self.player = Player()
        self.dealer = Dealer()
        self.font = pygame.font.SysFont("serif", 22, bold=True)
        self.big_font = pygame.font.SysFont("serif", 36, bold=True)
        self.state = 'idle'
        self.message = 'Click DEAL to start'
        self.animated_cards = []  # store CardSprite instances
        self.deck_pos = (self.base_width // 2 - CARD_WIDTH // 2, 50)  # center deck position

        self.fullscreen = False
        self.player_doubled = [False for _ in self.player.hands]

        # UI Buttons
        self.btn_deal = Button((20, self.base_height - 60, 100, 40), 'DEAL', self.font)
        self.btn_hit = Button((140, self.base_height - 60, 100, 40), 'HIT', self.font)
        self.btn_stand = Button((260, self.base_height - 60, 100, 40), 'STAND', self.font)
        self.btn_split = Button((380, self.base_height - 60, 100, 40), 'SPLIT', self.font)
        self.btn_double = Button((500, self.base_height - 60, 120, 40), 'DOUBLE', self.font)
        self.btn_quit = Button((self.base_width - 120, self.base_height - 60, 100, 40), 'QUIT', self.font)

        # Bank
        self.bank = Bank(initial_amount=1000, font=self.font)

    def animate_card_to_player(self, card, hand_index, card_index):
        hand_x = 50 + hand_index * (CARD_WIDTH + CARD_GAP) * 5
        base_y = self.base_height - CARD_HEIGHT - 120
        target_pos = (hand_x + card_index * (CARD_WIDTH + CARD_GAP), base_y)
        img = self.card_images.get((card.rank, card.suit), None)
        if img:
            sprite = CardSprite(img, self.deck_pos, target_pos, speed=15)
            self.animated_cards.append(sprite)

    def animate_card_to_dealer(self, card, card_index):
        dealer_x = 50
        dealer_y = 80
        target_pos = (dealer_x + card_index * (CARD_WIDTH + CARD_GAP), dealer_y)
        img = self.card_images.get((card.rank, card.suit), None)
        if img:
            sprite = CardSprite(img, self.deck_pos, target_pos, speed=15)
            self.animated_cards.append(sprite)

    def start_round(self):
        # Deduct bet first
        if not self.bank.place_bet():
            self.message = "Not enough money to bet!"
            return

        self.player.reset()
        self.dealer.reset()

        # Disable deal button, enable actions
        self.state = 'playing'
        self.message = ''
        self.btn_deal.enabled = False
        self.btn_hit.enabled = True
        self.btn_stand.enabled = True
        self.btn_split.enabled = self.player.can_split()
        self.btn_double.enabled = True
        self.player_doubled = [False for _ in self.player.hands]

        # Deal cards in order: player, dealer, player, dealer
        deal_order = [
            ('player', 0), 
            ('dealer', 0), 
            ('player', 0), 
            ('dealer', 0)
        ]

        for target, hand_index in deal_order:
            card = self.deck.draw()
            if target == 'player':
                # Logic: add to player's hand
                self.player.hands[hand_index].add(card)
                # Animation: slide from deck to hand
                self.animate_card_to_player(card, hand_index, len(self.player.hands[hand_index].cards)-1)
            else:
                # Logic: add to dealer's hand
                self.dealer.hands[hand_index].add(card)
                # Animation: slide from deck to dealer
                self.animate_card_to_dealer(card, len(self.dealer.hands[hand_index].cards)-1)

        # Check for Blackjack immediately
        player_blackjack = self.player.hands[0].is_blackjack()
        dealer_blackjack = self.dealer.hands[0].is_blackjack()

        if player_blackjack or dealer_blackjack:
            if player_blackjack and dealer_blackjack:
                self.message = 'Push: both have Blackjack'
            elif player_blackjack:
                self.message = 'Blackjack! You win!'
                self.bank.payout(2.5)
            else:
                self.message = 'Dealer has Blackjack! You lose.'

            # End round immediately if Blackjack occurs
            self.state = 'round_over'
            self.btn_deal.enabled = True
            self.btn_hit.enabled = False
            self.btn_stand.enabled = False
            self.btn_split.enabled = False
            self.btn_double.enabled = False


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

    def player_double(self):
        if self.state != 'playing':
            return

        hand_index = self.player.current_hand
        hand = self.player.hands[hand_index]

        # Only allow double once per hand
        if self.player_doubled[hand_index]:
            self.message = "You already doubled this hand!"
            return

        # Only allowed with exactly two cards
        if len(hand.cards) != 2:
            self.message = "You can only double on your first two cards!"
            return

        # Check for enough money
        if self.bank.bet > self.bank.amount:
            self.message = "Not enough money to double!"
            return

        # Deduct additional bet
        self.bank.place_bet()
        self.bank.bet *= 2
        self.player_doubled[hand_index] = True

        # Add one card
        hand.add(self.deck.draw())

        # Move to next hand or dealer
        if hand.is_bust():
            self.message = f"Hand {hand_index + 1} busted after double!"
        else:
            self.message = f"Hand {hand_index + 1} doubled down."

        # If more hands remain, move to the next one
        if hand_index + 1 < len(self.player.hands):
            self.player.current_hand += 1
            self.message += f" Playing hand {self.player.current_hand + 1}."
            self.btn_split.enabled = False
            self.btn_double.enabled = True
            self.btn_hit.enabled = True
            self.btn_stand.enabled = True
        else:
            # All hands done, dealer plays
            self.btn_hit.enabled = False
            self.btn_stand.enabled = False
            self.btn_split.enabled = False
            self.btn_double.enabled = False
            self.state = 'player_stand'
            self.dealer_play()

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
        result = self.determine_winner()

        # Handle payouts
        for i, hand in enumerate(self.player.hands):
            p_best = hand.best_value()
            d_best = self.dealer.hands[0].best_value()
            if hand.is_bust():
                continue
            elif self.dealer.hands[0].is_bust() or p_best > d_best:
                self.bank.payout(2)
            elif hand.is_blackjack() and not self.dealer.hands[0].is_blackjack():
                self.bank.payout(2.5)

        self.message = result

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
        surf = self.base_surface
        surf.fill(TABLE_COLOR)

        # Draw table pattern
        for y in range(0, self.base_height, 20):
            for x in range(0, self.base_width, 20):
                pygame.draw.circle(surf, (20, 120, 50), (x+10, y+10), 2)

        # Title
        title = self.big_font.render("Casino Clássico - Blackjack", True, (255, 255, 255))
        surf.blit(title, (self.base_width // 2 - title.get_width() // 2, 10))

        for sprite in self.animated_cards[:]:
            sprite.update()
            sprite.draw(surf)
            if sprite.done:
                self.animated_cards.remove(sprite)

        # Draw dealer
        dealer_x = 50
        dealer_y = 80
        surf.blit(self.font.render("Dealer", True, (255, 255, 255)), (dealer_x, dealer_y - 30))
        dealer_hand = self.dealer.hands[0]
        for i, card in enumerate(dealer_hand.cards):
            pos = (dealer_x + i*(CARD_WIDTH+CARD_GAP), dealer_y)
            if self.state == 'playing' and i == 0:
                self.draw_back_card(surf, pos)
            else:
                self.draw_card(surf, card, pos)

        # Dealer value
        if self.state == 'playing':
            visible_cards = dealer_hand.cards[1:]
            temp_hand = Hand()
            for c in visible_cards:
                temp_hand.add(c)
            val = temp_hand.best_value() if visible_cards else 0
            val_text = f"Value: {val if val > 0 else '?'}"
        else:
            val = dealer_hand.best_value()
            val_text = f"Value: {val}" if not dealer_hand.is_bust() else "Bust!"
        color = (255, 0, 0) if dealer_hand.is_bust() else (255, 255, 255)
        surf.blit(self.font.render(val_text, True, color), (dealer_x, dealer_y + CARD_HEIGHT + 5))

        # Draw player hands
        base_y = self.base_height - CARD_HEIGHT - 120
        for idx, hand in enumerate(self.player.hands):
            hand_x = 50 + idx * (CARD_WIDTH + CARD_GAP) * 5
            label = "Player" + (f" (Hand {idx+1})" if len(self.player.hands) > 1 else "")
            surf.blit(self.font.render(label, True, (255, 255, 255)), (hand_x, base_y - 30))

            for i, card in enumerate(hand.cards):
                pos = (hand_x + i*(CARD_WIDTH + CARD_GAP), base_y)
                self.draw_card(surf, card, pos)

            val = hand.best_value()
            val_text = f"Value: {val}" if not hand.is_bust() else "Bust!"
            color = (255, 0, 0) if hand.is_bust() else (255, 255, 255)
            surf.blit(self.font.render(val_text, True, color), (hand_x, base_y + CARD_HEIGHT + 5))

            # Highlight current hand
            if len(self.player.hands) > 1 and idx == self.player.current_hand:
                pygame.draw.rect(surf, (255, 255, 255),
                                (hand_x - 5, base_y - 5, (CARD_WIDTH + CARD_GAP) * len(hand.cards), CARD_HEIGHT + 10), 3)

        # Message
        msg_surf = self.font.render(self.message, True, (255, 255, 0))
        surf.blit(msg_surf, (self.base_width // 2 - msg_surf.get_width() // 2, self.base_height - 370 ))

        # Draw Bank
        self.bank.draw(surf, (self.base_width - 220, 70))

        # Determine scaled mouse position
        mx, my = pygame.mouse.get_pos()
        if self.fullscreen:
            screen_w, screen_h = self.screen.get_size()
            scale_w = screen_w / self.base_width
            scale_h = screen_h / self.base_height
            scale = min(scale_w, scale_h)

            new_w = int(self.base_width * scale)
            new_h = int(self.base_height * scale)
            pos_x = (screen_w - new_w) // 2
            pos_y = (screen_h - new_h) // 2

            mouse_pos = ((mx - pos_x) / scale, (my - pos_y) / scale)
        else:
            scale = 1
            pos_x = pos_y = 0
            mouse_pos = (mx, my)

        # Draw buttons on base surface
        self.btn_deal.draw(surf, mouse_pos)
        self.btn_hit.draw(surf, mouse_pos)
        self.btn_stand.draw(surf, mouse_pos)
        self.btn_split.draw(surf, mouse_pos)
        self.btn_double.draw(surf, mouse_pos)
        self.btn_quit.draw(surf, mouse_pos)

        # Blit scaled surface to screen
        if self.fullscreen:
            scaled_surface = pygame.transform.smoothscale(self.base_surface, (new_w, new_h))
            self.screen.fill((0, 0, 0))  # black bars
            self.screen.blit(scaled_surface, (pos_x, pos_y))
        else:
            self.screen.blit(self.base_surface, (0, 0))

        pygame.display.flip()


    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Toggle fullscreen
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()

                # Pass keyboard events to bank for typing
                self.bank.handle_event(event)

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                # Scale mouse coordinates for fullscreen
                mx, my = event.pos
                if self.fullscreen:
                    screen_w, screen_h = self.screen.get_size()
                    scale_w = screen_w / self.base_width
                    scale_h = screen_h / self.base_height
                    scale = min(scale_w, scale_h)
                    new_w = int(self.base_width * scale)
                    new_h = int(self.base_height * scale)
                    pos_x = (screen_w - new_w) // 2
                    pos_y = (screen_h - new_h) // 2
                    scaled_mouse = ((mx - pos_x) / scale, (my - pos_y) / scale)
                else:
                    scaled_mouse = (mx, my)

                # Pass mouse events to bank
                temp_event = pygame.event.Event(event.type, {**event.dict, "pos": scaled_mouse})
                self.bank.handle_event(temp_event)

                # Handle your buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_deal.clicked(temp_event):
                        self.start_round()
                    elif self.btn_hit.clicked(temp_event):
                        self.player_hit()
                    elif self.btn_stand.clicked(temp_event):
                        self.player_stand()
                    elif self.btn_split.clicked(temp_event):
                        self.player_split()
                    elif self.btn_double.clicked(temp_event):
                        self.player_double()
                    elif self.btn_quit.clicked(temp_event):
                        pygame.quit()
                        sys.exit()
