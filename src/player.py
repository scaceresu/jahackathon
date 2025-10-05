import pygame
from settings import GREEN, WIDTH, HEIGHT  # ancho/alto de pantalla desde settings
# funciones del módulo tilemap que asumimos en src/tilemap.py
from tilemap import rect_a_tiles, es_tile_transitable

class Player(pygame.sprite.Sprite):
    
    
    def __init__(self, x, y):
        super().__init__()
        # tamaño del sprite en píxeles; elegí 16x16 para encajar con un tile (ajustalo si tu sprite es mayor)
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))


        # Atributos del jugador
        self.velocidad = 3    # px por frame; mantener < TILE para evitar saltos
        self.coin = 0
        self.vidas = 3
        self.inventory = {"empanada": 0, "lomito": 0}
        self.spawn_point = (x, y)  # punto de reaparición inicial

    def intentar_mover_x(self, dx, mapa, muros_rects=None):
        """Intentar mover en X validando tiles transitables.
        - dx puede ser positivo o negativo.
        - mapa: matriz mapa[y][x] (enteros), 1 = transitable.
        - muros_rects: lista opcional de pygame.Rect (precomputada) para checks alternativos.
        """
        if dx == 0:
            return

        nuevo = self.rect.copy()
        nuevo.x += dx

        # Preferimos chequear tiles (exacto) — devuelve lista de (tx,ty) que cubre el rect
        tiles = rect_a_tiles(nuevo)
        if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
            # Todos los tiles que cubriría el nuevo rect son transitables -> aplicar movimiento
            self.rect.x = nuevo.x
            return

        # Si falla la comprobación por tiles, intentamos fallback con rects de muros (si los proveen)
        if muros_rects:
            col = any(nuevo.colliderect(m) for m in muros_rects)
            if not col:
                self.rect.x = nuevo.x
                return

        # Si llegamos aquí hubo colisión: ajustamos hasta el borde del tile libre para evitar "pegado"
        # Ajuste fino: movemos paso a paso en la dirección hasta que colisione (simple y robusto)
        step = 1 if dx > 0 else -1
        while dx != 0:
            test = self.rect.copy()
            test.x += step
            tiles = rect_a_tiles(test)
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                self.rect.x += step
                dx -= step
            else:
                break

    def intentar_mover_y(self, dy, mapa, muros_rects=None):
        """Mismo que intentar_mover_x pero para el eje Y."""
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
        while dy != 0:
            test = self.rect.copy()
            test.y += step
            tiles = rect_a_tiles(test)
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
                self.rect.y += step
                dy -= step
            else:
                break

    def update(self, teclas, mapa, muros_rects=None, enemigos=None,agujeros=None):
        """Actualizar estado del jugador cada frame.
        - teclas: pygame.key.get_pressed()
        - mapa: matriz mapa[y][x] cargada desde CSV (int)
        - muros_rects: lista de pygame.Rect generada por generar_muros(mapa) (opcional, mejora rendimiento)
        - enemigos: grupo de sprites enemigos para detectar colisiones
        """
        dx = dy = 0
        if teclas[pygame.K_LEFT]:
            dx = -self.velocidad
        elif teclas[pygame.K_RIGHT]:
            dx = self.velocidad

        if teclas[pygame.K_UP]:
            dy = -self.velocidad
        elif teclas[pygame.K_DOWN]:
            dy = self.velocidad

        # Mover separando ejes para evitar corner-cutting
        self.intentar_mover_x(dx, mapa, muros_rects)
        self.intentar_mover_y(dy, mapa, muros_rects)

        # Limitar dentro de los bordes de la pantalla (en coordenadas del mundo)
        # Ajustá los límites si tenés una cámara o un offset vertical (por ejemplo top offset 80 antes)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

        # Colisión con enemigos (sprite collision)
        if enemigos:
            colisiones = pygame.sprite.spritecollide(self, enemigos, False)
            if colisiones:
                # Penalización mínima: restar vida y reubicar al checkpoint inicial
                self.vidas -= 1
                self.rect.topleft = (self.spawn_point) # checkpoint inicial (ajustar según necesidad)
                print(f"¡Has sido golpeado! Vidas restantes: {self.vidas}")
                # Podés añadir invulnerabilidad temporal aquí
        if self.vidas <= 0:
            print("Game Over")
            pygame.quit()
            raise SystemExit()
        if agujeros:
            if pygame.sprite.spritecollide(self, agujeros, False):
                self.velocidad = 1   
            else:
                self.velocidad = 3   

    def add_item(self, item_name, amount=1):
        """Añadir item al inventario."""
        if item_name in self.inventory:
            self.inventory[item_name] += amount
        else:
            self.inventory[item_name] = amount
