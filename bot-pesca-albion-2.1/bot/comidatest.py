import pyautogui
import time
import os
import sys

TIEMPO_ENTRE_USO = 4
MAX_USOS_POR_STACK = 3
TIEMPO_ESPERA_EQUIPAR = 11

usos_comida = 0
stack_agotado = False

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def equipar_comida():
    print("[DEBUG] Buscando comida (comidatest.png)...")
    ruta = resource_path('img/comidatest.png')
    try:
        ubicacion = pyautogui.locateCenterOnScreen(ruta, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        ubicacion = None

    if ubicacion:
        print(f"✅ Comida encontrada en: {ubicacion}")
        pyautogui.moveTo(ubicacion, duration=0.3)
        pyautogui.click(button='right')
        print("✅ Comida equipada correctamente.")
        return True
    else:
        print("❌ No se encontró comida en el inventario (imagen no detectada).")
        return False

def consumir_comida():
    print("[DEBUG] Presionando '2' para consumir comida...")
    pyautogui.press('2')
    print("✅ Comida consumida.")
    return True

def preparar_comida():
    if equipar_comida():
        print(f"[DEBUG] Esperando {TIEMPO_ESPERA_EQUIPAR}s antes de consumir...")
        time.sleep(TIEMPO_ESPERA_EQUIPAR)
        return consumir_comida()
    return False

def iniciar_comida():
    global usos_comida, stack_agotado

    while True:
        if stack_agotado:
            print("♻️ Stack agotado. Reequipando comida...")
            if equipar_comida():
                print(f"[DEBUG] Esperando {TIEMPO_ESPERA_EQUIPAR}s antes de consumir...")
                time.sleep(TIEMPO_ESPERA_EQUIPAR)
                if consumir_comida():
                    usos_comida = 1
                    stack_agotado = False
                else:
                    print("⚠️ Fallo al consumir después de reequipar.")
                    time.sleep(10)
                    continue
            else:
                print("⚠️ No se pudo reequipar comida. Reintentando en 10s...")
                time.sleep(10)
                continue
        else:
            print(f"[DEBUG] Esperando {TIEMPO_ENTRE_USO}s para usar comida (uso {usos_comida + 1}/{MAX_USOS_POR_STACK})...")
            time.sleep(TIEMPO_ENTRE_USO)
            if consumir_comida():
                usos_comida += 1
                if usos_comida >= MAX_USOS_POR_STACK:
                    print("[DEBUG] Stack agotado tras el último uso. Esperando antes de reequipar...")
                    time.sleep(2)
                    stack_agotado = True
            else:
                print("⚠️ Falló el intento de consumir comida.")
                time.sleep(5)

if __name__ == "__main__":
    print("⏳ Tenés 5 segundos para posicionar la ventana de Albion...")
    time.sleep(5)
    if preparar_comida():
        usos_comida = 1
        iniciar_comida()
    else:
        print("❌ No se pudo preparar la comida. Cerrando script.")
