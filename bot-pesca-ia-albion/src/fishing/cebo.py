import time
from .funciones_utiles import mover_y_clickear


def aplicar_cebo(log_callback=print):
    log_callback("Aplicando cebo...")
    if not mover_y_clickear('cebo.PNG', 'Cebo', log_callback):
        log_callback("No se encontro el cebo.")
        return
    time.sleep(1)
    if not mover_y_clickear('ceboausar.PNG', 'Usar cebo', log_callback):
        log_callback("No se pudo usar el cebo.")
        return
    time.sleep(1)
    mover_y_clickear('ceboclose.PNG', 'Cerrar inventario', log_callback)
    log_callback("Cebo aplicado.")
