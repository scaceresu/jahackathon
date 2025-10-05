# src/tilemap.py
import csv
import os
import pygame

TILE = 16  # px por tile
MAPS_DIR = os.path.join(os.path.dirname(__file__), "maps")  # Carpeta donde están los mapas

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
