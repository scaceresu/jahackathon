# src/game.py
import os
import pygame
import sys
from spawnfunc import spawn_on_path
import random # para posiciones aleatorias de enemigos
from player import Player
from enemy import Enemy
from agujero import Agujero
from playermenu import PlayerMenu
from savezone import SaveZone
from coin import Coin
from food import FoodZone
from deliveryzone import DeliveryZone
# Nuevo: funciones del módulo tilemap (cargar CSV y generar muros)
from tilemap import cargar_mapa_csv, generar_muros, rect_a_tiles, es_tile_transitable, TILE
from settings import FPS, COLOR_FONDO


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
                   aggro_radius=150)
    
    ex, ey = spawn_on_path(mapa, enemy_w, enemy_h)
    enemy1 = Enemy(ex, ey, horizontal=True, distancia=64,
                    aggro_radius=150)
    
    ex, ey = spawn_on_path(mapa, enemy_w, enemy_h)
    enemy2 = Enemy(ex, ey, horizontal=False, distancia=64,
                    aggro_radius=150)
    
    enemigos = pygame.sprite.Group(enemy, enemy1, enemy2)

    menu_hud = PlayerMenu(jugador)

    # Zonas y grupos
    save_zone = SaveZone(500, 400, 100, 100)
    delivery_zone = DeliveryZone(10, 10, 100, 100)
    coin = Coin(700, 400, 20, 20)
    agujeros = pygame.sprite.Group()
    agujeros.add(Agujero(100, 150))
    agujeros.add(Agujero(700, 350))
    
    zone_coin = pygame.sprite.Group(coin)
    zones_group = pygame.sprite.Group(save_zone)

    todos = pygame.sprite.Group(jugador, *enemigos)
    lomito = FoodZone(100, 200, 75, 75, "lomito", color=(255,200,0))
    empanada = FoodZone(300, 150, 75, 75, "empanada", color=(200,150,50))
    lomito_group = pygame.sprite.Group(lomito)
    empanada_group = pygame.sprite.Group(empanada)
    delivery_zone_group = pygame.sprite.Group(delivery_zone)



    corriendo = True
    while corriendo:
        # --- Eventos ---
        eventos = pygame.event.get()

        # Проверка выхода (кнопка ESC, X или кнопка “Salir” в HUD)
        if menu_hud.manejar_eventos(eventos):
            break  # salir del nivel

        teclas = pygame.key.get_pressed()

        # --- Actualizaciones ---
        jugador.update(teclas, mapa, muros_rects=muros, enemigos=enemigos, agujeros=agujeros)

        for enemigo in enemigos:
            enemigo.update(jugador=jugador, mapa=mapa)

        # --- Dibujado del fondo ---
        if fondo:
            pantalla.blit(fondo, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO)

        # --- Grupos y zonas ---
        menu_hud.dibujar(pantalla)

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
        
        agujeros.draw(pantalla)
        agujeros.update(jugador)

        # --- Flip y control de FPS ---
        pygame.display.flip()
        reloj.tick(FPS)

        # --- Condición de éxito ---
        if jugador.coin >= 1:
            return True

