import pygame

pygame.init()

files = ['walk_right.png', 'walk_left.png', 'walk_up.png', 'walk_down.png', 'idle.png']

for f in files:
    img = pygame.image.load(f'assets/imagenes/enemy/{f}')
    print(f'{f}: {img.get_size()}')