import time
import os
import cv2
import mss
import numpy as np
import win32gui
import pyautogui
from datetime import datetime

# =============================
# CONFIGURACIÓN
# =============================
WINDOW_NAME = "Albion Online Client"
CAPTURE_INTERVAL = 1 * 60  # cada 10 minutos
MOUSE_INTERVAL = 30 * 60  # cada 5 minutos
SAVE_DIR = "out"

os.makedirs(SAVE_DIR, exist_ok=True)


# =============================
# CLASE DE CAPTURA
# =============================
class ScreenCapture:
    def __init__(self, window_name):
        self.window_name = window_name
        self.sct = mss.mss()
        self.hwnd = win32gui.FindWindow(None, window_name)

        if not self.hwnd:
            raise RuntimeError(f"No se encontró la ventana: {window_name}")

    def get_window_rect(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        return {
            "left": left,
            "top": top,
            "width": right - left,
            "height": bottom - top,
        }

    def capture(self):
        monitor = self.get_window_rect()
        img = self.sct.grab(monitor)
        return np.array(img)[:, :, :3]  # BGR


# =============================
# FUNCIONES AUXILIARES
# =============================
def move_mouse_and_click():
    """Movimiento leve y click para evitar AFK"""
    x, y = pyautogui.position()
    pyautogui.moveTo(x + 10, y + 5, duration=0.2)
    pyautogui.click()  # click primario
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()  # click opcional en la posición original
    print("[✔] Mouse movido y clickeado para evitar AFK.")


def save_image(img):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SAVE_DIR}/capture_{timestamp}.png"
    cv2.imwrite(filename, img)
    print(f"[✔] Imagen guardada: {filename}")


# =============================
# LOOP PRINCIPAL
# =============================
def main():
    print("Iniciando captura automática...")
    print("Presiona CTRL + C para detener")

    capturer = ScreenCapture(WINDOW_NAME)

    last_capture_time = 0
    last_mouse_time = 0

    while True:
        try:
            now = time.time()

            # Captura cada CAPTURE_INTERVAL
            if now - last_capture_time >= CAPTURE_INTERVAL:
                frame = capturer.capture()
                save_image(frame)
                last_capture_time = now

            # Mueve mouse y clickea cada MOUSE_INTERVAL
            if now - last_mouse_time >= MOUSE_INTERVAL:
                move_mouse_and_click()
                last_mouse_time = now

            time.sleep(1)  # espera 1 segundo entre ciclos

        except KeyboardInterrupt:
            print("\n[INFO] Captura detenida por el usuario.")
            break

        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
