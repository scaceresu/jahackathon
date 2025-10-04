import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(255, 255, 0, 255)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, player=None):
        if player:
            # Проверка столкновения с игроком
            if self.rect.colliderect(player.rect):
                player.coin += 1
                self.kill()