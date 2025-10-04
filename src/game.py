import pygame
import sys
from player import Player
from enemy import Enemy
from wall import cargar_mapa
from settings import FPS, COLOR_FONDO

def jugar(pantalla, mapa):
    reloj = pygame.time.Clock()

    # Муры карты
    muros = cargar_mapa(mapa)

    # Игрок
    jugador = Player(100, 100)

    # Враги
    enemy1 = Enemy(200, 200)
    enemy2 = Enemy(400, 300)
    enemigos = pygame.sprite.Group(enemy1, enemy2)

    # Все спрайты (для рисования)
    todos = pygame.sprite.Group()
    todos.add(jugador)
    todos.add(enemigos)

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return  # exit()

        # Keys
        teclas = pygame.key.get_pressed()
        jugador.update(teclas, muros)

        # Updates enemies
        enemigos.update()

        # Draw
        pantalla.fill(COLOR_FONDO)
        muros.draw(pantalla)
        todos.draw(pantalla)

        pygame.display.flip()
        reloj.tick(FPS)
