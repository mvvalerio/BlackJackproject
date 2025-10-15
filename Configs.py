import pygame

# --------- Constantes gerais ---------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_GAP = 20

# --------- Cores ---------
TABLE_COLOR = (18, 100, 41)
CARD_COLOR = (245, 245, 245)
CARD_BORDER = (20, 20, 20)
TEXT_COLOR = (10, 10, 10)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HIGHLIGHT = (170, 170, 170)

# --------- Baralho ---------
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = [pygame.image.load("https://upload.wikimedia.org/wikipedia/commons/e/e7/Spades.svg"), pygame.image.load("https://freesvg.org/img/jean_victor_balin_card_coeur.png"), pygame.image.load("https://upload.wikimedia.org/wikipedia/en/thumb/1/1f/Card_diamond.svg/1486px-Card_diamond.svg.png"), pygame.image.load("https://upload.wikimedia.org/wikipedia/en/thumb/0/0a/Card_club.svg/1954px-Card_club.svg.png")]
SUITS = pygame.transform.scale(SUITS, 50, 50)
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7,
          '8':8, '9':9, '10':10, 'J':10, 'Q':10, 'K':10}