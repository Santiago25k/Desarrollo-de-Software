"""
Herramienta de calibracion del minimapa — ejecutar antes del bot.

Uso:
    python calibrar_minimap.py           # seleccion de region + debug jugador
    python calibrar_minimap.py --debug   # solo debug jugador (usa config.py actual)
    python calibrar_minimap.py --agua    # calibrar color del agua en el minimapa
"""
import re
import sys
import time

import cv2
import numpy as np
import pyautogui

CONFIG_PATH = "src/config.py"


# ── Captura ───────────────────────────────────────────────────────────────────

def capturar_pantalla_completa() -> tuple[np.ndarray, float]:
    shot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    h, w = frame.shape[:2]
    escala = min(1.0, 1600 / w, 900 / h)
    if escala < 1.0:
        frame = cv2.resize(frame, (int(w * escala), int(h * escala)))
    return frame, escala


def _capturar_minimap(region: dict) -> np.ndarray:
    shot = pyautogui.screenshot(
        region=(region["left"], region["top"], region["width"], region["height"])
    )
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


# ── Seleccion de region ───────────────────────────────────────────────────────

def seleccionar_region() -> dict | None:
    print("\n[Paso 1] Seleccion de region del minimapa")
    print("  Cambia a Albion Online. Capturando en:")
    for i in range(3, 0, -1):
        print(f"    {i}...")
        time.sleep(1)

    frame, escala = capturar_pantalla_completa()
    print("  Arrastra sobre el minimapa y presiona ENTER o ESPACIO para confirmar.")

    roi = cv2.selectROI(
        "Paso 1 — Seleccionar minimapa (ENTER confirma, ESC cancela)",
        frame, fromCenter=False, showCrosshair=True,
    )
    cv2.destroyAllWindows()

    if roi == (0, 0, 0, 0):
        print("  Seleccion cancelada.")
        return None

    x, y, w, h = [round(v / escala) for v in roi]
    region = {"left": x, "top": y, "width": w, "height": h}
    print(f"  Region: {region}")
    return region


# ── Debug jugador ─────────────────────────────────────────────────────────────

def debug_region(region: dict, low: tuple, high: tuple):
    _low, _high = np.array(low), np.array(high)
    escala = 3
    ventana = "Minimap debug — jugador (ESC para salir)"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, region["width"] * escala * 2, region["height"] * escala)

    print("\nDebug jugador activo — ESC para salir.")
    print("  Izquierda: minimapa  |  Derecha: mascara HSV jugador")

    while True:
        frame = _capturar_minimap(region)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, _low, _high)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            best = max(contours, key=cv2.contourArea)
            if cv2.contourArea(best) >= 2:
                bx, by, bw, bh = cv2.boundingRect(best)
                pos = (bx + bw // 2, by + bh // 2)
                cv2.circle(frame, pos, 5, (0, 255, 0), -1)
                cv2.putText(frame, str(pos), (pos[0] + 6, pos[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        cv2.imshow(ventana, cv2.hconcat([frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)]))
        if cv2.waitKey(50) == 27:
            break
    cv2.destroyAllWindows()


# ── Calibracion agua ──────────────────────────────────────────────────────────

def calibrar_agua(region: dict):
    """
    Muestra el minimapa ampliado. El usuario hace click izquierdo sobre pixeles
    de agua para tomar muestras de color. La mascara se actualiza en tiempo real.
    Presiona S para guardar, ESC para salir sin guardar.
    """
    escala = 3
    ventana = "Calibrar agua — click en agua, S guardar, ESC salir"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, region["width"] * escala * 2, region["height"] * escala)

    muestras_hsv: list[np.ndarray] = []   # cada muestra es array [H, S, V]
    _low  = np.array([100, 80, 80])
    _high = np.array([130, 255, 255])
    frame_actual = _capturar_minimap(region)

    def on_click(event, x, y, flags, param):
        nonlocal _low, _high, frame_actual
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        # Las coordenadas del click son en la imagen IZQUIERDA (minimap),
        # que ocupa la mitad izquierda de la ventana concatenada.
        px = x // escala
        py = y // escala
        if px >= region["width"] or py >= region["height"]:
            return  # click en la mitad derecha (mascara), ignorar

        hsv_frame = cv2.cvtColor(frame_actual, cv2.COLOR_BGR2HSV)
        color = hsv_frame[py, px].astype(int)
        muestras_hsv.append(color)

        # Recalcular rango con margen
        todos = np.array(muestras_hsv)
        margen_h, margen_sv = 12, 50
        _low  = np.clip(todos.min(axis=0) - [margen_h, margen_sv, margen_sv], 0, [179, 255, 255])
        _high = np.clip(todos.max(axis=0) + [margen_h, margen_sv, margen_sv], 0, [179, 255, 255])
        print(f"  Muestra {len(muestras_hsv)}: HSV={tuple(color)}  "
              f"rango LOW={tuple(_low)}  HIGH={tuple(_high)}")

    cv2.setMouseCallback(ventana, on_click)

    print("\n[Calibrar agua] Haz click sobre los rios/lagos en el minimapa.")
    print("  Cuantos mas clicks, mejor el rango. S=guardar, ESC=salir.\n")

    while True:
        frame_actual = _capturar_minimap(region)
        hsv = cv2.cvtColor(frame_actual, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, _low, _high)

        display_frame = frame_actual.copy()
        # Resaltar pixeles detectados en verde sobre el minimapa
        overlay = display_frame.copy()
        overlay[mask > 0] = (0, 200, 0)
        cv2.addWeighted(overlay, 0.4, display_frame, 0.6, 0, display_frame)

        izq = cv2.resize(display_frame, (region["width"] * escala, region["height"] * escala),
                         interpolation=cv2.INTER_NEAREST)
        der = cv2.resize(cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR),
                         (region["width"] * escala, region["height"] * escala),
                         interpolation=cv2.INTER_NEAREST)
        cv2.imshow(ventana, cv2.hconcat([izq, der]))

        key = cv2.waitKey(100)
        if key == 27:
            print("Saliendo sin guardar.")
            break
        if key in (ord('s'), ord('S')):
            if not muestras_hsv:
                print("  Sin muestras. Haz click sobre el agua primero.")
                continue
            cv2.destroyAllWindows()
            return tuple(int(v) for v in _low), tuple(int(v) for v in _high)

    cv2.destroyAllWindows()
    return None, None


# ── Guardar config ────────────────────────────────────────────────────────────

def _reemplazar_en_config(patron: str, nuevo: str):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    content_nuevo = re.sub(patron, nuevo, content, flags=re.DOTALL)
    if content_nuevo == content:
        print(f"  ADVERTENCIA: patron no encontrado en config.py.")
        print(f"  Agrega manualmente: {nuevo}")
        return
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content_nuevo)


