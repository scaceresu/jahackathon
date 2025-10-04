import pygame
import time

class DeliveryZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0, 200, 0, 100)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.delivering = False
        self.start_time = 0
        self.item = None

    def update(self, player):
        # Проверка, есть ли игрок в зоне и есть ли у него ломито или эмпанада
        if player.rect.colliderect(self.rect) and (
            player.inventory.get("lomito", 0) > 0 or player.inventory.get("empanada", 0) > 0
        ):
            if not self.delivering:
                self.delivering = True
                self.start_time = time.time()
                # Определяем какой предмет доставляется первым
                if player.inventory.get("lomito", 0) > 0:
                    self.item = "lomito"
                else:
                    self.item = "empanada"

        # Если таймер активен, проверяем прошло ли 2 секунды
        if self.delivering:
            if time.time() - self.start_time >= 2:
                if self.item and player.inventory.get(self.item, 0) > 0:
                    player.inventory[self.item] -= 1
                self.delivering = False
                self.item = None

