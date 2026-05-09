import os
import sys
import pyautogui


def resource_path(relative_path: str) -> str:
    """Resuelve rutas tanto en desarrollo como en ejecutable PyInstaller."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def img_path(nombre: str) -> str:
    """Devuelve la ruta absoluta a una imagen en la carpeta img/ del proyecto."""
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(raiz, 'img', nombre)


def mover_y_clickear(nombre_imagen: str, descripcion: str, log_callback=print) -> bool:
    """
    Busca una imagen en pantalla y hace click en ella.
    nombre_imagen: nombre del archivo dentro de img/ (ej: 'cebo.PNG')
    Retorna True si encontro y clickeo, False si no.
    """
    ruta = img_path(nombre_imagen)
    try:
        ubicacion = pyautogui.locateCenterOnScreen(ruta, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        ubicacion = None

    if ubicacion:
        pyautogui.moveTo(ubicacion, duration=0.3)
        pyautogui.click()
        return True

    log_callback(f"[IMG] No encontrado: {descripcion} ({nombre_imagen})")
    return False
