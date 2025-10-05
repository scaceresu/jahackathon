# src/player.py
# Player con sprite sheet 4x1 (cada frame 44x44) escalado a 16x16 para que rect de colisión coincida con la imagen.

import os
import pygame
from settings import TILE, WIDTH, HEIGHT
from assets import cargar_frames_spritesheet
from tilemap import rect_a_tiles, es_tile_transitable

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Parámetros del spritesheet original
        FRAME_W, FRAME_H = 44, 44
        FRAMES_COUNT = 4

        # Tamaño visual de la imagen (mantener proporción original)
        TARGET_W, TARGET_H = 24, 24
        
        # Tamaño del área de colisión (más pequeña para mejor jugabilidad)
        COLLISION_W, COLLISION_H = 12, 24

        base = os.path.join("assets", "imagenes", "player")

        # helper para cargar y escalar cada spritesheet
        def load_anim(name):
            path = os.path.join(base, f"{name}.png")
            frames = cargar_frames_spritesheet(path, FRAME_W, FRAME_H, FRAMES_COUNT)
            # convertir + escalar cada frame a TARGET_W x TARGET_H
            out = []
            for f in frames:
                surf = f.convert_alpha()
                if surf.get_size() != (TARGET_W, TARGET_H):
                    surf = pygame.transform.scale(surf, (TARGET_W, TARGET_H))
                out.append(surf)
            return out

        # nombres esperados: idle.png, walk_down.png, walk_up.png, walk_left.png, walk_right.png
        self.frames = {
            "idle": load_anim("idle") or [],
            "walk_down": load_anim("walk_down") or [],
            "walk_up": load_anim("walk_up") or [],
            "walk_left": load_anim("walk_left") or [],
            "walk_right": load_anim("walk_right") or [],
        }

        # fallback visible (magenta) si alguna animación falta
        fallback = pygame.Surface((TARGET_W, TARGET_H), pygame.SRCALPHA)
        fallback.fill((255, 0, 255, 180))
        for k in list(self.frames.keys()):
            if not self.frames[k]:
                self.frames[k] = [fallback]

        # Estado y animación
        self.state = "idle"
        self.direction = "down"
        self.frame_index = 0
        self.frame_delay = 0.12
        self.last_frame_time = pygame.time.get_ticks() / 1000.0

        # imagen visible (mantiene tamaño original 24x24)
        self.image = self.frames["idle"][0]
        # rect de colisión (área más pequeña 12x24 para mejor jugabilidad)
        self.rect = pygame.Rect(x, y, COLLISION_W, COLLISION_H)

        # atributos de juego
        self.velocidad = 3
        self.coin = 0
        self.vidas = 3
        self.inventory = {"empanada": 0, "lomito": 0}
        self.spawn_point = (x, y)

    # ---------------- movimiento y colisiones ----------------
    def intentar_mover_x(self, dx, mapa, muros_rects=None):
        if dx == 0:
            return
        nuevo = self.rect.copy()
        nuevo.x += dx
        tiles = rect_a_tiles(nuevo)
        if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
            self.rect.x = nuevo.x
            return
        if muros_rects:
            col = any(nuevo.colliderect(m) for m in muros_rects)
            if not col:
                self.rect.x = nuevo.x
                return
        step = 1 if dx > 0 else -1
        moved = 0
        while abs(moved) < abs(dx):
            test = self.rect.copy()
            test.x += step
            tiles = rect_a_tiles(test)
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                self.rect.x += step
                moved += step
            else:
                break

    def intentar_mover_y(self, dy, mapa, muros_rects=None):
        if dy == 0:
            return
        nuevo = self.rect.copy()
        nuevo.y += dy
        tiles = rect_a_tiles(nuevo)
        if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
            self.rect.y = nuevo.y
            return
        if muros_rects:
            col = any(nuevo.colliderect(m) for m in muros_rects)
            if not col:
                self.rect.y = nuevo.y
                return
        step = 1 if dy > 0 else -1
        moved = 0
        while abs(moved) < abs(dy):
            test = self.rect.copy()
            test.y += step
            tiles = rect_a_tiles(test)
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                self.rect.y += step
                moved += step
            else:
                break

    # ---------------- animación y estado ----------------
    def set_state_direction(self, moving, dx, dy):
        new_state = "idle" if not moving else "walk"
        new_dir = self.direction
        if moving:
            if dx < 0: new_dir = "left"
            elif dx > 0: new_dir = "right"
            elif dy < 0: new_dir = "up"
            elif dy > 0: new_dir = "down"
        if new_state != self.state or new_dir != self.direction:
            self.state = new_state
            self.direction = new_dir
            self.frame_index = 0
            self.last_frame_time = pygame.time.get_ticks() / 1000.0
            key = self.state if self.state == "idle" else f"walk_{self.direction}"
            frames = self.frames.get(key) or self.frames["idle"]
            self.image = frames[self.frame_index]

    def advance_frame(self, now):
        key = self.state if self.state == "idle" else f"walk_{self.direction}"
        frames = self.frames.get(key) or self.frames["idle"]
        if not frames:
            return
        if now - self.last_frame_time >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            self.last_frame_time = now

    # ---------------- update público ----------------
    def update(self, teclas, mapa, muros_rects=None, enemigos=None):
        dx = dy = 0
        if teclas[pygame.K_LEFT]: dx = -self.velocidad
        elif teclas[pygame.K_RIGHT]: dx = self.velocidad
        if teclas[pygame.K_UP]: dy = -self.velocidad
        elif teclas[pygame.K_DOWN]: dy = self.velocidad

        moving = (dx != 0 or dy != 0)
        self.set_state_direction(moving, dx, dy)
        self.intentar_mover_x(dx, mapa, muros_rects)
        self.intentar_mover_y(dy, mapa, muros_rects)

        now = pygame.time.get_ticks() / 1000.0
        self.advance_frame(now)

        # mantener dentro de pantalla (ajustá si usás cámara)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

        if enemigos:
            colisiones = pygame.sprite.spritecollide(self, enemigos, False)
            if colisiones:
                self.vidas -= 1
                self.rect.topleft = self.spawn_point
                print(f"¡Has sido golpeado! Vidas restantes: {self.vidas}")
        if self.vidas <= 0:
            print("Game Over")
            pygame.quit()
            raise SystemExit()

    # utilidad para recoger items
    def add_item(self, item_name, amount=1):
        if item_name in self.inventory:
            self.inventory[item_name] += amount
        else:
            self.inventory[item_name] = amount
