import pygame
import sys
from settings import COLOR_FONDO, COLOR_BOTON, COLOR_TEXTO, FUENTE_TAM

def menu(pantalla):
    fuente = pygame.font.SysFont(None, FUENTE_TAM)
    botones = [
        {"texto": "Nivel 1", "rect": pygame.Rect(300, 200, 200, 60), "nivel": 1},
        {"texto": "Nivel 2", "rect": pygame.Rect(300, 300, 200, 60), "nivel": 2},
        {"texto": "Salir",   "rect": pygame.Rect(300, 400, 200, 60), "nivel": None},
    ]

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for boton in botones:
                    if boton["rect"].collidepoint(evento.pos):
                        if boton["nivel"] is None:
                            pygame.quit()
                            sys.exit()
                        else:
                            return boton["nivel"]

        pantalla.fill(COLOR_FONDO)

        for boton in botones:
            pygame.draw.rect(pantalla, COLOR_BOTON, boton["rect"])
            texto = fuente.render(boton["texto"], True, COLOR_TEXTO)
            pantalla.blit(texto, texto.get_rect(center=boton["rect"].center))

        pygame.display.flip()
