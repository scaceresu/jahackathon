# src/game.py
import os
import pygame
import sys
import random # para posiciones aleatorias de enemigos
from player import Player
from enemy import Enemy
from playermenu import PlayerMenu
from savezone import SaveZone
from coin import Coin
from food import FoodZone
from deliveryzone import DeliveryZone
# Nuevo: funciones del módulo tilemap (cargar CSV y generar muros)
from tilemap import cargar_mapa_csv, generar_muros, rect_a_tiles, es_tile_transitable, TILE
from settings import FPS, COLOR_FONDO


def spawn_on_path(mapa, sprite_width, sprite_height, max_attempts=2000):
    """
    Devuelve (x,y) en píxeles donde un sprite de tamaño sprite_width x sprite_height
    cabe y todos los tiles que ocuparía son transitables (mapa tile == 1).
    Intenta hasta max_attempts veces y lanza ValueError si no encuentra posición.
    """
    h = len(mapa)
    w = len(mapa[0]) if h else 0
    if w == 0 or h == 0:
        raise ValueError("Mapa vacío o inválido")

    # límites en píxeles para topleft de la entidad
    max_x = w * TILE - sprite_width
    max_y = h * TILE - sprite_height

    for _ in range(max_attempts):
        x = random.randint(0, max(0, max_x))
        y = random.randint(0, max(0, max_y))
        rect = pygame.Rect(x, y, sprite_width, sprite_height)
        # comprobar todos los tiles que cubriría el rect
        tiles = rect_a_tiles(rect)
        if tiles and all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
            return x, y
    raise ValueError("No se encontró posición en camino tras many attempts")


def jugar(pantalla, archivo_csv):
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 36)

    # --- Cargar imagen de fondo (una vez) ---
    base_dir = os.path.dirname(__file__)
    fondo_path = os.path.join(base_dir, "maps", "fondo.png")
    if os.path.exists(fondo_path):
        fondo_img = pygame.image.load(fondo_path).convert()
        screen_w, screen_h = pantalla.get_size()
        fondo = pygame.transform.scale(fondo_img, (screen_w, screen_h))
    else:
        fondo = None  # fallback para usar COLOR_FONDO

    # --- CARGAR MAPA CSV Y GENERAR MUROS (rects agrupados) ---
    # archivo_csv puede ser "mapa1.csv" si está en src/maps, o ruta absoluta
    mapa, map_w, map_h = cargar_mapa_csv(archivo_csv)
    muros = generar_muros(mapa)  # lista de pygame.Rect que representan bloques no transitables

    # --- ENTIDADES ---
    # jugador = Player(70, 70)
    # generar posiciones válidas
    px, py = spawn_on_path(mapa, 16, 16)
    jugador = Player(px, py)
    
    enemy_w, enemy_h = 3 * TILE, 2 * TILE  # según tu Enemy horizontal size; ajusta si difiere
    
    
    ex, ey = spawn_on_path(mapa, enemy_w, enemy_h)
    enemy = Enemy(ex, ey, horizontal=True, distancia=128,
                  anim_folder="assets/imagenes/cargreen", frame_delay=0.15, aggro_radius=350)

    print("enemy frames:", {k: len(v) for k,v in enemy.frames.items()})

    enemigos = pygame.sprite.Group(enemy)

    menu_hud = PlayerMenu(jugador)

    # Zonas y grupos
    save_zone = SaveZone(500, 400, 100, 100)
    delivery_zone = DeliveryZone(10, 10, 100, 100)
    coin = Coin(700, 400, 20, 20)
    zone_coin = pygame.sprite.Group(coin)
    zones_group = pygame.sprite.Group(save_zone)

    todos = pygame.sprite.Group(jugador, *enemigos)
    lomito = FoodZone(100, 200, 75, 75, "lomito", color=(255,200,0))
    empanada = FoodZone(300, 150, 75, 75, "empanada", color=(200,150,50))
    lomito_group = pygame.sprite.Group(lomito)
    empanada_group = pygame.sprite.Group(empanada)
    delivery_zone_group = pygame.sprite.Group(delivery_zone)

    boton_salir = pygame.Rect(650, 20, 120, 40)

    corriendo = True
    while corriendo:
        # --- Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_salir.collidepoint(evento.pos):
                    return

        teclas = pygame.key.get_pressed()

        # --- Actualizaciones: pasamos mapa y muros a las entidades ---
        # Player.update(teclas, mapa, muros_rects=muros, enemigos=enemigos)
        jugador.update(teclas, mapa, muros_rects=muros, enemigos=enemigos)
        for enemigo in enemigos:
            # Enemy.update(jugador=..., mapa=...)
            enemigo.update(jugador=jugador, mapa=mapa)

        # --- Dibujado del fondo ---
        if fondo:
            pantalla.blit(fondo, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO)

        # --- Opcional: dibujar muros en modo debug (descomentar para verificar) ---
        # for r in muros:
        #     pygame.draw.rect(pantalla, (120, 30, 30), r, 1)

        # --- Resto del dibujado y actualizaciones de grupos ---
        zones_group.draw(pantalla)
        zone_coin.draw(pantalla)
        zone_coin.update(jugador)

        delivery_zone_group.draw(pantalla)
        delivery_zone_group.update(jugador)

        empanada_group.draw(pantalla)
        empanada_group.update(jugador)
        lomito_group.draw(pantalla)
        lomito_group.update(jugador)

        todos.draw(pantalla)

        # Botón salir y HUD
        pygame.draw.rect(pantalla, (255, 80, 80), boton_salir)
        texto = fuente.render("Salir", True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=boton_salir.center))
        menu_hud.dibujar(pantalla)

        # --- Flip y control de FPS ---
        pygame.display.flip()
        reloj.tick(FPS)

        # Condición de éxito
        if jugador.coin == 1:
            return True
