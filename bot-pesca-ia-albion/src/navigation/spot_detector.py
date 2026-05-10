"""
Deteccion de spots de pesca por patron circular en un solo frame.
Corre en un hilo de fondo — no requiere que la camara este quieta.
Confirma un spot solo cuando el mismo circulo aparece en N frames consecutivos.
"""
import threading
import time

import cv2
import numpy as np
import pyautogui

from src.config import (
    REGION_MUNDO,
    SPOT_RADIO_MIN, SPOT_RADIO_MAX,
    SPOT_AGUA3D_LOW, SPOT_AGUA3D_HIGH, SPOT_AGUA3D_MIN_FRAC,
)

# ── Parametros internos ───────────────────────────────────────────────────────
_BUCKET         = 30   # pixeles de tolerancia para agrupar detecciones
_CONFIRMACIONES = 4    # frames en los que debe aparecer el circulo para confirmarlo
_DENSIDAD_MIN   = 0.15 # fraccion del anillo que debe tener bordes para ser valido
_SCAN_INTERVALO = 0.12 # segundos entre cada escaneo del hilo de fondo


def _capturar() -> np.ndarray:
    r = REGION_MUNDO
    shot = pyautogui.screenshot(region=(r['left'], r['top'], r['width'], r['height']))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def _mascara_agua(frame: np.ndarray) -> np.ndarray:
    """Retorna mascara binaria de los pixeles que son agua en la vista 3D."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv,
                       np.array(SPOT_AGUA3D_LOW,  dtype=np.uint8),
                       np.array(SPOT_AGUA3D_HIGH, dtype=np.uint8))


def _circulo_es_agua(mascara: np.ndarray, cx: int, cy: int, r: int) -> bool:
    """True si la fraccion de pixels de agua dentro del circulo supera el umbral."""
    disco = np.zeros_like(mascara)
    cv2.circle(disco, (cx, cy), r, 255, thickness=-1)
    total = cv2.countNonZero(disco)
    if total == 0:
        return False
    agua  = cv2.countNonZero(cv2.bitwise_and(mascara, disco))
    return (agua / total) >= SPOT_AGUA3D_MIN_FRAC


def _detectar_frame_unico(frame: np.ndarray) -> dict | None:
    """
    Detecta el spot de pesca mas probable en un solo frame.
    Aplica mascara de agua antes de Canny para ignorar tierra/arbustos.
    Selecciona el circulo con mayor densidad de bordes en el anillo.
    """
    agua  = _mascara_agua(frame)
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Canny solo sobre pixels de agua (lo demas queda a 0)
    gray_masked = cv2.bitwise_and(gray, gray, mask=agua)
    blur  = cv2.GaussianBlur(gray_masked, (7, 7), 1.5)
    edges = cv2.Canny(blur, 20, 60)

    circles = cv2.HoughCircles(
        edges,
        cv2.HOUGH_GRADIENT,
        dp=1.5,
        minDist=SPOT_RADIO_MIN * 2,
        param1=50,
        param2=18,
        minRadius=SPOT_RADIO_MIN,
        maxRadius=SPOT_RADIO_MAX,
    )

    if circles is None:
        return None

    mejor        = None
    mejor_score  = 0.0

    for cx, cy, r in np.round(circles[0]).astype(int):
        if not _circulo_es_agua(agua, cx, cy, r):
            continue
        grosor    = max(3, r // 5)
        anillo    = np.zeros_like(edges)
        cv2.circle(anillo, (cx, cy), r, 255, thickness=grosor)
        total_anillo = cv2.countNonZero(anillo)
        if total_anillo == 0:
            continue
        bordes_en_anillo = cv2.countNonZero(cv2.bitwise_and(edges, anillo))
        score = bordes_en_anillo / total_anillo
        if score > mejor_score and score >= _DENSIDAD_MIN:
            mejor_score = score
            mejor = (cx, cy, r)

    if mejor is None:
        return None

    cx, cy, r = mejor
    mitad = (SPOT_RADIO_MIN + SPOT_RADIO_MAX) // 2
    return {
        "cx": cx, "cy": cy, "radio": r,
        "tipo": "banco" if r >= mitad else "solo",
        "screen_x": REGION_MUNDO["left"] + cx,
        "screen_y": REGION_MUNDO["top"]  + cy,
    }


# ── SpotWatcher: hilo de deteccion en segundo plano ──────────────────────────

class SpotWatcher:
    """
    Corre en un hilo de fondo escanando el mundo 3D continuamente.
    Solo confirma un spot cuando aparece en _CONFIRMACIONES frames consecutivos
    dentro del mismo bucket de posicion.
    """

    def __init__(self):
        self._lock       = threading.Lock()
        self._spot: dict | None = None
        self._contadores: dict  = {}
        self._running    = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    @property
    def spot(self) -> dict | None:
        with self._lock:
            return self._spot

    def clear(self):
        with self._lock:
            self._spot = None
        self._contadores.clear()

    def _loop(self):
        while self._running:
            frame  = _capturar()
            result = _detectar_frame_unico(frame)

            with self._lock:
                if result:
                    key = (result["cx"] // _BUCKET, result["cy"] // _BUCKET)
                    self._contadores[key] = self._contadores.get(key, 0) + 1
                    for k in list(self._contadores):
                        if k != key:
                            self._contadores[k] -= 1
                            if self._contadores[k] <= 0:
                                del self._contadores[k]
                    if self._contadores[key] >= _CONFIRMACIONES:
                        self._spot = result
                else:
                    for k in list(self._contadores):
                        self._contadores[k] -= 1
                        if self._contadores[k] <= 0:
                            del self._contadores[k]

            time.sleep(_SCAN_INTERVALO)


# ── API publica simple ────────────────────────────────────────────────────────

_watcher = SpotWatcher()


def iniciar_busqueda():
    """Arranca el hilo de deteccion en segundo plano."""
    _watcher.clear()
    _watcher.start()


def detener_busqueda():
    """Detiene el hilo de deteccion."""
    _watcher.stop()


def get_spot() -> dict | None:
    """Retorna el spot confirmado o None si aun no se encontro."""
    return _watcher.spot


def spot_visible() -> bool:
    return _watcher.spot is not None


# ── Debug ─────────────────────────────────────────────────────────────────────

def debug_ventana():
    """
    Ventana de debug en tiempo real.
    Izquierda: imagen de color con mascara de agua (azul) y circulos marcados.
    Derecha: imagen Canny (solo pixels de agua) con los mismos circulos.
    Verde = confirmado  Amarillo = candidato  ESC para salir.
    """
    ventana = "Spot detector (ESC para salir)"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, 1200, 500)

    contadores: dict = {}
    print("Debug spot activo — ESC para salir.")
    print("  Verde = confirmado   Amarillo = candidato   Azul = pixels de agua detectados")

    while True:
        frame  = _capturar()
        agua   = _mascara_agua(frame)

        gray_masked = cv2.bitwise_and(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
            mask=agua,
        )
        blur  = cv2.GaussianBlur(gray_masked, (7, 7), 1.5)
        edges = cv2.Canny(blur, 20, 60)

        display_color = frame.copy()
        # Tinte azul sobre los pixels de agua para visualizar la mascara
        display_color[agua > 0] = (
            display_color[agua > 0] * 0.5 + np.array([180, 80, 0]) * 0.5
        ).astype(np.uint8)
        display_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        circles = cv2.HoughCircles(
            edges, cv2.HOUGH_GRADIENT, dp=1.5,
            minDist=SPOT_RADIO_MIN * 2, param1=50, param2=18,
            minRadius=SPOT_RADIO_MIN, maxRadius=SPOT_RADIO_MAX,
        )

        claves_activas = set()
        if circles is not None:
            for cx, cy, r in np.round(circles[0]).astype(int):
                if not _circulo_es_agua(agua, cx, cy, r):
                    continue
                grosor = max(3, r // 5)
                anillo = np.zeros_like(edges)
                cv2.circle(anillo, (cx, cy), r, 255, thickness=grosor)
                total  = cv2.countNonZero(anillo)
                if total == 0:
                    continue
                score = cv2.countNonZero(cv2.bitwise_and(edges, anillo)) / total
                if score < _DENSIDAD_MIN:
                    continue

                key = (cx // _BUCKET, cy // _BUCKET)
                contadores[key] = contadores.get(key, 0) + 1
                claves_activas.add(key)
                confirmado = contadores[key] >= _CONFIRMACIONES
                color = (0, 255, 0) if confirmado else (0, 220, 255)
                label = f"{'SPOT' if confirmado else 'cand'} r={r} ({contadores[key]}/{_CONFIRMACIONES})"
                for dst in (display_color, display_edges):
                    cv2.circle(dst, (cx, cy), r, color, 2)
                    cv2.circle(dst, (cx, cy), 4, color, -1)
                    cv2.putText(dst, label, (cx + r + 4, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

        for k in list(contadores):
            if k not in claves_activas:
                contadores[k] -= 1
                if contadores[k] <= 0:
                    del contadores[k]

        w = min(display_color.shape[1], 600)
        cv2.imshow(ventana, cv2.hconcat([
            cv2.resize(display_color, (w, 500)),
            cv2.resize(display_edges, (w, 500)),
        ]))

        if cv2.waitKey(int(_SCAN_INTERVALO * 1000)) == 27:
            break

    cv2.destroyAllWindows()
