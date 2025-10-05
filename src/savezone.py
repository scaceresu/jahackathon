import pygame

class SaveZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(255, 0, 0, 100)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))