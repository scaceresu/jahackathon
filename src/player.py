import pygame
from settings import GREEN, YELLOW, RED, PLAYER_SPEED

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)  # Cambié a 32x32 para el grid
        self.speed = PLAYER_SPEED
        self.packages_carried = []
        self.max_packages = 3
        self.is_caught = False
        self.invulnerable_timer = 0
        
        # Para el grid de Dijkstra
        self.grid_x = x // 32
        self.grid_y = y // 32

    def update(self, obstacles=None):
        keys = pygame.key.get_pressed()
        old_x, old_y = self.rect.x, self.rect.y
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        
        # Verificar colisiones con obstáculos
        if obstacles:
            for obstacle in obstacles:
                if self.rect.colliderect(obstacle):
                    self.rect.x, self.rect.y = old_x, old_y
                    break
        
        # Actualizar posición en grid
        self.grid_x = self.rect.centerx // 32
        self.grid_y = self.rect.centery // 32
        
        # Actualizar invulnerabilidad
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

    def pickup_package(self, package):
        if len(self.packages_carried) < self.max_packages:
            self.packages_carried.append(package)
            return True
        return False

    def get_caught(self):
        if self.invulnerable_timer <= 0:
            self.is_caught = True
            self.packages_carried = []
            self.invulnerable_timer = 180  # 3 segundos a 60 FPS
            return True
        return False

    def draw(self, screen):
        # Parpadeo si es invulnerable
        if self.invulnerable_timer > 0 and self.invulnerable_timer % 10 < 5:
            color = YELLOW
        else:
            color = GREEN
            
        pygame.draw.rect(screen, color, self.rect)
        
        # Indicador de paquetes
        if self.packages_carried:
            for i, package in enumerate(self.packages_carried):
                indicator_rect = pygame.Rect(
                    self.rect.x + i * 8, 
                    self.rect.y - 8, 
                    6, 6
                )
                pygame.draw.rect(screen, RED, indicator_rect)

