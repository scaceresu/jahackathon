import pygame
from settings import TILE, COLOR_TEXTO, FUENTE_TAM, COLOR_VIDA, COLOR_SCORE, COLOR_BOOST

class PlayerMenu:
    """
    HUD for player: scores, lifes, food, boost
    """
    def __init__(self, jugador):
        self.jugador = jugador
        self.fuente = pygame.font.SysFont(None, FUENTE_TAM)

    def dibujar(self, pantalla):
        # --- Coins ---
        texto_puntos = self.fuente.render(f"Puntos: {self.jugador.coin}", True, COLOR_SCORE)
        pantalla.blit(texto_puntos, (20, 20))

        # --- Lifes ---
        for i in range(self.jugador.vidas):
            rect_vida = pygame.Rect(240 + i * (TILE + 5), 30, TILE, TILE)
            pygame.draw.rect(pantalla, COLOR_VIDA, rect_vida)
        x_inventario = 20
        y_inventario = 50
        for item, cantidad in self.jugador.inventory.items():
            if cantidad > 0:
                texto_item = self.fuente.render(f"{item.capitalize()}: {cantidad}", True, (255, 255, 255))
                pantalla.blit(texto_item, (x_inventario, y_inventario))
                y_inventario += texto_item.get_height() + 5
                
        # # --- Буст (полоса) ---
        # boost_ancho = 80  # ширина полосы буста
        # boost_alto = 16
        # boost_x = 60
        # boost_y = 50
        # # рамка
        # pygame.draw.rect(pantalla, (100, 100, 100), (boost_x, boost_y, boost_ancho, boost_alto))
        # # текущий буст
        # if hasattr(self.jugador, "boost"):
        #     porcentaje = max(0, min(self.jugador.boost, 1))  # буст от 0 до 1
        #     pygame.draw.rect(pantalla, COLOR_BOOST, 
        #                      (boost_x, boost_y, boost_ancho * porcentaje, boost_alto))

        # # --- Иконка игрока ---
        # icono_jugador = pygame.Surface((TILE, TILE))
        # icono_jugador.fill((255, 0, 0))
        # pantalla.blit(icono_jugador, (20, 110))
