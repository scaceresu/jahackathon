import pygame
from enum import Enum
from settings import WIDTH, HEIGHT, WHITE, BLACK, RED, GREEN

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"

class GameStateManager:
    """Maneja los diferentes estados del juego"""
    
    def __init__(self):
        self.current_state = GameState.MENU
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.selected_option = 0
        self.init_fonts()
    
    def init_fonts(self):
        """Inicializa las fuentes"""
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont('Arial', 48)
            self.font_medium = pygame.font.SysFont('Arial', 32)
            self.font_small = pygame.font.SysFont('Arial', 24)
    
    def handle_menu_input(self, event):
        """Maneja input en el menú"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_option = min(1, self.selected_option + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_option == 0:  # Jugar
                    self.current_state = GameState.PLAYING
                    return "start_game"
                elif self.selected_option == 1:  # Salir
                    return "quit"
            # Teclas de inicio rápido
            elif event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, 
                              pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                # Cualquier tecla de movimiento inicia el juego directamente
                self.current_state = GameState.PLAYING
                return "start_game"
        return None
    
    def handle_game_over_input(self, event):
        """Maneja input en game over"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_option = min(1, self.selected_option + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_option == 0:  # Reiniciar
                    self.current_state = GameState.PLAYING
                    return "restart"
                elif self.selected_option == 1:  # Menú
                    self.current_state = GameState.MENU
                    self.selected_option = 0
                    return "menu"
            elif event.key == pygame.K_r:  # Reinicio rápido
                self.current_state = GameState.PLAYING
                return "restart"
            elif event.key == pygame.K_q:  # Salir rápido
                return "quit"
        return None
    
    def draw_menu(self, screen):
        """Dibuja el menú principal"""
        screen.fill(BLACK)
        
        # Título
        title_text = self.font_large.render("ESCAPE DEL JEEP", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_small.render("¡Escapa del enemigo y evita el jeep dañado!", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Opciones
        options = ["Jugar", "Salir"]
        for i, option in enumerate(options):
            color = GREEN if i == self.selected_option else WHITE
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
            screen.blit(option_text, option_rect)
            
            # Indicador de selección
            if i == self.selected_option:
                pygame.draw.rect(screen, GREEN, option_rect.inflate(20, 10), 2)
        
        # Controles
        controls_text = self.font_small.render("↑↓ navegar, ENTER seleccionar, WASD/Flechas para jugar", True, WHITE)
        controls_rect = controls_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        screen.blit(controls_text, controls_rect)
    
    def draw_game_over(self, screen):
        """Dibuja la pantalla de game over"""
        # Fondo semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Título de Game Over
        game_over_text = self.font_large.render("¡GAME OVER!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(game_over_text, game_over_rect)
        
        # Mensaje
        message_text = self.font_medium.render("¡El enemigo te ha alcanzado!", True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(message_text, message_rect)
        
        # Opciones
        options = ["Reintentar", "Menú Principal"]
        for i, option in enumerate(options):
            color = GREEN if i == self.selected_option else WHITE
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20 + i * 50))
            screen.blit(option_text, option_rect)
            
            # Indicador de selección
            if i == self.selected_option:
                pygame.draw.rect(screen, GREEN, option_rect.inflate(20, 10), 2)
        
        # Controles rápidos
        quick_controls = [
            "R - Reintentar rápido",
            "Q - Salir",
            "↑↓ - Navegar, ENTER - Seleccionar"
        ]
        
        for i, control in enumerate(quick_controls):
            control_text = self.font_small.render(control, True, WHITE)
            control_rect = control_text.get_rect(center=(WIDTH // 2, HEIGHT - 80 + i * 20))
            screen.blit(control_text, control_rect)
    
    def set_state(self, state):
        """Cambia el estado del juego"""
        self.current_state = state
        self.selected_option = 0
    
    def trigger_game_over(self):
        """Activa el estado de game over"""
        self.current_state = GameState.GAME_OVER
        self.selected_option = 0