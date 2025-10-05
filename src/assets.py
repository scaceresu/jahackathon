import os, pygame

def cargar_frames_dir(folder, colorkey=None):
    frames = []
    if not os.path.isdir(folder):
        return frames
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith((".png",".jpg")))
    for f in files:
        surf = pygame.image.load(os.path.join(folder, f)).convert_alpha()
        if colorkey is not None:
            surf.set_colorkey(colorkey)
        frames.append(surf)
    return frames

def cargar_frames_spritesheet(path, frame_w=44, frame_h=44, frames_count=4, scale_to=None):
    """
    Corta un spritesheet horizontal en frames_count frames de frame_w x frame_h.
    - path: ruta al png (ej. "assets/imagenes/player/walk_down.png").
    - frame_w, frame_h: tamaño de cada frame en el PNG (44,44).
    - frames_count: número de frames en la fila (4).
    - scale_to: (w,h) si querés escalar los frames resultantes (None = mantener tamaño original).
    Devuelve lista de Surfaces (convert_alpha aplicado).
    """
    surf = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(frames_count):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = surf.subsurface(rect).copy()
        if scale_to and frame.get_size() != scale_to:
            frame = pygame.transform.scale(frame, scale_to)
        frames.append(frame)
    return frames