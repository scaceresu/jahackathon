import pygame
import heapq
import math
import random
from settings import RED, DARK_RED, PLAYER_SPEED, ENEMY_SPEED_MULTIPLIER

class Enemy:
    def __init__(self, x, y, grid_width, grid_height):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = PLAYER_SPEED * ENEMY_SPEED_MULTIPLIER  # Velocidad basada en el jugador
        self.grid_x = x // 32
        self.grid_y = y // 32
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Para Dijkstra
        self.path = []
        self.target_grid_x = 0
        self.target_grid_y = 0
        self.recalculate_timer = 0
        self.recalculate_interval = 60  # Recalcular cada segundo
        
        # Movimiento suave
        self.target_x = x
        self.target_y = y
        self.moving = False
        
        # Para movimientos aleatorios cuando no hay camino
        self.random_mode = False
        self.random_direction = None
        self.random_timer = 0
        self.random_change_interval = 90  # Cambiar dirección cada 1.5 segundos
        
    def dijkstra(self, start_x, start_y, target_x, target_y, obstacles):
        """
        Implementación del algoritmo de Dijkstra para encontrar el camino más corto
        """
        # Crear grid de distancias
        distances = {}
        previous = {}
        unvisited = []
        
        # Inicializar todas las posiciones
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                distances[(x, y)] = float('inf')
                previous[(x, y)] = None
                heapq.heappush(unvisited, (float('inf'), x, y))
        
        # Distancia del punto inicial es 0
        distances[(start_x, start_y)] = 0
        heapq.heappush(unvisited, (0, start_x, start_y))
        
        # Direcciones: arriba, abajo, izquierda, derecha
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        while unvisited:
            current_distance, current_x, current_y = heapq.heappop(unvisited)
            
            # Si llegamos al objetivo, construir el camino
            if current_x == target_x and current_y == target_y:
                path = []
                while (current_x, current_y) != (start_x, start_y):
                    path.append((current_x, current_y))
                    prev = previous[(current_x, current_y)]
                    if prev is None:  # No hay camino disponible
                        return []
                    current_x, current_y = prev
                path.reverse()
                return path
            
            # Si ya encontramos una distancia mejor, saltar
            if current_distance > distances[(current_x, current_y)]:
                continue
            
            # Explorar vecinos
            for dx, dy in directions:
                neighbor_x = current_x + dx
                neighbor_y = current_y + dy
                
                # Verificar límites
                if (0 <= neighbor_x < self.grid_width and 
                    0 <= neighbor_y < self.grid_height):
                    
                    # Verificar si hay obstáculo
                    is_obstacle = False
                    neighbor_rect = pygame.Rect(
                        neighbor_x * 32, neighbor_y * 32, 32, 32
                    )
                    
                    for obstacle in obstacles:
                        if neighbor_rect.colliderect(obstacle):
                            is_obstacle = True
                            break
                    
                    if not is_obstacle:
                        # Calcular nueva distancia (peso = 1 para movimiento simple)
                        new_distance = distances[(current_x, current_y)] + 1
                        
                        if new_distance < distances[(neighbor_x, neighbor_y)]:
                            distances[(neighbor_x, neighbor_y)] = new_distance
                            previous[(neighbor_x, neighbor_y)] = (current_x, current_y)
                            heapq.heappush(unvisited, (new_distance, neighbor_x, neighbor_y))
        
        return []  # No se encontró camino
    
    def get_random_direction(self, obstacles):
        """Obtiene una dirección aleatoria válida"""
        directions = ['up', 'down', 'left', 'right']
        random.shuffle(directions)  # Mezclar direcciones para aleatoriedad
        
        for direction in directions:
            # Calcular nueva posición según la dirección
            new_x, new_y = self.rect.x, self.rect.y
            
            speed_int = int(self.speed)
            if direction == 'up':
                new_y -= speed_int * 4  # Mover más rápido en modo aleatorio
            elif direction == 'down':
                new_y += speed_int * 4
            elif direction == 'left':
                new_x -= speed_int * 4
            elif direction == 'right':
                new_x += speed_int * 4
            
            # Verificar límites de pantalla
            if (new_x < 32 or new_x >= self.grid_width * 32 - 32 or 
                new_y < 32 or new_y >= self.grid_height * 32 - 32):
                continue
            
            # Verificar colisiones con obstáculos
            test_rect = pygame.Rect(new_x, new_y, 32, 32)
            collision = False
            for obstacle in obstacles:
                if test_rect.colliderect(obstacle):
                    collision = True
                    break
            
            if not collision:
                return direction
        
        return 'right'  # Dirección por defecto si todas están bloqueadas
    
    def update_random_movement(self, obstacles):
        """Actualizar movimiento aleatorio cuando no hay camino"""
        self.random_timer += 1
        
        # Cambiar dirección periódicamente o si no tenemos dirección
        if (self.random_timer >= self.random_change_interval or 
            self.random_direction is None):
            self.random_direction = self.get_random_direction(obstacles)
            self.random_timer = 0
        
        # Mover en la dirección aleatoria
        old_x, old_y = self.rect.x, self.rect.y
        speed_int = int(self.speed)  # Convertir a entero para pygame.Rect
        
        if self.random_direction == 'up':
            self.rect.y -= speed_int
        elif self.random_direction == 'down':
            self.rect.y += speed_int
        elif self.random_direction == 'left':
            self.rect.x -= speed_int
        elif self.random_direction == 'right':
            self.rect.x += speed_int
        
        # Verificar colisiones después del movimiento
        collision = False
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                collision = True
                break
        
        # Si hay colisión, revertir movimiento y cambiar dirección
        if collision:
            self.rect.x, self.rect.y = old_x, old_y
            self.random_direction = self.get_random_direction(obstacles)
            self.random_timer = 0
        
        # Actualizar posición en grid
        self.grid_x = self.rect.centerx // 32
        self.grid_y = self.rect.centery // 32
    
    def update(self, player, obstacles):
        """Actualizar enemigo usando Dijkstra para perseguir al jugador"""
        
        # Recalcular camino periódicamente
        self.recalculate_timer += 1
        if self.recalculate_timer >= self.recalculate_interval or not self.path:
            self.target_grid_x = player.grid_x
            self.target_grid_y = player.grid_y
            
            self.path = self.dijkstra(
                self.grid_x, self.grid_y,
                self.target_grid_x, self.target_grid_y,
                obstacles
            )
            self.recalculate_timer = 0
            
            # Activar/desactivar modo aleatorio según si hay camino
            if not self.path:
                self.random_mode = True
                self.moving = False  # Detener movimiento de Dijkstra
            else:
                self.random_mode = False
        
        if self.random_mode:
            # Si no hay camino, usar movimientos aleatorios
            self.update_random_movement(obstacles)
        else:
            # Seguir el camino calculado por Dijkstra
            if self.path and not self.moving:
                next_grid_x, next_grid_y = self.path[0]
                self.target_x = next_grid_x * 32
                self.target_y = next_grid_y * 32
                self.moving = True
                self.path.pop(0)  # Remover el siguiente paso del camino
            
            # Movimiento suave hacia el objetivo
            if self.moving:
                dx = self.target_x - self.rect.x
                dy = self.target_y - self.rect.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > self.speed:
                    # Mover hacia el objetivo
                    self.rect.x += int((dx / distance) * self.speed)
                    self.rect.y += int((dy / distance) * self.speed)
                else:
                    # Llegamos al objetivo
                    self.rect.x = self.target_x
                    self.rect.y = self.target_y
                    self.grid_x = self.target_x // 32
                    self.grid_y = self.target_y // 32
                    self.moving = False
        
        # Verificar colisión con jugador
        if self.rect.colliderect(player.rect):
            return player.get_caught()
        
        return False
    
    def draw(self, screen):
        # Cambiar color según el modo
        color = (255, 100, 0) if self.random_mode else RED  # Naranja si aleatorio, rojo si Dijkstra
        pygame.draw.rect(screen, color, self.rect)
        
        # Dibujar borde más oscuro
        border_color = (150, 75, 0) if self.random_mode else DARK_RED
        pygame.draw.rect(screen, border_color, self.rect, 3)
        
        # Dibujar ojos simples
        eye_size = 4
        left_eye = pygame.Rect(
            self.rect.x + 8, self.rect.y + 8, eye_size, eye_size
        )
        right_eye = pygame.Rect(
            self.rect.x + 20, self.rect.y + 8, eye_size, eye_size
        )
        pygame.draw.rect(screen, (255, 255, 255), left_eye)
        pygame.draw.rect(screen, (255, 255, 255), right_eye)
        pygame.draw.rect(screen, (0, 0, 0), left_eye, 1)
        pygame.draw.rect(screen, (0, 0, 0), right_eye, 1)
        
        # Indicador visual de modo aleatorio
        if self.random_mode:
            # Dibujar pequeños puntos para indicar confusión
            for i in range(3):
                x = self.rect.x + 10 + i * 4
                y = self.rect.y - 5
                pygame.draw.circle(screen, (255, 255, 0), (x, y), 2)
    
    def draw_debug_path(self, screen):
        """Dibujar el camino calculado (para debug)"""
        if self.path:
            for i, (grid_x, grid_y) in enumerate(self.path):
                x = grid_x * 32 + 16
                y = grid_y * 32 + 16
                color = (255, 255, 0) if i == 0 else (255, 255, 255)
                pygame.draw.circle(screen, color, (x, y), 3)
                
                # Línea hacia el siguiente punto
                if i < len(self.path) - 1:
                    next_x = self.path[i + 1][0] * 32 + 16
                    next_y = self.path[i + 1][1] * 32 + 16
                    pygame.draw.line(screen, (200, 200, 200), (x, y), (next_x, next_y), 2)

