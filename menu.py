import pygame
import sys
import os
from Configs import SCREEN_WIDTH, SCREEN_HEIGHT, TABLE_COLOR, TEXT_COLOR
from botao import Button

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("serif", 36, bold=True)
        self.small_font = pygame.font.SysFont("serif", 24, bold=True)

        # Load logo
        logo_path = os.path.join(os.path.dirname(__file__), "logo", "logo.jpg")
        self.logo = pygame.image.load(logo_path).convert_alpha()
        # Scale logo to full screen size
        self.logo = pygame.transform.smoothscale(self.logo, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Buttons
        btn_y = self.screen.get_height() // 2 + 50
        self.btn_start = Button((self.screen.get_width() // 2 - 100, btn_y, 200, 50), "Start Game", self.small_font)
        self.btn_quit = Button((self.screen.get_width() // 2 - 100, btn_y + 70, 200, 50), "Quit", self.small_font)

    def run(self):
        while True:
            #No green background, logo covers the screen
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_start.clicked(event):
                        return "start_game"
                    elif self.btn_quit.clicked(event):
                        pygame.quit()
                        sys.exit()

            #logo full screen
            self.screen.blit(self.logo, (0, 0))

            #buttons
            mouse_pos = pygame.mouse.get_pos()
            self.btn_start.draw(self.screen, mouse_pos)
            self.btn_quit.draw(self.screen, mouse_pos)

            pygame.display.flip()
