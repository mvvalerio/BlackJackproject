import pygame
import random
import sys
import os

# --------- Constantes ---------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 80
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
