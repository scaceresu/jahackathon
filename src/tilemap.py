import pygame
import os
from settings import WIDTH, HEIGHT, TILE_SIZE
from sprite_manager import sprite_manager
from jeep import Jeep

class TileMap:
    def __init__(self):
        self.tile_size = TILE_SIZE
        self.map_data = []
        self.jeeps = []  # Lista de jeeps en el mapa
        self.create_urban_map_with_roads()
    
    def create_urban_map_with_roads(self):
        """Crea un mapa urbano con carreteras y jeeps como obstáculos"""
        # Calculamos el número de tiles que caben en pantalla
        cols = WIDTH // self.tile_size
        rows = HEIGHT // self.tile_size
        
        # Crear mapa base con césped
        self.map_data = [['grass' for _ in range(cols)] for _ in range(rows)]
        
        # Bordes del mapa con muros
        for row in range(rows):
            for col in range(cols):
                if row == 0 or row == rows-1 or col == 0 or col == cols-1:
                    self.map_data[row][col] = 'brick_wall'
        
        # Carretera principal horizontal en el centro
        road_row = rows // 2
        for col in range(1, cols-1):
            self.map_data[road_row][col] = 'road_straight_h'
        
        # Carretera vertical que cruza la horizontal
        road_col = cols // 2
        for row in range(1, rows-1):
            if row != road_row:  # No sobrescribir la intersección
                self.map_data[row][road_col] = 'road_straight_v'
        
        # Intersección en el centro
        self.map_data[road_row][road_col] = 'road_intersection'
        
        # Carretera secundaria horizontal en la parte superior
        secondary_road_row = 3
        for col in range(1, cols//2):
            self.map_data[secondary_road_row][col] = 'road_straight_h'
        
        # Conectar carretera secundaria con la principal
        for row in range(secondary_road_row + 1, road_row):
            self.map_data[row][cols//2] = 'road_straight_v'
        
        # T-junction para conectar carretera secundaria
        self.map_data[secondary_road_row][cols//2] = 'road_t_down'
        
        # Carretera en L en la esquina inferior derecha
        corner_start_row = rows - 4
        corner_start_col = cols - 8
        
        # Horizontal de la L
        for col in range(corner_start_col, cols-1):
            self.map_data[corner_start_row][col] = 'road_straight_h'
        
        # Vertical de la L
        for row in range(corner_start_row + 1, rows-1):
            self.map_data[row][corner_start_col] = 'road_straight_v'
        
        # Esquina de la L
        self.map_data[corner_start_row][corner_start_col] = 'road_corner_bl'
        
        # Aceras junto a las carreteras principales
        self.add_sidewalks(road_row, road_col, rows, cols)
        
        # Edificios y estructuras
        self.add_buildings(rows, cols)
        
        # Añadir algunos árboles en zonas verdes
        self.add_trees(rows, cols)
        
        # Colocar jeeps como obstáculos de daño
        self.place_jeeps()
    
    def add_sidewalks(self, road_row, road_col, rows, cols):
        """Añade aceras junto a las carreteras"""
        # Aceras horizontales
        for col in range(1, cols-1):
            if road_row - 1 > 0:
                self.map_data[road_row - 1][col] = 'sidewalk'
            if road_row + 1 < rows-1:
                self.map_data[road_row + 1][col] = 'sidewalk'
        
        # Aceras verticales
        for row in range(1, rows-1):
            if road_col - 1 > 0 and self.map_data[row][road_col - 1] == 'grass':
                self.map_data[row][road_col - 1] = 'sidewalk'
            if road_col + 1 < cols-1 and self.map_data[row][road_col + 1] == 'grass':
                self.map_data[row][road_col + 1] = 'sidewalk'
    
    def add_buildings(self, rows, cols):
        """Añade edificios al mapa"""
        # Edificio en esquina superior izquierda
        for row in range(2, 6):
            for col in range(2, 7):
                if row == 2 or row == 5:  # Techo
                    self.map_data[row][col] = 'roof_red'
                elif col == 2 or col == 6:  # Paredes
                    self.map_data[row][col] = 'brick_wall'
                elif row == 5 and col == 4:  # Puerta
                    self.map_data[row][col] = 'door'
                elif (row == 3 and col in [3, 5]) or (row == 4 and col in [3, 5]):  # Ventanas
                    self.map_data[row][col] = 'window'
                else:  # Interior
                    self.map_data[row][col] = 'stone_light'
        
        # Edificio en esquina superior derecha
        for row in range(2, 5):
            for col in range(cols-6, cols-1):
                if row == 2 or row == 4:  # Techo
                    self.map_data[row][col] = 'roof_blue'
                elif col == cols-6 or col == cols-2:  # Paredes
                    self.map_data[row][col] = 'brick_wall'
                else:  # Interior
                    self.map_data[row][col] = 'stone_dark'
    
    def add_trees(self, rows, cols):
        """Añade árboles decorativos"""
        tree_positions = [
            (7, 3), (7, 5), (7, 7),  # Fila de árboles
            (rows-3, 3), (rows-3, 5), (rows-3, 7),  # Otra fila
            (3, cols-3), (5, cols-3), (7, cols-3),  # Columna de árboles
        ]
        
        for row, col in tree_positions:
            if (0 < row < rows-1 and 0 < col < cols-1 and 
                self.map_data[row][col] == 'grass'):
                self.map_data[row][col] = 'tree_trunk'
    
    def place_jeeps(self):
        """Coloca jeeps como obstáculos de daño en el mapa"""
        # Posiciones estratégicas para los jeeps
        jeep_positions = [
            (TILE_SIZE * 8, TILE_SIZE * 6),    # Zona media-izquierda
            (TILE_SIZE * 15, TILE_SIZE * 4),   # Zona superior-derecha
            (TILE_SIZE * 12, TILE_SIZE * 12),  # Zona inferior-centro
            (TILE_SIZE * 5, TILE_SIZE * 10),   # Zona inferior-izquierda
        ]
        
        self.jeeps = []
        for x, y in jeep_positions:
            # Verificar que la posición esté dentro del mapa y no en carreteras
            if (x + TILE_SIZE * 2 < WIDTH - TILE_SIZE and 
                y + TILE_SIZE < HEIGHT - TILE_SIZE):
                jeep = Jeep(x, y)
                self.jeeps.append(jeep)
    
    def draw(self, screen):
        """Dibuja el mapa completo en pantalla"""
        # Dibujar tiles del mapa
        for row_idx, row in enumerate(self.map_data):
            for col_idx, tile_type in enumerate(row):
                sprite = sprite_manager.get_sprite(tile_type)
                if sprite:
                    x = col_idx * self.tile_size
                    y = row_idx * self.tile_size
                    screen.blit(sprite, (x, y))
                else:
                    # Fallback: dibujar un rectángulo de color si no hay sprite
                    x = col_idx * self.tile_size
                    y = row_idx * self.tile_size
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    pygame.draw.rect(screen, (255, 0, 255), rect)  # Magenta como error
        
        # Dibujar jeeps encima del mapa
        for jeep in self.jeeps:
            jeep.draw(screen)
    
    def get_tile_at_position(self, x, y):
        """Obtiene el tipo de tile en una posición específica"""
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)
        
        if 0 <= row < len(self.map_data) and 0 <= col < len(self.map_data[row]):
            return self.map_data[row][col]
        return None
    
    def is_walkable(self, x, y):
        """Verifica si una posición es caminable"""
        tile_type = self.get_tile_at_position(x, y)
        # Define qué tiles no son caminables
        non_walkable = [
            'brick_wall', 'tree_trunk', 'water', 'water_deep', 
            'roof_red', 'roof_blue', 'window'
        ]
        
        # Verificar colisión con jeeps
        for jeep in self.jeeps:
            if jeep.check_collision(pygame.Rect(x, y, 1, 1)):
                return False
        
        return tile_type not in non_walkable
    
    def get_tile_properties(self, tile_type):
        """Obtiene las propiedades de un tipo de tile"""
        properties = {
            # Terrenos básicos
            'grass': {'walkable': True, 'speed_modifier': 1.0},
            'stone_light': {'walkable': True, 'speed_modifier': 1.0},
            'stone_dark': {'walkable': True, 'speed_modifier': 1.0},
            'cobblestone': {'walkable': True, 'speed_modifier': 1.1},
            'dirt': {'walkable': True, 'speed_modifier': 0.8},
            'sand': {'walkable': True, 'speed_modifier': 0.7},
            'door': {'walkable': True, 'speed_modifier': 1.0},
            
            # Carreteras - velocidad alta
            'road_straight_h': {'walkable': True, 'speed_modifier': 1.3},
            'road_straight_v': {'walkable': True, 'speed_modifier': 1.3},
            'road_corner_tl': {'walkable': True, 'speed_modifier': 1.2},
            'road_corner_tr': {'walkable': True, 'speed_modifier': 1.2},
            'road_corner_bl': {'walkable': True, 'speed_modifier': 1.2},
            'road_corner_br': {'walkable': True, 'speed_modifier': 1.2},
            'road_intersection': {'walkable': True, 'speed_modifier': 1.2},
            'road_t_up': {'walkable': True, 'speed_modifier': 1.2},
            'road_t_down': {'walkable': True, 'speed_modifier': 1.2},
            'road_t_left': {'walkable': True, 'speed_modifier': 1.2},
            'road_t_right': {'walkable': True, 'speed_modifier': 1.2},
            
            # Aceras
            'sidewalk': {'walkable': True, 'speed_modifier': 1.1},
            'sidewalk_corner': {'walkable': True, 'speed_modifier': 1.1},
            
            # No caminables
            'brick_wall': {'walkable': False, 'speed_modifier': 0.0},
            'tree_trunk': {'walkable': False, 'speed_modifier': 0.0},
            'water': {'walkable': False, 'speed_modifier': 0.0},
            'water_deep': {'walkable': False, 'speed_modifier': 0.0},
            'roof_red': {'walkable': False, 'speed_modifier': 0.0},
            'roof_blue': {'walkable': False, 'speed_modifier': 0.0},
            'window': {'walkable': False, 'speed_modifier': 0.0}
        }
        return properties.get(tile_type, {'walkable': True, 'speed_modifier': 1.0})
    
    def check_jeep_collision(self, rect):
        """Verifica colisión con cualquier jeep en el mapa"""
        for jeep in self.jeeps:
            if jeep.check_collision(rect):
                return jeep
        return None
    
    def get_jeeps(self):
        """Devuelve la lista de jeeps"""
        return self.jeeps
    
    def find_safe_spawn_position(self, entity_width=30, entity_height=30, for_enemy=False):
        """Encuentra una posición segura y caminable para spawnear el jugador o enemigo"""
        if for_enemy:
            # Posiciones especiales para el enemigo con más espacio libre
            safe_positions = [
                # Áreas con más espacio en carreteras
                (TILE_SIZE * 6, TILE_SIZE * 9),           # Carretera principal horizontal
                (TILE_SIZE * 10, TILE_SIZE * 9),          # Carretera principal horizontal  
                (TILE_SIZE * 12, TILE_SIZE * 5),          # Carretera vertical
                (TILE_SIZE * 12, TILE_SIZE * 13),         # Carretera vertical inferior
                # Esquinas con espacio
                (TILE_SIZE * 3, TILE_SIZE * 3),           # Superior izquierda con espacio
                (WIDTH - TILE_SIZE * 5, TILE_SIZE * 3),   # Superior derecha con espacio
                (TILE_SIZE * 3, HEIGHT - TILE_SIZE * 5),  # Inferior izquierda con espacio
            ]
        else:
            # Posiciones para el jugador (originales)
            safe_positions = [
                (TILE_SIZE * 2, TILE_SIZE * 2),           # Superior izquierda
                (WIDTH - TILE_SIZE * 4, TILE_SIZE * 2),    # Superior derecha  
                (TILE_SIZE * 2, HEIGHT - TILE_SIZE * 4),   # Inferior izquierda
                (WIDTH - TILE_SIZE * 4, HEIGHT - TILE_SIZE * 4), # Inferior derecha
                (TILE_SIZE * 3, TILE_SIZE * 7),           # Lado izquierdo
                (WIDTH - TILE_SIZE * 5, TILE_SIZE * 7),    # Lado derecho
            ]
        
        for x, y in safe_positions:
            # Crear rect temporal para verificar
            temp_rect = pygame.Rect(x, y, entity_width, entity_height)
            
            # Verificar que la posición esté dentro de límites
            if (x >= 0 and y >= 0 and 
                x + entity_width <= WIDTH and 
                y + entity_height <= HEIGHT):
                
                # Verificar que sea caminable
                if self._is_rect_walkable(temp_rect):
                    # Verificar que no esté en un jeep
                    if not self.check_jeep_collision(temp_rect):
                        # Para enemigos, verificar que tenga espacio de movimiento
                        if for_enemy and not self._has_movement_space(x, y, entity_width, entity_height):
                            continue
                        return (x, y)
        
        # Si no encuentra posición segura, usar una por defecto
        if for_enemy:
            return (TILE_SIZE * 6, TILE_SIZE * 9)  # En carretera principal
        else:
            return (TILE_SIZE * 2, TILE_SIZE * 2)
    
    def _has_movement_space(self, x, y, width, height, min_space=3):
        """Verifica que haya suficiente espacio libre alrededor para que el enemigo se mueva"""
        # Verificar un área más grande alrededor de la entidad
        extended_area = pygame.Rect(
            x - TILE_SIZE * min_space, 
            y - TILE_SIZE * min_space,
            width + TILE_SIZE * min_space * 2,
            height + TILE_SIZE * min_space * 2
        )
        
        # Contar tiles caminables en el área extendida
        walkable_count = 0
        total_count = 0
        
        for check_y in range(int(extended_area.y), int(extended_area.y + extended_area.height), TILE_SIZE):
            for check_x in range(int(extended_area.x), int(extended_area.x + extended_area.width), TILE_SIZE):
                if (check_x >= 0 and check_y >= 0 and 
                    check_x < WIDTH and check_y < HEIGHT):
                    total_count += 1
                    if self.is_walkable(check_x, check_y):
                        walkable_count += 1
        
        # Debe haber al menos 60% de espacio caminable
        if total_count > 0:
            walkable_ratio = walkable_count / total_count
            return walkable_ratio >= 0.6
        
        return False
    
    def _is_rect_walkable(self, rect):
        """Verifica si todo el rectángulo está en una zona caminable"""
        # Verificar las cuatro esquinas del rectángulo
        corners = [
            (rect.x, rect.y),                                    # Superior izquierda
            (rect.x + rect.width - 1, rect.y),                   # Superior derecha
            (rect.x, rect.y + rect.height - 1),                  # Inferior izquierda
            (rect.x + rect.width - 1, rect.y + rect.height - 1)  # Inferior derecha
        ]
        
        for corner_x, corner_y in corners:
            if not self.is_walkable(corner_x, corner_y):
                return False
        return True