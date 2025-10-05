# src/game.py
import os
import pygame
import sys
import random # para posiciones aleatorias de enemigos
from player import Player
from enemy import Enemy
# from agujero import Agujero  # Comentado temporalmente
from playermenu import PlayerMenu
from savezone import SaveZone
from coin import Coin
from deliveryzone import DeliveryZone
# Nuevo: funciones del módulo tilemap (cargar CSV y generar muros)
from tilemap import (
    cargar_mapa_csv, generar_muros, rect_a_tiles, es_tile_transitable, TILE,
    generar_objetos_desde_mapa, obtener_posiciones_restaurantes, 
    obtener_posiciones_casas_clientes, crear_rects_colision
)
from settings import FPS, COLOR_FONDO

# Integración de sistemas avanzados de juego
from games_systems import (
    InventoryManager, 
    FoodSystem, 
    DeliverySystem
)


def spawn_on_path(mapa, sprite_width, sprite_height, max_attempts=2000, avoid_positions=None, min_distance=64):
    """
    Devuelve (x,y) en píxeles donde un sprite de tamaño sprite_width x sprite_height
    cabe y todos los tiles que ocuparía son transitables (mapa tile == 1).
    Intenta hasta max_attempts veces y lanza ValueError si no encuentra posición.
    
    Args:
        mapa: matriz del mapa
        sprite_width, sprite_height: dimensiones del sprite
        max_attempts: máximo número de intentos
        avoid_positions: lista de (x,y) posiciones a evitar
        min_distance: distancia mínima en píxeles a las posiciones a evitar
    """
    h = len(mapa)
    w = len(mapa[0]) if h else 0
    if w == 0 or h == 0:
        raise ValueError("Mapa vacío o inválido")

    # límites en píxeles para topleft de la entidad
    max_x = w * TILE - sprite_width
    max_y = h * TILE - sprite_height
    
    if avoid_positions is None:
        avoid_positions = []

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


