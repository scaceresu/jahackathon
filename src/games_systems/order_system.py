"""
Sistema de Pedidos Reutilizable
===============================

Maneja la generación, seguimiento y completado de pedidos de clientes.
Compatible con diferentes tipos de mapas y configuraciones.
"""

import pygame
import random
import time
from typing import List, Tuple, Optional, Dict, Any

class OrderRequest:
    """
    Clase que representa un pedido individual de un cliente
    """
    
    def __init__(self, order_id: int, client_position: Tuple[int, int], 
                 items_requested: Dict[str, int], reward: int = 100,
                 time_limit: int = 30000):  # 30 segundos por defecto
        """
        Inicializa un pedido
        
        Args:
            order_id: ID único del pedido
            client_position: Posición del cliente (x, y)
            items_requested: Diccionario de items requeridos {item: cantidad}
            reward: Recompensa por completar el pedido
            time_limit: Tiempo límite en milisegundos
        """
        self.order_id = order_id
        self.client_position = client_position
        self.items_requested = items_requested
        self.reward = reward
        self.time_limit = time_limit
        
        # Estado del pedido
        self.created_time = pygame.time.get_ticks()
        self.status = "active"  # active, completed, expired, cancelled
        self.completion_time = None
        
        # Visual
        self.color = (255, 255, 0, 150)  # Amarillo por defecto
        self.size = 30
        
    def get_remaining_time(self) -> int:
        """Obtiene el tiempo restante en milisegundos"""
        if self.status != "active":
            return 0
        
        elapsed = pygame.time.get_ticks() - self.created_time
        remaining = self.time_limit - elapsed
        return max(0, remaining)
    
    def is_expired(self) -> bool:
        """Verifica si el pedido ha expirado"""
        return self.get_remaining_time() <= 0 and self.status == "active"
    
    def get_completion_percentage(self) -> float:
        """Obtiene el porcentaje de finalización del tiempo (0.0 a 1.0)"""
        if self.status != "active":
            return 1.0
        
        elapsed = pygame.time.get_ticks() - self.created_time
        return min(1.0, elapsed / self.time_limit)
    
    def can_be_completed_by(self, player_inventory: Dict[str, int]) -> bool:
        """
        Verifica si el pedido puede ser completado con el inventario del jugador
        
        Args:
            player_inventory: Inventario del jugador
            
        Returns:
            bool: True si el pedido puede ser completado
        """
        for item, required_amount in self.items_requested.items():
            if player_inventory.get(item, 0) < required_amount:
                return False
        return True
    
    def complete_order(self, player):
        """
        Completa el pedido y retira los items del inventario del jugador
        
        Args:
            player: Objeto jugador con inventario
            
        Returns:
            bool: True si se completó exitosamente
        """
        if self.status != "active":
            return False
        
        # Verificar que el jugador tenga todos los items
        if not self.can_be_completed_by(player.inventory):
            return False
        
        # Retirar items del inventario
        for item, amount in self.items_requested.items():
            player.inventory[item] -= amount
        
        # Otorgar recompensa (monedas)
        if hasattr(player, 'coin'):
            player.coin += self.reward
        elif hasattr(player, 'coins'):
            player.coins += self.reward
        
        self.status = "completed"
        self.completion_time = pygame.time.get_ticks()
        
        print(f"📦 Pedido #{self.order_id} completado! Recompensa: {self.reward}")
        return True
    
    def draw_on_map(self, surface, offset_x: int = 0, offset_y: int = 0):
        """
        Dibuja el indicador del pedido en el mapa
        
        Args:
            surface: Superficie donde dibujar
            offset_x, offset_y: Offset de cámara
        """
        if self.status != "active":
            return
        
        x = self.client_position[0] - offset_x
        y = self.client_position[1] - offset_y
        
        # Cambiar color según tiempo restante
        progress = self.get_completion_percentage()
        if progress < 0.5:
            color = (0, 255, 0, 150)  # Verde
        elif progress < 0.8:
            color = (255, 255, 0, 150)  # Amarillo
        else:
            color = (255, 0, 0, 150)  # Rojo
        
        # Dibujar círculo indicador
        pygame.draw.circle(surface, color, (int(x), int(y)), self.size)
        pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), self.size, 2)
        
        # Dibujar ID del pedido
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"#{self.order_id}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        surface.blit(text, text_rect)


