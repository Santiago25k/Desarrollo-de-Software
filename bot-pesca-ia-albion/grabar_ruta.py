"""
Grabador de rutas de pesca.

Uso:
    python grabar_ruta.py willowfish_marsh

Durante la grabacion (con Albion Online abierto):
    Mové con right-click hold normalmente — los movimientos se graban solos
    F3 = marcar spot de pesca (abre ventana para clickar sobre el spot)
    F4 = terminar y guardar

El bot guarda una referencia del minimapa como punto de inicio.
"""
import ctypes
import json
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

from src.config import REGION_MINIMAP, SCREEN_WIDTH, SCREEN_HEIGHT

WAYPOINTS_DIR = "waypoints"
_CENTRO_X     = SCREEN_WIDTH  // 2
_CENTRO_Y     = SCREEN_HEIGHT // 2
_MIN_DURACION = 0.3   # segundos minimos para registrar un movimiento


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_right_down() -> bool:
    return bool(ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000)


def _capturar_pantalla_escalada():
    shot  = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    h, w  = frame.shape[:2]
    escala = min(1.0, 1280 / w, 720 / h)
    if escala < 1.0:
        frame = cv2.resize(frame, (int(w * escala), int(h * escala)))
    return frame, escala


def _capturar_minimap() -> np.ndarray:
    r    = REGION_MINIMAP
    shot = pyautogui.screenshot(region=(r['left'], r['top'], r['width'], r['height']))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def _guardar_ref_minimap(nombre: str) -> str:
    """Recorta 150x150 del centro del minimapa y lo guarda como referencia de inicio."""
    minimap = _capturar_minimap()
    h, w    = minimap.shape[:2]
    cy, cx  = h // 2, w // 2
    radio   = 75
    crop    = minimap[max(0, cy-radio):cy+radio, max(0, cx-radio):cx+radio]
    os.makedirs(WAYPOINTS_DIR, exist_ok=True)
    path = os.path.join(WAYPOINTS_DIR, f"{nombre}_start.png")
    cv2.imwrite(path, crop)
    return path


# ── Grabador de movimientos (hilo de fondo) ───────────────────────────────────

class GrabadorMovimientos:
    def __init__(self):
        self.ruta:  list = []
        self._lock        = threading.Lock()
        self._activo      = True
        self._pausado     = False   # pausa mientras CV2 esta abierto

    def pausar(self):
        self._pausado = True

    def reanudar(self):
        self._pausado = False

    def detener(self):
        self._activo = False

    def loop(self):
        en_movimiento = False
        seg_inicio    = 0.0
        posiciones: list = []

        while self._activo:
            if self._pausado:
                time.sleep(0.05)
                continue

            if _is_right_down():
                if not en_movimiento:
                    en_movimiento = True
                    seg_inicio    = time.time()
                    posiciones    = []
                x, y = pyautogui.position()
                posiciones.append((x, y))
            else:
                if en_movimiento:
                    en_movimiento = False
                    duracion = time.time() - seg_inicio
                    if duracion >= _MIN_DURACION and posiciones:
                        xs = [p[0] for p in posiciones]
                        ys = [p[1] for p in posiciones]
                        ax = sum(xs) / len(xs) - _CENTRO_X
                        ay = sum(ys) / len(ys) - _CENTRO_Y
                        mag = (ax**2 + ay**2) ** 0.5
                        if mag > 0:
                            seg = {
                                "tipo":     "mover",
                                "dx":       round(ax / mag, 3),
                                "dy":       round(ay / mag, 3),
                                "duracion": round(duracion, 2),
                            }
                            with self._lock:
                                self.ruta.append(seg)
                            print(f"  [REC] mover  dx={seg['dx']:+.2f}  dy={seg['dy']:+.2f}  {duracion:.1f}s")

            time.sleep(0.05)


# ── Marcado de spot (hilo principal, para poder abrir CV2) ────────────────────

