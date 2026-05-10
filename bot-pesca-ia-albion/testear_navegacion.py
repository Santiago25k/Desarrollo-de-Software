"""
Test standalone de navegacion por agua (hold click izquierdo).

Uso:
    python testear_navegacion.py           # navega hasta el agua
    python testear_navegacion.py --orilla  # navega al agua + recorre orilla
    python testear_navegacion.py --dry-run # mueve cursor sin presionar boton

F4 para detener en cualquier momento.
"""
import math
import sys
import threading
import time

import keyboard
import pyautogui
import pydirectinput

from src.navigation.minimap import get_water_direction, is_at_water
from src.config import (
    NAV_CLICK_DISTANCIA, NAV_DURACION_HOLD,
    NAV_STUCK_INTENTOS, SCREEN_WIDTH, SCREEN_HEIGHT,
)

_CENTRO_X = SCREEN_WIDTH  // 2
_CENTRO_Y = SCREEN_HEIGHT // 2
_stop     = threading.Event()


def _setup_stop():
    keyboard.add_hotkey('f4', lambda: (_stop.set(), print("\n[F4] Deteniendo...")))


def _pos(dx, dy):
    return (int(_CENTRO_X + dx * NAV_CLICK_DISTANCIA),
            int(_CENTRO_Y + dy * NAV_CLICK_DISTANCIA))


def _mover(dx, dy, dry_run=False):
    cx, cy = _pos(dx, dy)
    pyautogui.moveTo(cx, cy)
    if not dry_run:
        pydirectinput.mouseDown(button='right')
    time.sleep(NAV_DURACION_HOLD)
    if not dry_run:
        pydirectinput.mouseUp(button='right')


def _rotar(dx, dy, grados):
    rad = math.radians(grados)
    return (dx * math.cos(rad) - dy * math.sin(rad),
            dx * math.sin(rad) + dy * math.cos(rad))


def _esta_atascado(historial, dx, dy):
    historial.append((dx, dy))
    if len(historial) > NAV_STUCK_INTENTOS:
        historial.pop(0)
    if len(historial) < NAV_STUCK_INTENTOS:
        return False
    for hx, hy in historial[:-1]:
        if hx * dx + hy * dy < 0.92:
            return False
    return True


def navegar_al_agua(dry_run=False):
    print("Navegando al agua (hold click izquierdo)...")
    historial  = []
    evasion    = 0
    ultima_dir = None
    inicio     = time.time()

    try:
        while not _stop.is_set():
            if time.time() - inicio > 180:
                print("\nTimeout.")
                return False

            if is_at_water():
                print("\nAgua alcanzada.")
                return True

            direccion = get_water_direction()

            if direccion is None:
                if ultima_dir:
                    print(f"  Sin agua — inercia              ", end="\r")
                    _mover(*ultima_dir, dry_run=dry_run)
                else:
                    time.sleep(0.3)
                continue

            dx, dy = direccion
            if dx == 0.0 and dy == 0.0:
                print("\nJugador en agua.")
                return True

            ultima_dir = (dx, dy)
            estado = "OK"

            if evasion > 0:
                dx, dy = _rotar(dx, dy, 90)
                evasion -= 1
                estado = f"EVASION({evasion})"
            elif _esta_atascado(historial, dx, dy):
                evasion = 4
                historial.clear()
                estado = "ATASCADO"

            cx, cy = _pos(dx, dy)
            print(f"  [{estado}] dir=({dx:+.2f},{dy:+.2f})  cursor=({cx},{cy})   ", end="\r")
            _mover(dx, dy, dry_run=dry_run)

    finally:
        pydirectinput.mouseUp(button='right')

    return False


def recorrer_orilla(dry_run=False):
    print("\nRecorriendo orilla... (F4 para detener)")
    sentido  = 1
    sin_agua = 0
    inicio   = time.time()

    try:
        while not _stop.is_set():
            if time.time() - inicio > 120:
                print("\nTimeout orilla.")
                return

            # TODO Fase 3: detectar spot → break

            direccion = get_water_direction()

            if direccion is None or (direccion[0] == 0.0 and direccion[1] == 0.0):
                print(f"  [ORILLA] paralela sentido={sentido}   ", end="\r")
                _mover(sentido * 1.0, 0.0, dry_run=dry_run)
                sin_agua = 0
                continue

            dx, dy = direccion
            sin_agua += 1

            if sin_agua > 3:
                print(f"  [ORILLA] volviendo al agua            ", end="\r")
                _mover(dx, dy, dry_run=dry_run)
                sin_agua = 0
            else:
                perp_x, perp_y = _rotar(dx, dy, 90 * sentido)
                print(f"  [ORILLA] perp=({perp_x:+.2f},{perp_y:+.2f})    ", end="\r")
                _mover(perp_x, perp_y, dry_run=dry_run)
    finally:
        pydirectinput.mouseUp(button='right')


if __name__ == "__main__":
    dry_run    = "--dry-run" in sys.argv
    con_orilla = "--orilla"  in sys.argv
    modo       = "DRY-RUN (sin clicks)" if dry_run else "ACTIVO"

    print(f"Modo: {modo}  |  hold={NAV_DURACION_HOLD}s  |  dist={NAV_CLICK_DISTANCIA}px")
    print("F4 = detener en cualquier momento")
    print("Cambia a Albion Online en 3 segundos...\n")

    _setup_stop()
    time.sleep(3)

    try:
        llego = navegar_al_agua(dry_run=dry_run)
        if llego and con_orilla and not _stop.is_set():
            recorrer_orilla(dry_run=dry_run)
    except KeyboardInterrupt:
        pass
    finally:
        pydirectinput.mouseUp(button='right')
        print("\nDetenido.")
