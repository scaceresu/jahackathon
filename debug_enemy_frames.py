import pygame
import os
from src.assets import cargar_frames_spritesheet

pygame.init()
# Inicializar un modo de video mínimo
pygame.display.set_mode((1, 1))

# Parámetros del enemy
H_FRAME_W, H_FRAME_H = 64, 32   # horizontales (5x64x32)
V_FRAME_W, V_FRAME_H = 32, 65   # verticales  (5x32x65)
FRAMES_COUNT = 5

base = "assets/imagenes/enemy"

def debug_load_and_scale(path, frame_w, frame_h):
    print(f"\n=== Debugging {path} ===")
    print(f"Existe archivo: {os.path.isfile(path)}")
    
    frames = []
    if os.path.isfile(path):
        try:
            frames = cargar_frames_spritesheet(path, frame_w, frame_h, FRAMES_COUNT)
            print(f"Frames cargados: {len(frames)}")
            if frames:
                print(f"Tamaño primer frame: {frames[0].get_size()}")
        except Exception as e:
            print(f"Error cargando frames: {e}")
    else:
        print("Archivo no existe")
    
    out = []
    for i, f in enumerate(frames):
        surf = f.convert_alpha()
        print(f"Frame {i} tamaño antes de escalar: {surf.get_size()}")
        if surf.get_size() != (24, 24):
            surf = pygame.transform.scale(surf, (24, 24))
            print(f"Frame {i} escalado a: {surf.get_size()}")
        out.append(surf)
    
    print(f"Frames finales: {len(out)}")
    return out

# Probar cada animación
animations = [
    ("idle.png", V_FRAME_W, V_FRAME_H),
    ("walk_right.png", H_FRAME_W, H_FRAME_H),
    ("walk_left.png", H_FRAME_W, H_FRAME_H),
    ("walk_up.png", V_FRAME_W, V_FRAME_H),
    ("walk_down.png", V_FRAME_W, V_FRAME_H),
]

for filename, frame_w, frame_h in animations:
    path = os.path.join(base, filename)
    frames = debug_load_and_scale(path, frame_w, frame_h)
    print(f"¿Lista vacía? {not frames}")
    print(f"Número de frames resultantes: {len(frames)}")
    print("---")