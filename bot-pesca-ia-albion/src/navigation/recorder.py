"""
Grabador de waypoints para la ruta de navegacion.

Uso:
    python -m src.navigation.recorder <nombre_ruta>

Controles durante la grabacion:
    F2  — graba la posicion actual del mouse (debe estar sobre el minimapa)
    F3  — graba la posicion detectada del jugador en el minimapa (automatica)
    ESC — guarda y termina

Los puntos se guardan en waypoints/<nombre_ruta>.json
"""

import sys
import time
import pyautogui
import keyboard

from src.config import REGION_MINIMAP
from .waypoints import guardar
from .minimap import get_player_pos


def _en_minimapa(x: int, y: int) -> bool:
    r = REGION_MINIMAP
    return r['left'] <= x < r['left'] + r['width'] and r['top'] <= y < r['top'] + r['height']


def grabar(nombre: str):
    puntos = []
    mm = REGION_MINIMAP

    print(f"\nGrabando ruta '{nombre}'")
    print(f"  Minimapa en: left={mm['left']} top={mm['top']} {mm['width']}x{mm['height']}px")
    print("  F2  → grabar posicion del mouse sobre el minimapa")
    print("  F3  → grabar posicion del jugador detectada automaticamente")
    print("  ESC → guardar y salir\n")

    while True:
        if keyboard.is_pressed('f2'):
            mx, my = pyautogui.position()
            if _en_minimapa(mx, my):
                rx, ry = mx - mm['left'], my - mm['top']
                puntos.append({"x": rx, "y": ry})
                print(f"  [{len(puntos)}] Mouse grabado: ({rx}, {ry})")
            else:
                print("  [!] El cursor no esta sobre el minimapa.")
            time.sleep(0.35)

        elif keyboard.is_pressed('f3'):
            pos = get_player_pos()
            if pos:
                puntos.append({"x": pos[0], "y": pos[1]})
                print(f"  [{len(puntos)}] Jugador detectado: ({pos[0]}, {pos[1]})")
            else:
                print("  [!] No se pudo detectar al jugador en el minimapa.")
            time.sleep(0.35)

        elif keyboard.is_pressed('esc'):
            break

        time.sleep(0.05)

    if puntos:
        path = guardar(nombre, puntos)
        print(f"\nRuta guardada: {path} ({len(puntos)} waypoints)")
    else:
        print("\nNo se grabo ningun punto.")


if __name__ == "__main__":
    nombre = sys.argv[1] if len(sys.argv) > 1 else "ruta_default"
    grabar(nombre)
