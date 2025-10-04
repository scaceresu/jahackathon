import pygame
import sys
from player import Player
from enemy import Enemy
from playermenu import PlayerMenu
from tile import cargar_mapa_tmj
from settings import FPS, COLOR_FONDO

def jugar(pantalla, archivo_tmj):
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 36)


    jugador = Player(100, 100)
    enemy = Enemy(x=600,y=600,horizontal=True, distancia=128, anim_folder="assets/imagenes/cargreen", frame_delay=0.15,aggro_radius=350)
    enemy1 = Enemy(x=400,y=400 ,horizontal=True, distancia=64, anim_folder="assets/imagenes/cargreen", frame_delay=0.15,aggro_radius=350)
    enemy2 = Enemy(x=600,y=600 ,horizontal=False, distancia=64, anim_folder="assets/imagenes/cargreen", frame_delay=0.15,aggro_radius=350)
    enemigos = pygame.sprite.Group(
        enemy,
        enemy1,
        enemy2
    )
    menu_hud = PlayerMenu(jugador)
    tiles_group, tile_w, tile_h = cargar_mapa_tmj(archivo_tmj)
    for tile in tiles_group:
        tile.rect.y += 80

    muros = pygame.sprite.Group()
    todos = pygame.sprite.Group(jugador,*enemigos)

    # --- КНОПКА "SALIR" ---
    boton_salir = pygame.Rect(650, 20, 120, 40)

    # --- ЦИКЛ ИГРЫ ---
    corriendo = True
    while corriendo:
        # --- СОБЫТИЯ ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return  # выход в меню
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_salir.collidepoint(evento.pos):
                    return  # выход в меню

        # --- ЛОГИКА ---
        teclas = pygame.key.get_pressed()
        jugador.update(teclas, muros,enemigos)
        for enemigo in enemigos:
            enemigo.update(jugador)
        # --- ОТРИСОВКА ---
        pantalla.fill(COLOR_FONDO)

        # Отрисовка карты (тайлов)
        tiles_group.draw(pantalla)

        # Отрисовка игрока
        todos.draw(pantalla)

        # --- КНОПКА ВЫХОДА ---
        pygame.draw.rect(pantalla, (255, 80, 80), boton_salir)
        texto = fuente.render("Salir", True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=boton_salir.center))

        # --- HUD ---
        menu_hud.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(FPS)
