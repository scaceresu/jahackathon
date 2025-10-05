import pygame                             # Biblioteca principal para ventanas, eventos y dibujo
from menu import menu                     # Función que muestra el menú y devuelve el nivel seleccionado
from game import jugar                    # Función que ejecuta el nivel/juego y devuelve True si se completa
from settings import ANCHO_PANTALLA, ALTO_PANTALLA  # Constantes de tamaño de la ventana
from progressmanager import cargarProgreso, guardarProgreso  # Funciones para persistir el progreso del jugador

# Rutas a los archivos de mapa (JSON o formato que uses)
mapa1 = "mapa1.csv"
mapa2 = "mapa1.csv"            # Aquí parece un copy/paste; probablemente querías "mapa2.json"

def main():
    pygame.init()                          # Inicializa todos los módulos de pygame necesarios
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))  # Crea la ventana del juego
    pygame.display.set_caption("Juego")    # Texto de la ventana

    # Cargamos el progreso guardado; retorna el nivel desbloqueado (int)
    nivel_desbloqueado = cargarProgreso()

    # Bucle principal del lanzador/menu; aquí se vuelve hasta que el usuario cierre la aplicación
    while True:
        # Llamamos al menú, le pasamos la pantalla para que dibuje; recibe cual nivel seleccionó el jugador
        nivel = menu(pantalla, nivel_desbloqueado)

        # Si el jugador eligió jugar el nivel 1
        if nivel == 1:
            # Ejecuta la función jugar con la pantalla y la ruta del mapa; devuelve True si el nivel fue completado
            completado = jugar(pantalla, "mapa1.csv","fondo.png")
            if completado:
                # Si se completó, desbloqueamos el siguiente nivel (al menos 2)
                nivel_desbloqueado = max(nivel_desbloqueado, 2)
                # Guardamos el progreso actualizado en disco
                guardarProgreso(nivel_desbloqueado)

        # Si el jugador eligió jugar el nivel 2
        elif nivel == 2:
            # Verificamos si ese nivel está desbloqueado según el progreso guardado
            if nivel_desbloqueado >= 2:
                # Ejecuta el nivel 2
                completado = jugar(pantalla, "mapa1.csv")
                if completado:
                    # Desbloquea el siguiente nivel (al menos 3) y guarda
                    nivel_desbloqueado = max(nivel_desbloqueado, 3)
                    guardarProgreso(nivel_desbloqueado)
            else:
                # Si intenta acceder a un nivel bloqueado, avisamos (aquí solo imprime en consola)
                print("❌!")

# Entrada del script: si se ejecuta directamente, arrancamos main
if __name__ == "__main__":
    main()
