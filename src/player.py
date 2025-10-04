import pygame
from settings import GREEN

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidad = 5
        self.scores = 0
        self.vidas = 3

    def update(self, teclas, muros, enemigos=None):
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

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(1088, self.rect.right)

        self.rect.y += dy
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                if dy > 0: self.rect.bottom = muro.rect.top
                if dy < 0: self.rect.top = muro.rect.bottom

        self.rect.top = max(80, self.rect.top)
        self.rect.bottom = min(800, self.rect.bottom)

        if enemigos:
            colisiones = pygame.sprite.spritecollide(self, enemigos, False)
            for enemigo in colisiones:
                self.vidas -= 1
                self.rect.topleft = (100, 100)  # стартовая позиция
                break  

        if self.vidas <= 0:
            print("Game Over")
            exit()

