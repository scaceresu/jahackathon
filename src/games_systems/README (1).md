# Game Systems Module

Módulo reutilizable de sistemas de juego para proyectos Pygame. Contiene todas las funcionalidades extraídas del proyecto original para que puedan ser reutilizadas en diferentes implementaciones.

## 🎯 Características

- **Modular**: Cada sistema funciona independientemente
- **Reutilizable**: Compatible con diferentes estructuras de proyecto
- **Integrable**: Los sistemas se conectan automáticamente cuando es necesario
- **Configurable**: Soporte para múltiples configuraciones CSV y tipos de juego

## 📦 Sistemas Incluidos

### 1. InventoryManager
Sistema completo de manejo de inventarios.

```python
from game_systems import InventoryManager

inventory = InventoryManager()
inventory.add_item("sword", 1)
inventory.add_item("potion", 5)
print(inventory.get_inventory())  # {'sword': 1, 'potion': 5}
```

**Características:**
- Agregar/remover items con validación
- Transferir items entre inventarios
- Verificar disponibilidad de items
- Display visual del inventario
- Debugging y logging

### 2. CSVMapper
Sistema de mapeo y extracción de zonas desde archivos CSV.

```python
from game_systems import CSVMapper

mapper = CSVMapper("mapa.csv", config="ypane_unified")
restaurants = mapper.extract_restaurants()
clients = mapper.extract_client_houses()
collisions = mapper.generate_collision_rects()
```

**Configuraciones soportadas:**
- `ypane_unified`: 963=walkable, 973=collision, 894=restaurants, 822=clients, 861=superpowers
- `simple`: 1=walkable, 0=collision, 2=special
- `alexis`: 1=walkable, 2=collision, 3=restaurants, 4=clients

### 3. FoodSystem
Sistema completo de generación y recolección de comida.

```python
from game_systems import FoodSystem

food_system = FoodSystem(restaurant_positions)
food_system.spawn_food_item()
food_system.add_food_zone(x, y, width, height, "ron", give_time=2.0)

# En el game loop
food_system.update(player)
food_system.draw(screen)
```

**Características:**
- Spawn automático de comida en restaurantes
- Items recolectables con sprites visuales
- Zonas automáticas que otorgan comida
- Control de máximo de items en mapa
- Tipos de comida: ron, tabaco, miel, empanada, lomito, pizza, hamburguesa

### 4. OrderSystem
Sistema de generación y manejo de pedidos.

```python
from game_systems import OrderSystem

order_system = OrderSystem(client_house_positions)
order_system.generate_order()

# En el game loop
order_system.update(current_time_ms)
order_system.draw_orders_on_map(screen)
```

**Características:**
- Generación automática de pedidos
- Templates configurables de pedidos
- Sistema de tiempo límite y expiración
- Recompensas por completar pedidos
- Tracking de estadísticas completas

### 5. DeliverySystem
Sistema de zonas especiales y entregas.

```python
from game_systems import DeliverySystem

delivery_system = DeliverySystem(order_system, food_system)
delivery_system.create_client_delivery_zones(client_positions)
delivery_system.add_save_zone(x, y, width, height, save_callback)

# En el game loop
delivery_system.update(player)
delivery_system.draw(screen)
```

**Características:**
- Zonas de entrega con progreso visual
- Zonas de guardado automático
- Integración automática con otros sistemas
- Callbacks personalizables

## 🚀 Uso Rápido

### Integración Completa

```python
import pygame
from game_systems import *

# Configurar datos del mapa
mapper = CSVMapper("tu_mapa.csv", "ypane_unified")
restaurants = mapper.extract_restaurants()
clients = mapper.extract_client_houses()

# Crear todos los sistemas
inventory = InventoryManager()
food_system = FoodSystem(restaurants, max_food_items=10)
order_system = OrderSystem(clients, max_active_orders=5)
delivery_system = DeliverySystem(order_system, food_system)

# Configurar zonas de entrega
delivery_system.create_client_delivery_zones(clients)

# En tu game loop
def game_loop():
    current_time = pygame.time.get_ticks()
    
    # Actualizar sistemas
    food_system.update(player)
    order_system.update(current_time)
    delivery_system.update(player)
    
    # Dibujar todo
    food_system.draw(screen)
    order_system.draw_orders_on_map(screen)
    delivery_system.draw(screen)
```

