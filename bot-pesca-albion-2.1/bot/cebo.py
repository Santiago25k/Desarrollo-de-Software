import time
from funciones_utiles import mover_y_clickear

def aplicar_cebo(log_callback=print):
    log_callback("🛠️ Aplicando cebo...")
    if mover_y_clickear('img/cebo.PNG', 'Cebo'):
        time.sleep(1)
        if mover_y_clickear('img/ceboausar.png', 'Usar Cebo'):
            time.sleep(1)
            mover_y_clickear('img/ceboclose.png', 'Cerrar Inventario')
            log_callback("✅ Cebo aplicado correctamente.")
        else:
            log_callback("⚠️ No se pudo usar el cebo.")
    else:
        log_callback("❌ No se encontró el cebo.")
