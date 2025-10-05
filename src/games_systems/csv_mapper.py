"""
Sistema de Mapeo de CSV Reutilizable
====================================

Extrae posiciones de zonas especiales desde archivos CSV de mapas.
Compatible con diferentes formatos y códigos de tiles.
"""

import csv
import os
from typing import List, Tuple, Dict, Optional, Any

class ZoneExtractor:
    """
    Extractor base para diferentes tipos de zonas desde CSV
    """
    
    def __init__(self, tile_size: int = 16):
        """
        Inicializa el extractor de zonas
        
        Args:
            tile_size: Tamaño de cada tile en píxeles
        """
        self.tile_size = tile_size
        self.map_matrix = []
        self.width = 0
        self.height = 0
    
    def load_csv(self, csv_path: str) -> bool:
        """
        Carga un archivo CSV y lo convierte en matriz
        
        Args:
            csv_path: Ruta al archivo CSV
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            if not os.path.exists(csv_path):
                print(f"❌ Archivo CSV no encontrado: {csv_path}")
                return False
            
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                self.map_matrix = []
                
                for row_idx, row in enumerate(reader):
                    map_row = []
                    for col_idx, cell in enumerate(row):
                        try:
                            cell_value = int(cell.strip())
                            map_row.append(cell_value)
                        except ValueError:
                            # Valor por defecto si no se puede convertir
                            map_row.append(0)
                    if map_row:  # Solo agregar filas no vacías
                        self.map_matrix.append(map_row)
                
                # Calcular dimensiones
                self.height = len(self.map_matrix)
                self.width = len(self.map_matrix[0]) if self.map_matrix else 0
                
                print(f"✅ CSV cargado: {self.width}x{self.height} tiles")
                return True
                
        except Exception as e:
            print(f"❌ Error cargando CSV {csv_path}: {e}")
            return False
    
    def extract_positions_by_code(self, tile_code: int, return_format: str = "pixels") -> List[Tuple[int, int]]:
        """
        Extrae todas las posiciones de un código de tile específico
        
        Args:
            tile_code: Código del tile a buscar
            return_format: "pixels" para coordenadas de píxeles, "tiles" para coordenadas de tile
            
        Returns:
            List[Tuple[int, int]]: Lista de posiciones (x, y)
        """
        positions = []
        
        for row_idx in range(self.height):
            for col_idx in range(self.width):
                if self.map_matrix[row_idx][col_idx] == tile_code:
                    if return_format == "pixels":
                        # Coordenadas de píxeles (centro del tile)
                        x = col_idx * self.tile_size + self.tile_size // 2
                        y = row_idx * self.tile_size + self.tile_size // 2
                    else:
                        # Coordenadas de tile
                        x = col_idx
                        y = row_idx
                    positions.append((x, y))
        
        return positions
    
    def extract_multiple_codes(self, tile_codes: List[int], return_format: str = "pixels") -> Dict[int, List[Tuple[int, int]]]:
        """
        Extrae posiciones para múltiples códigos de tile
        
        Args:
            tile_codes: Lista de códigos de tile a buscar
            return_format: "pixels" para coordenadas de píxeles, "tiles" para coordenadas de tile
            
        Returns:
            Dict[int, List[Tuple[int, int]]]: Diccionario {código: [(x, y), ...]}
        """
        result = {code: [] for code in tile_codes}
        
        for row_idx in range(self.height):
            for col_idx in range(self.width):
                cell_value = self.map_matrix[row_idx][col_idx]
                if cell_value in tile_codes:
                    if return_format == "pixels":
                        x = col_idx * self.tile_size + self.tile_size // 2
                        y = row_idx * self.tile_size + self.tile_size // 2
                    else:
                        x = col_idx
                        y = row_idx
                    result[cell_value].append((x, y))
        
        return result
    
    def get_tile_at_position(self, x: int, y: int, input_format: str = "pixels") -> Optional[int]:
        """
        Obtiene el código de tile en una posición específica
        
        Args:
            x, y: Coordenadas
            input_format: "pixels" si las coordenadas están en píxeles, "tiles" si están en tiles
            
        Returns:
            Optional[int]: Código del tile o None si está fuera de límites
        """
        if input_format == "pixels":
            tile_x = int(x // self.tile_size)
            tile_y = int(y // self.tile_size)
        else:
            tile_x = x
            tile_y = y
        
        if (tile_x < 0 or tile_x >= self.width or 
            tile_y < 0 or tile_y >= self.height):
            return None
        
        return self.map_matrix[tile_y][tile_x]
    
    def print_statistics(self):
        """Imprime estadísticas de los códigos de tile encontrados"""
        if not self.map_matrix:
            print("❌ No hay datos de mapa cargados")
            return
        
        tile_counts = {}
        total_tiles = self.width * self.height
        
        for row in self.map_matrix:
            for cell in row:
                tile_counts[cell] = tile_counts.get(cell, 0) + 1
        
        print(f"\n📊 Estadísticas del mapa ({total_tiles} tiles totales):")
        for tile_code, count in sorted(tile_counts.items()):
            percentage = (count / total_tiles) * 100
            print(f"   Código {tile_code}: {count} tiles ({percentage:.1f}%)")
        print()


class CSVMapper:
    """
    Mapeador principal que maneja diferentes tipos de configuraciones de CSV
    """
    
    # Configuraciones predefinidas para diferentes proyectos
    CONFIGURATIONS = {
        "ypane_unified": {
            "walkable": [963],
            "collision": [973], 
            "restaurant": [894],
            "client_house": [822],
            "safe_zone": [861]
        },
        "simple": {
            "walkable": [0, 1],
            "collision": [2],
            "restaurant": [3],
            "client_house": [4],
            "safe_zone": [5]
        },
        "alexis": {
            "walkable": [1],
            "collision": [0],
            "restaurant": [2], 
            "client_house": [3],
            "safe_zone": [4]
        }
    }
    
    def __init__(self, csv_path: str, configuration: str = "ypane_unified", tile_size: int = 16):
        """
        Inicializa el mapeador de CSV
        
        Args:
            csv_path: Ruta al archivo CSV
            configuration: Nombre de la configuración a usar
            tile_size: Tamaño de cada tile en píxeles
        """
        self.csv_path = csv_path
        self.configuration = configuration
        self.tile_size = tile_size
        self.extractor = ZoneExtractor(tile_size)
        
        # Cargar configuración
        if configuration in self.CONFIGURATIONS:
            self.config = self.CONFIGURATIONS[configuration]
        else:
            print(f"⚠️ Configuración {configuration} no encontrada, usando ypane_unified")
            self.config = self.CONFIGURATIONS["ypane_unified"]
        
        # Cargar mapa
        self.loaded = self.extractor.load_csv(csv_path)
        
        if self.loaded:
            print(f"✅ CSVMapper inicializado con configuración '{configuration}'")
            self.extractor.print_statistics()
    
    def get_restaurant_positions(self) -> List[Tuple[int, int]]:
        """Obtiene todas las posiciones de restaurantes"""
        if not self.loaded:
            return []
        
        positions = []
        for code in self.config["restaurant"]:
            positions.extend(self.extractor.extract_positions_by_code(code))
        
        print(f"🍴 Encontradas {len(positions)} posiciones de restaurante")
        return positions
    
    def get_client_house_positions(self) -> List[Tuple[int, int]]:
        """Obtiene todas las posiciones de casas de clientes"""
        if not self.loaded:
            return []
        
        positions = []
        for code in self.config["client_house"]:
            positions.extend(self.extractor.extract_positions_by_code(code))
        
        print(f"🏠 Encontradas {len(positions)} posiciones de casas de clientes")
        return positions
    
    def get_safe_zone_positions(self) -> List[Tuple[int, int]]:
        """Obtiene todas las posiciones de zonas seguras"""
        if not self.loaded:
            return []
        
        positions = []
        for code in self.config["safe_zone"]:
            positions.extend(self.extractor.extract_positions_by_code(code))
        
        print(f"🛡️ Encontradas {len(positions)} posiciones de zonas seguras")
        return positions
    
    def get_collision_positions(self) -> List[Tuple[int, int]]:
        """Obtiene todas las posiciones de colisión"""
        if not self.loaded:
            return []
        
        positions = []
        for code in self.config["collision"]:
            positions.extend(self.extractor.extract_positions_by_code(code))
        
        print(f"🚫 Encontradas {len(positions)} posiciones de colisión")
        return positions
    
    def is_position_walkable(self, x: int, y: int) -> bool:
        """
        Verifica si una posición es transitable
        
        Args:
            x, y: Coordenadas en píxeles
            
        Returns:
            bool: True si es transitable
        """
        if not self.loaded:
            return True
        
        tile_code = self.extractor.get_tile_at_position(x, y, "pixels")
        if tile_code is None:
            return False
        
        # Verificar si el código está en las listas de tiles transitables
        walkable_codes = (self.config["walkable"] + 
                         self.config["restaurant"] + 
                         self.config["client_house"] + 
                         self.config["safe_zone"])
        
        return tile_code in walkable_codes
    
    def get_all_special_zones(self) -> Dict[str, List[Tuple[int, int]]]:
        """
        Obtiene todas las zonas especiales en un diccionario
        
        Returns:
            Dict[str, List[Tuple[int, int]]]: Diccionario con todas las zonas
        """
        return {
            "restaurants": self.get_restaurant_positions(),
            "client_houses": self.get_client_house_positions(),
            "safe_zones": self.get_safe_zone_positions(),
            "collisions": self.get_collision_positions()
        }
    
    def create_collision_rects(self):
        """
        Crea rectángulos de pygame para todas las colisiones
        
        Returns:
            List[pygame.Rect]: Lista de rectángulos de colisión
        """
        import pygame
        
        collision_rects = []
        collision_positions = self.get_collision_positions()
        
        for x, y in collision_positions:
            # Convertir de centro del tile a esquina superior izquierda
            rect_x = x - self.tile_size // 2
            rect_y = y - self.tile_size // 2
            rect = pygame.Rect(rect_x, rect_y, self.tile_size, self.tile_size)
            collision_rects.append(rect)
        
        print(f"🔲 Creados {len(collision_rects)} rectángulos de colisión")
        return collision_rects


def create_csv_mapper(csv_path: str, project_type: str = "ypane_unified") -> CSVMapper:
    """
    Función de conveniencia para crear un CSVMapper
    
    Args:
        csv_path: Ruta al archivo CSV
        project_type: Tipo de proyecto ("ypane_unified", "simple", "alexis")
        
    Returns:
        CSVMapper: Instancia configurada del mapper
    """
    return CSVMapper(csv_path, project_type)


def detect_csv_format(csv_path: str) -> str:
    """
    Intenta detectar automáticamente el formato del CSV
    
    Args:
        csv_path: Ruta al archivo CSV
        
    Returns:
        str: Configuración detectada
    """
    extractor = ZoneExtractor()
    if not extractor.load_csv(csv_path):
        return "ypane_unified"
    
    # Contar códigos únicos
    unique_codes = set()
    for row in extractor.map_matrix:
        unique_codes.update(row)
    
    # Heurísticas simples para detectar formato
    if 963 in unique_codes and 973 in unique_codes:
        return "ypane_unified"
    elif max(unique_codes) <= 10:
        return "simple"
    else:
        return "alexis"