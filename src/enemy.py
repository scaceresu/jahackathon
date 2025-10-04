import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((30, 30))
        self.image.fill((200, 200, 220))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.velocidad = 2
        self.direccion = 1 

    def update(self):
        self.rect.x += self.velocidad * self.direccion

        if self.rect.left < 0 or self.rect.right > 800: 
            self.direccion *= -1
