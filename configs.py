import pygame
import os

# --------- Constantes gerais --------- 
SCREEN_WIDTH = 900 
SCREEN_HEIGHT = 600 
FPS = 30 
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

# caminho absoluto da pasta do ficheiro atual
BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "imgs")

# --------- Naipes ---------
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] 
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':10, 'Q':10, 'K':10}

SUITS = {
    'spade': pygame.image.load(os.path.join(IMG_DIR, "spades.png")),
    'heart': pygame.image.load(os.path.join(IMG_DIR, "hearts.png")),
    'diamond': pygame.image.load(os.path.join(IMG_DIR, "diamonds.png")),
    'club': pygame.image.load(os.path.join(IMG_DIR, "clubs.png"))
}

SUIT_SYMBOLS = { 'spade': '♠', 'heart': '♥', 'diamond': '♦', 'club': '♣' }

# redimensionar
for key in SUITS:
    SUITS[key] = pygame.transform.scale(SUITS[key], (50, 50))
for name in ["spades.png", "hearts.png", "diamonds.png", "clubs.png"]:
    path = os.path.join(IMG_DIR, name)
    print(f"{name}: {os.path.exists(path)}")