class OrderSystem:
    """
    Sistema principal que maneja todos los pedidos activos
    """
    
    def __init__(self, client_positions: List[Tuple[int, int]], 
                 max_active_orders: int = 3,
                 order_generation_interval: int = 10000):  # 10 segundos
        """
        Inicializa el sistema de pedidos
        
        Args:
            client_positions: Lista de posiciones de clientes
            max_active_orders: Máximo número de pedidos activos
            order_generation_interval: Intervalo de generación en ms
        """
        self.client_positions = client_positions
        self.max_active_orders = max_active_orders
        self.order_generation_interval = order_generation_interval
        
        # Estado del sistema
        self.active_orders: Dict[int, OrderRequest] = {}
        self.completed_orders: List[OrderRequest] = []
        self.next_order_id = 1
        self.last_generation_time = 0
        
        # Configuración de pedidos
        self.available_items = ["empanada", "lomito", "pizza", "hamburguesa", "ron", "tabaco", "miel"]
        self.order_templates = [
            {"empanada": 2, "ron": 1},
            {"lomito": 1, "tabaco": 1}, 
            {"pizza": 1, "miel": 2},
            {"hamburguesa": 2},
            {"empanada": 1, "lomito": 1, "ron": 1}
        ]
        
        print(f"📋 OrderSystem inicializado con {len(client_positions)} clientes")
    
    def generate_order(self, force_position: Optional[Tuple[int, int]] = None) -> Optional[OrderRequest]:
        """
        Genera un nuevo pedido aleatorio
        
        Args:
            force_position: Posición forzada para el pedido
            
        Returns:
            OrderRequest: Pedido generado o None si no se pudo generar
        """
        if len(self.active_orders) >= self.max_active_orders:
            return None
        
        if not self.client_positions:
            return None
        
        # Seleccionar posición de cliente
        client_pos = force_position or random.choice(self.client_positions)
        
        # Seleccionar template de pedido
        items_requested = random.choice(self.order_templates).copy()
        
        # Calcular recompensa basada en dificultad
        total_items = sum(items_requested.values())
        reward = total_items * 50  # 50 monedas por item
        
        # Crear pedido
        order = OrderRequest(
            order_id=self.next_order_id,
            client_position=client_pos,
            items_requested=items_requested,
            reward=reward,
            time_limit=30000 + (total_items * 5000)  # Más tiempo para pedidos complejos
        )
        
        self.active_orders[self.next_order_id] = order
        self.next_order_id += 1
        
        print(f"📝 Nuevo pedido #{order.order_id}: {items_requested} en {client_pos}")
        return order
    
    def update(self, current_time: int):
        """
        Actualiza el sistema de pedidos
        
        Args:
            current_time: Tiempo actual en milisegundos
        """
        # Generar nuevos pedidos
        if (current_time - self.last_generation_time) >= self.order_generation_interval:
            if len(self.active_orders) < self.max_active_orders:
                self.generate_order()
            self.last_generation_time = current_time
        
        # Verificar pedidos expirados
        expired_orders = []
        for order_id, order in self.active_orders.items():
            if order.is_expired():
                order.status = "expired"
                expired_orders.append(order_id)
        
        # Remover pedidos expirados
        for order_id in expired_orders:
            expired_order = self.active_orders.pop(order_id)
            print(f"⏰ Pedido #{expired_order.order_id} expirado")
    
    def try_complete_order_at_position(self, player, position: Tuple[int, int], 
                                     tolerance: int = 50) -> bool:
        """
        Intenta completar un pedido en una posición específica
        
        Args:
            player: Objeto jugador
            position: Posición donde intentar completar
            tolerance: Tolerancia de distancia en píxeles
            
        Returns:
            bool: True si se completó un pedido
        """
        for order_id, order in list(self.active_orders.items()):
            if order.status != "active":
                continue
            
            # Verificar distancia
            distance = ((position[0] - order.client_position[0]) ** 2 + 
                       (position[1] - order.client_position[1]) ** 2) ** 0.5
            
            if distance <= tolerance:
                if order.complete_order(player):
                    # Mover a completados
                    completed_order = self.active_orders.pop(order_id)
                    self.completed_orders.append(completed_order)
                    return True
        
        return False
    
    def get_active_orders(self) -> List[OrderRequest]:
        """Obtiene lista de pedidos activos"""
        return [order for order in self.active_orders.values() if order.status == "active"]
    
    def get_orders_for_player(self, player) -> List[OrderRequest]:
        """Obtiene pedidos que el jugador puede completar"""
        completable = []
        for order in self.get_active_orders():
            if order.can_be_completed_by(player.inventory):
                completable.append(order)
        return completable
    
    def draw_orders_on_map(self, surface, offset_x: int = 0, offset_y: int = 0):
        """
        Dibuja todos los pedidos activos en el mapa
        
        Args:
            surface: Superficie donde dibujar
            offset_x, offset_y: Offset de cámara
        """
        for order in self.get_active_orders():
            order.draw_on_map(surface, offset_x, offset_y)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        return {
            "active_orders": len(self.active_orders),
            "completed_orders": len(self.completed_orders),
            "total_orders": self.next_order_id - 1,
            "completion_rate": len(self.completed_orders) / max(1, self.next_order_id - 1)
        }


def create_order_system(client_positions: List[Tuple[int, int]], 
                       **kwargs) -> OrderSystem:
    """
    Función de conveniencia para crear un sistema de pedidos
    
    Args:
        client_positions: Posiciones de clientes
        **kwargs: Argumentos adicionales para OrderSystem
        
    Returns:
        OrderSystem: Sistema de pedidos configurado
    """
    return OrderSystem(client_positions, **kwargs)