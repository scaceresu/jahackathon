# src/tilemap.py
import csv
import os
import pygame
from typing import List, Tuple, Dict, Optional

TILE = 16  # px por tile
MAPS_DIR = os.path.join(os.path.dirname(__file__), "maps")  # Carpeta donde están los mapas

# Configuración de códigos de tiles según el sistema Alexis
TILE_CONFIG = {
    "walkable": [1],
    "collision": [0],
    "restaurant": [2], 
    "client_house": [3],
    "safe_zone": [4]
}

def cargar_mapa_csv(nombre_csv):
    """
    Carga mapa CSV y devuelve (mapa, width, height).
    - nombre_csv puede ser nombre relativo dentro de src/maps o ruta absoluta.
    - Cada fila debe tener el mismo número de columnas.
    """
    # resolver ruta absoluta o relativa
    path = nombre_csv if os.path.isabs(nombre_csv) else os.path.join(MAPS_DIR, nombre_csv)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Mapa no encontrado: {path}")

    mapa = []
    with open(path, newline='') as f:
        # detectar separador básico: preferimos coma, pero toleramos ;
        sample = f.read(1024)
        sep = ',' if sample.count(',') >= sample.count(';') else ';'
        f.seek(0) # volver al inicio
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            if not row:
                continue
            # filtrar celdas vacías y convertir a int, fallar si conversion no es posible
            fila = [] # lista temporal de la fila
            for x in row: # limpiar espacios y filtrar vacíos
                s = x.strip() # limpiar espacios
                if s == '': 
                    continue # ignorar celdas vacías
                fila.append(int(s)) # convertir a int (fallará si no es posible)
            if fila: # agregar fila no vacía
                mapa.append(fila) # agregar fila no vacía
                #imprime en nueva linea la fila leída
                # print(fila)

    if not mapa:
        raise ValueError(f"Mapa vacío o inválido: {path}")

    # comprobar consistencia de ancho
    width = len(mapa[0])
    for i, fila in enumerate(mapa):
        if len(fila) != width:
            raise ValueError(f"Fila {i} del mapa tiene longitud {len(fila)} (esperado {width})")
    print(mapa)
    height = len(mapa)
    return mapa, width, height

def pixel_a_tile(px, py):
    """Convierte coordenadas en píxeles a coordenadas de tile (tx, ty)."""
    return int(px) // TILE, int(py) // TILE

def rect_a_tiles(rect: pygame.Rect):
    """Devuelve lista de (tx,ty) de todos los tiles que cubre rect (inclusive)."""
    tx1, ty1 = pixel_a_tile(rect.left, rect.top)
    tx2, ty2 = pixel_a_tile(rect.right - 1, rect.bottom - 1)
    return [(tx, ty) for ty in range(ty1, ty2 + 1) for tx in range(tx1, tx2 + 1)]

def es_tile_transitable(mapa, tx, ty):
    """True si el tile (tx,ty) está dentro del mapa y su valor es 1 (camino transitable). Los valores 0 representan obstáculos."""
    if ty < 0 or ty >= len(mapa) or tx < 0 or tx >= len(mapa[0]):
        return False
    return mapa[ty][tx] == 1

def generar_muros(mapa):
    """
    Agrupa tiles == 0 (obstáculos/muros) en rects horizontales por fila para reducir checks de colisión.
    Devuelve lista de pygame.Rect en coordenadas en píxeles.
    """
    muros = []
    h = len(mapa) # alto del mapa en tiles
    w = len(mapa[0]) if h else 0 # ancho del mapa en tiles
    # recorrer filas
    for y in range(h):
        for x in range(w):
            if mapa[y][x] == 0: # Los valores 0 representan obstáculos/muros
                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE) # en píxeles
                muros.append(rect)
                
    return muros


def extraer_posiciones_por_codigo(mapa, tile_code: int) -> List[Tuple[int, int]]:
    """
    Extrae todas las posiciones (en píxeles) donde aparece un código de tile específico.
    
    Args:
        mapa: Matriz del mapa cargada
        tile_code: Código del tile a buscar
        
    Returns:
        List[Tuple[int, int]]: Lista de posiciones (x, y) en píxeles (centro del tile)
    """
    positions = []
    h = len(mapa)
    w = len(mapa[0]) if h else 0
    
    for row_idx in range(h):
        for col_idx in range(w):
            if mapa[row_idx][col_idx] == tile_code:
                # Coordenadas del centro del tile en píxeles
                x = col_idx * TILE + TILE // 2
                y = row_idx * TILE + TILE // 2
                positions.append((x, y))
    
    return positions