def _marcar_spot(grabador: GrabadorMovimientos, spots: list) -> bool:
    """
    Congela la pantalla, el usuario clickea sobre el spot, se guarda la posicion.
    Retorna True si el spot fue guardado, False si se cancelo.
    """
    spot_id = len(spots) + 1
    print(f"\n[F3] Spot #{spot_id} — se abre la pantalla congelada.")
    print(f"      Hace click sobre donde esta el spot de pesca, luego ENTER.")

    grabador.pausar()
    time.sleep(0.15)

    frame, escala = _capturar_pantalla_escalada()

    click_pos = [None]

    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            click_pos[0] = (x, y)

    ventana = f"Spot #{spot_id} — click izquierdo sobre el spot, luego ENTER (ESC=cancelar)"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    h, w = frame.shape[:2]
    cv2.resizeWindow(ventana, min(w, 1280), min(h, 720))
    cv2.setMouseCallback(ventana, on_click)

    display = frame.copy()
    cv2.putText(display, f"Spot #{spot_id}: click izquierdo sobre el spot -> ENTER para confirmar",
                (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    cv2.imshow(ventana, display)

    guardado = False
    while True:
        key = cv2.waitKey(50) & 0xFF
        if click_pos[0]:
            px, py = click_pos[0]
            disp2  = frame.copy()
            cv2.circle(disp2, (px, py), 14, (0, 255, 0), 3)
            cv2.circle(disp2, (px, py), 5,  (0, 255, 0), -1)
            cv2.putText(disp2, "ENTER para confirmar  |  click para reposicionar",
                        (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
            cv2.imshow(ventana, disp2)

        if key == 13 and click_pos[0]:   # ENTER confirma
            cast_x = round(click_pos[0][0] / escala)
            cast_y = round(click_pos[0][1] / escala)
            spot   = {
                "id":         spot_id,
                "nombre":     f"spot_{spot_id}",
                "cast_x":     cast_x,
                "cast_y":     cast_y,
                "timeout":    120,
                "reintentos": 3,
            }
            spots.append(spot)
            with grabador._lock:
                grabador.ruta.append({"tipo": "spot", "id": spot_id})
            print(f"  Spot #{spot_id} guardado en ({cast_x}, {cast_y})")
            guardado = True
            break

        if key == 27:   # ESC cancela
            print("  Cancelado.")
            break

    cv2.destroyWindow(ventana)
    grabador.reanudar()
    return guardado


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    nombre = None
    for a in sys.argv[1:]:
        if not a.startswith("--"):
            nombre = a
            break
    if nombre is None:
        print("Uso: python grabar_ruta.py <nombre_mapa>")
        print("     python grabar_ruta.py willowfish_marsh")
        sys.exit(1)

    os.makedirs(WAYPOINTS_DIR, exist_ok=True)
    json_path = os.path.join(WAYPOINTS_DIR, f"{nombre}.json")

    print(f"\n=== Grabador de ruta: {nombre} ===")
    print("  Párate en el punto de inicio (outpost o landmark fijo).")
    print("  Capturando referencia del minimapa en 5 segundos...")
    print("  (Cambia a Albion Online ahora)\n")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    ref_path = _guardar_ref_minimap(nombre)
    print(f"  Referencia guardada: {ref_path}")
    print("\n  Ahora caminá al primer spot.")
    print("  F3 = marcar spot   F4 = terminar y guardar\n")
    time.sleep(0.5)

    grabador   = GrabadorMovimientos()
    spots: list = []
    cmd_queue  = queue.Queue()
    fin_event  = threading.Event()

    hilo = threading.Thread(target=grabador.loop, daemon=True)
    hilo.start()

    keyboard.add_hotkey("f3", lambda: cmd_queue.put("spot"))
    keyboard.add_hotkey("f4", fin_event.set)

    # Bucle principal — CV2 debe abrirse desde el hilo principal
    while not fin_event.is_set():
        try:
            cmd = cmd_queue.get(timeout=0.1)
            if cmd == "spot":
                _marcar_spot(grabador, spots)
        except queue.Empty:
            pass

    grabador.detener()
    keyboard.unhook_all()

    n_movimientos = sum(1 for s in grabador.ruta if s["tipo"] == "mover")
    if not spots and n_movimientos == 0:
        print("\n  Sin datos grabados. Saliendo.")
        sys.exit(0)

    data = {
        "nombre":    nombre,
        "zoom":      "cercano",
        "inicio":    "Párate en el outpost/landmark antes de iniciar el bot",
        "start_ref": ref_path,
        "spots":     spots,
        "ruta":      grabador.ruta,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n  Ruta guardada en: {json_path}")
    print(f"  Spots: {len(spots)}   Segmentos de movimiento: {n_movimientos}")
    print(f"\n  Para testear: python ejecutar_ruta.py {nombre}")


if __name__ == "__main__":
    main()
