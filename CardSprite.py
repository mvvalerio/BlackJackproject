import pygame

class CardSprite:
    def __init__(self, image, start_pos, target_pos, speed=10):
        self.image = image
        self.pos = pygame.Vector2(start_pos)
        self.target = pygame.Vector2(target_pos)
        self.speed = speed  # pixels per frame
        self.done = False

    def update(self):
        if not self.done:
            direction = self.target - self.pos
            if direction.length() < self.speed:
                self.pos = self.target
                self.done = True
            else:
                self.pos += direction.normalize() * self.speed

    def draw(self, surf):
        surf.blit(self.image, self.pos)