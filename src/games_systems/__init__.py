"""
Paquete de sistemas de juego reutilizables
==========================================

Este paquete contiene sistemas modulares que pueden ser reutilizados
en diferentes proyectos de juegos.
"""

# Importar todos los sistemas disponibles
from .inventory import InventoryManager
from .food_system import FoodSystem  
from .csv_mapper import CSVMapper
from .delivery_system import DeliverySystem
from .order_system import OrderSystem

# Lista de sistemas exportados
__all__ = [
    'InventoryManager',
    'FoodSystem', 
    'CSVMapper',
    'DeliverySystem',
    'OrderSystem'
]

# Versión del sistema
__version__ = "1.0.0"

# Importaciones principales para facilitar uso
from .inventory import InventoryManager
from .food_system import FoodSystem, FoodItem, FoodZone
from .csv_mapper import CSVMapper, ZoneExtractor
from .delivery_system import DeliverySystem

# OrderSystem no está disponible por el momento
# from .order_system import OrderSystem, OrderRequest

__all__ = [
    'InventoryManager',
    'FoodSystem', 'FoodItem', 'FoodZone', 
    'CSVMapper', 'ZoneExtractor',
    'DeliverySystem'
    # 'OrderSystem', 'OrderRequest',  # Commented out until available
]