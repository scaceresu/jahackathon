import pygame
from settings import RED

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 3

    def update(self):
        # Movimiento básico de prueba
        self.rect.y += self.speed
        if self.rect.y > 600:
            self.rect.y = -40

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

