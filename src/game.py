import pygame
import sys
from player import Player
from enemy import Enemy
from wall import cargar_mapa
from settings import FPS, COLOR_FONDO

def jugar(pantalla, mapa):
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 36)  

    # maps
    muros = cargar_mapa(mapa)

    # player
    jugador = Player(100, 100)

    # enemies
    enemy1 = Enemy(200, 200)
    enemy2 = Enemy(400, 300)
    enemigos = pygame.sprite.Group(enemy1, enemy2)

    # spites
    todos = pygame.sprite.Group()
    todos.add(jugador)
    todos.add(enemigos)

    # button salir
    boton_salir = pygame.Rect(650, 20, 120, 40) 
    
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return  # salir en menu
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_salir.collidepoint(evento.pos):
                    return  # salir en menu

        # update player
        teclas = pygame.key.get_pressed()
        jugador.update(teclas, muros)

        # update enemies
        enemigos.update()

        # --- draw ---
        pantalla.fill(COLOR_FONDO)
        muros.draw(pantalla)
        todos.draw(pantalla)

        # exit
        pygame.draw.rect(pantalla, (255, 80, 80), boton_salir)
        texto = fuente.render("Salir", True, (255, 255, 255))
        texto_rect = texto.get_rect(center=boton_salir.center)
        pantalla.blit(texto, texto_rect)

        pygame.display.flip()
        reloj.tick(FPS)
