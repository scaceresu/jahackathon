"""
Sistema de Inventario Reutilizable
==================================

Maneja el inventario del jugador de forma independiente del resto del juego.
Funciona con cualquier estructura de player que tenga un atributo 'inventory'.
"""

import pygame
from typing import Dict, Any, Optional, List

class InventoryManager:
    """
    Gestor de inventario reutilizable que maneja items de cualquier tipo
    """
    
    def __init__(self, initial_items: Optional[Dict[str, int]] = None):
        """
        Inicializa el gestor de inventario
        
        Args:
            initial_items: Diccionario inicial de items {nombre: cantidad}
        """
        self.default_items = initial_items or {
            "empanada": 0,
            "lomito": 0, 
            "pizza": 0,
            "hamburguesa": 0,
            "ron": 0,
            "tabaco": 0,
            "miel": 0
        }
        
    def initialize_player_inventory(self, player):
        """
        Inicializa el inventario de un jugador si no lo tiene
        
        Args:
            player: Objeto player que tendrá el atributo inventory
        """
        if not hasattr(player, 'inventory'):
            player.inventory = self.default_items.copy()
        else:
            # Asegurar que tiene todos los items necesarios
            for item, amount in self.default_items.items():
                if item not in player.inventory:
                    player.inventory[item] = amount
    
    def add_item(self, player, item_name: str, amount: int = 1) -> bool:
        """
        Agrega un item al inventario del jugador
        
        Args:
            player: Objeto player con atributo inventory
            item_name: Nombre del item a agregar
            amount: Cantidad a agregar
            
        Returns:
            bool: True si se agregó exitosamente
        """
        try:
            self.initialize_player_inventory(player)
            
            if item_name in player.inventory:
                player.inventory[item_name] += amount
                print(f"✅ Agregado {amount} {item_name}. Total: {player.inventory[item_name]}")
                return True
            else:
                player.inventory[item_name] = amount
                print(f"✅ Nuevo item {item_name}: {amount}")
                return True
                
        except Exception as e:
            print(f"❌ Error agregando item {item_name}: {e}")
            return False
    
    def remove_item(self, player, item_name: str, amount: int = 1) -> bool:
        """
        Remueve un item del inventario del jugador
        
        Args:
            player: Objeto player con atributo inventory
            item_name: Nombre del item a remover
            amount: Cantidad a remover
            
        Returns:
            bool: True si se removió exitosamente
        """
        try:
            self.initialize_player_inventory(player)
            
            if item_name in player.inventory and player.inventory[item_name] >= amount:
                player.inventory[item_name] -= amount
                print(f"🔽 Removido {amount} {item_name}. Restante: {player.inventory[item_name]}")
                return True
            else:
                print(f"❌ No hay suficiente {item_name} para remover {amount}")
                return False
                
        except Exception as e:
            print(f"❌ Error removiendo item {item_name}: {e}")
            return False
    
    def has_item(self, player, item_name: str, amount: int = 1) -> bool:
        """
        Verifica si el jugador tiene suficiente cantidad de un item
        
        Args:
            player: Objeto player con atributo inventory
            item_name: Nombre del item a verificar
            amount: Cantidad mínima requerida
            
        Returns:
            bool: True si tiene suficiente cantidad
        """
        try:
            self.initialize_player_inventory(player)
            return player.inventory.get(item_name, 0) >= amount
        except:
            return False
    
    def get_item_count(self, player, item_name: str) -> int:
        """
        Obtiene la cantidad de un item específico
        
        Args:
            player: Objeto player con atributo inventory
            item_name: Nombre del item
            
        Returns:
            int: Cantidad del item (0 si no existe)
        """
        try:
            self.initialize_player_inventory(player)
            return player.inventory.get(item_name, 0)
        except:
            return 0
    
    def get_inventory_summary(self, player) -> Dict[str, int]:
        """
        Obtiene un resumen completo del inventario
        
        Args:
            player: Objeto player con atributo inventory
            
        Returns:
            Dict[str, int]: Copia del inventario completo
        """
        try:
            self.initialize_player_inventory(player)
            return player.inventory.copy()
        except:
            return {}
    
    def clear_inventory(self, player):
        """
        Limpia completamente el inventario del jugador
        
        Args:
            player: Objeto player con atributo inventory
        """
        try:
            self.initialize_player_inventory(player)
            for item in player.inventory:
                player.inventory[item] = 0
            print("🧹 Inventario limpiado")
        except Exception as e:
            print(f"❌ Error limpiando inventario: {e}")
    
    def transfer_item(self, from_player, to_player, item_name: str, amount: int = 1) -> bool:
        """
        Transfiere un item entre dos jugadores
        
        Args:
            from_player: Jugador origen
            to_player: Jugador destino  
            item_name: Nombre del item
            amount: Cantidad a transferir
            
        Returns:
            bool: True si la transferencia fue exitosa
        """
        if self.has_item(from_player, item_name, amount):
            if self.remove_item(from_player, item_name, amount):
                if self.add_item(to_player, item_name, amount):
                    print(f"↔️ Transferido {amount} {item_name}")
                    return True
                else:
                    # Revertir si falló agregar al destino
                    self.add_item(from_player, item_name, amount)
        return False
    
    def print_inventory(self, player, title: str = "Inventario"):
        """
        Imprime el inventario del jugador para debugging
        
        Args:
            player: Objeto player con atributo inventory
            title: Título para mostrar
        """
        try:
            self.initialize_player_inventory(player)
            print(f"\n📦 {title}:")
            for item, amount in player.inventory.items():
                if amount > 0:
                    print(f"   {item}: {amount}")
            print()
        except Exception as e:
            print(f"❌ Error mostrando inventario: {e}")


class InventoryDisplay:
    """
    Clase para mostrar el inventario en pantalla (opcional)
    """
    
    def __init__(self, font_size: int = 24):
        """
        Inicializa el display del inventario
        
        Args:
            font_size: Tamaño de la fuente
        """
        pygame.font.init()
        self.font = pygame.font.SysFont(None, font_size)
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0, 128)
    
    def draw_inventory(self, surface, player, position: tuple = (10, 10)):
        """
        Dibuja el inventario en pantalla
        
        Args:
            surface: Superficie donde dibujar
            player: Objeto player con inventario
            position: Posición (x, y) donde dibujar
        """
        try:
            if not hasattr(player, 'inventory'):
                return
            
            x, y = position
            line_height = self.font.get_height() + 2
            
            # Título
            title_text = self.font.render("Inventario:", True, self.text_color)
            surface.blit(title_text, (x, y))
            y += line_height
            
            # Items
            for item, amount in player.inventory.items():
                if amount > 0:
                    item_text = self.font.render(f"{item}: {amount}", True, self.text_color)
                    surface.blit(item_text, (x, y))
                    y += line_height
                    
        except Exception as e:
            print(f"❌ Error dibujando inventario: {e}")


# Instancia global para facilitar uso
default_inventory_manager = InventoryManager()

def add_item_to_player(player, item_name: str, amount: int = 1) -> bool:
    """Función de conveniencia para agregar items"""
    return default_inventory_manager.add_item(player, item_name, amount)

def remove_item_from_player(player, item_name: str, amount: int = 1) -> bool:
    """Función de conveniencia para remover items"""
    return default_inventory_manager.remove_item(player, item_name, amount)

def player_has_item(player, item_name: str, amount: int = 1) -> bool:
    """Función de conveniencia para verificar items"""
    return default_inventory_manager.has_item(player, item_name, amount)