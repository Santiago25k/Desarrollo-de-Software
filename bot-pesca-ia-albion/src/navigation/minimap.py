import cv2
import numpy as np
import pyautogui

from src.config import (
    REGION_MINIMAP,
    MINIMAP_JUGADOR_LOW, MINIMAP_JUGADOR_HIGH,
    MINIMAP_AGUA_LOW, MINIMAP_AGUA_HIGH,
    NAV_AGUA_RADIO,
)

_LOW       = np.array(MINIMAP_JUGADOR_LOW)
_HIGH      = np.array(MINIMAP_JUGADOR_HIGH)
_AGUA_LOW  = np.array(MINIMAP_AGUA_LOW)
_AGUA_HIGH = np.array(MINIMAP_AGUA_HIGH)

_CENTRO_X = REGION_MINIMAP['width']  // 2
_CENTRO_Y = REGION_MINIMAP['height'] // 2


def _capturar() -> np.ndarray:
    r = REGION_MINIMAP
    shot = pyautogui.screenshot(region=(r['left'], r['top'], r['width'], r['height']))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def get_player_pos() -> tuple | None:
    """Retorna (x, y) de la flecha del jugador en pixeles relativos al minimapa, o None."""
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


def get_water_direction() -> tuple | None:
    """
    Detecta agua en el minimapa y retorna la direccion normalizada (dx, dy)
    desde el centro (jugador) hacia el area de agua mas grande.
    Retorna (0.0, 0.0) si el jugador ya esta en el agua, None si no hay agua visible.
    """
    frame = _capturar()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, _AGUA_LOW, _AGUA_HIGH)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    best = max(contours, key=cv2.contourArea)
    if cv2.contourArea(best) < 20:
        return None

    M = cv2.moments(best)
    if M["m00"] == 0:
        return None

    agua_x = int(M["m10"] / M["m00"])
    agua_y = int(M["m01"] / M["m00"])

    dx = agua_x - _CENTRO_X
    dy = agua_y - _CENTRO_Y
    mag = (dx ** 2 + dy ** 2) ** 0.5

    if mag < 8:
        return (0.0, 0.0)

    return (dx / mag, dy / mag)


def is_at_water() -> bool:
    """Retorna True si hay agua detectada alrededor del centro del minimapa (jugador en agua)."""
    frame = _capturar()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, _AGUA_LOW, _AGUA_HIGH)

    r = NAV_AGUA_RADIO
    region = mask[
        max(0, _CENTRO_Y - r): _CENTRO_Y + r,
        max(0, _CENTRO_X - r): _CENTRO_X + r,
    ]
    return cv2.countNonZero(region) > 20


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
            cv2.putText(frame, str(pos), (pos[0] + 6, pos[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        display = cv2.hconcat([frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])
        cv2.imshow(ventana, display)
        if cv2.waitKey(50) == 27:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print(f"REGION_MINIMAP: {REGION_MINIMAP}")
    print("Abriendo debug... presiona ESC para salir.")
    debug_ventana()
