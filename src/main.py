import pygame
from menu import menu
from game import jugar
from settings import ANCHO_PANTALLA, ALTO_PANTALLA
from progressmanager import cargarProgreso, guardarProgreso

mapa1 = r"src/maps/mapa1.json"
mapa2 = r"src/maps/mapa1.json"

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Juego")

    # Загружаем сохранённый прогресс
    nivel_desbloqueado = cargarProgreso()

    while True:
        nivel = menu(pantalla, nivel_desbloqueado)

        if nivel == 1:
            completado = jugar(pantalla, mapa1)
            if completado:
                nivel_desbloqueado = max(nivel_desbloqueado, 2)
                guardarProgreso(nivel_desbloqueado)

        elif nivel == 2:
            if nivel_desbloqueado >= 2:
                completado = jugar(pantalla, mapa2)
                if completado:
                    nivel_desbloqueado = max(nivel_desbloqueado, 3)
                    guardarProgreso(nivel_desbloqueado)
            else:
                print("❌!")

if __name__ == "__main__":
    main()
