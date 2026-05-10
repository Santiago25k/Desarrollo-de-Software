"""
Ejecuta una ruta de pesca grabada.

Uso:
    python ejecutar_ruta.py <nombre_mapa>
    python ejecutar_ruta.py willowfish_marsh
    python ejecutar_ruta.py willowfish_marsh --dry-run   # mueve cursor, sin clicks reales
    python ejecutar_ruta.py willowfish_marsh --loop      # repite la ruta al terminar

F4 para detener en cualquier momento.
"""
import json
import os
import sys
import threading
import time

import cv2
import keyboard
import numpy as np
import pyautogui
import pydirectinput

from src.config import (
    REGION_MINIMAP, SCREEN_WIDTH, SCREEN_HEIGHT, TIEMPO_LANZO,
)

WAYPOINTS_DIR  = "waypoints"
_CENTRO_X      = SCREEN_WIDTH  // 2
_CENTRO_Y      = SCREEN_HEIGHT // 2
_STOP          = threading.Event()
_UMBRAL_INICIO = 0.60   # similitud minima del minimapa para confirmar punto de inicio


# ── Minimap ───────────────────────────────────────────────────────────────────

def _capturar_minimap() -> np.ndarray:
    r    = REGION_MINIMAP
    shot = pyautogui.screenshot(region=(r['left'], r['top'], r['width'], r['height']))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def verificar_inicio(ref_path: str) -> bool:
    """
    Busca la imagen de referencia dentro del minimapa actual.
    Retorna True si la similitud supera el umbral.
    """
    if not os.path.exists(ref_path):
        print("  [AVISO] No hay imagen de referencia — saltando verificacion.")
        return True

    ref     = cv2.imread(ref_path)
    minimap = _capturar_minimap()

    rh, rw = ref.shape[:2]
    mh, mw = minimap.shape[:2]
    if rh > mh or rw > mw:
        print("  [AVISO] Referencia mas grande que el minimapa — saltando verificacion.")
        return True

    result = cv2.matchTemplate(minimap, ref, cv2.TM_CCOEFF_NORMED)
    _, maxv, _, _ = cv2.minMaxLoc(result)
    print(f"  Similitud punto de inicio: {maxv:.2f}  (minimo={_UMBRAL_INICIO})")
    return maxv >= _UMBRAL_INICIO


# ── Ejecucion de pasos ────────────────────────────────────────────────────────

def _mover(dx: float, dy: float, duracion: float, dry_run: bool):
    cx = int(_CENTRO_X + dx * 300)
    cy = int(_CENTRO_Y + dy * 300)
    pyautogui.moveTo(cx, cy)
    if not dry_run:
        pydirectinput.mouseDown(button='right')
    tiempo_fin = time.time() + duracion
    while not _STOP.is_set() and time.time() < tiempo_fin:
        time.sleep(0.05)
    if not dry_run:
        pydirectinput.mouseUp(button='right')


def _pescar_en_spot(spot: dict, dry_run: bool):
    cast_x    = spot["cast_x"]
    cast_y    = spot["cast_y"]
    timeout   = spot.get("timeout", 120)
    reintentos = spot.get("reintentos", 3)
    nombre    = spot.get("nombre", f"spot_{spot['id']}")

    print(f"\n  [SPOT] {nombre}  cast=({cast_x},{cast_y})  reintentos={reintentos}")

    for intento in range(1, reintentos + 1):
        if _STOP.is_set():
            return

        print(f"    Intento {intento}/{reintentos} — lanzando linea...")

        pyautogui.moveTo(cast_x, cast_y)
        if not dry_run:
            pydirectinput.mouseDown(button='left')
            fin_cast = time.time() + TIEMPO_LANZO
            while not _STOP.is_set() and time.time() < fin_cast:
                time.sleep(0.05)
            pydirectinput.mouseUp(button='left')
        else:
            time.sleep(0.5)

        if _STOP.is_set():
            return

        # Esperar picada hasta timeout
        # NOTA: aqui se integrara el detector de bobber en la Fase siguiente
        print(f"    Esperando picada ({timeout}s)... (F4 para detener)")
        inicio = time.time()
        while not _STOP.is_set() and time.time() - inicio < timeout:
            time.sleep(0.1)

        if _STOP.is_set():
            return

        if intento < reintentos:
            print(f"    Sin picada — reintentando...")
        else:
            print(f"    Sin picada — pasando al siguiente paso.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    nombre  = None
    dry_run = "--dry-run" in sys.argv
    loop    = "--loop"    in sys.argv

    for a in sys.argv[1:]:
        if not a.startswith("--"):
            nombre = a
            break

    if nombre is None:
        print("Uso: python ejecutar_ruta.py <nombre_mapa> [--dry-run] [--loop]")
        sys.exit(1)

    json_path = os.path.join(WAYPOINTS_DIR, f"{nombre}.json")
    if not os.path.exists(json_path):
        print(f"Ruta no encontrada: {json_path}")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    modo = "DRY-RUN (sin clicks)" if dry_run else "ACTIVO"
    print(f"\n=== Ejecutar ruta: {data['nombre']} [{modo}] ===")
    print(f"  {data.get('inicio', '')}")
    print(f"  Zoom minimapa: {data.get('zoom', 'cercano')}")
    print(f"  Spots: {len(data['spots'])}   Pasos: {len(data['ruta'])}")
    print(f"  Loop: {'si' if loop else 'no'}")
    print("\n  Verificando punto de inicio...\n")

    keyboard.add_hotkey("f4", lambda: (_STOP.set(), print("\n[F4] Deteniendo...")))

    ref_path = data.get("start_ref", "")
    if not verificar_inicio(ref_path):
        print("\n  [!] No estas en el punto de inicio correcto.")
        print(f"  [!] {data.get('inicio', 'Reposicionate en el punto de inicio.')}")
        print("  [!] Volvé al punto de inicio y ejecutá de nuevo.")
        keyboard.unhook_all()
        sys.exit(1)

    print("  Punto de inicio confirmado.")
    print(f"\n  Iniciando en 3 segundos... (F4 para cancelar)\n")
    for i in range(3, 0, -1):
        if _STOP.is_set():
            keyboard.unhook_all()
            sys.exit(0)
        time.sleep(1)

    spots_map = {s["id"]: s for s in data["spots"]}
    vuelta    = 0

    try:
        while not _STOP.is_set():
            vuelta += 1
            if loop:
                print(f"\n--- Vuelta {vuelta} ---")

            for paso in data["ruta"]:
                if _STOP.is_set():
                    break

                if paso["tipo"] == "mover":
                    print(f"  [MOVER] dx={paso['dx']:+.2f}  dy={paso['dy']:+.2f}  {paso['duracion']}s")
                    _mover(paso["dx"], paso["dy"], paso["duracion"], dry_run)

                elif paso["tipo"] == "spot":
                    spot = spots_map.get(paso["id"])
                    if spot:
                        _pescar_en_spot(spot, dry_run)
                    else:
                        print(f"  [!] Spot id={paso['id']} no encontrado en el JSON.")

            if not loop or _STOP.is_set():
                break

    finally:
        if not dry_run:
            pydirectinput.mouseUp(button='right')
            pydirectinput.mouseUp(button='left')
        keyboard.unhook_all()

    if _STOP.is_set():
        print("\n  Detenido.")
    else:
        print("\n  Ruta completada.")


if __name__ == "__main__":
    main()
