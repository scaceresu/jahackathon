"""
Sistema de Entrega Reutilizable
===============================

Maneja la lógica de pickup/delivery y zonas especiales de forma independiente.
Compatible con diferentes tipos de mapas y sistemas de juego.
"""

import pygame
import time
from typing import List, Tuple, Optional, Dict, Any, Callable

class DeliveryZone(pygame.sprite.Sprite):
    """
    Zona especializada para entregas con lógica específica
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 zone_type: str = "delivery", zone_id: Optional[int] = None,
                 color: Tuple[int, int, int, int] = (0, 255, 0, 100),
                 activation_time: float = 1.0):
        """
        Inicializa una zona de entrega
        
        Args:
            x, y: Posición de la zona
            width, height: Dimensiones
            zone_type: Tipo de zona (delivery, pickup, safe, special)
            zone_id: ID único de la zona
            color: Color de la zona (RGBA)
            activation_time: Tiempo para activar la zona
        """
        super().__init__()
        
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        
        # Agregar borde
        pygame.draw.rect(self.image, (0, 0, 0), self.image.get_rect(), 2)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Propiedades de la zona
        self.zone_type = zone_type
        self.zone_id = zone_id or id(self)
        self.activation_time = activation_time
        
        # Estado de activación
        self.player_timers = {}  # {player: start_time}
        self.activated_players = set()
        
        # Callbacks personalizados
        self.on_enter_callback: Optional[Callable] = None
        self.on_exit_callback: Optional[Callable] = None
        self.on_activate_callback: Optional[Callable] = None
        
        print(f"🏪 Zona creada: {zone_type} #{zone_id} en ({x}, {y})")
    
    def set_callbacks(self, on_enter=None, on_exit=None, on_activate=None):
        """
        Configura callbacks para eventos de la zona
        
        Args:
            on_enter: Función llamada al entrar (player, zone)
            on_exit: Función llamada al salir (player, zone)
            on_activate: Función llamada al activar (player, zone)
        """
        self.on_enter_callback = on_enter
        self.on_exit_callback = on_exit
        self.on_activate_callback = on_activate
    
    def update(self, player=None):
        """
        Actualiza la zona de entrega
        
        Args:
            player: Objeto player para verificar colisión
        """
        if not player:
            return
        
        player_in_zone = self.rect.colliderect(player.rect)
        player_was_in_timers = player in self.player_timers
        
        if player_in_zone:
            if not player_was_in_timers:
                # Player entra a la zona
                self.player_timers[player] = time.time()
                if self.on_enter_callback:
                    self.on_enter_callback(player, self)
            else:
                # Player está en la zona, verificar activación
                elapsed = time.time() - self.player_timers[player]
                if elapsed >= self.activation_time and player not in self.activated_players:
                    self.activated_players.add(player)
                    if self.on_activate_callback:
                        self.on_activate_callback(player, self)
        else:
            if player_was_in_timers:
                # Player sale de la zona
                del self.player_timers[player]
                if player in self.activated_players:
                    self.activated_players.remove(player)
                if self.on_exit_callback:
                    self.on_exit_callback(player, self)
    
    def get_activation_progress(self, player) -> float:
        """
        Obtiene el progreso de activación de un player (0.0 a 1.0)
        
        Args:
            player: Objeto player
            
        Returns:
            float: Progreso de activación
        """
        if player not in self.player_timers:
            return 0.0
        
        elapsed = time.time() - self.player_timers[player]
        return min(1.0, elapsed / self.activation_time)
    
    def is_player_activated(self, player) -> bool:
        """Verifica si un player ha activado la zona"""
        return player in self.activated_players


class SaveZone(DeliveryZone):
    """
    Zona de guardado que permite salvar el progreso del jugador
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 save_callback: Optional[Callable] = None):
        """
        Inicializa una zona de guardado
        
        Args:
            x, y: Posición de la zona
            width, height: Dimensiones
            save_callback: Función para guardar progreso
        """
        super().__init__(x, y, width, height, "save", 
                        color=(0, 0, 255, 100), activation_time=2.0)
        
        self.save_callback = save_callback
        self.last_save_time = 0
        self.save_cooldown = 5.0  # Cooldown entre guardados
        
        # Configurar callback de activación
        self.set_callbacks(on_activate=self._handle_save)
    
    def _handle_save(self, player, zone):
        """Maneja el guardado del progreso"""
        current_time = time.time()
        
        if current_time - self.last_save_time < self.save_cooldown:
            return
        
        try:
            if self.save_callback:
                self.save_callback(player)
            
            self.last_save_time = current_time
            print(f"💾 Progreso guardado para player en zona #{self.zone_id}")
            
        except Exception as e:
            print(f"❌ Error guardando progreso: {e}")


