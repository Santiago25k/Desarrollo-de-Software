import pyautogui
import time
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def mover_y_clickear(imagen_relativa, nombre):
    ruta_imagen = resource_path(imagen_relativa)
    print(f"Buscando {nombre} en {ruta_imagen}...")
    ubicacion = pyautogui.locateCenterOnScreen(ruta_imagen, confidence=0.8)
    if ubicacion:
        print(f"{nombre} encontrado en: {ubicacion}")
        pyautogui.moveTo(ubicacion, duration=0.5)
        pyautogui.click()
        print(f"{nombre} clickeado.")
        return True
    else:
        print(f"No se encontró {nombre}.")
        return False
