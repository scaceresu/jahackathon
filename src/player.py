import pygame
from settings import GREEN, WIDTH, HEIGHT
from tilemap import rect_a_tiles, es_tile_transitable


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.velocidad = 3
        self.coin = 0
        self.vidas = 3
        self.inventory = {"empanada": 0, "lomito": 0}
        self.spawn_point = (x, y)

    def intentar_mover_x(self, dx, mapa, muros_rects=None, delivery_zones=None, food_zones=None):
        if dx == 0:
            return

        nuevo = self.rect.copy()
        nuevo.x += dx

        # функции-помощники
        def dentro_delivery(rect):
            return any(rect.colliderect(zone.rect) for zone in delivery_zones) if delivery_zones else False

        def dentro_food(rect):
            return any(rect.colliderect(zone.rect) for zone in food_zones) if food_zones else False

        tiles = rect_a_tiles(nuevo)
        if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles) or dentro_delivery(nuevo) or dentro_food(nuevo):
            self.rect.x = nuevo.x
            return

        if muros_rects:
            col = any(nuevo.colliderect(m) for m in muros_rects)
            if not col:
                self.rect.x = nuevo.x
                return

        step = 1 if dx > 0 else -1
        while dx != 0:
            test = self.rect.copy()
            test.x += step
            tiles = rect_a_tiles(test)
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles) or dentro_delivery(test) or dentro_food(test):
                self.rect.x += step
                dx -= step
            else:
                break


    def intentar_mover_y(self, dy, mapa, muros_rects=None, delivery_zones=None, food_zones=None):
        if dy == 0:
            return

        nuevo = self.rect.copy()
        nuevo.y += dy

        def dentro_delivery(rect):
            return any(rect.colliderect(zone.rect) for zone in delivery_zones) if delivery_zones else False

        def dentro_food(rect):
            return any(rect.colliderect(zone.rect) for zone in food_zones) if food_zones else False

        tiles = rect_a_tiles(nuevo)
        if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles) or dentro_delivery(nuevo) or dentro_food(nuevo):
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
            if all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles) or dentro_delivery(test) or dentro_food(test):
                self.rect.y += step
                dy -= step
            else:
                break


    def update(self, teclas, mapa, muros_rects=None, enemigos=None, agujeros=None, delivery_zones=None, food_zones=None):
        dx = dy = 0
        if teclas[pygame.K_LEFT]:
            dx = -self.velocidad
        elif teclas[pygame.K_RIGHT]:
            dx = self.velocidad

        if teclas[pygame.K_UP]:
            dy = -self.velocidad
        elif teclas[pygame.K_DOWN]:
            dy = self.velocidad

        self.intentar_mover_x(dx, mapa, muros_rects, delivery_zones, food_zones)
        self.intentar_mover_y(dy, mapa, muros_rects, delivery_zones, food_zones)

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

        if agujeros:
            if pygame.sprite.spritecollide(self, agujeros, False):
                self.velocidad = 1
            else:
                self.velocidad = 3

    def add_item(self, item_name, amount=1):
        if item_name in self.inventory:
            self.inventory[item_name] += amount
        else:
            self.inventory[item_name] = amount
