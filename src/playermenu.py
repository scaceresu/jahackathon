import pygame
from settings import TILE, COLOR_TEXTO, FUENTE_TAM, COLOR_VIDA, COLOR_SCORE, COLOR_BOOST

class PlayerMenu:
    """
    HUD for player: scores, lifes, food, boost
    """
    def __init__(self, jugador):
        self.jugador = jugador
        self.fuente = pygame.font.SysFont(None, FUENTE_TAM)
        self.fuente_pequena = pygame.font.SysFont(None, 20)
        self.order_system = None  # Se asignará desde el juego

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
                
        # --- Información de pedidos ---
        if self.order_system:
            y_pedidos = y_inventario + 20
            
            # Título de pedidos
            titulo_pedidos = self.fuente.render("Pedidos Activos:", True, (255, 255, 100))
            pantalla.blit(titulo_pedidos, (20, y_pedidos))
            y_pedidos += titulo_pedidos.get_height() + 5
            
            # Listar pedidos que el jugador puede completar
            pedidos_completables = self.order_system.get_orders_for_player(self.jugador)
            
            if pedidos_completables:
                for orden in pedidos_completables[:3]:  # Máximo 3 pedidos en pantalla
                    # Información básica del pedido
                    items_text = ", ".join([f"{item}x{cant}" for item, cant in orden.items_requested.items()])
                    texto_pedido = self.fuente_pequena.render(
                        f"#{orden.order_id}: {items_text} - ${orden.reward}", 
                        True, (0, 255, 0)
                    )
                    pantalla.blit(texto_pedido, (25, y_pedidos))
                    y_pedidos += texto_pedido.get_height() + 2
                    
                    # Barra de tiempo restante
                    tiempo_restante = orden.get_remaining_time()
                    progreso = orden.get_completion_percentage()
                    
                    barra_ancho = 150
                    barra_alto = 8
                    barra_x = 25
                    barra_y = y_pedidos
                    
                    # Fondo de la barra
                    pygame.draw.rect(pantalla, (100, 100, 100), (barra_x, barra_y, barra_ancho, barra_alto))
                    
                    # Color según tiempo restante
                    if progreso < 0.5:
                        color_tiempo = (0, 255, 0)  # Verde
                    elif progreso < 0.8:
                        color_tiempo = (255, 255, 0)  # Amarillo
                    else:
                        color_tiempo = (255, 0, 0)  # Rojo
                    
                    # Barra de progreso
                    progreso_ancho = int(barra_ancho * (1 - progreso))
                    pygame.draw.rect(pantalla, color_tiempo, (barra_x, barra_y, progreso_ancho, barra_alto))
                    
                    y_pedidos += barra_alto + 10
            else:
                # No hay pedidos completables
                active_orders = self.order_system.get_active_orders()
                if active_orders:
                    texto_no_completable = self.fuente_pequena.render(
                        "Necesitas más items para completar pedidos", 
                        True, (255, 150, 150)
                    )
                    pantalla.blit(texto_no_completable, (25, y_pedidos))
                else:
                    texto_sin_pedidos = self.fuente_pequena.render(
                        "No hay pedidos activos", 
                        True, (150, 150, 150)
                    )
                    pantalla.blit(texto_sin_pedidos, (25, y_pedidos))
            
            # Instrucciones
            y_pedidos += 30
            instruccion = self.fuente_pequena.render(
                "Presiona ESPACIO cerca de un cliente para entregar", 
                True, (200, 200, 200)
            )
            pantalla.blit(instruccion, (20, y_pedidos))
                
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
