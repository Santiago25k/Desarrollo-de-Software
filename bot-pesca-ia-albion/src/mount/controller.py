import time
import pyautogui

from src.config import TECLA_MONTURA, TIEMPO_MONTAR, TIEMPO_DESMONTAR


def montar(log_callback=print):
    """Presiona la tecla de montura y espera el cast."""
    log_callback("Montando...")
    pyautogui.press(TECLA_MONTURA)
    time.sleep(TIEMPO_MONTAR)
    log_callback("Montado.")


def desmontar(log_callback=print):
    """Presiona la tecla de montura para desmontar."""
    log_callback("Desmontando...")
    pyautogui.press(TECLA_MONTURA)
    time.sleep(TIEMPO_DESMONTAR)
    log_callback("Desmontado.")
