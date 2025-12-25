import time
from funciones_utiles import mover_y_clickear


def usar_alga():
    print("Buscando imagen 'alga2.png' en inventario...")
    if mover_y_clickear("img/alga.png", "Alga"):
        time.sleep(0.5)
        try:
            if mover_y_clickear("img/ceboclose.png", "Cerrar ventana"):
                time.sleep(0.2)  # Espera a que la ventana se cierre completamente
        except Exception as e:
            print(f"⚠️ Error al cerrar ventana: {e}")
