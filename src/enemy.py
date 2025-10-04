import pygame
import os
import time
from settings import TILE_SIZE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, horizontal=True, distancia=128, velocidad=1, anim_folder=None, frame_delay=0.2):
        super().__init__()

        self.full_frames = []
        if anim_folder:
            frames = [pygame.image.load(os.path.join(anim_folder, f"{i}.png")).convert_alpha() for i in range(1,7)]
            
            # Определяем кол-во колонок и рядов в зависимости от направления
            if horizontal:
                cols, rows = 3, 2
            else:
                cols, rows = 2, 3

            surf = pygame.Surface((TILE_SIZE*cols, TILE_SIZE*rows), pygame.SRCALPHA)
            for idx, frame in enumerate(frames):
                col = idx % cols
                row = idx // cols
                surf.blit(frame, (col*TILE_SIZE, row*TILE_SIZE))
            
            self.full_frames.append(surf)
        else:
            # fallback
            if horizontal:
                surf = pygame.Surface((TILE_SIZE*3, TILE_SIZE*2))
            else:
                surf = pygame.Surface((TILE_SIZE*2, TILE_SIZE*3))
            surf.fill((200,200,220))
            self.full_frames.append(surf)

        # анимация
        self.current_frame = 0
        self.frame_delay = frame_delay
        self.last_frame_time = time.time()
        self.image = self.full_frames[self.current_frame]

        # размер rect в зависимости от ориентации
        if horizontal:
            self.rect = pygame.Rect(x, y, TILE_SIZE*3, TILE_SIZE*2)
        else:
            self.rect = pygame.Rect(x, y, TILE_SIZE*2, TILE_SIZE*3)

        # движение
        self.horizontal = horizontal
        self.velocidad = velocidad
        self.direccion = 1
        self.distancia = distancia
        self.start_pos = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)

    def update(self):
        ahora = time.time()

        # движение
        if self.horizontal:
            self.pos.x += self.velocidad * self.direccion
            if abs(self.pos.x - self.start_pos.x) >= self.distancia:
                self.direccion *= -1
        else:
            self.pos.y += self.velocidad * self.direccion
            if abs(self.pos.y - self.start_pos.y) >= self.distancia:
                self.direccion *= -1

        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # анимация
        if ahora - self.last_frame_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.full_frames)
            self.image = self.full_frames[self.current_frame]
            self.last_frame_time = ahora

