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
        self.delivery_time = 2  # stay en zone how long

    def update(self, player):
        # check if we are staying
        in_zone = self.rect.colliderect(player.rect)

        # if in zone and he got object
        if in_zone and (player.inventory.get("lomito", 0) > 0 or player.inventory.get("empanada", 0) > 0):
            #   start timer only 1 time
            if not self.delivering:
                self.delivering = True
                self.start_time = time.time()
                self.item = "lomito" if player.inventory.get("lomito", 0) > 0 else "empanada"
            
            # check if delivery food 
            elif time.time() - self.start_time >= self.delivery_time:
                if self.item and player.inventory.get(self.item, 0) > 0:
                    player.inventory[self.item] -= 1
                self.delivering = False
                self.item = None

        else:
            # if he exit the square time would start again
            if self.delivering:
                self.delivering = False
                self.item = None
