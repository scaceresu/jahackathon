# src/enemy.py
import os
import time
import math
import pygame
from settings import TILE, WIDTH, HEIGHT, TILE_SIZE
from assets import cargar_frames_spritesheet
from tilemap import rect_a_tiles, es_tile_transitable
import heapq

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y,
                 horizontal=True,
                 distancia=128,
                 anim_folder="assets/imagenes/enemy",
                 frame_delay=0.12,
                 aggro_radius=200,
                 velocidad=2):
        """
        Inicializa el enemigo con atributos necesarios para el update antiguo.
        - x,y: posición inicial en píxeles (top-left)
        - horizontal: si la patrulla es horizontal (True) o vertical (False)
        - distancia: distancia de patrulla en píxeles
        - anim_folder: carpeta donde están los spritesheets
        - frame_delay: demora entre frames (segundos)
        - aggro_radius: radio para empezar chase
        - velocidad: píxeles por frame (enteros recomendados)
        """
        super().__init__()

        # --- parámetros spritesheet según tu descripción ---
        H_FRAME_W, H_FRAME_H = 64, 32   # horizontales (5x64x32)
        V_FRAME_W, V_FRAME_H = 32, 65   # verticales  (5x32x65)
        FRAMES_COUNT = 5

        # Tamaño objetivo visible y de colisión (coincide con Player: TILE)
        TARGET_W, TARGET_H = 24, 24

        base = "assets/imagenes/enemy"
        print(os.path.exists(os.path.join(base, "walk_right.png")))
        print(os.path.exists(os.path.join(base, "walk_left.png")))
        print(os.path.exists(os.path.join(base, "walk_up.png")))
        print(os.path.exists(os.path.join(base, "walk_down.png")))
        print(os.path.exists(os.path.join(base, "idle.png")))

        from assets import cargar_frames_spritesheet
        print(len(cargar_frames_spritesheet("assets/imagenes/enemy/walk_right.png", 64, 32, 5)))
        print(len(cargar_frames_spritesheet("assets/imagenes/enemy/walk_up.png", 32, 65, 5)))


        base = anim_folder

        # helpers para cargar y escalar
        def load_and_scale(path, frame_w, frame_h):
            frames = []
            if os.path.isfile(path):
                frames = cargar_frames_spritesheet(path, frame_w, frame_h, FRAMES_COUNT)
            out = []
            for f in frames:
                surf = f.convert_alpha()
                if surf.get_size() != (TARGET_W, TARGET_H):
                    surf = pygame.transform.scale(surf, (TARGET_W, TARGET_H))
                out.append(surf)
            return out

        # cargar animaciones esperadas (nombres de archivo dentro de anim_folder: walk_right.png, walk_left.png, walk_up.png, walk_down.png, idle.png opcional)
        self.frames = {
            "idle": load_and_scale(os.path.join(base, "idle.png"), H_FRAME_W, H_FRAME_H) or load_and_scale(os.path.join(base, "idle.png"), V_FRAME_W, V_FRAME_H) or [],
            "walk_right": load_and_scale(os.path.join(base, "walk_right.png"), H_FRAME_W, H_FRAME_H),
            "walk_left": load_and_scale(os.path.join(base, "walk_left.png"), H_FRAME_W, H_FRAME_H),
            "walk_up": load_and_scale(os.path.join(base, "walk_up.png"), V_FRAME_W, V_FRAME_H),
            "walk_down": load_and_scale(os.path.join(base, "walk_down.png"), V_FRAME_W, V_FRAME_H),
        }

        # fallback visible si faltan animaciones
        fallback = pygame.Surface((TARGET_W, TARGET_H), pygame.SRCALPHA)
        fallback.fill((255, 128, 0, 200))
        for k in list(self.frames.keys()):
            if not self.frames[k]:
                self.frames[k] = [fallback]

        # --- animación y estado ---
        self.state = "patrolling"   # patrolling | chasing | returning | idle
        self.direction = "down"     # left/right/up/down (se actualiza en update)
        self.frame_index = 0
        self.frame_delay = frame_delay
        self.last_frame_time = time.time()
        self.current_frame = 0

        # imagen visible y rect de colisión (TARGET x TARGET)
        self.image = self.frames["idle"][0]
        self.rect = pygame.Rect(round(x), round(y), TARGET_W, TARGET_H)

        # --- posición como Vector2 para la lógica (coherente con tu versión antigua) ---
        self.pos = pygame.Vector2(float(x), float(y))

        

        
        # --- patrulla / IA / pathfinding ---
        self.horizontal = horizontal
        self.distancia = distancia
        self.patrol_origin = pygame.Vector2(self.pos)  # origen de la patrulla (pos inicial)
        # patrol target en píxeles (dependiendo de horizontal/vertical)
        self.patrol_target = (self.patrol_origin + pygame.Vector2(distancia, 0)) if horizontal else (self.patrol_origin + pygame.Vector2(0, distancia))

        self.direccion = 1  # 1 o -1 para invertir patrulla
        self.velocidad = velocidad

        # A* / chasing
        self.aggro_radius = aggro_radius
        self.path = []            # lista de tiles [(tx,ty),...]
        self.waypoint = None      # waypoint en píxeles (Vector2) para seguir path
        self.last_repath_time = 0.0
        self.repath_cooldown = 0.5

        # vida / estado
        self.health = 1
        self.alive = True

        # utilidades para compatibilidad con tu update antiguo
        # self.current_frame ya inicializado arriba
        # self.full_frames antiguamente refería a la lista de frames actuales; mantenemos diccionario frames

    # -----------------------
    # Helpers para tiles / path
    # -----------------------
    def pixel_a_tile(self, px, py):
        """Convierte píxeles (px,py) al tile (tx,ty) usando TILE global."""
        return int(px) // TILE, int(py) // TILE

    def tile_centro_a_pixel(self, tx, ty):
        """Devuelve el centro en píxeles de un tile (tx,ty)."""
        cx = tx * TILE + TILE // 2
        cy = ty * TILE + TILE // 2
        return pygame.Vector2(cx - self.rect.width//2, cy - self.rect.height//2)

    # -----------------------
    # Movimiento que acepta muros_rects
    # -----------------------
    def intentar_mover_con_tiles(self, vx, vy, mapa, muros_rects=None):
        """
        Mueve el enemigo intentado validar tiles y usando muros_rects como fallback.
        - vx, vy: desplazamiento en píxeles (enteros)
        - mapa: matriz mapa[y][x] (1 = transitable)
        - muros_rects: lista opcional de pygame.Rect para comprobación rápida
        Actualiza self.pos (Vector2) y self.rect.topleft.
        """
        if not self.alive:
            return

        # mover separando ejes para evitar corner-cutting
        # eje X
        if vx != 0:
            sign = 1 if vx > 0 else -1
            steps = abs(int(vx))
            for _ in range(steps):
                test_pos = pygame.Vector2(self.pos.x + sign, self.pos.y)
                test_rect = pygame.Rect(round(test_pos.x), round(test_pos.y), self.rect.width, self.rect.height)
                tiles = rect_a_tiles(test_rect)
                if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                    self.pos.x += sign
                else:
                    # fallback: si muros_rects está dado, aceptar si no colisiona con ellos
                    if muros_rects and not any(test_rect.colliderect(m) for m in muros_rects):
                        self.pos.x += sign
                    else:
                        break

        # eje Y
        if vy != 0:
            sign = 1 if vy > 0 else -1
            steps = abs(int(vy))
            for _ in range(steps):
                test_pos = pygame.Vector2(self.pos.x, self.pos.y + sign)
                test_rect = pygame.Rect(round(test_pos.x), round(test_pos.y), self.rect.width, self.rect.height)
                tiles = rect_a_tiles(test_rect)
                if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                    self.pos.y += sign
                else:
                    if muros_rects and not any(test_rect.colliderect(m) for m in muros_rects):
                        self.pos.y += sign
                    else:
                        break

        # sincronizar rect con pos
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    # -----------------------
    # Animación auxiliar (útil si tu update usa time.time())
    # -----------------------
    def advance_frame_time(self):
        """Avanza current_frame basado en time.time() y actualiza self.image según dirección."""
        if time.time() - getattr(self, "last_frame_time", 0) > getattr(self, "frame_delay", 0.12):
            key = "idle"
            if self.direction in ("left", "right"):
                key = f"walk_{self.direction}"
            elif self.direction in ("up", "down"):
                key = f"walk_{self.direction}"
            frames = self.frames.get(key) or self.frames.get("idle")
            self.current_frame = (getattr(self, "current_frame", 0) + 1) % len(frames)
            self.image = frames[self.current_frame]
            self.last_frame_time = time.time()

    # -----------------------
    # (Opcional) método sencillo para setear frames compartidos desde fuera
    # -----------------------
    def set_shared_frames(self, frames_dict):
        """
        Permite inyectar un diccionario frames compartido (para ahorrar memoria).
        frames_dict debe tener mismas keys que self.frames.
        """
        for k in frames_dict:
            if k in self.frames and frames_dict[k]:
                self.frames[k] = frames_dict[k]
        # actualizar imagen actual por si cambia
        key = "idle"
        if self.direction in ("left", "right"):
            key = f"walk_{self.direction}"
        elif self.direction in ("up", "down"):
            key = f"walk_{self.direction}"
        self.image = self.frames.get(key, self.frames["idle"])[0]


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
def update(self, jugador=None, mapa=None, muros_rects=None):
    """
    Compatibilidad con el update antiguo:
    - Patrulla (patrolling)
    - Repath A* y chasing dentro de aggro_radius (repath cooldown)
    - Returning al origen
    - Usa self.intentar_mover_con_tiles(vx, vy, mapa) para movimiento seguro por tiles
    - Actualiza self.rect.topleft desde self.pos
    - Mantiene timing de animación con time.time()
    - muros_rects: lista opcional de rects precomputados para fallback
    """
    ahora = time.time()

    # --- AGGRO / REPATH (igual a tu versión antigua) ---
    if jugador:
        jugador_pos = pygame.Vector2(jugador.rect.center)
        dist = (jugador_pos - self.pos).length()
        if dist <= self.aggro_radius:
            # si el jugador está en rango, intentar perseguir (chase)
            if ahora - getattr(self, "last_repath_time", 0) > getattr(self, "repath_cooldown", 0.5):
                # computar tiles de inicio/goal usando métodos que ya tenías
                start_tile = self.pixel_a_tile(self.rect.centerx, self.rect.centery)
                goal_tile = self.pixel_a_tile(jugador.rect.centerx, jugador.rect.centery)
                if mapa and es_tile_transitable(mapa, *start_tile) and es_tile_transitable(mapa, *goal_tile):
                    # a_star debe devolver lista de tiles [(tx,ty),...]
                    try:
                        self.path = self.a_star(mapa, start_tile, goal_tile) or []
                    except Exception:
                        self.path = []
                    # obtener next waypoint en pixeles (centro del tile)
                    if len(self.path) > 1:
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
                # si hay path, pasar a chasing
                if self.path:
                    self.state = "chasing"

    # ---------------- comportamiento por estado ----------------
    if self.state == "patrolling" or not mapa:
        # patrulla simple en píxeles (como antes), pero usando intentar_mover_con_tiles
        if self.horizontal:
            vx = self.velocidad * self.direccion
            vy = 0
            # usar tu método de movimiento que valida tiles
            self.intentar_mover_con_tiles(vx, vy, mapa or [[0]], muros_rects=muros_rects)
            if abs(self.pos.x - self.patrol_origin.x) >= self.distancia:
                self.direccion *= -1
        else:
            vx = 0
            vy = self.velocidad * self.direccion
            self.intentar_mover_con_tiles(vx, vy, mapa or [[0]], muros_rects=muros_rects)
            if abs(self.pos.y - self.patrol_origin.y) >= self.distancia:
                self.direccion *= -1

    elif self.state == "chasing":
        # seguir la ruta generada por A*
        if getattr(self, "path", None) and getattr(self, "waypoint", None):
            target = pygame.Vector2(self.waypoint)
            vec = target - self.pos
            if vec.length() < 1:
                # avanzar al siguiente waypoint/tile de la ruta
                if len(self.path) > 1:
                    # pop la primera tile (ya alcanzada)
                    self.path.pop(0)
                    next_tile = self.path[1] if len(self.path) > 1 else self.path[0]
                    self.waypoint = self.tile_centro_a_pixel(*next_tile)
                else:
                    # alcanzó objetivo de path
                    self.path = []
                    self.waypoint = None
            else:
                move = vec.normalize() * self.velocidad
                # limitar movimiento a enteros y usar checks por tiles
                self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa, muros_rects=muros_rects)
        else:
            # sin ruta válida: intentar mover directo hacia jugador validando tiles
            if jugador:
                dirvec = (pygame.Vector2(jugador.rect.center) - self.pos)
                if dirvec.length() > 0:
                    move = dirvec.normalize() * self.velocidad
                    self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa, muros_rects=muros_rects)
                else:
                    self.state = "returning"
            else:
                self.state = "returning"

    elif self.state == "returning":
        # volver al origen de patrulla
        to_origin = self.patrol_origin - self.pos
        if to_origin.length() > 1:
            move = to_origin.normalize() * self.velocidad
            self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa, muros_rects=muros_rects)
        else:
            self.state = "patrolling"

    # ---------------- sincronizar self.pos y self.rect ----------------
    # tu implementación antigua mantenía self.pos como Vector2; actualizar rect desde pos
    self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    # ---------------- actualizar dirección/estado para animación ----------------
    # derivar dirección visible (up/down/left/right) priorizando el eje mayor si hay movimiento
    # intentamos fijar self.direction para que la animación muestre correcto
    # si tenemos waypoint o path, compute last movement vector aproximado
    movement_vec = pygame.Vector2(0, 0)
    if getattr(self, "waypoint", None):
        movement_vec = (pygame.Vector2(self.waypoint) - self.pos)
    elif getattr(self, "path", None) and len(self.path) > 0:
        # mirar hacia el siguiente tile si existe
        next_tile = self.path[0] if len(self.path) > 0 else None
        if next_tile:
            tgt = pygame.Vector2(self.tile_centro_a_pixel(*next_tile))
            movement_vec = tgt - self.pos

    # si movement_vec es 0, intentar inferir por last velocity si guardás alguno (opcional)
    if movement_vec.length() > 0:
        dx, dy = movement_vec.x, movement_vec.y
        if abs(dx) >= abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"
    # si no hay movimiento, mantener direction actual

    # ---------------- animación usando time.time() como antes ----------------
    if time.time() - getattr(self, "last_frame_time", 0) > getattr(self, "frame_delay", 0.12):
        # seleccionar la lista de frames adecuada segun direction y si es horiz/vert
        key = "idle"
        if self.direction in ("left", "right"):
            key = f"walk_{self.direction}"
        elif self.direction in ("up", "down"):
            key = f"walk_{self.direction}"
        # full_frames en tu clase antigua era la lista completa; aquí usamos self.frames dict
        frames = self.frames.get(key) or self.frames.get("idle") or [self.image]
        # actualizar current frame (mantengo current_frame nombre antiguo)
        self.current_frame = (getattr(self, "current_frame", 0) + 1) % len(frames)
        self.image = frames[self.current_frame]
        self.last_frame_time = time.time()




    # ---------------- utilidades de animación ----------------
    def set_state_direction(self, state, direction):
        if state != self.state or direction != self.direction:
            self.state = state
            self.direction = direction
            self.frame_index = 0
            self.last_frame_time = pygame.time.get_ticks() / 1000.0
            key = self._anim_key()
            frames = self.frames.get(key) or self.frames.get("idle")
            self.image = frames[self.frame_index]

    def _anim_key(self):
        if self.state == "idle":
            return "idle"
        return f"walk_{self.direction}"

    def advance_frame(self, now):
        key = self._anim_key()
        frames = self.frames.get(key) or self.frames["idle"]
        if not frames:
            return
        if now - self.last_frame_time >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            self.last_frame_time = now

    # ---------------- movimiento seguro por tiles ----------------
    def _can_move_rect(self, rect, mapa, muros_rects=None):
        """Comprueba si el rect propuesto cabe sobre tiles transitables o sin colisión con muros_rects."""
        tiles = rect_a_tiles(rect)
        if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
            return True
        if muros_rects:
            # si ninguna colisión con los rects de muros, es válido (fallback)
            return not any(rect.colliderect(m) for m in muros_rects)
        return False

    def _step_towards(self, target, mapa, muros_rects=None):
        """Mueve el rect 1 px hacia target si es posible (retorna vector de movimiento aplicado)."""
        if not self.alive:
            return pygame.Vector2(0, 0)
        dir_vec = (target - pygame.Vector2(self.rect.x, self.rect.y))
        if dir_vec.length() == 0:
            return pygame.Vector2(0, 0)
        move = dir_vec.normalize() * min(self.speed, dir_vec.length())
        # mover por ejes separados para evitar corner-cutting
        moved = pygame.Vector2(0, 0)
        # X
        if move.x != 0:
            step_x = int(math.copysign(1, move.x))
            for _ in range(abs(int(move.x))):
                test = self.rect.copy()
                test.x += step_x
                if self._can_move_rect(test, mapa, muros_rects):
                    self.rect.x += step_x
                    moved.x += step_x
                else:
                    break
        # Y
        if move.y != 0:
            step_y = int(math.copysign(1, move.y))
            for _ in range(abs(int(move.y))):
                test = self.rect.copy()
                test.y += step_y
                if self._can_move_rect(test, mapa, muros_rects):
                    self.rect.y += step_y
                    moved.y += step_y
                else:
                    break
        return moved