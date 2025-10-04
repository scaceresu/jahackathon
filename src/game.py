import pygame, sys
from settings import WIDTH, HEIGHT, FPS, TITLE, BLACK
from player import Player
from enemy import Enemy 


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Entidades
        self.player = Player(WIDTH//2, HEIGHT//2)
        self.enemy = Enemy(200,-40) 

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

    def update(self):
        self.player.update()
        self.enemy.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        pygame.display.flip()

