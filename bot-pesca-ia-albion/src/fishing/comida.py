import time
import pyautogui

from .funciones_utiles import img_path
from src.config import TECLA_COMIDA, TIEMPO_ESPERA_EQUIP

MAX_USOS_POR_STACK = 10


def equipar_comida(log_callback=print) -> bool:
    log_callback("Buscando comida en inventario...")
    nombres = ['comida.PNG'] + [f'comida{i}.PNG' for i in range(1, 12)]

    for nombre in nombres:
        ruta = img_path(nombre)
        try:
            ubicacion = pyautogui.locateCenterOnScreen(ruta, confidence=0.8)
        except pyautogui.ImageNotFoundException:
            ubicacion = None

        if ubicacion:
            pyautogui.moveTo(ubicacion, duration=0.3)
            pyautogui.click(button='right')
            log_callback("Comida encontrada y equipada.")
            return True

    log_callback("No se encontro comida en el inventario.")
    return False


def consumir_comida(log_callback=print) -> bool:
    pyautogui.press(TECLA_COMIDA)
    log_callback("Comida consumida.")
    return True


def preparar_comida(log_callback=print) -> bool:
    if not equipar_comida(log_callback):
        return False
    log_callback(f"Esperando {TIEMPO_ESPERA_EQUIP}s antes de usar comida...")
    time.sleep(TIEMPO_ESPERA_EQUIP)
    return consumir_comida(log_callback)
