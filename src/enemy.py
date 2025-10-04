import pygame
import os
import time
from settings import TILE_SIZE,SAFE_ZONE_X,SAFE_ZONE_Y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, horizontal=True, distancia=128, velocidad=1,
                 anim_folder=None, frame_delay=0.2, aggro_radius=150):
        super().__init__()
        # --- Sprites ---
        self.full_frames = []
        if anim_folder:
            frames = [pygame.image.load(os.path.join(anim_folder, f"{i}.png")).convert_alpha()
                      for i in range(1, 7)]
            cols, rows = (3, 2) if horizontal else (2, 3)
            surf = pygame.Surface((TILE_SIZE * cols, TILE_SIZE * rows), pygame.SRCALPHA)
            for idx, frame in enumerate(frames):
                col = idx % cols
                row = idx // cols
                surf.blit(frame, (col * TILE_SIZE, row * TILE_SIZE))
            self.full_frames.append(surf)
        else:
            surf = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 2)) if horizontal else pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 3))
            surf.fill((200, 200, 220))
            self.full_frames.append(surf)

        self.current_frame = 0
        self.frame_delay = frame_delay
        self.last_frame_time = time.time()
        self.image = self.full_frames[self.current_frame]

        w, h = (TILE_SIZE * 3, TILE_SIZE * 2) if horizontal else (TILE_SIZE * 2, TILE_SIZE * 3)
        self.rect = pygame.Rect(x, y, w, h)

        self.horizontal = horizontal
        self.velocidad = velocidad
        self.direccion = 1
        self.distancia = distancia
        self.patrol_origin = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)
        self.aggro_radius = aggro_radius
        self.state = "patrolling"  # patrolling / chasing / returning

    def update(self, jugador=None):
        ahora = time.time()
        jugador_pos = pygame.Vector2(jugador.rect.center)
        vector_distancia = jugador_pos - self.pos
        # --- check zone agr ---
        if (vector_distancia.length() <= self.aggro_radius and
            not (SAFE_ZONE_X[0] <= jugador_pos.x <= SAFE_ZONE_X[1] and
                 SAFE_ZONE_Y[0] <= jugador_pos.y <= SAFE_ZONE_Y[1])):
            self.state = "chasing"
        elif self.state == "chasing":
            self.state = "returning"

        # --- action by status ---
        if self.state == "chasing":
            # идём к игроку
            direction = pygame.Vector2(jugador.rect.center) - self.pos
            if direction.length() > 0:
                self.pos += direction.normalize() * self.velocidad

        elif self.state == "returning":
            # back for patrolling 
            to_origin = self.patrol_origin - self.pos
            if to_origin.length() > 1:
                self.pos += to_origin.normalize() * self.velocidad
            else:
                self.state = "patrolling"

        elif self.state == "patrolling":
            # regular patrolling
            if self.horizontal:
                self.pos.x += self.velocidad * self.direccion
                if abs(self.pos.x - self.patrol_origin.x) >= self.distancia:
                    self.direccion *= -1
            else:
                self.pos.y += self.velocidad * self.direccion
                if abs(self.pos.y - self.patrol_origin.y) >= self.distancia:
                    self.direccion *= -1

        # --- Update rect ---
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # --- Animation ---
        if ahora - self.last_frame_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.full_frames)
            self.image = self.full_frames[self.current_frame]
            self.last_frame_time = ahora




