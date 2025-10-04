import pygame
from settings import GREEN

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidad = 5

    def update(self, teclas, muros):
        dx, dy = 0, 0
        if teclas[pygame.K_LEFT]:
            dx = -self.velocidad
        if teclas[pygame.K_RIGHT]:
            dx = self.velocidad
        if teclas[pygame.K_UP]:
            dy = -self.velocidad
        if teclas[pygame.K_DOWN]:
            dy = self.velocidad

        self.rect.x += dx
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                if dx > 0: self.rect.right = muro.rect.left
                if dx < 0: self.rect.left = muro.rect.right

        self.rect.y += dy
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                if dy > 0: self.rect.bottom = muro.rect.top
                if dy < 0: self.rect.top = muro.rect.bottom

