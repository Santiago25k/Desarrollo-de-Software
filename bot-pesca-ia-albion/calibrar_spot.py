"""
Herramienta de calibracion de spots de pesca.

Uso:
    python calibrar_spot.py            # seleccionar REGION_MUNDO + debug
    python calibrar_spot.py --debug    # solo debug de deteccion
    python calibrar_spot.py --colores  # calibrar colores de los peces
    python calibrar_spot.py --agua3d   # calibrar color del agua en la vista 3D
"""
import os
import re
import sys
import time

import cv2
import numpy as np
import pyautogui

TEMPLATES_DIR = "img/spot_templates"

CONFIG_PATH = "src/config.py"


# ── Captura ───────────────────────────────────────────────────────────────────

def _capturar_pantalla() -> tuple[np.ndarray, float]:
    shot  = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    h, w  = frame.shape[:2]
    escala = min(1.0, 1600 / w, 900 / h)
    if escala < 1.0:
        frame = cv2.resize(frame, (int(w * escala), int(h * escala)))
    return frame, escala


def _capturar_region(region: dict) -> np.ndarray:
    shot = pyautogui.screenshot(
        region=(region["left"], region["top"], region["width"], region["height"])
    )
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


# ── Seleccion de region mundo ─────────────────────────────────────────────────

def seleccionar_region_mundo() -> dict | None:
    print("\n[Paso 1] Selecciona la region del mundo 3D")
    print("  Excluye el minimapa, barras de UI y hotkeys.")
    print("  Capturando en 3 segundos — cambia a Albion Online...")
    for i in range(3, 0, -1):
        print(f"    {i}...")
        time.sleep(1)

    frame, escala = _capturar_pantalla()
    roi = cv2.selectROI(
        "Seleccionar mundo 3D (ENTER confirma, ESC cancela)",
        frame, fromCenter=False, showCrosshair=True,
    )
    cv2.destroyAllWindows()

    if roi == (0, 0, 0, 0):
        print("  Cancelado.")
        return None

    x, y, w, h = [round(v / escala) for v in roi]
    region = {"left": x, "top": y, "width": w, "height": h}
    print(f"  Region: {region}")
    return region


def guardar_region_mundo(region: dict):
    _reemplazar_config(
        r"REGION_MUNDO\s*=\s*\{[^}]+\}",
        f"REGION_MUNDO = {{\n"
        f"    'left': {region['left']}, 'top': {region['top']}, "
        f"'width': {region['width']}, 'height': {region['height']},\n"
        f"}}"
    )
    print(f"  REGION_MUNDO guardado: {region}")


# ── Calibracion de colores de peces ──────────────────────────────────────────

def _tomar_captura(region: dict) -> np.ndarray:
    """Cuenta regresiva y captura un frame congelado de la region."""
    print("\nPositionate con peces visibles en pantalla. Capturando en:")
    for i in range(3, 0, -1):
        print(f"    {i}...")
        time.sleep(1)
    frame = _capturar_region(region)
    print("  Captura tomada.")
    return frame