class DeliverySystem:
    """
    Sistema principal que maneja toda la lógica de entrega y pickup
    """
    
    def __init__(self, order_system=None, food_system=None):
        """
        Inicializa el sistema de entrega
        
        Args:
            order_system: Sistema de pedidos para integración
            food_system: Sistema de comida para integración
        """
        self.order_system = order_system
        self.food_system = food_system
        
        # Zonas de entrega
        self.delivery_zones = pygame.sprite.Group()
        self.save_zones = pygame.sprite.Group()
        
        # Estadísticas
        self.deliveries_made = 0
        self.items_picked_up = 0
        self.zones_activated = 0
        
        print(f"🚚 DeliverySystem inicializado")
        if order_system:
            print(f"   - Integrado con OrderSystem")
        if food_system:
            print(f"   - Integrado con FoodSystem")
    
    def add_delivery_zone(self, x: int, y: int, width: int, height: int,
                         zone_type: str = "delivery", zone_id: Optional[int] = None,
                         **kwargs) -> DeliveryZone:
        """
        Agrega una zona de entrega
        
        Args:
            x, y: Posición de la zona
            width, height: Dimensiones
            zone_type: Tipo de zona
            zone_id: ID de la zona
            **kwargs: Argumentos adicionales para la zona
            
        Returns:
            DeliveryZone: Zona creada
        """
        zone = DeliveryZone(x, y, width, height, zone_type, zone_id, **kwargs)
        self.delivery_zones.add(zone)
        return zone
    
    def add_save_zone(self, x: int, y: int, width: int, height: int,
                     save_callback: Optional[Callable] = None) -> SaveZone:
        """
        Agrega una zona de guardado
        
        Args:
            x, y: Posición de la zona
            width, height: Dimensiones
            save_callback: Función para guardar
            
        Returns:
            SaveZone: Zona de guardado creada
        """
        zone = SaveZone(x, y, width, height, save_callback)
        self.save_zones.add(zone)
        self.delivery_zones.add(zone)  # También es una zona de entrega
        return zone
    
    def create_client_delivery_zones(self, client_positions: List[Tuple[int, int, int]],
                                   zone_size: Tuple[int, int] = (64, 64)):
        """
        Crea zonas de entrega para todas las casas de clientes
        
        Args:
            client_positions: Lista de (x, y, house_id)
            zone_size: Tamaño de las zonas (width, height)
        """
        width, height = zone_size
        
        for x, y, house_id in client_positions:
            # Crear zona centrada en la posición de la casa
            zone_x = x - width // 2
            zone_y = y - height // 2
            
            zone = self.add_delivery_zone(
                zone_x, zone_y, width, height,
                zone_type="client_delivery",
                zone_id=house_id,
                color=(255, 255, 0, 80),
                activation_time=1.5
            )
            
            # Configurar callback para entregas
            zone.set_callbacks(on_activate=self._handle_client_delivery)
    
    def _handle_client_delivery(self, player, zone):
        """
        Maneja la entrega en una zona de cliente
        
        Args:
            player: Objeto jugador
            zone: Zona de entrega
        """
        if not self.order_system:
            return
        
        # Intentar entregar pedido
        delivered_order = self.order_system.check_delivery(player, delivery_range=64)
        if delivered_order:
            self.deliveries_made += 1
            self.zones_activated += 1
            print(f"📦 Entrega completada en zona #{zone.zone_id}")
    
    def update(self, player=None):
        """
        Actualiza el sistema de entrega
        
        Args:
            player: Objeto jugador
        """
        # Actualizar todas las zonas
        for zone in self.delivery_zones:
            zone.update(player)
        
        # Verificar pickup de comida si hay food_system
        if self.food_system and player:
            picked_items = self.food_system.check_food_pickup(player)
            self.items_picked_up += len(picked_items)
    
    def get_zone_by_id(self, zone_id: int) -> Optional[DeliveryZone]:
        """Busca una zona por su ID"""
        for zone in self.delivery_zones:
            if zone.zone_id == zone_id:
                return zone
        return None
    
    def get_zones_by_type(self, zone_type: str) -> List[DeliveryZone]:
        """Obtiene todas las zonas de un tipo específico"""
        return [zone for zone in self.delivery_zones if zone.zone_type == zone_type]
    
    def get_player_progress_in_zones(self, player) -> Dict[int, float]:
        """
        Obtiene el progreso del jugador en todas las zonas
        
        Args:
            player: Objeto jugador
            
        Returns:
            Dict[int, float]: {zone_id: progress}
        """
        progress = {}
        for zone in self.delivery_zones:
            if zone.zone_id:
                progress[zone.zone_id] = zone.get_activation_progress(player)
        return progress
    
    def clear_all_zones(self):
        """Limpia todas las zonas del sistema"""
        self.delivery_zones.empty()
        self.save_zones.empty()
        print("🧹 Todas las zonas de entrega removidas")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        return {
            "delivery_zones": len(self.delivery_zones),
            "save_zones": len(self.save_zones),
            "deliveries_made": self.deliveries_made,
            "items_picked_up": self.items_picked_up,
            "zones_activated": self.zones_activated
        }
    
    def draw(self, surface):
        """
        Dibuja todas las zonas de entrega
        
        Args:
            surface: Superficie donde dibujar
        """
        self.delivery_zones.draw(surface)
    
    def draw_activation_progress(self, surface, player, font):
        """
        Dibuja el progreso de activación de las zonas
        
        Args:
            surface: Superficie donde dibujar
            player: Objeto jugador
            font: Fuente para el texto
        """
        for zone in self.delivery_zones:
            progress = zone.get_activation_progress(player)
            
            if progress > 0:
                # Dibujar barra de progreso sobre la zona
                bar_width = zone.rect.width
                bar_height = 8
                bar_x = zone.rect.x
                bar_y = zone.rect.y - bar_height - 4
                
                # Fondo de la barra
                pygame.draw.rect(surface, (50, 50, 50), 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Progreso
                progress_width = int(bar_width * progress)
                color = (255, 255, 0) if progress < 1.0 else (0, 255, 0)
                pygame.draw.rect(surface, color,
                               (bar_x, bar_y, progress_width, bar_height))
                
                # Borde
                pygame.draw.rect(surface, (255, 255, 255),
                               (bar_x, bar_y, bar_width, bar_height), 1)
    
    def draw_debug_info(self, surface, font, position: Tuple[int, int] = (10, 300)):
        """
        Dibuja información de debug
        
        Args:
            surface: Superficie donde dibujar
            font: Fuente para el texto
            position: Posición donde dibujar
        """
        x, y = position
        line_height = font.get_height() + 2
        
        stats = self.get_statistics()
        
        info_lines = [
            f"Delivery System Debug:",
            f"Zones: {stats['delivery_zones']} (Save: {stats['save_zones']})",
            f"Deliveries: {stats['deliveries_made']}",
            f"Items Picked: {stats['items_picked_up']}",
            f"Activations: {stats['zones_activated']}"
        ]
        
        # Dibujar líneas
        for i, line in enumerate(info_lines):
            text = font.render(line, True, (255, 255, 255))
            surface.blit(text, (x, y + i * line_height))


def create_delivery_system(order_system=None, food_system=None) -> DeliverySystem:
    """
    Función de conveniencia para crear un sistema de entrega
    
    Args:
        order_system: Sistema de pedidos opcional
        food_system: Sistema de comida opcional
        
    Returns:
        DeliverySystem: Sistema de entrega configurado
    """
    return DeliverySystem(order_system, food_system)