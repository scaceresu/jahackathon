import pygame
import sys
from settings import COLOR_FONDO, COLOR_BOTON, COLOR_TEXTO, FUENTE_TAM

COLOR_BLOQUEADO = (100, 100, 100)
COLOR_HOVER = (180, 180, 250)

def menu(pantalla, nivel_desbloqueado=1):
    fuente = pygame.font.SysFont(None, FUENTE_TAM)

    botones = []
    y = 200
    for i in range(1, 5):
        botones.append({"texto": f"Nivel {i}", "rect": pygame.Rect(300, y, 200, 60), "nivel": i})
        y += 80
    botones.append({"texto": "Salir", "rect": pygame.Rect(300, y, 200, 60), "nivel": None})

    lock_img = pygame.image.load(r"assets/imagenes/lock/lock.png").convert_alpha()
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

        mouse_pos = pygame.mouse.get_pos()
        for boton in botones:
            bloqueado = boton["nivel"] and boton["nivel"] > nivel_desbloqueado
            hover = boton["rect"].collidepoint(mouse_pos)

            if bloqueado:
                color = COLOR_BLOQUEADO
            elif hover:
                color = COLOR_HOVER
            else:
                color = COLOR_BOTON

            pygame.draw.rect(pantalla, color, boton["rect"], border_radius=10)

            texto = fuente.render(boton["texto"], True, COLOR_TEXTO)
            texto_rect = texto.get_rect(center=boton["rect"].center)
            pantalla.blit(texto, texto_rect)

            if bloqueado:
                lock_rect = lock_img.get_rect()
                lock_rect.centery = boton["rect"].centery
                lock_rect.left = texto_rect.right + 5
                pantalla.blit(lock_img, lock_rect)

        pygame.display.flip()
