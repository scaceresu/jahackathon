# Aquí pueden ir funciones auxiliares (ejemplo: colisiones, cargar imágenes, etc.)

import pygame

def load_image(path):
    return pygame.image.load(path).convert_alpha()

