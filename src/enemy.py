import os
import time
import heapq
import pygame
from settings import TILE_SIZE
# funciones del módulo tilemap que usamos:
# cargar_mapa_csv, rect_a_tiles, es_tile_transitable
from tilemap import rect_a_tiles, es_tile_transitable

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, horizontal=True, distancia=128, velocidad=1,
                 anim_folder=None, frame_delay=0.2, aggro_radius=150):
        super().__init__()
        # --- Sprites / fallback visual ---
        self.full_frames = []
        # Carga simple de frames si existe carpeta; se deja como en tu versión vieja
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

        # --- Rect y posición en float para movimiento suave ---
        w, h = (TILE_SIZE * 3, TILE_SIZE * 2) if horizontal else (TILE_SIZE * 2, TILE_SIZE * 3)
        self.rect = pygame.Rect(x, y, w, h)
        self.pos = pygame.Vector2(x, y)  # posición en floats para movimiento
        self.horizontal = horizontal

        # --- comportamiento / patrulla ---
        self.velocidad = velocidad
        self.direccion = 1
        self.distancia = distancia
        self.patrol_origin = pygame.Vector2(x, y)
        self.aggro_radius = aggro_radius
        self.state = "patrolling"  # patrolling / chasing / returning

        # --- pathfinding ---
        self.path = []         # lista de tiles (tx,ty) por recorrer
        self.waypoint = None   # coordenada pixel objetivo actual (Vector2)
        self.repath_cooldown = 0.5
        self.last_repath_time = 0

    # ---------------------------
    # MOVIMIENTO Y COLISIÓN (usa la misma regla que Player)
    # ---------------------------
    def intentar_mover_con_tiles(self, dx, dy, mapa):
        """Movimiento seguro: intenta mover en X y Y por separado validando tiles."""
        # X
        if dx != 0:
            nuevo = self.rect.copy()
            nuevo.x += dx
            tiles = rect_a_tiles(nuevo)
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                self.rect.x = nuevo.x
                self.pos.x = self.rect.x
            else:
                # ajuste fino pixel a pixel
                step = 1 if dx > 0 else -1
                moved = 0
                for _ in range(abs(dx)):
                    test = self.rect.copy()
                    test.x += step
                    tiles = rect_a_tiles(test)
                    if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                        self.rect.x += step
                        moved += step
                    else:
                        break
                self.pos.x = self.rect.x

        # Y
        if dy != 0:
            nuevo = self.rect.copy()
            nuevo.y += dy
            tiles = rect_a_tiles(nuevo)
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                self.rect.y = nuevo.y
                self.pos.y = self.rect.y
            else:
                step = 1 if dy > 0 else -1
                moved = 0
                for _ in range(abs(dy)):
                    test = self.rect.copy()
                    test.y += step
                    tiles = rect_a_tiles(test)
                    if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                        self.rect.y += step
                        moved += step
                    else:
                        break
                self.pos.y = self.rect.y

    # ---------------------------
    # UTIL: A* PATHFINDING SOBRE LA GRID DE TILES (4-vecinos)
    # ---------------------------
    def a_star(self, mapa, start, goal):
        """Devuelve lista de (tx,ty) desde start hasta goal o [] si no hay camino."""
        h = len(mapa)
        w = len(mapa[0]) if h else 0

        def vecinos(node):
            x, y = node
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0 <= ny < h and 0 <= nx < w and es_tile_transitable(mapa, nx, ny):
                    yield (nx, ny)

        def heur(a, b):
            return abs(a[0]-b[0]) + abs(a[1]-b[1])

        open_heap = []
        heapq.heappush(open_heap, (0 + heur(start, goal), 0, start))
        came_from = {start: None}
        gscore = {start: 0}

        while open_heap:
            _, g, current = heapq.heappop(open_heap)
            if current == goal:
                # reconstruir path
                path = []
                n = current
                while n:
                    path.append(n)
                    n = came_from[n]
                return list(reversed(path))
            for nb in vecinos(current):
                tentative_g = g + 1
                if nb not in gscore or tentative_g < gscore[nb]:
                    gscore[nb] = tentative_g
                    f = tentative_g + heur(nb, goal)
                    heapq.heappush(open_heap, (f, tentative_g, nb))
                    came_from[nb] = current
        return []

    # ---------------------------
    # HELPERS: conversión tile <-> pixel
    # ---------------------------
    def tile_centro_a_pixel(self, tx, ty):
        """Devuelve Vector2 del centro del tile (en píxeles)."""
        cx = tx * TILE_SIZE + TILE_SIZE // 2 - self.rect.width // 2
        cy = ty * TILE_SIZE + TILE_SIZE // 2 - self.rect.height // 2
        return pygame.Vector2(cx, cy)

    def pixel_a_tile(self, px, py):
        return int(px) // TILE_SIZE, int(py) // TILE_SIZE

    # ---------------------------
    # UPDATE PRINCIPAL
    # ---------------------------
    def update(self, jugador=None, mapa=None):
        """Mapa debe ser la matriz mapa[y][x] cargada desde CSV (1 = camino)."""
        ahora = time.time()

        # --- estado de aggro básico ---
        if jugador:
            jugador_pos = pygame.Vector2(jugador.rect.center)
            dist = (jugador_pos - self.pos).length()
            if dist <= self.aggro_radius:
                # si el jugador está en rango, intentar perseguir (chase)
                # recalcular ruta periódicamente (cooldown)
                if ahora - self.last_repath_time > self.repath_cooldown:
                    start_tile = self.pixel_a_tile(self.rect.centerx, self.rect.centery)
                    goal_tile = self.pixel_a_tile(jugador.rect.centerx, jugador.rect.centery)
                    # si goal o start no son transitables devolvemos path vacío
                    if mapa and es_tile_transitable(mapa, *start_tile) and es_tile_transitable(mapa, *goal_tile):
                        self.path = self.a_star(mapa, start_tile, goal_tile)
                        # convertir primer waypoint a pixel
                        if len(self.path) > 1:
                            # la primera tile de path probablemente sea la tile actual; nos movemos a la siguiente
                            next_tile = self.path[1]
                        elif len(self.path) == 1:
                            next_tile = self.path[0]
                        else:
                            next_tile = None
                        self.waypoint = self.tile_centro_a_pixel(*next_tile) if next_tile else None
                    else:
                        self.path = []
                        self.waypoint = None
                    self.last_repath_time = ahora
                    self.state = "chasing" if self.path else self.state

        # --- comportamiento según estado ---
        if self.state == "patrolling" or not mapa:
            # patrulla simple en píxeles (igual a versión vieja), pero sin atravesar tiles
            if self.horizontal:
                vx = self.velocidad * self.direccion
                vy = 0
                self.intentar_mover_con_tiles(vx, vy, mapa or [[0]])
                if abs(self.pos.x - self.patrol_origin.x) >= self.distancia:
                    self.direccion *= -1
            else:
                vx = 0
                vy = self.velocidad * self.direccion
                self.intentar_mover_con_tiles(vx, vy, mapa or [[0]])
                if abs(self.pos.y - self.patrol_origin.y) >= self.distancia:
                    self.direccion *= -1

        elif self.state == "chasing":
            # seguir la ruta generada por A*; si no hay path, tratar de moverse en dirección directa validando tiles
            if self.path and self.waypoint:
                target = self.waypoint
                vec = target - self.pos
                if vec.length() < 1:
                    # avanzar al siguiente tile en la ruta
                    if len(self.path) > 1:
                        self.path.pop(0)
                        next_tile = self.path[1] if len(self.path) > 1 else self.path[0]
                        self.waypoint = self.tile_centro_a_pixel(*next_tile)
                    else:
                        # alcanzó objetivo de path
                        self.path = []
                        self.waypoint = None
                else:
                    move = vec.normalize() * self.velocidad
                    # limitar movimiento a entero de píxeles y usar checks por tiles
                    self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa)
            else:
                # sin ruta válida: movimiento directo pero validando tiles
                if jugador:
                    dirvec = (pygame.Vector2(jugador.rect.center) - self.pos)
                    if dirvec.length() > 0:
                        move = dirvec.normalize() * self.velocidad
                        self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa)
                else:
                    self.state = "returning"

        elif self.state == "returning":
            # volver al origen de patrulla
            to_origin = self.patrol_origin - self.pos
            if to_origin.length() > 1:
                move = to_origin.normalize() * self.velocidad
                self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa)
            else:
                self.state = "patrolling"

        # --- actualizar rect a partir de self.pos ---
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # --- animación (igual que antes) ---
        if time.time() - self.last_frame_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.full_frames)
            self.image = self.full_frames[self.current_frame]
            self.last_frame_time = time.time()
