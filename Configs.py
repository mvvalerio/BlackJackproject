import pygame
<<<<<<< HEAD
import os

# --------- Diretorio de Imagens ---------

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "png-cards")
=======
import random
import sys
import os
>>>>>>> 72de899d5273040baa6d0fc6d3431c6e2a1d6d8c

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
