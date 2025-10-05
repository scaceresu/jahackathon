import pygame
from settings import TILE, COLOR_TEXTO, FUENTE_TAM, COLOR_VIDA, COLOR_SCORE

class PlayerMenu:
    """
    HUD for player: scores, lifes, food, exit button
    """
    def __init__(self, jugador):
        self.jugador = jugador
        self.fuente = pygame.font.SysFont(None, FUENTE_TAM)
        self.boton_salir = pygame.Rect(650, 20, 120, 40)

    def dibujar(self, pantalla):
        # --- Coins ---
        texto_puntos = self.fuente.render(f"Puntos: {self.jugador.coin}", True, COLOR_SCORE)
        pantalla.blit(texto_puntos, (20, 20))

        # --- Lifes ---
        for i in range(self.jugador.vidas):
            rect_vida = pygame.Rect(240 + i * (TILE + 5), 30, TILE, TILE)
            pygame.draw.rect(pantalla, COLOR_VIDA, rect_vida)

        # --- Inventario ---
        x_inventario, y_inventario = 20, 50
        for item, cantidad in self.jugador.inventory.items():
            if cantidad > 0:
                texto_item = self.fuente.render(f"{item.capitalize()}: {cantidad}", True, (255, 255, 255))
                pantalla.blit(texto_item, (x_inventario, y_inventario))
                y_inventario += texto_item.get_height() + 5

        # --- Botón salir ---
        pygame.draw.rect(pantalla, (255, 80, 80), self.boton_salir, border_radius=5)
        texto = self.fuente.render("Salir", True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=self.boton_salir.center))

    def manejar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                return True
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return True
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.boton_salir.collidepoint(evento.pos):
                    return True
        return False
