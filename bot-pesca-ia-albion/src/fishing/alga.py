import time
from .funciones_utiles import mover_y_clickear


def usar_alga(log_callback=print):
    log_callback("Limpiando manos con alga...")
    if mover_y_clickear('alga.PNG', 'Alga', log_callback):
        time.sleep(1)
        mover_y_clickear('ceboclose.PNG', 'Cerrar ventana', log_callback)
