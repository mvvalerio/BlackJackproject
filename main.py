import pygame, sys
from configs import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from jogo import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Blackjack - OOP Pygame')
    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            game.handle_event(event)

        game.render()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
