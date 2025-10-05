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
                 aggro_radius=600,
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

        base = anim_folder

        # helpers para cargar y escalar al 50% del tamaño original
        def load_frames_scaled_50(path, frame_w, frame_h):
            frames = []
            if os.path.isfile(path):
                frames = cargar_frames_spritesheet(path, frame_w, frame_h, FRAMES_COUNT)
            # Convertir a formato alpha y escalar al 50%
            out = []
            for f in frames:
                surf = f.convert_alpha()
                # Escalar al 50% del tamaño original
                new_w = int(surf.get_width() * 0.5)
                new_h = int(surf.get_height() * 0.5)
                scaled_surf = pygame.transform.scale(surf, (new_w, new_h))
                out.append(scaled_surf)
            return out

        # cargar animaciones esperadas escaladas al 50%
        self.frames = {
            "idle": load_frames_scaled_50(os.path.join(base, "idle.png"), V_FRAME_W, V_FRAME_H),  # idle usa dimensiones verticales
            "walk_right": load_frames_scaled_50(os.path.join(base, "walk_right.png"), H_FRAME_W, H_FRAME_H),
            "walk_left": load_frames_scaled_50(os.path.join(base, "walk_left.png"), H_FRAME_W, H_FRAME_H),
            "walk_up": load_frames_scaled_50(os.path.join(base, "walk_up.png"), V_FRAME_W, V_FRAME_H),
            "walk_down": load_frames_scaled_50(os.path.join(base, "walk_down.png"), V_FRAME_W, V_FRAME_H),
        }

        # Usar el tamaño de idle como tamaño base del rect de colisión (reducido para mejor jugabilidad)
        # Área de colisión reducida al 37.5% del tamaño original para colisiones más precisas
        self.base_width = int((V_FRAME_W if self.frames["idle"] else 32) * 0.375)
        self.base_height = int((V_FRAME_H if self.frames["idle"] else 65) * 0.375)
        
        # fallback visible si faltan animaciones
        fallback = pygame.Surface((self.base_width, self.base_height), pygame.SRCALPHA)
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

        # imagen visible y rect de colisión usando dimensiones base
        self.image = self.frames["idle"][0] if self.frames["idle"] else fallback
        self.rect = pygame.Rect(round(x), round(y), self.base_width, self.base_height)

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
            return False

        original_pos = pygame.Vector2(self.pos)
        moved_successfully = False

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
                    moved_successfully = True
                else:
                    # fallback: si muros_rects está dado, aceptar si no colisiona con ellos
                    if muros_rects and not any(test_rect.colliderect(m) for m in muros_rects):
                        self.pos.x += sign
                        moved_successfully = True
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
                    moved_successfully = True
                else:
                    if muros_rects and not any(test_rect.colliderect(m) for m in muros_rects):
                        self.pos.y += sign
                        moved_successfully = True
                    else:
                        break

        # sincronizar rect con pos
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        # Detectar si está atascado (no se movió nada)
        if not moved_successfully and (vx != 0 or vy != 0):
            # Activar comportamiento de desatascarse
            if not hasattr(self, 'stuck_counter'):
                self.stuck_counter = 0
            self.stuck_counter += 1
            
            # Si está atascado por varios frames, cambiar dirección
            if self.stuck_counter > 5:
                self.handle_stuck_situation(mapa, muros_rects)
                self.stuck_counter = 0
        else:
            # Se movió exitosamente, resetear contador
            if hasattr(self, 'stuck_counter'):
                self.stuck_counter = 0
                
        return moved_successfully

    def handle_stuck_situation(self, mapa, muros_rects=None):
        """
        Maneja la situación cuando el enemigo está atascado contra una pared.
        Intenta moverse en direcciones alternativas para desatascarse.
        """
        import random
        
        # Direcciones posibles para desatascarse
        directions = [
            (0, -self.velocidad),   # arriba
            (0, self.velocidad),    # abajo
            (-self.velocidad, 0),   # izquierda
            (self.velocidad, 0),    # derecha
            (-self.velocidad, -self.velocidad),  # diagonal arriba-izquierda
            (self.velocidad, -self.velocidad),   # diagonal arriba-derecha
            (-self.velocidad, self.velocidad),   # diagonal abajo-izquierda
            (self.velocidad, self.velocidad),    # diagonal abajo-derecha
        ]
        
        # Probar direcciones en orden aleatorio
        random.shuffle(directions)
        
        for dx, dy in directions:
            test_pos = pygame.Vector2(self.pos.x + dx, self.pos.y + dy)
            test_rect = pygame.Rect(round(test_pos.x), round(test_pos.y), self.rect.width, self.rect.height)
            tiles = rect_a_tiles(test_rect)
            
            # Verificar si esta dirección es válida
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                # Mover en esta dirección para desatascarse
                self.pos.x += dx
                self.pos.y += dy
                self.rect.topleft = (round(self.pos.x), round(self.pos.y))
                
                # Resetear el path para recalcular ruta
                self.path = []
                self.waypoint = None
                break
            elif muros_rects and not any(test_rect.colliderect(m) for m in muros_rects):
                # Si no colisiona con muros_rects, también es válido
                self.pos.x += dx
                self.pos.y += dy
                self.rect.topleft = (round(self.pos.x), round(self.pos.y))
                self.path = []
                self.waypoint = None
                break

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
    # UTIL: DIJKSTRA PATHFINDING SOBRE LA GRID DE TILES (4-vecinos)
    # ---------------------------
    def dijkstra(self, mapa, start, goal):
        """Devuelve lista de (tx,ty) desde start hasta goal usando algoritmo de Dijkstra."""
        h = len(mapa)
        w = len(mapa[0]) if h else 0

        def vecinos(node):
            x, y = node
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0 <= ny < h and 0 <= nx < w and es_tile_transitable(mapa, nx, ny):
                    yield (nx, ny)

        # Dijkstra: usar solo distancia acumulada, sin heurística
        open_heap = []
        heapq.heappush(open_heap, (0, start))
        came_from = {start: None}
        distance = {start: 0}
        visited = set()

        while open_heap:
            current_dist, current = heapq.heappop(open_heap)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == goal:
                # reconstruir path
                path = []
                n = current
                while n:
                    path.append(n)
                    n = came_from[n]
                return list(reversed(path))
                
            for neighbor in vecinos(current):
                if neighbor in visited:
                    continue
                    
                new_distance = current_dist + 1
                
                if neighbor not in distance or new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    came_from[neighbor] = current
                    heapq.heappush(open_heap, (new_distance, neighbor))
        
        return []

    # ---------------------------
    # MOVIMIENTO ALEATORIO
    # ---------------------------
    def get_random_target(self, mapa):
        """Obtiene un tile aleatorio válido para moverse."""
        import random
        h = len(mapa)
        w = len(mapa[0]) if h else 0
        
        # Intentar encontrar un tile válido hasta 20 veces
        for _ in range(20):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            if es_tile_transitable(mapa, x, y):
                return (x, y)
        
        # Si no encuentra, usar posición actual
        current_tile = self.pixel_a_tile(self.rect.centerx, self.rect.centery)
        return current_tile

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
        Actualización del enemigo con:
        - Detección del jugador a 600 píxeles de distancia (triplicado)
        - Seguimiento usando algoritmo de Dijkstra
        - Movimiento aleatorio cuando no detecta al jugador
        - Sistema de desatascamiento cuando choca con paredes
        """
        if not self.alive or not mapa:
            return
            
        ahora = time.time()
        
        # Detección del jugador a 200 píxeles
        player_detected = False
        if jugador:
            jugador_pos = pygame.Vector2(jugador.rect.center)
            enemy_pos = pygame.Vector2(self.rect.center)
            dist = (jugador_pos - enemy_pos).length()
            
            if dist <= 600:  # Distancia de detección de 600 píxeles (triplicada)
                player_detected = True
                
                # Recalcular ruta cada 0.5 segundos
                if ahora - getattr(self, "last_repath_time", 0) > 0.5:
                    start_tile = self.pixel_a_tile(self.rect.centerx, self.rect.centery)
                    goal_tile = self.pixel_a_tile(jugador.rect.centerx, jugador.rect.centery)
                    
                    if es_tile_transitable(mapa, *start_tile) and es_tile_transitable(mapa, *goal_tile):
                        try:
                            # Usar Dijkstra para encontrar el camino
                            self.path = self.dijkstra(mapa, start_tile, goal_tile) or []
                        except Exception:
                            self.path = []
                        
                        # Establecer el primer waypoint
                        if len(self.path) > 1:
                            next_tile = self.path[1]  # El primer elemento es la posición actual
                            self.waypoint = self.tile_centro_a_pixel(*next_tile)
                        else:
                            self.waypoint = None
                            
                        self.state = "chasing"
                    else:
                        self.path = []
                        self.waypoint = None
                        
                    self.last_repath_time = ahora
        
        # Comportamiento basado en detección del jugador
        if player_detected and self.state == "chasing":
            # Seguir la ruta calculada por Dijkstra
            if self.path and self.waypoint:
                target = pygame.Vector2(self.waypoint)
                vec = target - pygame.Vector2(self.rect.center)
                
                if vec.length() < 5:  # Llegó al waypoint actual
                    # Avanzar al siguiente waypoint
                    if len(self.path) > 1:
                        self.path.pop(0)  # Eliminar el waypoint alcanzado
                        if len(self.path) > 0:
                            next_tile = self.path[0]
                            self.waypoint = self.tile_centro_a_pixel(*next_tile)
                        else:
                            self.waypoint = None
                    else:
                        # Llegó al objetivo
                        self.path = []
                        self.waypoint = None
                else:
                    # Moverse hacia el waypoint
                    if vec.length() > 0:
                        move = vec.normalize() * self.velocidad
                        self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa, muros_rects)
            else:
                # Sin ruta válida, moverse directamente hacia el jugador
                if jugador:
                    dirvec = (pygame.Vector2(jugador.rect.center) - pygame.Vector2(self.rect.center))
                    if dirvec.length() > 0:
                        move = dirvec.normalize() * self.velocidad
                        self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa, muros_rects)
        
        else:
            # Movimiento aleatorio cuando no detecta al jugador
            if not hasattr(self, 'random_target') or not hasattr(self, 'last_random_time'):
                self.random_target = None
                self.last_random_time = 0
            
            # Cambiar objetivo aleatorio cada 3 segundos
            if ahora - self.last_random_time > 3.0 or not self.random_target:
                self.random_target = self.get_random_target(mapa)
                self.last_random_time = ahora
                
                # Calcular ruta hacia el objetivo aleatorio
                if self.random_target:
                    start_tile = self.pixel_a_tile(self.rect.centerx, self.rect.centery)
                    try:
                        self.path = self.dijkstra(mapa, start_tile, self.random_target) or []
                        if len(self.path) > 1:
                            next_tile = self.path[1]
                            self.waypoint = self.tile_centro_a_pixel(*next_tile)
                        else:
                            self.waypoint = None
                    except Exception:
                        self.path = []
                        self.waypoint = None
            
            # Seguir la ruta hacia el objetivo aleatorio
            if self.path and self.waypoint:
                target = pygame.Vector2(self.waypoint)
                vec = target - pygame.Vector2(self.rect.center)
                
                if vec.length() < 5:  # Llegó al waypoint
                    if len(self.path) > 1:
                        self.path.pop(0)
                        if len(self.path) > 0:
                            next_tile = self.path[0]
                            self.waypoint = self.tile_centro_a_pixel(*next_tile)
                        else:
                            self.waypoint = None
                    else:
                        # Llegó al objetivo aleatorio
                        self.path = []
                        self.waypoint = None
                        self.random_target = None  # Forzar nuevo objetivo
                else:
                    # Moverse hacia el waypoint
                    if vec.length() > 0:
                        move = vec.normalize() * self.velocidad
                        self.intentar_mover_con_tiles(round(move.x), round(move.y), mapa, muros_rects)

        # ---------------- sincronizar self.pos y self.rect ----------------
        # tu implementación antigua mantenía self.pos como Vector2; actualizar rect desde pos
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # ---------------- actualizar dirección/estado para animación ----------------
        # Determinar dirección basada en el waypoint actual o el objetivo
        movement_vec = pygame.Vector2(0, 0)
        
        if hasattr(self, 'waypoint') and self.waypoint:
            movement_vec = (pygame.Vector2(self.waypoint) - pygame.Vector2(self.rect.center))
        elif hasattr(self, 'path') and self.path and len(self.path) > 0:
            # mirar hacia el siguiente tile si existe
            next_tile = self.path[0]
            if next_tile:
                tgt = self.tile_centro_a_pixel(*next_tile)
                movement_vec = tgt - pygame.Vector2(self.rect.center)

        # Actualizar dirección basada en el movimiento
        if movement_vec.length() > 1:
            dx, dy = movement_vec.x, movement_vec.y
            if abs(dx) >= abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"
        # Si no hay movimiento, mantener dirección actual

        # ---------------- animación usando time.time() como antes ----------------
        if time.time() - getattr(self, "last_frame_time", 0) > getattr(self, "frame_delay", 0.12):
            # seleccionar la lista de frames adecuada segun direction y si es horiz/vert
            key = "idle"
            if self.direction in ("left", "right"):
                key = f"walk_{self.direction}"
            elif self.direction in ("up", "down"):
                key = f"walk_{self.direction}"
            # full_frames en tu clase antigua era la lista completa; aquí usamos self.frames dict
            frames = self.frames.get(key) or self.frames.get("idle")
            
            # Verificar que frames no sea None o vacío
            if frames and len(frames) > 0:
                # actualizar current frame (mantengo current_frame nombre antiguo)
                self.current_frame = (getattr(self, "current_frame", 0) + 1) % len(frames)
                self.image = frames[self.current_frame]
                self.last_frame_time = time.time()