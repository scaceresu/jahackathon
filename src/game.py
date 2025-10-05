import pygame, sys
from settings import WIDTH, HEIGHT, FPS, TITLE, WHITE, DARK_GRAY, GRID_WIDTH, GRID_HEIGHT
from player import Player
from enemy import Enemy


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Crear jugador y enemigo
        self.player = Player(64, 64)
        self.enemy = Enemy(800, 600, GRID_WIDTH, GRID_HEIGHT)
        
        # Crear algunos obstáculos de ejemplo (laberinto simple)
        self.obstacles = self.create_test_obstacles()
        
        # Configuración de debug
        self.debug_mode = False
        self.font = pygame.font.Font(None, 36)
        
        # Estado del juego
        self.game_over = False
        self.caught_message_timer = 0

    def create_test_obstacles(self):
        """Crear obstáculos de prueba para el laberinto"""
        obstacles = []
        
        # Bordes del mapa
        obstacles.extend([
            pygame.Rect(0, 0, WIDTH, 32),      # Borde superior
            pygame.Rect(0, HEIGHT-32, WIDTH, 32), # Borde inferior
            pygame.Rect(0, 0, 32, HEIGHT),     # Borde izquierdo
            pygame.Rect(WIDTH-32, 0, 32, HEIGHT), # Borde derecho
        ])
        
        # Obstáculos internos (laberinto simple)
        obstacles.extend([
            pygame.Rect(200, 100, 64, 200),    # Pared vertical
            pygame.Rect(400, 200, 200, 64),    # Pared horizontal
            pygame.Rect(600, 50, 64, 150),     # Otra pared
            pygame.Rect(300, 400, 150, 64),    # Pared central
            pygame.Rect(700, 350, 64, 150),    # Pared derecha
            pygame.Rect(100, 500, 200, 64),    # Pared inferior
        ])
        
        return obstacles

    def run(self):
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
                if event.key == pygame.K_F1:  # Toggle debug mode
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_r and self.game_over:  # Restart
                    self.restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        if not self.game_over:
            # Actualizar jugador
            self.player.update(self.obstacles)
            
            # Actualizar enemigo con Dijkstra
            caught = self.enemy.update(self.player, self.obstacles)
            
            if caught:
                self.caught_message_timer = 180  # 3 segundos a 60 FPS
                print("¡Te atraparon! Presiona R para reiniciar")
        
        # Actualizar timer de mensaje
        if self.caught_message_timer > 0:
            self.caught_message_timer -= 1

    def restart_game(self):
        """Reiniciar el juego"""
        self.player = Player(64, 64)
        self.enemy = Enemy(800, 600, GRID_WIDTH, GRID_HEIGHT)
        self.game_over = False
        self.caught_message_timer = 0

    def draw(self):
        self.screen.fill(WHITE)
        
        # Dibujar grid (opcional para debug)
        if self.debug_mode:
            self.draw_grid()
        
        # Dibujar obstáculos
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, DARK_GRAY, obstacle)
        
        # Dibujar entidades
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        
        # Debug: mostrar camino del enemigo
        if self.debug_mode:
            self.enemy.draw_debug_path(self.screen)
        
        # Dibujar UI
        self.draw_ui()
        
        # Mensaje de capturado
        if self.caught_message_timer > 0:
            self.draw_caught_message()
        
        pygame.display.flip()
    
    def draw_grid(self):
        """Dibujar grid para debug"""
        for x in range(0, WIDTH, 32):
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 32):
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (WIDTH, y))
    
    def draw_ui(self):
        """Dibujar interfaz de usuario"""
        # Instrucciones
        instructions = [
            "WASD/Flechas: Mover",
            "F1: Debug Mode",
            "ESC: Salir"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, (0, 0, 0))
            self.screen.blit(text, (10, 10 + i * 25))
        
        # Información de debug
        if self.debug_mode:
            debug_info = [
                f"Player Grid: ({self.player.grid_x}, {self.player.grid_y})",
                f"Enemy Grid: ({self.enemy.grid_x}, {self.enemy.grid_y})",
                f"Path Length: {len(self.enemy.path)}",
                f"Invulnerable: {self.player.invulnerable_timer}"
            ]
            
            for i, info in enumerate(debug_info):
                text = self.font.render(info, True, (0, 0, 255))
                self.screen.blit(text, (10, HEIGHT - 100 + i * 20))
    
    def draw_caught_message(self):
        """Dibujar mensaje cuando el jugador es atrapado"""
        message = "¡TE ATRAPARON! Presiona R para reiniciar"
        text = self.font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        # Fondo semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texto del mensaje
        self.screen.blit(text, text_rect)

