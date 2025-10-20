import pygame, sys
from configs import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from jogo import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Blackjack')
    clock = pygame.time.Clock()
    game = Game(screen)

    fullscreen = False  # inicializacao do fullscreen state

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- Fullscreen toggle ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    game.screen = screen  # update da referencia

                elif event.key == pygame.K_ESCAPE and fullscreen:
                    fullscreen = False
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    game.screen = screen
            game.handle_event(event)

        game.render()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
