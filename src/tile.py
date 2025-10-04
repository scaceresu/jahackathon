import pygame
import json

TILE_SIZE = 16

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

def cargar_mapa_tmj(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        data = json.load(f)

    tiles_group = pygame.sprite.Group()
    width = data["width"]
    height = data["height"]
    layers = data["layers"]

    for layer in layers:
        if layer["type"] == "tilelayer" and "data" in layer:
            tile_data = layer["data"]
            for y in range(height):
                for x in range(width):
                    tile_id = tile_data[y * width + x]
                    if tile_id != 0:
                        # generate color for map
                        color = (
                            (tile_id * 50) % 255,
                            (tile_id * 80) % 255,
                            (tile_id * 110) % 255
                        )
                        tile = Tile(x * TILE_SIZE, y * TILE_SIZE, color)
                        tiles_group.add(tile)

    return tiles_group, TILE_SIZE, TILE_SIZE
