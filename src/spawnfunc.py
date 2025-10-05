import random

import pygame
from settings import TILE
from tilemap import es_tile_transitable, rect_a_tiles


def spawn_on_path(mapa, sprite_width, sprite_height, max_attempts=2000):
    """
    Devuelve (x,y) en píxeles donde un sprite de tamaño sprite_width x sprite_height
    cabe y todos los tiles que ocuparía son transitables (mapa tile == 1).
    Intenta hasta max_attempts veces y lanza ValueError si no encuentra posición.
    """
    h = len(mapa)
    w = len(mapa[0]) if h else 0
    if w == 0 or h == 0:
        raise ValueError("Mapa vacío o inválido")

    # límites en píxeles para topleft de la entidad
    max_x = w * TILE - sprite_width
    max_y = h * TILE - sprite_height

    for _ in range(max_attempts):
        x = random.randint(0, max(0, max_x))
        y = random.randint(0, max(0, max_y))
        rect = pygame.Rect(x, y, sprite_width, sprite_height)
        # comprobar todos los tiles que cubriría el rect
        tiles = rect_a_tiles(rect)
        if tiles and all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
            return x, y
    raise ValueError("No se encontró posición en camino tras many attempts")