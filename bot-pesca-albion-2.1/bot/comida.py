import pyautogui
import time
from cebo import aplicar_cebo
import os
import sys

# --- MODIFICACIÓN: función para compatibilidad con PyInstaller ---
def resource_path(relative_path):
    """
    Devuelve la ruta absoluta del recurso, compatible con ejecución normal y .exe generado por PyInstaller.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
# ---------------------------------------------------------------

TIEMPO_ENTRE_USO = 1800  # 30 minutos
MAX_USOS_POR_STACK = 10
TIEMPO_ESPERA_EQUIPAR = 11

comida_en_uso = False
usos_comida = 0
stack_agotado = False

def equipar_comida(log_callback=print):
    log_callback("🔍 Buscando comida en el inventario...")

    # --- MODIFICACIÓN: usa la ruta correcta para la imagen dentro del ejecutable ---
    ruta = resource_path('img/comida.PNG')
    try:
        ubicacion = pyautogui.locateCenterOnScreen(ruta, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        ubicacion = None

    if ubicacion:
        log_callback("✅ Comida encontrada y equipada correctamente.")
        pyautogui.moveTo(ubicacion, duration=0.3)
        pyautogui.click(button='right')
        return True

    log_callback("❌ No se encontró comida en el inventario.")
    return False

def consumir_comida(log_callback=print):
    log_callback("🍽️ Usando comida...")
    pyautogui.press('2')
    log_callback("✅ Comida consumida.")
    return True

def preparar_comida(log_callback=print):
    if equipar_comida(log_callback=log_callback):
        log_callback(f"⏳ Esperando {TIEMPO_ESPERA_EQUIPAR} segundos para usar comida...")
        time.sleep(TIEMPO_ESPERA_EQUIPAR)
        if consumir_comida(log_callback=log_callback):
            return True
    return False

def iniciar_comida(log_callback=print):
    global usos_comida, comida_en_uso, stack_agotado

    while True:
        if stack_agotado:
            log_callback("♻️ Stack de comida terminado. Reequipando...")
            if equipar_comida(log_callback=log_callback):
                log_callback(f"⌛ Esperando {TIEMPO_ESPERA_EQUIPAR} segundos para usar comida...")
                time.sleep(TIEMPO_ESPERA_EQUIPAR)
                comida_en_uso = True
                if consumir_comida(log_callback=log_callback):
                    usos_comida = 1
                    stack_agotado = False
                    aplicar_cebo(log_callback=log_callback)
                else:
                    log_callback("⚠️ No se pudo consumir comida después de equipar.")
                    time.sleep(60)
                    comida_en_uso = False
                    continue
                comida_en_uso = False
            else:
                log_callback("⚠️ No se pudo reequipar comida. Esperando...")
                time.sleep(60)
                continue

        else:
            log_callback(f"⏳ Esperando {TIEMPO_ENTRE_USO} segundos para próximo uso de comida ({usos_comida + 1}/{MAX_USOS_POR_STACK})...")
            time.sleep(TIEMPO_ENTRE_USO)
            comida_en_uso = True
            log_callback(f"🔄 Usando comida (uso {usos_comida + 1}/{MAX_USOS_POR_STACK})...")
            if consumir_comida(log_callback=log_callback):
                usos_comida += 1
                aplicar_cebo(log_callback=log_callback)
                if usos_comida >= MAX_USOS_POR_STACK:
                    log_callback("♻️ Stack agotado. Preparando para reequipar...")
                    stack_agotado = True
            else:
                log_callback("⚠️ Falló el intento de consumir comida.")
            comida_en_uso = False

if __name__ == "__main__":
    if preparar_comida():
        usos_comida = 1
        iniciar_comida()
    else:
        print("❌ No se pudo preparar la comida. Cerrando script.")
