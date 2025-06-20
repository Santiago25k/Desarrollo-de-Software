import time
from funciones_utiles import mover_y_clickear

def usar_alga():
    print("Buscando imagen 'alga.png' en inventario...")
    if mover_y_clickear('img/alga.png', 'Alga'):
        time.sleep(1)
        mover_y_clickear('img/ceboclose.png', 'Cerrar ventana')
