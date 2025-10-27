import pygame
from configs import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from jogo import Game

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