def calibrar_colores_pez(region: dict):
    """
    Captura un frame congelado y deja clickear sobre los peces para muestrear colores.
    A = modo azul  N = modo naranja  C = nueva captura  S = guardar  ESC = salir.
    """
    ESCALA  = 3
    ventana = "Calibrar peces (frame congelado)"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, region["width"] * ESCALA, region["height"] * ESCALA)

    muestras_azul    = []
    muestras_naranja = []
    modo_color       = [0]        # 0=azul, 1=naranja
    frame_fijo       = [_tomar_captura(region)]

    def _recalcular_display():
        """Dibuja el frame congelado con overlay de colores detectados."""
        base = frame_fijo[0].copy()
        hsv  = cv2.cvtColor(base, cv2.COLOR_BGR2HSV)
        margen = [12, 50, 50]

        if muestras_azul:
            arr = np.array(muestras_azul)
            low  = np.clip(arr.min(axis=0) - margen, 0, [179, 255, 255])
            high = np.clip(arr.max(axis=0) + margen, 0, [179, 255, 255])
            m = cv2.inRange(hsv, low, high)
            base[m > 0] = (255, 80, 0)      # azul resaltado en naranja brillante

        if muestras_naranja:
            arr = np.array(muestras_naranja)
            low  = np.clip(arr.min(axis=0) - margen, 0, [179, 255, 255])
            high = np.clip(arr.max(axis=0) + margen, 0, [179, 255, 255])
            m = cv2.inRange(hsv, low, high)
            base[m > 0] = (0, 100, 255)     # naranja resaltado en rojo-naranja

        display = cv2.resize(base, (region["width"] * ESCALA, region["height"] * ESCALA),
                             interpolation=cv2.INTER_NEAREST)
        modo_txt = "AZUL" if modo_color[0] == 0 else "NARANJA"
        az_n = len(muestras_azul)
        na_n = len(muestras_naranja)
        cv2.putText(display,
                    f"Modo:{modo_txt} Az:{az_n} Na:{na_n}  A=azul N=naranja C=captura S=guardar",
                    (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        return display

    def on_click(event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        px, py = x // ESCALA, y // ESCALA
        px = min(px, region["width"]  - 1)
        py = min(py, region["height"] - 1)
        hsv   = cv2.cvtColor(frame_fijo[0], cv2.COLOR_BGR2HSV)
        color = hsv[py, px].astype(int)
        if modo_color[0] == 0:
            muestras_azul.append(color)
            print(f"  Azul    #{len(muestras_azul)}: HSV={tuple(color)}")
        else:
            muestras_naranja.append(color)
            print(f"  Naranja #{len(muestras_naranja)}: HSV={tuple(color)}")
        cv2.imshow(ventana, _recalcular_display())

    cv2.setMouseCallback(ventana, on_click)

    print("\n[Calibrar colores pez] — frame congelado")
    print("  Click = muestrear color del pez")
    print("  A = modo AZUL   N = modo NARANJA   C = nueva captura")
    print("  S = guardar     ESC = salir\n")

    cv2.imshow(ventana, _recalcular_display())

    while True:
        key = cv2.waitKey(50)
        if key == 27:
            break
        if key in (ord('a'), ord('A')):
            modo_color[0] = 0
            print("  Modo: AZUL")
            cv2.imshow(ventana, _recalcular_display())
        if key in (ord('n'), ord('N')):
            modo_color[0] = 1
            print("  Modo: NARANJA")
            cv2.imshow(ventana, _recalcular_display())
        if key in (ord('c'), ord('C')):
            cv2.destroyAllWindows()
            frame_fijo[0] = _tomar_captura(region)
            cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(ventana, region["width"] * ESCALA, region["height"] * ESCALA)
            cv2.setMouseCallback(ventana, on_click)
            cv2.imshow(ventana, _recalcular_display())
        if key in (ord('s'), ord('S')):
            if not muestras_azul and not muestras_naranja:
                print("  Sin muestras. Haz click sobre los peces primero.")
                continue
            cv2.destroyAllWindows()
            return muestras_azul, muestras_naranja

    cv2.destroyAllWindows()
    return None, None


def guardar_colores_pez(muestras_azul: list, muestras_naranja: list):
    margen = [12, 50, 50]

    def rango(muestras):
        arr  = np.array(muestras)
        low  = tuple(int(v) for v in np.clip(arr.min(axis=0) - margen, 0, [179, 255, 255]))
        high = tuple(int(v) for v in np.clip(arr.max(axis=0) + margen, 0, [179, 255, 255]))
        return low, high

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if muestras_azul:
        low, high = rango(muestras_azul)
        content = re.sub(r"SPOT_PEZ_AZUL_LOW\s*=\s*\([^)]+\)",
                         f"SPOT_PEZ_AZUL_LOW    = {low}", content)
        content = re.sub(r"SPOT_PEZ_AZUL_HIGH\s*=\s*\([^)]+\)",
                         f"SPOT_PEZ_AZUL_HIGH   = {high}", content)
        print(f"  Azul    LOW={low}  HIGH={high}")

    if muestras_naranja:
        low, high = rango(muestras_naranja)
        content = re.sub(r"SPOT_PEZ_NARANJA_LOW\s*=\s*\([^)]+\)",
                         f"SPOT_PEZ_NARANJA_LOW  = {low}", content)
        content = re.sub(r"SPOT_PEZ_NARANJA_HIGH\s*=\s*\([^)]+\)",
                         f"SPOT_PEZ_NARANJA_HIGH = {high}", content)
        print(f"  Naranja LOW={low}  HIGH={high}")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  Colores guardados en config.py")


# ── Calibracion del color del agua en la vista 3D ────────────────────────────

def calibrar_agua3d(_region_ignorada=None):
    """
    Toma una captura de pantalla completa con cuenta regresiva larga.
    El usuario hace click sobre el agua del rio en cualquier parte de la pantalla.
    Los pixels detectados se resaltan en azul para verificar.
    S = guardar   C = nueva captura   ESC = salir.
    """
    ventana = "Calibrar agua 3D — click sobre el agua (S=guardar, C=captura, ESC=salir)"

    muestras   = []
    frame_fijo = [None]
    escala_ref = [1.0]

    def _capturar_completa():
        print("\nPositionate cerca del agua en Albion Online.")
        print("Capturando pantalla completa en 5 segundos...\n")
        for i in range(5, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        frame, escala = _capturar_pantalla()
        frame_fijo[0] = frame
        escala_ref[0] = escala
        print("  Captura tomada.")

    def _recalcular_display():
        base = frame_fijo[0].copy()
        if muestras:
            hsv    = cv2.cvtColor(base, cv2.COLOR_BGR2HSV)
            arr    = np.array(muestras)
            margen = np.array([10, 50, 50])
            low  = np.clip(arr.min(axis=0) - margen, 0, [179, 255, 255]).astype(np.uint8)
            high = np.clip(arr.max(axis=0) + margen, 0, [179, 255, 255]).astype(np.uint8)
            mask = cv2.inRange(hsv, low, high)
            base[mask > 0] = (200, 120, 0)
        cv2.putText(base,
                    f"Click=agua ({len(muestras)} muestras)  S=guardar  C=nueva captura  ESC=salir",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        return base

    def on_click(event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        h, w = frame_fijo[0].shape[:2]
        px = min(x, w - 1)
        py = min(y, h - 1)
        hsv   = cv2.cvtColor(frame_fijo[0], cv2.COLOR_BGR2HSV)
        color = hsv[py, px].astype(int)
        muestras.append(color)
        print(f"  Muestra #{len(muestras)}: HSV={tuple(color)}")
        cv2.imshow(ventana, _recalcular_display())

    _capturar_completa()

    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    h, w = frame_fijo[0].shape[:2]
    cv2.resizeWindow(ventana, min(w, 1400), min(h, 800))
    cv2.setMouseCallback(ventana, on_click)

    print("\n[Calibrar agua 3D]")
    print("  Haz click sobre varios puntos del agua del rio en la imagen.")
    print("  S = guardar   C = nueva captura   ESC = salir\n")
    cv2.imshow(ventana, _recalcular_display())

    while True:
        key = cv2.waitKey(50)
        if key == 27:
            break
        if key in (ord('c'), ord('C')):
            cv2.destroyAllWindows()
            muestras.clear()
            _capturar_completa()
            cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
            h, w = frame_fijo[0].shape[:2]
            cv2.resizeWindow(ventana, min(w, 1400), min(h, 800))
            cv2.setMouseCallback(ventana, on_click)
            cv2.imshow(ventana, _recalcular_display())
        if key in (ord('s'), ord('S')):
            if not muestras:
                print("  Sin muestras. Haz click sobre el agua primero.")
                continue
            cv2.destroyAllWindows()
            _guardar_agua3d(muestras)
            print("  Corre '--debug' para verificar que el agua queda bien resaltada.")
            return

    cv2.destroyAllWindows()


def _guardar_agua3d(muestras: list):
    arr    = np.array(muestras)
    margen = np.array([10, 50, 50])
    low  = tuple(int(v) for v in np.clip(arr.min(axis=0) - margen, 0, [179, 255, 255]))
    high = tuple(int(v) for v in np.clip(arr.max(axis=0) + margen, 0, [179, 255, 255]))

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r"SPOT_AGUA3D_LOW\s*=\s*\([^)]+\)",
                     f"SPOT_AGUA3D_LOW  = {low}", content)
    content = re.sub(r"SPOT_AGUA3D_HIGH\s*=\s*\([^)]+\)",
                     f"SPOT_AGUA3D_HIGH = {high}", content)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  SPOT_AGUA3D_LOW  = {low}")
    print(f"  SPOT_AGUA3D_HIGH = {high}")
    print("  Guardado en config.py")


# ── Captura de templates de spots (imagen Canny) ─────────────────────────────

def _canny_de_region(region: dict) -> tuple[np.ndarray, np.ndarray]:
    """Retorna (frame_bgr, edges_canny) de la region."""
    frame = _capturar_region(region)
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur  = cv2.GaussianBlur(gray, (7, 7), 1.5)
    edges = cv2.Canny(blur, 20, 60)
    return frame, edges


def _siguiente_nombre_template() -> str:
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    existentes = [f for f in os.listdir(TEMPLATES_DIR) if f.startswith("spot_") and f.endswith(".png")]
    return os.path.join(TEMPLATES_DIR, f"spot_{len(existentes):03d}.png")


def capturar_templates(region: dict):
    """
    Cuenta regresiva → captura screenshot → muestra imagen Canny congelada.
    Selecciona el spot con ROI (ENTER confirma).
    C = nueva captura.  ESC = salir.
    """
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    ANCHO_VIS = max(region["width"] * 3, 600)
    ALTO_VIS  = max(region["height"] * 3, 400)
    guardados = 0

    print("\n[Capturar templates de spots]")
    print("  Acercate a un spot de pesca antes de continuar.")
    print("  ENTER = confirmar seleccion   C = nueva captura   ESC = salir\n")

    def _tomar_y_mostrar():
        print("Capturando en 3 segundos — posicionate cerca del spot...")
        for i in range(3, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        frame, edges = _canny_de_region(region)
        print("  Captura tomada.")
        return frame, edges

    while True:
        frame, edges = _tomar_y_mostrar()

        # Escalar para mejor visibilidad al seleccionar
        edges_scaled = cv2.resize(edges, (ANCHO_VIS, ALTO_VIS), interpolation=cv2.INTER_NEAREST)
        edges_bgr    = cv2.cvtColor(edges_scaled, cv2.COLOR_GRAY2BGR)
        cv2.putText(edges_bgr,
                    f"Selecciona el spot (ENTER confirma, ESC cancela) — guardados: {guardados}",
                    (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 255), 1)

        roi = cv2.selectROI("Capturar spot (ENTER confirma, ESC cancela)",
                            edges_bgr, fromCenter=False, showCrosshair=True)
        cv2.destroyAllWindows()

        if roi != (0, 0, 0, 0):
            rx, ry, rw, rh = roi
            escala_x = region["width"]  / ANCHO_VIS
            escala_y = region["height"] / ALTO_VIS
            ox = round(rx * escala_x)
            oy = round(ry * escala_y)
            ow = max(1, round(rw * escala_x))
            oh = max(1, round(rh * escala_y))
            crop = edges[oy:oy+oh, ox:ox+ow]
            if crop.size > 0:
                nombre = _siguiente_nombre_template()
                cv2.imwrite(nombre, crop)
                guardados += 1
                print(f"  Template guardado: {nombre}  ({ow}x{oh}px)")
            else:
                print("  Seleccion demasiado pequena, intenta de nuevo.")

        print("  C = nueva captura   ESC/cualquier tecla = salir")
        print("  Presiona una tecla en la consola...")
        key = input("> ").strip().lower()
        if key != 'c':
            break

    print(f"\n  Total templates guardados: {guardados}")
    print(f"  Directorio: {TEMPLATES_DIR}/")
    if guardados > 0:
        print("  Corre '--debug' para verificar la deteccion con los nuevos templates.")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _reemplazar_config(patron: str, nuevo: str):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    content_nuevo = re.sub(patron, nuevo, content, flags=re.DOTALL)
    if content_nuevo == content:
        print(f"  ADVERTENCIA: patron no encontrado en config.py.")
        return
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content_nuevo)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    solo_debug   = "--debug"   in sys.argv
    modo_colores = "--colores" in sys.argv
    modo_agua3d  = "--agua3d"  in sys.argv

    if solo_debug:
        from src.navigation.spot_detector import debug_ventana
        from src.config import REGION_MUNDO
        print(f"REGION_MUNDO: {REGION_MUNDO}")
        debug_ventana()
        return

    if modo_colores:
        from src.config import REGION_MUNDO
        print(f"REGION_MUNDO: {REGION_MUNDO}")
        print("Parate cerca del agua con peces visibles.")
        az, na = calibrar_colores_pez(REGION_MUNDO)
        if az or na:
            guardar_colores_pez(az or [], na or [])
            print("\nListo. Corre '--debug' para verificar.")
        return

    if modo_agua3d:
        from src.config import REGION_MUNDO
        print(f"REGION_MUNDO: {REGION_MUNDO}")
        print("Parate cerca del agua para que el rio sea visible en pantalla.")
        calibrar_agua3d(REGION_MUNDO)
        return

    # Flujo completo
    region = seleccionar_region_mundo()
    if region is None:
        sys.exit(0)
    guardar_region_mundo(region)

    from src.navigation.spot_detector import debug_ventana
    print("\nRegion guardada. Abriendo debug...")
    time.sleep(1)
    debug_ventana()


if __name__ == "__main__":
    main()
