import pygame
import os
from settings import TILE_SIZE, ORIGINAL_TILE_SIZE

class SpriteManager:
    """Gestor de sprites para el juego"""
    
    def __init__(self):
        self.sprites = {}
        self.tilesets = {}
        self.load_all_sprites()
    
    def load_all_sprites(self):
        """Carga todos los sprites disponibles"""
        self.load_kenney_tiles()
        self.create_entity_sprites()
    
    def load_kenney_tiles(self):
        """Carga los tiles de Kenney"""
        tiles_path = os.path.join("src", "assets", "kenney_rpg-urban-pack", "Tiles")
        
        # Mapeo de archivos de tiles a nombres descriptivos
        tile_mapping = {
            # Terrenos básicos
            'grass': 'tile_0000.png',
            'stone_light': 'tile_0001.png',
            'stone_dark': 'tile_0002.png',
            'cobblestone': 'tile_0003.png',
            'dirt': 'tile_0030.png',
            'sand': 'tile_0031.png',
            
            # Carreteras y calles
            'road_straight_h': 'tile_0004.png',     # Carretera horizontal
            'road_straight_v': 'tile_0014.png',     # Carretera vertical
            'road_corner_tl': 'tile_0005.png',      # Esquina superior izquierda
            'road_corner_tr': 'tile_0006.png',      # Esquina superior derecha
            'road_corner_bl': 'tile_0015.png',      # Esquina inferior izquierda
            'road_corner_br': 'tile_0016.png',      # Esquina inferior derecha
            'road_intersection': 'tile_0024.png',   # Intersección
            'road_t_up': 'tile_0025.png',           # T hacia arriba
            'road_t_down': 'tile_0035.png',         # T hacia abajo
            'road_t_left': 'tile_0034.png',         # T hacia izquierda
            'road_t_right': 'tile_0026.png',        # T hacia derecha
            
            # Edificios
            'brick_wall': 'tile_0011.png',
            'tree_trunk': 'tile_0012.png',
            'roof_red': 'tile_0040.png',
            'roof_blue': 'tile_0041.png',
            'window': 'tile_0050.png',
            'door': 'tile_0051.png',
            
            # Agua
            'water': 'tile_0021.png',
            'water_deep': 'tile_0022.png',
            
            # Aceras
            'sidewalk': 'tile_0007.png',
            'sidewalk_corner': 'tile_0017.png'
        }
        
        for sprite_name, filename in tile_mapping.items():
            file_path = os.path.join(tiles_path, filename)
            self.load_sprite(sprite_name, file_path, scale=(TILE_SIZE, TILE_SIZE))
    
    def create_entity_sprites(self):
        """Crea sprites para entidades del juego"""
        # Sprite del jugador (verde con borde)
        player_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(player_surface, (0, 200, 0), (0, 0, 30, 30))
        pygame.draw.rect(player_surface, (0, 255, 0), (0, 0, 30, 30), 3)
        # Añadir una cara simple
        pygame.draw.circle(player_surface, (0, 255, 0), (15, 10), 3)
        pygame.draw.rect(player_surface, (0, 255, 0), (10, 20, 10, 5))
        self.sprites['player'] = player_surface
        
        # Sprite del enemigo (rojo con borde)
        enemy_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.rect(enemy_surface, (200, 0, 0), (0, 0, 25, 25))
        pygame.draw.rect(enemy_surface, (255, 0, 0), (0, 0, 25, 25), 2)
        # Añadir ojos malvados
        pygame.draw.circle(enemy_surface, (255, 255, 255), (8, 8), 2)
        pygame.draw.circle(enemy_surface, (255, 255, 255), (17, 8), 2)
        pygame.draw.circle(enemy_surface, (0, 0, 0), (8, 8), 1)
        pygame.draw.circle(enemy_surface, (0, 0, 0), (17, 8), 1)
        self.sprites['enemy'] = enemy_surface
    
    def load_sprite(self, name, path, scale=None):
        """Carga un sprite individual"""
        try:
            sprite = pygame.image.load(path).convert_alpha()
            if scale:
                sprite = pygame.transform.scale(sprite, scale)
            self.sprites[name] = sprite
            return sprite
        except (pygame.error, FileNotFoundError) as e:
            print(f"No se pudo cargar el sprite '{name}' desde '{path}': {e}")
            return self.create_fallback_sprite(name, scale)
    
    def create_fallback_sprite(self, name, scale=None):
        """Crea un sprite de respaldo si no se puede cargar el original"""
        size = scale or (TILE_SIZE, TILE_SIZE)
        surface = pygame.Surface(size)
        
        # Colores de respaldo basados en el nombre
        color_map = {
            # Terrenos
            'grass': (34, 139, 34),
            'stone_light': (160, 160, 160),
            'stone_dark': (96, 96, 96),
            'cobblestone': (112, 112, 112),
            'dirt': (139, 69, 19),
            'sand': (238, 203, 173),
            
            # Carreteras - gris oscuro
            'road_straight_h': (64, 64, 64),
            'road_straight_v': (64, 64, 64),
            'road_corner_tl': (64, 64, 64),
            'road_corner_tr': (64, 64, 64),
            'road_corner_bl': (64, 64, 64),
            'road_corner_br': (64, 64, 64),
            'road_intersection': (64, 64, 64),
            'road_t_up': (64, 64, 64),
            'road_t_down': (64, 64, 64),
            'road_t_left': (64, 64, 64),
            'road_t_right': (64, 64, 64),
            
            # Aceras
            'sidewalk': (192, 192, 192),
            'sidewalk_corner': (192, 192, 192),
            
            # Edificios
            'brick_wall': (139, 69, 19),
            'tree_trunk': (101, 67, 33),
            'roof_red': (178, 34, 34),
            'roof_blue': (70, 130, 180),
            'window': (135, 206, 235),
            'door': (160, 82, 45),
            
            # Agua
            'water': (30, 144, 255),
            'water_deep': (0, 100, 200)
        }
        
        color = color_map.get(name, (255, 0, 255))  # Magenta como color de error
        surface.fill(color)
        
        # Añadir patrones específicos para distinguir mejor
        if name in ['cobblestone', 'brick_wall']:
            # Patrón de ladrillos
            for i in range(0, size[0], 8):
                pygame.draw.line(surface, (0, 0, 0), (i, 0), (i, size[1]), 1)
            for i in range(0, size[1], 8):
                pygame.draw.line(surface, (0, 0, 0), (0, i), (size[0], i), 1)
        
        elif 'road' in name:
            # Patrón de carreteras con líneas amarillas
            if 'straight_h' in name:
                # Línea amarilla horizontal en el centro
                pygame.draw.line(surface, (255, 255, 0), (0, size[1]//2), (size[0], size[1]//2), 2)
            elif 'straight_v' in name:
                # Línea amarilla vertical en el centro
                pygame.draw.line(surface, (255, 255, 0), (size[0]//2, 0), (size[0]//2, size[1]), 2)
            elif 'intersection' in name:
                # Cruz amarilla para intersección
                pygame.draw.line(surface, (255, 255, 0), (0, size[1]//2), (size[0], size[1]//2), 2)
                pygame.draw.line(surface, (255, 255, 0), (size[0]//2, 0), (size[0]//2, size[1]), 2)
        
        elif name == 'sidewalk':
            # Patrón de baldosas para aceras
            for i in range(0, size[0], size[0]//4):
                for j in range(0, size[1], size[1]//4):
                    pygame.draw.rect(surface, (160, 160, 160), (i, j, size[0]//4-1, size[1]//4-1), 1)
        
        self.sprites[name] = surface
        return surface
    
    def get_sprite(self, name):
        """Obtiene un sprite por nombre"""
        return self.sprites.get(name)
    
    def get_all_sprites(self):
        """Obtiene todos los sprites cargados"""
        return self.sprites.copy()

# Instancia global del gestor de sprites
sprite_manager = SpriteManager()