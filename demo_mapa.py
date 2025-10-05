#!/usr/bin/env python3
"""
Demo del Sistema de Mapas y Sprites
====================================

Este script crea una demostración visual del sistema de mapas implementado.
Muestra todos los tipos de tiles disponibles y sus propiedades.
"""

import pygame
import sys
import os

# Añadir el directorio src al path para importar los módulos
sys.path.append('src')

try:
    from settings import WIDTH, HEIGHT, FPS, TITLE, TILE_SIZE
    from tilemap import TileMap
    from sprite_manager import sprite_manager
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que pygame esté instalado: pip install pygame")
    sys.exit(1)

class MapDemo:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"{TITLE} - Demo del Mapa")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Crear el mapa
        self.tilemap = TileMap()
        
        # Fuente para mostrar información
        try:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        except:
            self.font = None
            self.small_font = None
    
    def run(self):
        print("=== Demo del Sistema de Mapas y Sprites ===")
        print("Controles:")
        print("- Mouse: Hover sobre tiles para ver información")
        print("- ESC o cerrar ventana: Salir")
        print("- Tiles cargados:", len(sprite_manager.get_all_sprites()))
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Dibujar el mapa
        self.tilemap.draw(self.screen)
        
        # Obtener posición del mouse
        mouse_pos = pygame.mouse.get_pos()
        tile_type = self.tilemap.get_tile_at_position(mouse_pos[0], mouse_pos[1])
        
        # Mostrar información del tile bajo el mouse
        if tile_type and self.font:
            properties = self.tilemap.get_tile_properties(tile_type)
            info_text = f"Tile: {tile_type}"
            walkable_text = f"Caminable: {'Sí' if properties['walkable'] else 'No'}"
            speed_text = f"Velocidad: {int(properties['speed_modifier'] * 100)}%"
            
            # Crear superficie semi-transparente para el fondo del texto
            info_surface = pygame.Surface((250, 80))
            info_surface.set_alpha(200)
            info_surface.fill((0, 0, 0))
            
            # Renderizar textos
            text1 = self.font.render(info_text, True, (255, 255, 255))
            text2 = self.small_font.render(walkable_text, True, (255, 255, 255))
            text3 = self.small_font.render(speed_text, True, (255, 255, 255))
            
            # Posicionar el panel de información
            panel_x = min(mouse_pos[0] + 10, WIDTH - 260)
            panel_y = min(mouse_pos[1] + 10, HEIGHT - 90)
            
            self.screen.blit(info_surface, (panel_x, panel_y))
            self.screen.blit(text1, (panel_x + 10, panel_y + 10))
            self.screen.blit(text2, (panel_x + 10, panel_y + 35))
            self.screen.blit(text3, (panel_x + 10, panel_y + 55))
        
        # Mostrar estadísticas generales
        if self.font:
            stats_text = f"Sprites cargados: {len(sprite_manager.get_all_sprites())}"
            map_size_text = f"Mapa: {len(self.tilemap.map_data[0])}x{len(self.tilemap.map_data)} tiles"
            
            stats_surface = self.font.render(stats_text, True, (255, 255, 255))
            map_surface = self.small_font.render(map_size_text, True, (255, 255, 255))
            
            self.screen.blit(stats_surface, (10, 10))
            self.screen.blit(map_surface, (10, 35))
        
        pygame.display.flip()

if __name__ == "__main__":
    demo = MapDemo()
    demo.run()