def guardar_region(region: dict):
    nuevo = (
        f"REGION_MINIMAP = {{\n"
        f"    'left': {region['left']}, 'top': {region['top']}, "
        f"'width': {region['width']}, 'height': {region['height']},\n"
        f"}}"
    )
    _reemplazar_en_config(r"REGION_MINIMAP\s*=\s*\{[^}]+\}", nuevo)
    print(f"  REGION_MINIMAP guardado: {region}")


def guardar_agua(low: tuple, high: tuple):
    nuevo_low  = f"MINIMAP_AGUA_LOW  = {low}"
    nuevo_high = f"MINIMAP_AGUA_HIGH = {high}"

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "MINIMAP_AGUA_LOW" in content:
        content = re.sub(r"MINIMAP_AGUA_LOW\s*=\s*\([^)]+\)", nuevo_low, content)
        content = re.sub(r"MINIMAP_AGUA_HIGH\s*=\s*\([^)]+\)", nuevo_high, content)
    else:
        # Insertar despues de MINIMAP_JUGADOR_HIGH
        content = re.sub(
            r"(MINIMAP_JUGADOR_HIGH\s*=\s*\([^)]+\))",
            r"\1\n# Color HSV del agua en el minimapa\n" + nuevo_low + "\n" + nuevo_high,
            content,
        )

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  MINIMAP_AGUA_LOW  = {low}")
    print(f"  MINIMAP_AGUA_HIGH = {high}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    solo_debug = "--debug" in sys.argv
    modo_agua  = "--agua"  in sys.argv
    no_guardar = "--no-save" in sys.argv

    if solo_debug:
        from src.config import REGION_MINIMAP, MINIMAP_JUGADOR_LOW, MINIMAP_JUGADOR_HIGH
        print(f"REGION_MINIMAP: {REGION_MINIMAP}")
        debug_region(REGION_MINIMAP, MINIMAP_JUGADOR_LOW, MINIMAP_JUGADOR_HIGH)
        return

    if modo_agua:
        from src.config import REGION_MINIMAP
        print(f"REGION_MINIMAP: {REGION_MINIMAP}")
        low, high = calibrar_agua(REGION_MINIMAP)
        if low and not no_guardar:
            guardar_agua(low, high)
            print("\nColor del agua guardado en config.py.")
        return

    # Flujo completo: seleccion de region → debug jugador → guardar
    region = seleccionar_region()
    if region is None:
        sys.exit(0)

    import importlib.util
    spec = importlib.util.spec_from_file_location("cfg", CONFIG_PATH)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    debug_region(region, cfg.MINIMAP_JUGADOR_LOW, cfg.MINIMAP_JUGADOR_HIGH)

    if not no_guardar:
        guardar_region(region)
        print("Listo. Corre 'python calibrar_minimap.py --debug' para verificar.")


if __name__ == "__main__":
    main()
