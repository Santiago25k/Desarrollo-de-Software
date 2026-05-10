"""
Recorre el rio por el minimapa y graba/pesca spots de pesca.

Modos:
    python recorrer_spots.py --explorar [--nombre willowfish_marsh]
        Bot camina el rio. Presiona F3 cuando veas un spot para marcarlo.
        F4 para terminar y guardar.

    python recorrer_spots.py [--nombre willowfish_marsh] [--dry-run]
        Bot camina el rio y pesca en los spots grabados.
        F4 para detener.
"""
import json
import math
import os
import queue
import sys
import threading
import time

import cv2
import keyboard
import numpy as np
import pyautogui
import pydirectinput

from src.config import (
    REGION_MINIMAP, NAV_CLICK_DISTANCIA, NAV_DURACION_HOLD,
    SCREEN_WIDTH, SCREEN_HEIGHT, TIEMPO_LANZO,
)
from src.navigation.minimap import get_water_direction, is_at_water

WAYPOINTS_DIR = "waypoints"
_CENTRO_X     = SCREEN_WIDTH  // 2
_CENTRO_Y     = SCREEN_HEIGHT // 2
_UMBRAL_SPOT  = 0.65   # similitud minima del minimapa para reconocer un spot
_COOLDOWN_SEG = 60     # segundos sin volver a pescar en el mismo spot

_STOP  = threading.Event()
_PAUSA = threading.Event()   # set = navegacion pausada (mientras se marca un spot)


# ── Movimiento ────────────────────────────────────────────────────────────────

def _rotar(dx: float, dy: float, grados: float) -> tuple:
    rad = math.radians(grados)
    return (dx * math.cos(rad) - dy * math.sin(rad),
            dx * math.sin(rad) + dy * math.cos(rad))


def _mover_paso(dx: float, dy: float, dry_run: bool = False):
    cx = int(_CENTRO_X + dx * NAV_CLICK_DISTANCIA)
    cy = int(_CENTRO_Y + dy * NAV_CLICK_DISTANCIA)
    pyautogui.moveTo(cx, cy)
    if not dry_run:
        pydirectinput.mouseDown(button='right')
    fin = time.time() + NAV_DURACION_HOLD
    while not _STOP.is_set() and not _PAUSA.is_set() and time.time() < fin:
        time.sleep(0.05)
    if not dry_run:
        pydirectinput.mouseUp(button='right')


# ── Minimap ───────────────────────────────────────────────────────────────────

def _minimap_completo() -> np.ndarray:
    r    = REGION_MINIMAP
    shot = pyautogui.screenshot(region=(r['left'], r['top'], r['width'], r['height']))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def _minimap_crop_centro() -> np.ndarray:
    """Recorte 150x150 del centro del minimapa — referencia de posicion del jugador."""
    mm     = _minimap_completo()
    h, w   = mm.shape[:2]
    cy, cx = h // 2, w // 2
    r      = 75
    return mm[max(0, cy - r):cy + r, max(0, cx - r):cx + r]


def _similitud_spot(ref_path: str) -> float:
    """Busca la referencia guardada dentro del minimapa actual. Retorna 0-1."""
    ref = cv2.imread(ref_path)
    if ref is None:
        return 0.0
    mm        = _minimap_completo()
    rh, rw    = ref.shape[:2]
    mh, mw    = mm.shape[:2]
    if rh > mh or rw > mw:
        return 0.0
    result    = cv2.matchTemplate(mm, ref, cv2.TM_CCOEFF_NORMED)
    _, maxv, _, _ = cv2.minMaxLoc(result)
    return float(maxv)


# ── Navegacion compartida ─────────────────────────────────────────────────────

def _ir_al_agua(dry_run: bool):
    print("[NAV] Navegando al agua...")
    ultima_dir = None
    while not _STOP.is_set() and not is_at_water():
        if _PAUSA.is_set():
            time.sleep(0.05)
            continue
        direccion = get_water_direction()
        if direccion is None:
            if ultima_dir:
                _mover_paso(*ultima_dir, dry_run)
            else:
                time.sleep(0.1)
            continue
        dx, dy = direccion
        if dx == 0.0 and dy == 0.0:
            break
        ultima_dir = (dx, dy)
        _mover_paso(dx, dy, dry_run)
    if not _STOP.is_set():
        print("[NAV] Agua alcanzada.")


