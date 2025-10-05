#!/usr/bin/env python3
"""
Vista Previa del Mapa (Modo Texto)
==================================

Este script muestra una representación en texto del mapa creado,
útil para verificar la estructura sin necesidad de pygame.
"""

import sys
import os

# Añadir el directorio src al path
sys.path.append('src')

def preview_map():
    """Muestra una vista previa del mapa en modo texto"""
    
    print("=== VISTA PREVIA DEL MAPA ===")
    print()
    
    # Simulamos la creación del mapa sin pygame
    width, height = 800, 600
    tile_size = 32
    cols = width // tile_size
    rows = height // tile_size
    
    print(f"Dimensiones del mapa: {cols}x{rows} tiles ({width}x{height} píxeles)")
    print(f"Tamaño de cada tile: {tile_size}x{tile_size} píxeles")
    print()
    
    # Creamos el mapa con la misma lógica que TileMap
    map_data = []
    for row in range(rows):
        map_row = []
        for col in range(cols):
            # Bordes del mapa con muros de ladrillo
            if row == 0 or row == rows-1 or col == 0 or col == cols-1:
                map_row.append('🧱')  # brick_wall
            
            # Casa en la esquina superior izquierda
            elif 2 <= row <= 5 and 2 <= col <= 6:
                if row == 2 or row == 5:  # Techo
                    map_row.append('🏠')  # roof_red
                elif col == 2 or col == 6:  # Paredes
                    map_row.append('🧱')  # brick_wall
                elif row == 5 and col == 4:  # Puerta
                    map_row.append('🚪')  # door
                elif (row == 3 and col in [3, 5]) or (row == 4 and col in [3, 5]):  # Ventanas
                    map_row.append('🪟')  # window
                else:  # Interior
                    map_row.append('⬜')  # stone_light
            
            # Lago en el centro-derecha
            elif col > cols * 0.6 and row > rows * 0.3 and row < rows * 0.7:
                # Lago con diferentes profundidades
                center_col = cols * 0.75
                center_row = rows * 0.5
                distance = ((col - center_col) ** 2 + (row - center_row) ** 2) ** 0.5
                if distance < 3:
                    map_row.append('🌊')  # water_deep
                else:
                    map_row.append('💧')  # water
            
            # Bosque de árboles en la parte inferior
            elif row > rows * 0.75:
                if (row + col) % 3 == 0:  # Patrón para distribuir árboles
                    map_row.append('🌳')  # tree_trunk
                else:
                    map_row.append('🌱')  # grass
            
            # Camino de piedra horizontal
            elif row == rows // 2:
                map_row.append('🪨')  # cobblestone
            # Camino de piedra vertical
            elif col == cols // 2:
                map_row.append('⬜')  # stone_light
            
            # Zona desértica en la esquina inferior derecha
            elif row > rows * 0.6 and col > cols * 0.8:
                map_row.append('🏜️')  # sand
            
            # Zona de tierra cultivada
            elif rows * 0.7 <= row < rows * 0.75 and cols * 0.1 <= col < cols * 0.4:
                map_row.append('🟫')  # dirt
            
            # Algunos árboles dispersos en zona de césped
            elif (row == 3 and col in [10, 15, 20]) or (row == 8 and col in [8, 18]) or (row == 12 and col in [5, 12, 22]):
                map_row.append('🌳')  # tree_trunk
            
            # El resto es césped
            else:
                map_row.append('🌱')  # grass
                
        map_data.append(map_row)
    
    # Mostrar el mapa
    print("MAPA (Vista general):")
    print("=" * (cols + 2))
    for row in map_data:
        print("|" + "".join(row) + "|")
    print("=" * (cols + 2))
    print()
    
    # Leyenda
    print("LEYENDA:")
    legend = {
        '🌱': 'Césped (caminable, velocidad normal)',
        '⬜': 'Piedra (caminable, velocidad +10%)',
        '🪨': 'Adoquines (caminable, velocidad +10%)',
        '🧱': 'Muro (NO caminable)',
        '🌳': 'Árbol (NO caminable)',
        '💧': 'Agua (NO caminable)',
        '🌊': 'Agua profunda (NO caminable)',
        '🏠': 'Techo (NO caminable)',
        '🚪': 'Puerta (caminable)',
        '🪟': 'Ventana (NO caminable)',
        '🏜️': 'Arena (caminable, velocidad -30%)',
        '🟫': 'Tierra (caminable, velocidad -20%)'
    }
    
    for emoji, description in legend.items():
        print(f"  {emoji} = {description}")
    
    print()
    print("CARACTERÍSTICAS DEL MAPA:")
    print("- Casa completa con techo, paredes, ventanas y puerta")
    print("- Lago con centro profundo y orillas normales")
    print("- Bosque denso en la parte inferior")
    print("- Caminos de piedra horizontales y verticales")
    print("- Zona desértica en esquina inferior derecha")
    print("- Área de cultivo en la zona media-izquierda")
    print("- Árboles dispersos en zonas de césped")
    print("- Perímetro completamente amurallado")
    
    # Estadísticas
    total_tiles = rows * cols
    tile_counts = {}
    for row in map_data:
        for tile in row:
            tile_counts[tile] = tile_counts.get(tile, 0) + 1
    
    print(f"\nESTADÍSTICAS:")
    print(f"Total de tiles: {total_tiles}")
    for tile, count in sorted(tile_counts.items()):
        percentage = (count / total_tiles) * 100
        print(f"  {tile}: {count} tiles ({percentage:.1f}%)")

if __name__ == "__main__":
    preview_map()