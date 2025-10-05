import pygameimport pygameimport pygame



class Agujero(pygame.sprite.Sprite):

    def __init__(self, x, y):

        super().__init__()class Agujero(pygame.sprite.Sprite):class Agujero(pygame.sprite.Sprite):

        # Tamaño del sprite en píxeles

        self.image = pygame.Surface((8, 8))    def __init__(self, x, y):    def __init__(self, x, y):

        self.image.fill((150, 75, 0))  # Color marrón para el agujero

        self.rect = self.image.get_rect(topleft=(x, y))        super().__init__()        super().__init__()

        # tamaño del sprite en píxeles; elegí 8x8 para un agujero pequeño        # tamaño del sprite en píxeles; elegí 16x16 para encajar con un tile (ajustalo si tu sprite es mayor)

        self.image = pygame.Surface((8, 8))        self.image = pygame.Surface((8, 8))

        self.image.fill((150, 75, 0))  # Color marrón para el agujero        self.image.fill((150, 75, 0))

        self.rect = self.image.get_rect(topleft=(x, y))        self.rect = self.image.get_rect(topleft=(x, y))