def _paso_orilla(sentido: int, sin_agua: int, dry_run: bool) -> int:
    """Ejecuta un paso a lo largo de la orilla. Retorna sin_agua actualizado."""
    direccion = get_water_direction()
    if direccion is None or (direccion[0] == 0.0 and direccion[1] == 0.0):
        _mover_paso(float(sentido), 0.0, dry_run)
        return 0
    dx, dy    = direccion
    sin_agua += 1
    if sin_agua > 3:
        _mover_paso(dx, dy, dry_run)
        return 0
    perp_x, perp_y = _rotar(dx, dy, 90.0 * sentido)
    _mover_paso(perp_x, perp_y, dry_run)
    return sin_agua


# ── Pesca ─────────────────────────────────────────────────────────────────────

def _pescar(spot: dict, dry_run: bool):
    cast_x    = spot["cast_x"]
    cast_y    = spot["cast_y"]
    timeout   = spot.get("timeout", 120)
    reintentos = spot.get("reintentos", 3)
    nombre    = spot.get("nombre", f"spot_{spot['id']}")

    print(f"  [PESCANDO] {nombre}  cast=({cast_x},{cast_y})")
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
        # Esperar picada — se integrara el detector de bobber en la siguiente fase
        print(f"    Esperando picada ({timeout}s)...")
        inicio = time.time()
        while not _STOP.is_set() and time.time() - inicio < timeout:
            time.sleep(0.1)
    print(f"  Terminado {nombre}.")


# ── Loop explorar (hilo de fondo) ─────────────────────────────────────────────

def _loop_explorar(dry_run: bool):
    _ir_al_agua(dry_run)
    if _STOP.is_set():
        return

    sentido  = 1
    sin_agua = 0
    print("[NAV] Recorriendo orilla — F3 en cada spot, F4 para terminar.")

    while not _STOP.is_set():
        if _PAUSA.is_set():
            pydirectinput.mouseUp(button='right')
            time.sleep(0.05)
            continue
        sin_agua = _paso_orilla(sentido, sin_agua, dry_run)

    pydirectinput.mouseUp(button='right')


# ── Loop pesca (hilo de fondo) ────────────────────────────────────────────────

def _loop_pesca(spots: list, dry_run: bool):
    _ir_al_agua(dry_run)
    if _STOP.is_set():
        return

    sentido   = 1
    sin_agua  = 0
    cooldown: dict = {}
    print("[NAV] Recorriendo orilla en modo pesca — F4 para detener.")

    while not _STOP.is_set():
        # Verificar spots antes de cada paso
        ahora   = time.time()
        pescado = False
        for spot in spots:
            ref = spot.get("minimap_ref", "")
            if not ref or not os.path.exists(ref):
                continue
            if ahora < cooldown.get(spot["id"], 0):
                continue
            sim = _similitud_spot(ref)
            if sim >= _UMBRAL_SPOT:
                print(f"\n[SPOT] {spot['nombre']} detectado (similitud={sim:.2f})")
                pydirectinput.mouseUp(button='right')
                _pescar(spot, dry_run)
                cooldown[spot["id"]] = time.time() + _COOLDOWN_SEG
                pescado = True
                break

        if _STOP.is_set():
            break
        if not pescado:
            sin_agua = _paso_orilla(sentido, sin_agua, dry_run)

    pydirectinput.mouseUp(button='right')


# ── UI de marcado de spots (hilo principal) ───────────────────────────────────