### Uso Individual

Cada sistema puede usarse independientemente:

```python
# Solo inventario
from game_systems import InventoryManager
inventory = InventoryManager()

# Solo comida
from game_systems import FoodSystem
food_system = FoodSystem([(100, 100), (200, 200)])

# Solo pedidos
from game_systems import OrderSystem
order_system = OrderSystem([(150, 150, 1), (250, 250, 2)])
```

## 🔧 Configuración

### Configuraciones CSV Predefinidas

El sistema incluye configuraciones para diferentes tipos de mapas:

#### YPANE Unified (Recomendado)
```python
mapper = CSVMapper("mapa.csv", "ypane_unified")
# 963 = walkable
# 973 = collision  
# 894 = restaurants
# 822 = client houses
# 861 = superpowers
```

#### Simple
```python
mapper = CSVMapper("mapa.csv", "simple")
# 1 = walkable
# 0 = collision
# 2 = special zones
```

#### Alexis Format
```python
mapper = CSVMapper("mapa.csv", "alexis")
# 1 = walkable
# 2 = collision
# 3 = restaurants
# 4 = client houses
```

### Configuración Personalizada

```python
custom_config = {
    "walkable": [1, 5, 9],
    "collision": [0, 2],
    "restaurants": [3],
    "client_houses": [4],
    "superpowers": [7]
}

mapper = CSVMapper("mapa.csv", custom_config)
```

## 🎮 Ejemplo Completo

Ejecuta el ejemplo incluido para ver todos los sistemas funcionando:

```bash
python game_systems_example.py
```

**Controles del ejemplo:**
- WASD: Mover jugador
- SPACE: Mostrar estadísticas detalladas
- ESC: Salir

El ejemplo muestra:
- Spawn automático de comida
- Generación de pedidos
- Zonas de entrega activas
- Sistema de inventario funcionando
- Integración completa entre sistemas

## 📊 Debug y Estadísticas

Todos los sistemas incluyen información de debug:

```python
# Estadísticas de comida
print(food_system.get_food_count())
print(food_system.get_food_by_type())

# Estadísticas de pedidos
print(order_system.get_statistics())

# Estadísticas de entrega
print(delivery_system.get_statistics())

# Debug visual en pantalla
food_system.draw_debug_info(screen, font, (10, 100))
order_system.draw_debug_info(screen, font, (10, 200))
delivery_system.draw_debug_info(screen, font, (10, 300))
```

## 🔄 Migración

### Desde proyecto jahackathon
Los sistemas extraen la funcionalidad de:
- `restaurant_manager.py` → `FoodSystem` + `OrderSystem`
- `unified_ypane_map.py` → `CSVMapper`
- Inventarios dispersos → `InventoryManager`
- Zonas de entrega → `DeliverySystem`

### Hacia proyecto devAlexis-nuevo
Los sistemas son compatibles con diferentes estructuras de archivos y pueden adaptarse fácilmente.

## ⚙️ Dependencias

- pygame
- Python 3.6+

## 🚨 Notas Importantes

1. **Compatibilidad**: Los sistemas detectan automáticamente el tipo de player y se adaptan
2. **Performance**: Spawn y generación están optimizados para no sobrecargar el juego
3. **Extensibilidad**: Cada sistema puede extenderse con nuevas funcionalidades
4. **Error Handling**: Todos los sistemas incluyen manejo robusto de errores

## 📝 Contribuir

Para agregar nuevos sistemas o mejorar existentes:

1. Crear nuevo archivo en `game_systems/`
2. Seguir el patrón de los sistemas existentes
3. Incluir documentación y ejemplos
4. Actualizar `__init__.py` con las importaciones
5. Agregar tests si es necesario

¡Los sistemas están listos para usar en cualquier proyecto Pygame! 🎉