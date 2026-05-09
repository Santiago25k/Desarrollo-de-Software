import cv2
import numpy as np
import pyautogui

from src.config import REGION_MINIMAP, MINIMAP_JUGADOR_LOW, MINIMAP_JUGADOR_HIGH

_LOW  = np.array(MINIMAP_JUGADOR_LOW)
_HIGH = np.array(MINIMAP_JUGADOR_HIGH)


def _capturar() -> np.ndarray:
    r = REGION_MINIMAP
    shot = pyautogui.screenshot(region=(r['left'], r['top'], r['width'], r['height']))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def get_player_pos() -> tuple | None:
    """
    Detecta el punto del jugador en el minimapa.
    Retorna (x, y) en pixeles relativos a REGION_MINIMAP, o None si no se detecta.
    """
    frame = _capturar()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, _LOW, _HIGH)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    best = max(contours, key=cv2.contourArea)
    if cv2.contourArea(best) < 2:
        return None
    x, y, w, h = cv2.boundingRect(best)
    return (x + w // 2, y + h // 2)


def distancia(a: tuple, b: tuple) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def debug_ventana():
    """Muestra el minimapa con deteccion en tiempo real. Presiona ESC para salir."""
    ventana = "Minimap debug"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, REGION_MINIMAP['width'] * 3, REGION_MINIMAP['height'] * 3)
    while True:
        frame = _capturar()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, _LOW, _HIGH)
        pos = get_player_pos()
        if pos:
            cv2.circle(frame, pos, 5, (0, 255, 0), -1)
            cv2.putText(frame, str(pos), (pos[0] + 6, pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        display = cv2.hconcat([frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])
        cv2.imshow(ventana, display)
        if cv2.waitKey(50) == 27:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print(f"REGION_MINIMAP: {REGION_MINIMAP}")
    print("Abriendo debug... presiona ESC para salir.")
    debug_ventana()
