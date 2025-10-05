import pygame
import time

class FoodZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, item_name="lomito", color=(255, 255, 0, 100)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.item_name = item_name
        self.player_timer = {}  # dict: {player: start_time}
        self.give_time = 2  # how long to stay in zone

    def update(self, player=None):
        if player and player.inventory[self.item_name]<1:
            if self.rect.colliderect(player.rect):
                # Если игрок в зоне и таймер ещё не запущен
                if player not in self.player_timer:
                    self.player_timer[player] = time.time()
                else:
                    # Проверяем прошло ли нужное время
                    if (time.time() - self.player_timer[player] >= self.give_time 
                        and self.rect.colliderect(player.rect)):
                        player.add_item(self.item_name, 1)
            else:
                # Если игрок ушёл — сбрасываем таймер
                if player in self.player_timer:
                    del self.player_timer[player]
