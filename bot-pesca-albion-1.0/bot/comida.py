import pyautogui
import time
from cebo import aplicar_cebo
import os
import sys

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

TIEMPO_ENTRE_USO = 1800
MAX_USOS_POR_STACK = 10
TIEMPO_ESPERA_EQUIPAR = 11
comida_en_uso = False
usos_comida = 0

def equipar_comida():
    print("🔍 Buscando comida en el inventario para equipar...")
    ubicacion = pyautogui.locateCenterOnScreen(resource_path('img/comida.png'), confidence=0.8)
    if ubicacion:
        print(f"✅ Comida encontrada en: {ubicacion}")
        pyautogui.moveTo(ubicacion, duration=0.3)
        pyautogui.click(button='right')
        print("✅ Comida equipada correctamente.")
        return True
    else:
        print("❌ No se encontró comida en el inventario.")
        return False

def preparar_comida():
    if equipar_comida():
        print(f"⏳ Esperando {TIEMPO_ESPERA_EQUIPAR} segundos antes de usarla...")
        time.sleep(TIEMPO_ESPERA_EQUIPAR)
        pyautogui.press('2')
        print("✅ Comida usada (inicio del bot).")

def iniciar_comida():
    global comida_en_uso, usos_comida
    while True:
        if usos_comida >= MAX_USOS_POR_STACK:
            print("♻️ Stack terminado. Reequipando comida...")
            if equipar_comida():
                print(f"⌛ Esperando {TIEMPO_ESPERA_EQUIPAR} segundos para usar...")
                time.sleep(TIEMPO_ESPERA_EQUIPAR)
                comida_en_uso = True
                pyautogui.press('2')
                time.sleep(4)
                aplicar_cebo()
                usos_comida = 1
                comida_en_uso = False
            else:
                print("⚠️ No se pudo reequipar comida.")
                time.sleep(60)
                continue
        else:
            time.sleep(TIEMPO_ENTRE_USO)
            comida_en_uso = True
            print(f"🔄 Usando comida (uso {usos_comida + 1}/{MAX_USOS_POR_STACK})...")
            pyautogui.press('2')
            time.sleep(4)
            aplicar_cebo()
            usos_comida += 1
            comida_en_uso = False
