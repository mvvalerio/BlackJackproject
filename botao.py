import pygame
from Configs import BUTTON_COLOR, BUTTON_HIGHLIGHT, CARD_BORDER, TEXT_COLOR

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