def _manejar_f3(nombre: str, spots: list, cmd_queue: queue.Queue):
    """Corre en el hilo principal. Procesa F3 del queue y abre ventanas CV2."""
    while not _STOP.is_set():
        try:
            cmd = cmd_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        if cmd != "spot":
            continue

        _PAUSA.set()
        time.sleep(0.35)   # esperar que el personaje frene y la camara se estabilice

        spot_id = len(spots) + 1
        print(f"\n[F3] Spot #{spot_id} — hace click sobre el spot en la pantalla, luego ENTER")

        # Captura de pantalla completa
        shot   = pyautogui.screenshot()
        frame  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        h, w   = frame.shape[:2]
        escala = min(1.0, 1280 / w, 720 / h)
        if escala < 1.0:
            frame = cv2.resize(frame, (int(w * escala), int(h * escala)))

        # Guardar referencia del minimapa
        mm_crop = _minimap_crop_centro()
        os.makedirs(WAYPOINTS_DIR, exist_ok=True)
        mm_path = os.path.join(WAYPOINTS_DIR, f"{nombre}_spot{spot_id}_mm.png")
        cv2.imwrite(mm_path, mm_crop)

        # Ventana de seleccion del spot
        click_pos = [None]

        def on_click(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                click_pos[0] = (x, y)

        ventana = f"Spot #{spot_id} — click izquierdo sobre el spot, ENTER confirma (ESC cancela)"
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
        fh, fw = frame.shape[:2]
        cv2.resizeWindow(ventana, min(fw, 1280), min(fh, 720))
        cv2.setMouseCallback(ventana, on_click)

        disp = frame.copy()
        cv2.putText(disp, f"Spot #{spot_id}: click izquierdo sobre el spot -> ENTER",
                    (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        cv2.imshow(ventana, disp)

        guardado = False
        while not _STOP.is_set():
            key = cv2.waitKey(50) & 0xFF
            if click_pos[0]:
                px, py = click_pos[0]
                d2 = frame.copy()
                cv2.circle(d2, (px, py), 14, (0, 255, 0), 3)
                cv2.circle(d2, (px, py),  5, (0, 255, 0), -1)
                cv2.putText(d2, "ENTER confirma  |  click para reposicionar  |  ESC cancela",
                            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)
                cv2.imshow(ventana, d2)
            if key == 13 and click_pos[0]:   # ENTER
                cast_x = round(click_pos[0][0] / escala)
                cast_y = round(click_pos[0][1] / escala)
                spot   = {
                    "id":          spot_id,
                    "nombre":      f"spot_{spot_id}",
                    "minimap_ref": mm_path,
                    "cast_x":      cast_x,
                    "cast_y":      cast_y,
                    "timeout":     120,
                    "reintentos":  3,
                }
                spots.append(spot)
                print(f"  Spot #{spot_id} guardado en ({cast_x}, {cast_y})")
                guardado = True
                break
            if key == 27:   # ESC
                print("  Cancelado.")
                break

        cv2.destroyWindow(ventana)

        if not guardado and os.path.exists(mm_path):
            os.remove(mm_path)

        _PAUSA.clear()


# ── Modos principales ─────────────────────────────────────────────────────────

def modo_explorar(nombre: str, dry_run: bool):
    spots: list = []
    cmd_queue   = queue.Queue()
    json_path   = os.path.join(WAYPOINTS_DIR, f"{nombre}_spots.json")

    print(f"\n=== Modo explorar: {nombre} ===")
    print("  El bot navega al agua y recorre la orilla automaticamente.")
    print("  Cuando veas un spot de pesca presiona F3.")
    print("  F4 para terminar y guardar.\n")
    print("  Iniciando en 3 segundos — cambia a Albion Online...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    keyboard.add_hotkey("f3", lambda: cmd_queue.put("spot"))
    keyboard.add_hotkey("f4", _STOP.set)

    nav = threading.Thread(target=_loop_explorar, args=(dry_run,), daemon=True)
    nav.start()

    _manejar_f3(nombre, spots, cmd_queue)   # bloquea hasta F4

    nav.join(timeout=2)
    keyboard.unhook_all()

    if spots:
        os.makedirs(WAYPOINTS_DIR, exist_ok=True)
        data = {"nombre": nombre, "spots": spots}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n  {len(spots)} spot(s) guardados en: {json_path}")
        print(f"  Para pescar: python recorrer_spots.py --nombre {nombre}")
    else:
        print("\n  Sin spots grabados.")


def modo_pesca(nombre: str, dry_run: bool):
    json_path = os.path.join(WAYPOINTS_DIR, f"{nombre}_spots.json")
    if not os.path.exists(json_path):
        print(f"No hay spots grabados para '{nombre}'.")
        print(f"Corré primero:  python recorrer_spots.py --explorar --nombre {nombre}")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    spots = data.get("spots", [])

    modo = "DRY-RUN" if dry_run else "ACTIVO"
    print(f"\n=== Modo pesca: {nombre} [{modo}] ===")
    print(f"  Spots cargados: {len(spots)}")
    for s in spots:
        print(f"    #{s['id']} {s['nombre']}  cast=({s['cast_x']},{s['cast_y']})")
    print("\n  F4 para detener.")
    print("  Iniciando en 3 segundos — cambia a Albion Online...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    keyboard.add_hotkey("f4", _STOP.set)

    try:
        _loop_pesca(spots, dry_run)
    finally:
        pydirectinput.mouseUp(button='right')
        pydirectinput.mouseUp(button='left')
        keyboard.unhook_all()

    print("\n  Detenido." if _STOP.is_set() else "\n  Completado.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    explorar = "--explorar" in sys.argv
    dry_run  = "--dry-run"  in sys.argv

    nombre = "spots"
    args   = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--nombre" and i + 1 < len(args):
            nombre = args[i + 1]
            i += 2
        elif a.startswith("--nombre="):
            nombre = a.split("=", 1)[1]
            i += 1
        elif not a.startswith("--"):
            nombre = a
            i += 1
        else:
            i += 1

    if explorar:
        modo_explorar(nombre, dry_run)
    else:
        modo_pesca(nombre, dry_run)


if __name__ == "__main__":
    main()