def jugar(pantalla, archivo_csv,fondo_path):
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 36)

    # --- Cargar imagen de fondo (una vez) ---
    base_dir = os.path.dirname(__file__)
    fondo_path = os.path.join(base_dir, "maps", fondo_path)
    if os.path.exists(fondo_path):
        fondo_img = pygame.image.load(fondo_path).convert()
        screen_w, screen_h = pantalla.get_size()
        fondo = pygame.transform.scale(fondo_img, (screen_w, screen_h))
    else:
        fondo = None  # fallback para usar COLOR_FONDO

    # --- CARGAR MAPA CSV Y GENERAR MUROS (rects agrupados) ---
    # archivo_csv puede ser "mapa1.csv" si está en src/maps, o ruta absoluta
    mapa, map_w, map_h = cargar_mapa_csv(archivo_csv)
    muros = generar_muros(mapa)  # lista de pygame.Rect que representan bloques no transitables

    # --- INICIALIZACIÓN DE SISTEMAS AVANZADOS ---
    print("🔧 Inicializando sistemas de juego avanzados...")
    
    # 1. Configuración para el formato del juego (1=camino, 0=muro)  
    # Generar algunas posiciones de restaurantes y clientes de manera procedural
    restaurant_positions = []
    client_positions = []
    
    # Generar objetos desde los códigos del mapa CSV
    objetos_mapa = generar_objetos_desde_mapa(mapa)
    restaurant_positions = objetos_mapa["restaurants"]
    client_positions = objetos_mapa["client_houses"]
    food_generator_positions = objetos_mapa["safe_zones"]  # Código 4 = generadores de comida
    
    # Si no hay restaurantes o clientes en el mapa, generar algunos aleatorios como respaldo
    if not restaurant_positions:
        print("⚠️ No se encontraron restaurantes en el mapa, generando algunos aleatorios...")
        for _ in range(3):  
            try:
                rx, ry = spawn_on_path(mapa, 32, 32, max_attempts=100)
                restaurant_positions.append((rx, ry))
            except ValueError:
                pass
    
    if not client_positions:
        print("⚠️ No se encontraron casas de clientes en el mapa, generando algunas aleatorias...")
        for _ in range(2):  
            try:
                cx, cy = spawn_on_path(mapa, 32, 32, max_attempts=100, 
                                     avoid_positions=restaurant_positions, min_distance=128)
                client_positions.append((cx, cy))
            except ValueError:
                pass
    
    if not food_generator_positions:
        print("⚠️ No se encontraron generadores de comida (código 4) en el mapa, generando algunos aleatorios...")
        for _ in range(2):  
            try:
                fx, fy = spawn_on_path(mapa, 32, 32, max_attempts=100, 
                                     avoid_positions=restaurant_positions + client_positions, min_distance=128)
                food_generator_positions.append((fx, fy))
            except ValueError:
                pass
    
    # 2. Sistema de inventario avanzado
    inventory_manager = InventoryManager()
    
    # 3. Sistema de comida avanzado - usar solo posiciones del código 4
    food_system = FoodSystem(food_generator_positions, max_food_items=8)
    
    # 4. Sistema de entregas avanzado  
    delivery_system = DeliverySystem()
    
    # 5. Sistema de pedidos
    from games_systems import OrderSystem
    order_system = OrderSystem(
        client_positions=client_positions,
        max_active_orders=3,
        order_generation_interval=15000  # 15 segundos
    )
    
    # --- ENTIDADES BÁSICAS ---
    # Spawn del jugador en posición válida
    px, py = spawn_on_path(mapa, 12, 24)  # Usar dimensiones de colisión del jugador
    jugador = Player(px, py)
    
    # Agregar algunos agujeros decorativos al mapa (comentado temporalmente)
    agujeros = pygame.sprite.Group()
    # for _ in range(3):  # Crear 3 agujeros aleatorios
    #     try:
    #         ax, ay = spawn_on_path(mapa, 8, 8, max_attempts=50)
    #         agujero = Agujero(ax, ay)
    #         agujeros.add(agujero)
    #     except ValueError:
    #         pass  # Si no se puede colocar, continuar
    
    # Inicializar inventario del jugador
    inventory_manager.initialize_player_inventory(jugador)
    
    # Tamaño del enemigo reducido al 50% (16x32.5 ≈ 16x33)
    enemy_w, enemy_h = 16, 33  # 50% de las dimensiones originales (32x65)
    
    # Spawn del enemigo lejos del jugador (mínimo 128 píxeles de distancia)
    ex, ey = spawn_on_path(mapa, enemy_w, enemy_h, avoid_positions=[(px, py)], min_distance=128)
    enemy = Enemy(ex, ey, horizontal=True, distancia=128,
                  anim_folder="assets/imagenes/enemy", frame_delay=0.15, aggro_radius=350)
    

    enemigos = pygame.sprite.Group(enemy)
    menu_hud = PlayerMenu(jugador)
    
    # Conectar sistema de pedidos al HUD dinámicamente
    setattr(menu_hud, 'order_system', order_system)

    # --- ZONAS TRADICIONALES (mantenidas por compatibilidad) ---
    save_zone = SaveZone(500, 400, 100, 100)
    delivery_zone = DeliveryZone(10, 10, 100, 100)
    coin = Coin(700, 400, 20, 20)
    zone_coin = pygame.sprite.Group(coin)
    zones_group = pygame.sprite.Group(save_zone)
    delivery_zone_group = pygame.sprite.Group(delivery_zone)

    todos = pygame.sprite.Group(jugador, *enemigos)
    
    # --- CONFIGURAR SISTEMAS AVANZADOS ---
    # Crear UN SOLO generador de comida en las posiciones del código 4 (safe_zone)
    food_types = ["empanada", "lomito", "ron", "tabaco", "miel"]
    for i, (fx, fy) in enumerate(food_generator_positions):
        food_type = food_types[i % len(food_types)]  # Alternar tipos de comida
        food_system.add_food_zone(fx-25, fy-25, 50, 50, food_type, give_time=2.0)
        print(f"�️ Generador de comida {i+1}: {food_type} en posición ({fx}, {fy})")
    
    # Crear zonas de entrega para clientes
    for i, (cx, cy) in enumerate(client_positions):
        delivery_system.add_delivery_zone(cx-25, cy-25, 50, 50, f"cliente_{i}")
    
    # Generar comida inicial solo en los generadores (posiciones código 4)
    for i in range(len(food_generator_positions) * 2):
        food_system.spawn_food_item()
    
    # Forzar spawn de comida en posiciones específicas de generadores
    for fx, fy in food_generator_positions:
        food_system.spawn_food_item(force_position=(fx, fy))
    
    print(f"✅ Sistemas inicializados:")
    print(f"   �️ {len(food_generator_positions)} generadores de comida (código 4): {food_generator_positions}")
    print(f"   �🍴 {len(restaurant_positions)} restaurantes: {restaurant_positions}")
    print(f"   🏠 {len(client_positions)} clientes: {client_positions}")
    print(f"   � {len(food_system.food_items)} items de comida generados inicialmente")

    boton_salir = pygame.Rect(650, 20, 120, 40)

    corriendo = True
    while corriendo:
        # --- Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_salir.collidepoint(evento.pos):
                    return

        teclas = pygame.key.get_pressed()

        # --- Actualizaciones: pasamos mapa y muros a las entidades ---
        jugador.update(teclas, mapa, muros_rects=muros, enemigos=enemigos)
        for enemigo in enemigos:
            enemigo.update(jugador=jugador, mapa=mapa)
        
        # --- Actualizar sistemas avanzados ---
        food_system.update(jugador)  # Actualizar sistema de comida
        delivery_system.update(jugador)  # Actualizar sistema de entregas
        order_system.update(pygame.time.get_ticks())  # Actualizar sistema de pedidos
        
        # --- Asegurar que siempre haya comida en los generadores (código 4) ---
        # Intentar generar comida cada cierto tiempo si hay pocos items
        if len(food_system.food_items) < len(food_generator_positions) and pygame.time.get_ticks() % 2000 < 50:
            for fx, fy in food_generator_positions:
                # Verificar si hay poca comida cerca de este generador
                nearby_food = [item for item in food_system.food_items 
                             if abs(item.rect.centerx - fx) < 64 and abs(item.rect.centery - fy) < 64]
                if len(nearby_food) < 1:  # Si hay menos de 1 comida cerca
                    food_system.spawn_food_item(force_position=(fx + random.randint(-32, 32), fy + random.randint(-32, 32)))
        
        # --- Verificar completado de pedidos ---
        if teclas[pygame.K_SPACE]:  # Presionar espacio para entregar
            order_system.try_complete_order_at_position(
                jugador, 
                (jugador.rect.centerx, jugador.rect.centery), 
                tolerance=60
            )

        # --- Dibujado del fondo ---
        if fondo:
            pantalla.blit(fondo, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO)

        # --- Opcional: dibujar muros en modo debug (descomentar para verificar) ---
        # for r in muros:
        #     pygame.draw.rect(pantalla, (120, 30, 30), r, 1)

        # --- Dibujar sistemas avanzados ---
        food_system.draw(pantalla)  # Dibujar items y zonas de comida  
        delivery_system.draw(pantalla)  # Dibujar zonas de entrega
        order_system.draw_orders_on_map(pantalla)  # Dibujar pedidos activos
        
        # --- Dibujar indicadores de generadores de comida ---
        for i, (fx, fy) in enumerate(food_generator_positions):
            # Dibujar un círculo para marcar el generador de comida
            pygame.draw.circle(pantalla, (0, 255, 0), (fx, fy), 30, 4)  # Círculo verde más grande
            # Dibujar texto "F" para food generator
            fuente_pequeña = pygame.font.Font(None, 24)
            texto_f = fuente_pequeña.render("F", True, (0, 255, 0))
            pantalla.blit(texto_f, (fx-8, fy-12))
        
        # --- Dibujar agujeros decorativos ---
        agujeros.draw(pantalla)
        
        # --- Resto del dibujado y actualizaciones de grupos originales ---
        # zones_group.draw(pantalla)
        # zone_coin.draw(pantalla)
        # zone_coin.update(jugador)

        # delivery_zone_group.draw(pantalla)
        # delivery_zone_group.update(jugador)

        # empanada_group.draw(pantalla)
        # empanada_group.update(jugador)
        # lomito_group.draw(pantalla)
        # lomito_group.update(jugador)

        todos.draw(pantalla)

        # Botón salir y HUD
        pygame.draw.rect(pantalla, (255, 80, 80), boton_salir)
        texto = fuente.render("Salir", True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=boton_salir.center))
        menu_hud.dibujar(pantalla)

        # --- Flip y control de FPS ---
        pygame.display.flip()
        reloj.tick(FPS)

        # Condición de éxito
        if jugador.coin == 1:
            return True
