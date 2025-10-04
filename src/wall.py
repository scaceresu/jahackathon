import pygame
from settings import TILE

class Muro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

def cargar_mapa(mapa):
    muros = pygame.sprite.Group()
    for fila, linea in enumerate(mapa):
        for col, celda in enumerate(linea):
            if celda == "#":
                muro = Muro(col * TILE, fila * TILE)
                muros.add(muro)
    return muros