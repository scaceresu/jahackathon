"""
Sistema de Comida Reutilizable
==============================

Maneja la generación, spawn y recolección de comida de forma independiente.
Compatible con diferentes tipos de mapas y configuraciones.
"""

import pygame
import random
import time
from typing import List, Tuple, Optional, Dict, Any

class FoodItem(pygame.sprite.Sprite):
    """
    Clase para items individuales de comida que se pueden recoger
    """
    
    def __init__(self, x: int, y: int, food_type: str, size: int = 16):
        """
        Inicializa un item de comida
        
        Args:
            x, y: Posición en píxeles
            food_type: Tipo de comida
            size: Tamaño del sprite
        """
        super().__init__()
        
        # Tipos de comida predefinidos con colores
        self.food_types = {
            "ron": {"name": "Ron", "initial": "R", "color": (139, 69, 19)},
            "tabaco": {"name": "Tabaco", "initial": "T", "color": (101, 67, 33)}, 
            "miel": {"name": "Miel", "initial": "M", "color": (255, 215, 0)},
            "empanada": {"name": "Empanada", "initial": "E", "color": (255, 165, 0)},
            "lomito": {"name": "Lomito", "initial": "L", "color": (255, 99, 71)},
            "pizza": {"name": "Pizza", "initial": "P", "color": (255, 69, 0)},
            "hamburguesa": {"name": "Hamburguesa", "initial": "H", "color": (160, 82, 45)}
        }
        
        self.food_type = food_type
        self.food_data = self.food_types.get(food_type, {
            "name": "Unknown", 
            "initial": "?", 
            "color": (255, 0, 255)
        })
        
        # Crear sprite visual
        self.image = pygame.Surface((size, size))
        self.image.fill(self.food_data["color"])
        pygame.draw.rect(self.image, (0, 0, 0), self.image.get_rect(), 1)
        
        # Agregar letra inicial
        pygame.font.init()
        font = pygame.font.SysFont(None, max(12, size - 4))
        text = font.render(self.food_data["initial"], True, (255, 255, 255))
        text_rect = text.get_rect(center=(size//2, size//2))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect(center=(x, y))
        
        # Metadatos
        self.spawn_time = pygame.time.get_ticks()
        self.collected = False
    
    def pickup(self, player) -> bool:
        """
        Permite al jugador recoger este item
        
        Args:
            player: Objeto player que recoge el item
            
        Returns:
            bool: True si se recogió exitosamente
        """
        if self.collected:
            return False
        
        try:
            # Agregar al inventario del jugador
            if hasattr(player, 'inventory'):
                if self.food_type in player.inventory:
                    player.inventory[self.food_type] += 1
                else:
                    player.inventory[self.food_type] = 1
            elif hasattr(player, 'add_item'):
                player.add_item(self.food_type, 1)
            else:
                print(f"⚠️ Player no tiene sistema de inventario compatible")
                return False
            
            self.collected = True
            print(f"🍽️ Recogido: {self.food_data['name']}")
            self.kill()  # Remover del grupo de sprites
            return True
            
        except Exception as e:
            print(f"❌ Error recogiendo comida: {e}")
            return False


class FoodZone(pygame.sprite.Sprite):
    """
    Zona donde se genera comida automáticamente al permanecer en ella
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 item_name: str = "lomito", give_time: float = 2.0,
                 color: Tuple[int, int, int, int] = (255, 255, 0, 100)):
        """
        Inicializa una zona de comida
        
        Args:
            x, y: Posición de la zona
            width, height: Dimensiones de la zona
            item_name: Tipo de comida que genera
            give_time: Tiempo en segundos para generar comida
            color: Color de la zona (RGBA)
        """
        super().__init__()
        
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.item_name = item_name
        self.give_time = give_time
        self.player_timers = {}  # {player: start_time}
    
    def update(self, player=None):
        """
        Actualiza la zona de comida
        
        Args:
            player: Objeto player para verificar colisión
        """
        if not player:
            return
        
        # Verificar si el player necesita este item
        needs_item = True
        if hasattr(player, 'inventory'):
            needs_item = player.inventory.get(self.item_name, 0) < 1
        
        if needs_item and self.rect.colliderect(player.rect):
            # Player está en la zona y necesita el item
            if player not in self.player_timers:
                self.player_timers[player] = time.time()
            else:
                # Verificar si pasó el tiempo necesario
                elapsed = time.time() - self.player_timers[player]
                if elapsed >= self.give_time:
                    self._give_item_to_player(player)
                    del self.player_timers[player]
        else:
            # Player salió de la zona o ya tiene el item
            if player in self.player_timers:
                del self.player_timers[player]
    
    def _give_item_to_player(self, player):
        """Otorga el item al jugador"""
        try:
            if hasattr(player, 'inventory'):
                player.inventory[self.item_name] = player.inventory.get(self.item_name, 0) + 1
            elif hasattr(player, 'add_item'):
                player.add_item(self.item_name, 1)
            
            print(f"🎁 Zona otorgó: {self.item_name}")
        except Exception as e:
            print(f"❌ Error otorgando item de zona: {e}")


class FoodSystem:
    """
    Sistema principal que maneja toda la lógica de comida
    """
    
    def __init__(self, restaurant_positions: List[Tuple[int, int]], 
                 food_types: Optional[List[str]] = None,
                 max_food_items: int = 5,
                 spawn_interval: int = 3000):
        """
        Inicializa el sistema de comida
        
        Args:
            restaurant_positions: Lista de posiciones donde spawnear comida
            food_types: Lista de tipos de comida disponibles
            max_food_items: Máximo de items en el mapa
            spawn_interval: Intervalo de spawn en milisegundos
        """
        self.restaurant_positions = restaurant_positions
        self.food_types = food_types or ["ron", "tabaco", "miel", "empanada", "lomito"]
        self.max_food_items = max_food_items
        self.spawn_interval = spawn_interval
        
        # Grupos de sprites
        self.food_items = pygame.sprite.Group()
        self.food_zones = pygame.sprite.Group()
        
        # Control de tiempo
        self.last_spawn_time = 0
        
        print(f"🍽️ FoodSystem inicializado:")
        print(f"   - {len(self.restaurant_positions)} posiciones de restaurante")
        print(f"   - {len(self.food_types)} tipos de comida: {self.food_types}")
        print(f"   - Máximo {self.max_food_items} items, spawn cada {spawn_interval}ms")
    
    def add_food_zone(self, x: int, y: int, width: int, height: int, 
                     item_name: str, give_time: float = 2.0):
        """
        Agrega una zona de comida automática
        
        Args:
            x, y: Posición de la zona
            width, height: Dimensiones
            item_name: Tipo de comida que genera
            give_time: Tiempo para generar
        """
        zone = FoodZone(x, y, width, height, item_name, give_time)
        self.food_zones.add(zone)
        print(f"➕ Zona de comida agregada: {item_name} en ({x}, {y})")
    
    def spawn_food_item(self, force_position: Optional[Tuple[int, int]] = None) -> bool:
        """
        Spawnea un item de comida en una posición aleatoria o específica
        
        Args:
            force_position: Posición específica o None para aleatoria
            
        Returns:
            bool: True si se spawneó exitosamente
        """
        if len(self.food_items) >= self.max_food_items:
            return False
        
        if not self.restaurant_positions and not force_position:
            print("⚠️ No hay posiciones de restaurante disponibles")
            return False
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Seleccionar posición
                if force_position:
                    x, y = force_position
                else:
                    x, y = random.choice(self.restaurant_positions)
                
                # Verificar que no haya otra comida muy cerca
                too_close = False
                min_distance = 32  # Mínima distancia entre items
                
                for existing_food in self.food_items:
                    distance = ((x - existing_food.rect.centerx) ** 2 + 
                              (y - existing_food.rect.centery) ** 2) ** 0.5
                    if distance < min_distance:
                        too_close = True
                        break
                
                if too_close and not force_position:
                    continue
                
                # Crear item de comida
                food_type = random.choice(self.food_types)
                food_item = FoodItem(x, y, food_type)
                self.food_items.add(food_item)
                
                print(f"🍽️ Comida spawneada: {food_type} en ({x}, {y})")
                return True
                
            except Exception as e:
                print(f"❌ Error en spawn intento {attempt + 1}: {e}")
                continue
        
        print(f"⚠️ No se pudo spawnear comida después de {max_attempts} intentos")
        return False
    
    def update(self, player=None):
        """
        Actualiza el sistema de comida
        
        Args:
            player: Objeto player para interacciones
        """
        current_time = pygame.time.get_ticks()
        
        # Spawn automático de comida
        if (current_time - self.last_spawn_time > self.spawn_interval and 
            len(self.food_items) < self.max_food_items):
            if self.spawn_food_item():
                self.last_spawn_time = current_time
        
        # Actualizar zonas de comida
        if player:
            for zone in self.food_zones:
                zone.update(player)
        
        # Verificar recolección de items
        if player:
            self.check_food_pickup(player)
    
    def check_food_pickup(self, player) -> List[str]:
        """
        Verifica si el jugador puede recoger algún item de comida
        
        Args:
            player: Objeto player
            
        Returns:
            List[str]: Lista de items recogidos
        """
        collected_items = []
        
        for food_item in list(self.food_items):
            if player.rect.colliderect(food_item.rect):
                if food_item.pickup(player):
                    collected_items.append(food_item.food_type)
        
        return collected_items
    
    def clear_all_food(self):
        """Limpia toda la comida del sistema"""
        self.food_items.empty()
        print("🧹 Toda la comida removida")
    
    def get_food_count(self) -> int:
        """Obtiene la cantidad actual de items de comida"""
        return len(self.food_items)
    
    def get_food_by_type(self) -> Dict[str, int]:
        """Obtiene conteo de comida por tipo"""
        counts = {}
        for food_item in self.food_items:
            food_type = food_item.food_type
            counts[food_type] = counts.get(food_type, 0) + 1
        return counts
    
    def draw(self, surface):
        """
        Dibuja todo el sistema de comida
        
        Args:
            surface: Superficie donde dibujar
        """
        self.food_zones.draw(surface)
        self.food_items.draw(surface)
    
    def draw_debug_info(self, surface, font, position: Tuple[int, int] = (10, 100)):
        """
        Dibuja información de debug del sistema
        
        Args:
            surface: Superficie donde dibujar
            font: Fuente para el texto
            position: Posición donde dibujar
        """
        x, y = position
        line_height = font.get_height() + 2
        
        # Información general
        info_lines = [
            f"Food System Debug:",
            f"Items: {len(self.food_items)}/{self.max_food_items}",
            f"Zones: {len(self.food_zones)}",
            f"Restaurants: {len(self.restaurant_positions)}"
        ]
        
        # Conteo por tipo
        counts = self.get_food_by_type()
        if counts:
            info_lines.append("Types:")
            for food_type, count in counts.items():
                info_lines.append(f"  {food_type}: {count}")
        
        # Dibujar líneas
        for i, line in enumerate(info_lines):
            text = font.render(line, True, (255, 255, 255))
            surface.blit(text, (x, y + i * line_height))


def create_food_system(restaurant_positions: List[Tuple[int, int]], 
                      food_types: Optional[List[str]] = None) -> FoodSystem:
    """
    Función de conveniencia para crear un sistema de comida
    
    Args:
        restaurant_positions: Posiciones donde spawnear comida
        food_types: Tipos de comida disponibles
        
    Returns:
        FoodSystem: Sistema de comida configurado
    """
    return FoodSystem(restaurant_positions, food_types)