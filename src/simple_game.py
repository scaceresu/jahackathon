import pygame, sys
from settings import WIDTH, HEIGHT, FPS, TITLE, BLACK, TILE_SIZE
from player import Player
from enemy import Enemy
from tilemap import TileMap

class SimpleGame:
    """Versión simplificada que inicia directamente en el juego"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"{TITLE} - Modo Directo")
        self.clock = pygame.time.Clock()
        self.running = True

        # Inicializar componentes del juego directamente
        print("🎮 Iniciando juego en modo directo...")
        print("📋 Controles: WASD o Flechas para moverse")
        print("⚠️  Objetivo: Evita el enemigo rojo y los jeeps verdes")
        
        self.init_game_components()

    def init_game_components(self):
        """Inicializa los componentes del juego"""
        # Mapa
        self.tilemap = TileMap()
        
        # Entidades - posiciones iniciales seguras
        # Encontrar posición segura para el jugador
        safe_x, safe_y = self.tilemap.find_safe_spawn_position(for_enemy=False)
        self.player = Player(safe_x, safe_y, self.tilemap)
        
        # Encontrar posición segura para el enemigo con espacio de movimiento
        enemy_x, enemy_y = self.tilemap.find_safe_spawn_position(entity_width=25, entity_height=25, for_enemy=True)
        
        # Verificar que el enemigo no esté demasiado cerca del jugador
        distance_to_player = ((enemy_x - safe_x) ** 2 + (enemy_y - safe_y) ** 2) ** 0.5
        if distance_to_player < 150:  # Si está muy cerca, intentar otras posiciones
            alternative_positions = [
                (TILE_SIZE * 10, TILE_SIZE * 9),   # Carretera principal
                (TILE_SIZE * 12, TILE_SIZE * 13),  # Carretera inferior
                (TILE_SIZE * 6, TILE_SIZE * 5),    # Carretera superior
            ]
            
            for alt_x, alt_y in alternative_positions:
                alt_distance = ((alt_x - safe_x) ** 2 + (alt_y - safe_y) ** 2) ** 0.5
                if alt_distance >= 150:
                    temp_rect = pygame.Rect(alt_x, alt_y, 25, 25)
                    if (self.tilemap._is_rect_walkable(temp_rect) and 
                        not self.tilemap.check_jeep_collision(temp_rect) and
                        self.tilemap._has_movement_space(alt_x, alt_y, 25, 25)):
                        enemy_x, enemy_y = alt_x, alt_y
                        break
            
        self.enemy = Enemy(enemy_x, enemy_y, self.tilemap)
        
        # El enemigo persigue al jugador
        self.enemy.set_target(self.player)
        
        print(f"✅ Jugador creado en posición ({self.player.rect.x}, {self.player.rect.y})")
        print(f"✅ Enemigo creado en posición ({self.enemy.rect.x}, {self.enemy.rect.y})")
        print(f"✅ Mapa cargado con {len(self.tilemap.get_jeeps())} jeeps")

    def run(self):
        print("🚀 ¡Juego iniciado! Usa WASD para moverte")
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("👋 Saliendo del juego...")
                    self.running = False
                elif event.key == pygame.K_r:
                    print("🔄 Reiniciando juego...")
                    self.init_game_components()

    def update(self):
        self.player.update()
        self.enemy.update()
        
        # Verificar colisión con jeeps (damage)
        jeep_collision = self.player.check_jeep_collision()
        if jeep_collision:
            print("💥 ¡Colisión con jeep! Reiniciando...")
            self.init_game_components()
            return
        
        # Verificar si el enemigo alcanzó al jugador
        if self.enemy.check_collision_with_player(self.player.rect):
            print("👹 ¡El enemigo te alcanzó! Reiniciando...")
            self.init_game_components()
            return

    def draw(self):
        self.screen.fill(BLACK)
        
        # Dibujamos el mapa primero (fondo)
        self.tilemap.draw(self.screen)
        # Luego las entidades (primer plano)
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        
        # Información básica
        self.draw_info()
        
        pygame.display.flip()
    
    def draw_info(self):
        """Dibuja información básica del juego"""
        try:
            font = pygame.font.Font(None, 20)
            
            # Instrucciones básicas
            instructions = [
                "WASD/Flechas: Moverse",
                "ESC: Salir | R: Reiniciar",
                "⚠️ Evita: Enemigo rojo y jeeps verdes"
            ]
            
            for i, instruction in enumerate(instructions):
                text = font.render(instruction, True, (255, 255, 255))
                # Fondo para el texto
                text_bg = pygame.Surface((text.get_width() + 6, text.get_height() + 2))
                text_bg.set_alpha(150)
                text_bg.fill((0, 0, 0))
                
                y_pos = 10 + i * 25
                self.screen.blit(text_bg, (8, y_pos))
                self.screen.blit(text, (10, y_pos + 1))
                
        except Exception as e:
            pass

if __name__ == "__main__":
    simple_game = SimpleGame()
    simple_game.run()