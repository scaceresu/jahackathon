import pygame
import pytmx
mapa1 = r"src/maps/mapa1.json"
mapa2 = "maps/mapa2.tmj"
from menu import menu
from game import jugar
from settings import ANCHO_PANTALLA, ALTO_PANTALLA

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Juego con menú y niveles")

    while True:
        nivel = menu(pantalla)
        if nivel == 1:
            jugar(pantalla, mapa1)
        elif nivel == 2:
            jugar(pantalla, mapa2)

if __name__ == "__main__":
    main()
