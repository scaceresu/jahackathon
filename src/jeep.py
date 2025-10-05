import pygame
from settings import TILE_SIZE
from sprite_manager import sprite_manager

class Jeep:
    """Clase para el Jeep que actúa como obstáculo de daño"""
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE)  # Jeep de 2x1 tiles
        self.type = "damage"
        self.sprite = self.create_jeep_sprite()
        
    def create_jeep_sprite(self):
        """Crea el sprite del jeep"""
        # Intentar cargar sprite específico o crear uno personalizado
        jeep_surface = pygame.Surface((TILE_SIZE * 2, TILE_SIZE), pygame.SRCALPHA)
        
        # Cuerpo principal del jeep (verde militar)
        pygame.draw.rect(jeep_surface, (85, 107, 47), (0, 8, TILE_SIZE * 2, TILE_SIZE - 16))
        
        # Ventanas
        pygame.draw.rect(jeep_surface, (135, 206, 235), (8, 12, 16, 12))
        pygame.draw.rect(jeep_surface, (135, 206, 235), (TILE_SIZE + 8, 12, 16, 12))
        
        # Ruedas
        pygame.draw.circle(jeep_surface, (0, 0, 0), (8, TILE_SIZE - 8), 6)
        pygame.draw.circle(jeep_surface, (0, 0, 0), (TILE_SIZE * 2 - 8, TILE_SIZE - 8), 6)
        pygame.draw.circle(jeep_surface, (64, 64, 64), (8, TILE_SIZE - 8), 4)
        pygame.draw.circle(jeep_surface, (64, 64, 64), (TILE_SIZE * 2 - 8, TILE_SIZE - 8), 4)
        
        # Detalles
        pygame.draw.rect(jeep_surface, (0, 0, 0), (TILE_SIZE - 2, 12, 4, 12))  # División del parabrisas
        pygame.draw.rect(jeep_surface, (139, 69, 19), (4, 4, TILE_SIZE * 2 - 8, 4))  # Techo
        
        return jeep_surface
    
    def draw(self, screen):
        """Dibuja el jeep en pantalla"""
        if self.sprite:
            screen.blit(self.sprite, self.rect)
        else:
            # Fallback
            pygame.draw.rect(screen, (85, 107, 47), self.rect)
    
    def check_collision(self, other_rect):
        """Verifica colisión con otro rectángulo"""
        return self.rect.colliderect(other_rect)
    
    def get_position(self):
        """Obtiene la posición del jeep"""
        return (self.rect.x, self.rect.y)