import pygame

class Food(pygame.sprite.Sprite):
    def __init__(self, x,y,width,height, item_name="lomito", color=(255,255,255)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.item_name = item_name
    def update(self, player=None):
        if player:
            if self.rect.colliderect(player.rect):
                player.add_item(self.item_name,1)
                self.kill()