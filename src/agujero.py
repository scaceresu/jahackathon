import pygame

class Agujero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # tamaño del sprite en píxeles; elegí 16x16 para encajar con un tile (ajustalo si tu sprite es mayor)
        self.image = pygame.Surface((8, 8))
        self.image.fill((150, 75, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
