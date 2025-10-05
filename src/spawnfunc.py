import randomimport random

import pygameimport pygame

from settings import TILEfrom settings import TILE

from tilemap import es_tile_transitable, rect_a_tilesfrom tilemap import es_tile_transitable, rect_a_tiles





def spawn_on_path(mapa, sprite_width, sprite_height, max_attempts=2000, avoid_positions=None, min_distance=64):

    """def spawn_on_path(mapa, sprite_width, sprite_height, max_attempts=2000, avoid_positions=None, min_distance=64):

    Devuelve (x,y) en píxeles donde un sprite de tamaño sprite_width x sprite_height

    cabe y todos los tiles que ocuparía son transitables (mapa tile == 1).    """def spawn_on_path(mapa, sprite_width, sprite_height, max_attempts=2000):

    Intenta hasta max_attempts veces y lanza ValueError si no encuentra posición.

        Devuelve (x,y) en píxeles donde un sprite de tamaño sprite_width x sprite_height    """

    Args:

        mapa: matriz del mapa    cabe y todos los tiles que ocuparía son transitables (mapa tile == 1).    Devuelve (x,y) en píxeles donde un sprite de tamaño sprite_width x sprite_height

        sprite_width, sprite_height: dimensiones del sprite

        max_attempts: máximo número de intentos    Intenta hasta max_attempts veces y lanza ValueError si no encuentra posición.    cabe y todos los tiles que ocuparía son transitables (mapa tile == 1).

        avoid_positions: lista de (x,y) posiciones a evitar

        min_distance: distancia mínima en píxeles a las posiciones a evitar        Intenta hasta max_attempts veces y lanza ValueError si no encuentra posición.

    """

    h = len(mapa)    Args:    """

    w = len(mapa[0]) if h else 0

    if w == 0 or h == 0:        mapa: matriz del mapa    h = len(mapa)

        raise ValueError("Mapa vacío o inválido")

        sprite_width, sprite_height: dimensiones del sprite    w = len(mapa[0]) if h else 0

    # límites en píxeles para topleft de la entidad

    max_x = w * TILE - sprite_width        max_attempts: máximo número de intentos    if w == 0 or h == 0:

    max_y = h * TILE - sprite_height

            avoid_positions: lista de (x,y) posiciones a evitar        raise ValueError("Mapa vacío o inválido")

    if avoid_positions is None:

        avoid_positions = []        min_distance: distancia mínima en píxeles a las posiciones a evitar



    for _ in range(max_attempts):    """    # límites en píxeles para topleft de la entidad

        x = random.randint(0, max(0, max_x))

        y = random.randint(0, max(0, max_y))    h = len(mapa)    max_x = w * TILE - sprite_width

        rect = pygame.Rect(x, y, sprite_width, sprite_height)

            w = len(mapa[0]) if h else 0    max_y = h * TILE - sprite_height

        # comprobar todos los tiles que cubriría el rect

        tiles = rect_a_tiles(rect)    if w == 0 or h == 0:

        if tiles and all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):

            # Verificar distancia a posiciones a evitar        raise ValueError("Mapa vacío o inválido")    for _ in range(max_attempts):

            position_valid = True

            for avoid_x, avoid_y in avoid_positions:        x = random.randint(0, max(0, max_x))

                distance = ((x - avoid_x) ** 2 + (y - avoid_y) ** 2) ** 0.5

                if distance < min_distance:    # límites en píxeles para topleft de la entidad        y = random.randint(0, max(0, max_y))

                    position_valid = False

                    break    max_x = w * TILE - sprite_width        rect = pygame.Rect(x, y, sprite_width, sprite_height)

            

            if position_valid:    max_y = h * TILE - sprite_height        # comprobar todos los tiles que cubriría el rect

                return x, y

                            tiles = rect_a_tiles(rect)

    raise ValueError("No se encontró posición en camino tras many attempts")
    if avoid_positions is None:        if tiles and all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):

        avoid_positions = []            return x, y

    raise ValueError("No se encontró posición en camino tras many attempts")
    for _ in range(max_attempts):
        x = random.randint(0, max(0, max_x))
        y = random.randint(0, max(0, max_y))
        rect = pygame.Rect(x, y, sprite_width, sprite_height)
        
        # comprobar todos los tiles que cubriría el rect
        tiles = rect_a_tiles(rect)
        if tiles and all(es_tile_transitable(mapa, tx, ty) for tx, ty in tiles):
            # Verificar distancia a posiciones a evitar
            position_valid = True
            for avoid_x, avoid_y in avoid_positions:
                distance = ((x - avoid_x) ** 2 + (y - avoid_y) ** 2) ** 0.5
                if distance < min_distance:
                    position_valid = False
                    break
            
            if position_valid:
                return x, y
                
    raise ValueError("No se encontró posición en camino tras many attempts")