def obtener_posiciones_restaurantes(mapa) -> List[Tuple[int, int]]:
    """Obtiene todas las posiciones de restaurantes (código 2)"""
    positions = []
    for code in TILE_CONFIG["restaurant"]:
        positions.extend(extraer_posiciones_por_codigo(mapa, code))
    
    print(f"🍴 Encontradas {len(positions)} posiciones de restaurante")
    return positions


def obtener_posiciones_casas_clientes(mapa) -> List[Tuple[int, int]]:
    """Obtiene todas las posiciones de casas de clientes (código 3)"""
    positions = []
    for code in TILE_CONFIG["client_house"]:
        positions.extend(extraer_posiciones_por_codigo(mapa, code))
    
    print(f"🏠 Encontradas {len(positions)} posiciones de casas de clientes")
    return positions


def obtener_posiciones_zonas_seguras(mapa) -> List[Tuple[int, int]]:
    """Obtiene todas las posiciones de zonas seguras (código 4)"""
    positions = []
    for code in TILE_CONFIG["safe_zone"]:
        positions.extend(extraer_posiciones_por_codigo(mapa, code))
    
    print(f"🛡️ Encontradas {len(positions)} posiciones de zonas seguras")
    return positions


def obtener_posiciones_colision(mapa) -> List[Tuple[int, int]]:
    """Obtiene todas las posiciones de colisión (código 0)"""
    positions = []
    for code in TILE_CONFIG["collision"]:
        positions.extend(extraer_posiciones_por_codigo(mapa, code))
    
    print(f"🚫 Encontradas {len(positions)} posiciones de colisión")
    return positions


def generar_objetos_desde_mapa(mapa) -> Dict[str, List[Tuple[int, int]]]:
    """
    Genera todas las posiciones de objetos especiales desde el mapa.
    
    Args:
        mapa: Matriz del mapa cargada
        
    Returns:
        Dict con las posiciones de todos los tipos de objetos
    """
    objetos = {
        "restaurants": obtener_posiciones_restaurantes(mapa),
        "client_houses": obtener_posiciones_casas_clientes(mapa),
        "safe_zones": obtener_posiciones_zonas_seguras(mapa),
        "collisions": obtener_posiciones_colision(mapa)
    }
    
    print(f"\n✅ Objetos generados desde mapa:")
    for tipo, posiciones in objetos.items():
        print(f"   - {tipo}: {len(posiciones)} objetos")
    
    return objetos


def es_posicion_transitable(mapa, x: int, y: int) -> bool:
    """
    Verifica si una posición en píxeles es transitable
    
    Args:
        mapa: Matriz del mapa
        x, y: Coordenadas en píxeles
        
    Returns:
        bool: True si es transitable
    """
    tile_x = int(x // TILE)
    tile_y = int(y // TILE)
    
    # Verificar límites
    if (tile_x < 0 or tile_x >= len(mapa[0]) or 
        tile_y < 0 or tile_y >= len(mapa)):
        return False
    
    tile_code = mapa[tile_y][tile_x]
    
    # Verificar si el código está en las listas de tiles transitables
    walkable_codes = (TILE_CONFIG["walkable"] + 
                     TILE_CONFIG["restaurant"] + 
                     TILE_CONFIG["client_house"] + 
                     TILE_CONFIG["safe_zone"])
    
    return tile_code in walkable_codes


def crear_rects_colision(mapa) -> List[pygame.Rect]:
    """
    Crea rectángulos de pygame para todas las colisiones
    
    Args:
        mapa: Matriz del mapa
        
    Returns:
        List[pygame.Rect]: Lista de rectángulos de colisión
    """
    collision_rects = []
    collision_positions = obtener_posiciones_colision(mapa)
    
    for x, y in collision_positions:
        # Convertir de centro del tile a esquina superior izquierda
        rect_x = x - TILE // 2
        rect_y = y - TILE // 2
        rect = pygame.Rect(rect_x, rect_y, TILE, TILE)
        collision_rects.append(rect)
    
    print(f"🔲 Creados {len(collision_rects)} rectángulos de colisión")
    return collision_rects
