import pygame
import sys

# --- Константы ---
ANCHO_PANTALLА = 800
ALTO_PANTALLА = 600
FPS = 60
TILE = 40

# --- Карты ---
mapa1 = [
    "########################",
    "#......................#",
    "#........####..........#",
    "#...1..................#",
    "#..........####........#",
    "#......................#",
    "#...................1..#",
    "########################",
]

mapa2 = [
    "########################",
    "#......................#",
    "#..######..............#",
    "#......................#",
    "#..........####........#",
    "#......................#",
    "#......................#",
    "########################",
]

# --- Player ---
class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidad = 5

    def update(self, teclas, muros):
        dx, dy = 0, 0
        if teclas[pygame.K_LEFT]:
            dx = -self.velocidad
        if teclas[pygame.K_RIGHT]:
            dx = self.velocidad
        if teclas[pygame.K_UP]:
            dy = -self.velocidad
        if teclas[pygame.K_DOWN]:
            dy = self.velocidad

        self.rect.x += dx
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                if dx > 0: self.rect.right = muro.rect.left
                if dx < 0: self.rect.left = muro.rect.right

        self.rect.y += dy
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                if dy > 0: self.rect.bottom = muro.rect.top
                if dy < 0: self.rect.top = muro.rect.bottom
# --- Enemy ---
class Enemy(pygame.sprite.Sprite):
     def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((200, 200, 220))
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Wall ---
class Muro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

def cargar_mapa(mapa):
    muros = pygame.sprite.Group()
    for fila, linea in enumerate(mapa):
        for col, celda in enumerate(linea):
            if celda == "#":
                muro = Muro(col * TILE, fila * TILE)
                muros.add(muro)
    return muros

# --- Menu ---
def menu(pantalla):
    fuente = pygame.font.SysFont(None, 60)
    botones = [
        {"texto": "Nivel 1", "rect": pygame.Rect(300, 200, 200, 60), "nivel": 1},
        {"texto": "Nivel 2", "rect": pygame.Rect(300, 300, 200, 60), "nivel": 2},
        {"texto": "Salir",   "rect": pygame.Rect(300, 400, 200, 60), "nivel": None},
    ]

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for boton in botones:
                    if boton["rect"].collidepoint(evento.pos):
                        if boton["nivel"] is None:
                            pygame.quit()
                            sys.exit()
                        else:
                            return boton["nivel"]

        pantalla.fill((180, 200, 255))

        # Рисуем кнопки
        for boton in botones:
            pygame.draw.rect(pantalla, (100, 150, 255), boton["rect"])
            texto = fuente.render(boton["texto"], True, (255, 255, 255))
            texto_rect = texto.get_rect(center=boton["rect"].center)
            pantalla.blit(texto, texto_rect)

        pygame.display.flip()


# --- Game funcion ---
def jugar(pantalla, mapa):
    reloj = pygame.time.Clock()
    muros = cargar_mapa(mapa)
    jugador = Jugador(100, 100)
    enemy = Enemy(100, 100) 
    todos = pygame.sprite.Group(jugador,enemy)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return  # back menu

        teclas = pygame.key.get_pressed()
        jugador.update(teclas, muros)

        pantalla.fill((200, 220, 255))
        muros.draw(pantalla)
        todos.draw(pantalla)
        pygame.display.flip()
        reloj.tick(FPS)


# --- Menu ---
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLА, ALTO_PANTALLА))
    pygame.display.set_caption("Juego con menú y niveles")

    while True:
        nivel = menu(pantalla)
        if nivel == 1:
            jugar(pantalla, mapa1)
        elif nivel == 2:
            jugar(pantalla, mapa2)

if __name__ == "__main__":
    main()
