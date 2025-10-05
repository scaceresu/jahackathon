import pygame
import sys
from settings import COLOR_FONDO, COLOR_BOTON, COLOR_TEXTO, FUENTE_TAM

COLOR_BLOQUEADO = (100, 100, 100)

def menu(pantalla, nivel_desbloqueado=1):
    fuente = pygame.font.SysFont(None, FUENTE_TAM)
    botones = [
        {"texto": "Nivel 1", "rect": pygame.Rect(300, 200, 200, 60), "nivel": 1},
        {"texto": "Nivel 2", "rect": pygame.Rect(300, 300, 200, 60), "nivel": 2},
        {"texto": "Salir",   "rect": pygame.Rect(300, 400, 200, 60), "nivel": None},
    ]
    lock_img = pygame.image.load("assets\imagenes\lock\lock.png").convert_alpha()
    lock_img = pygame.transform.scale(lock_img, (32, 32))
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
                        elif boton["nivel"] <= nivel_desbloqueado:
                            return boton["nivel"]

        pantalla.fill(COLOR_FONDO)

        for boton in botones:
            bloqueado = boton["nivel"] and boton["nivel"] > nivel_desbloqueado

            # Button color
            color = COLOR_BLOQUEADO if bloqueado else COLOR_BOTON
            pygame.draw.rect(pantalla, color, boton["rect"], border_radius=10)

            # Text
            texto = fuente.render(boton["texto"], True, COLOR_TEXTO)
            texto_rect = texto.get_rect(center=boton["rect"].center)
            pantalla.blit(texto, texto_rect)

            # Locker
            if bloqueado and lock_img:
                    lock_rect = lock_img.get_rect()
                    lock_rect.centery = boton["rect"].centery
                    # Locker afte text
                    lock_rect.left = texto_rect.right + 5
                    pantalla.blit(lock_img, lock_rect)

        pygame.display.flip()