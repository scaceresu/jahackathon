import pygame
import sys
from player import Player
from enemy import Enemy
from playermenu import PlayerMenu
from savezone import SaveZone
from coin import Coin
from food import FoodZone
from deliveryzone import DeliveryZone
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
        
    save_zone = SaveZone(500, 400, 100, 100)
    delivery_zone = DeliveryZone(10,10,100,100)
    coin = Coin(700, 400, 20, 20)
    zone_coin=pygame.sprite.Group(coin)
    zones_group = pygame.sprite.Group(save_zone)
    
    muros = pygame.sprite.Group()
    todos = pygame.sprite.Group(jugador,*enemigos)
    lomito = FoodZone(100, 200, 75, 75, "lomito", color=(255,200,0))
    empanada = FoodZone(300, 150, 75, 75, "empanada", color=(200,150,50))
    lomito_group=pygame.sprite.Group(lomito)
    empanada_group=pygame.sprite.Group(empanada)
    delivery_zone_group=pygame.sprite.Group(delivery_zone)
    # --- button "SALIR" ---
    boton_salir = pygame.Rect(650, 20, 120, 40)

    # --- cycle пфьу ---
    corriendo = True
    while corriendo:
        # --- Actions ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return  # exit to menu
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_salir.collidepoint(evento.pos):
                    return  #exit to menu

        # --- LOgic ---
        teclas = pygame.key.get_pressed()
        jugador.update(teclas, muros,enemigos)
        for enemigo in enemigos:
            enemigo.update(jugador)
        # --- Paint ---
        pantalla.fill(COLOR_FONDO)
        #  Paint (map)
        tiles_group.draw(pantalla)
        zones_group.draw(pantalla)
        zone_coin.draw(pantalla)
        zone_coin.update(jugador)
        
        delivery_zone_group.draw(pantalla)
        delivery_zone_group.update(jugador)
        
        empanada_group.draw(pantalla)
        empanada_group.update(jugador)
        lomito_group.draw(pantalla)
        lomito_group.update(jugador)
        # Paint player
        todos.draw(pantalla)

        # --- Button salir ---
        pygame.draw.rect(pantalla, (255, 80, 80), boton_salir)
        texto = fuente.render("Salir", True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=boton_salir.center))

        # --- HUD ---
        menu_hud.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(FPS)
        
        if jugador.coin==1:
            return True
