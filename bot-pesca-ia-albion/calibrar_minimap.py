"""
Herramienta de calibracion del minimapa — ejecutar antes del bot.

Paso 1: Selecciona la region del minimapa arrastrando el mouse.
Paso 2: Verifica la deteccion del punto del jugador en tiempo real.
Paso 3: Guarda la region en src/config.py (opcional).

Uso:
    python calibrar_minimap.py           # seleccion + debug
    python calibrar_minimap.py --debug   # solo debug (usa config.py actual)
"""
import re
import sys
import time

import cv2
import numpy as np
import pyautogui

CONFIG_PATH = "src/config.py"


# ── Paso 1: Seleccion de region ───────────────────────────────────────────────

def capturar_pantalla_completa() -> tuple[np.ndarray, float]:
    """Retorna (frame_bgr, escala) donde escala < 1 si se redujo para mostrar."""
    shot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    h, w = frame.shape[:2]
    escala = min(1.0, 1600 / w, 900 / h)
    if escala < 1.0:
        frame = cv2.resize(frame, (int(w * escala), int(h * escala)))
    return frame, escala


def seleccionar_region() -> dict | None:
    """
    Muestra la pantalla y deja que el usuario arrastre para marcar el minimapa.
    Retorna el dict con coordenadas en pixeles REALES de pantalla.
    """
    print("\n[Paso 1] Seleccion de region del minimapa")
    print("  Cambia a Albion Online. Capturando en:")
    for i in range(3, 0, -1):
        print(f"    {i}...")
        time.sleep(1)

    frame, escala = capturar_pantalla_completa()

    print("  Arrastra sobre el minimapa y presiona ENTER o ESPACIO para confirmar.")
    print("  Presiona C o ESC para cancelar.")

    roi = cv2.selectROI(
        "Paso 1 — Seleccionar minimapa (ENTER confirma, ESC cancela)",
        frame,
        fromCenter=False,
        showCrosshair=True,
    )
    cv2.destroyAllWindows()

    if roi == (0, 0, 0, 0):
        print("  Seleccion cancelada.")
        return None

    x, y, w, h = [round(v / escala) for v in roi]
    region = {"left": x, "top": y, "width": w, "height": h}
    print(f"  Region: {region}")
    return region


# ── Paso 2: Debug de deteccion ────────────────────────────────────────────────

def _leer_colores_config() -> tuple:
    """Lee MINIMAP_JUGADOR_LOW/HIGH del config.py actual."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("cfg", CONFIG_PATH)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    return cfg.MINIMAP_JUGADOR_LOW, cfg.MINIMAP_JUGADOR_HIGH


def debug_region(region: dict, low: tuple, high: tuple):
    """
    Muestra el minimapa capturado y la mascara HSV en tiempo real.
    El punto verde indica la posicion detectada del jugador.
    Presiona ESC para salir.
    """
    _low = np.array(low)
    _high = np.array(high)

    escala_display = 3
    ventana = "Minimap debug (ESC para salir)"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, region["width"] * escala_display * 2,
                     region["height"] * escala_display)

    print("\n[Paso 2] Debug de deteccion activo — presiona ESC para salir.")
    print("  Izquierda: imagen del minimapa  |  Derecha: mascara HSV del jugador")

    while True:
        shot = pyautogui.screenshot(
            region=(region["left"], region["top"], region["width"], region["height"])
        )
        frame = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, _low, _high)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pos = None
        if contours:
            best = max(contours, key=cv2.contourArea)
            if cv2.contourArea(best) >= 2:
                bx, by, bw, bh = cv2.boundingRect(best)
                pos = (bx + bw // 2, by + bh // 2)
                cv2.circle(frame, pos, 5, (0, 255, 0), -1)
                cv2.putText(frame, str(pos), (pos[0] + 6, pos[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        display = cv2.hconcat([frame, mask_bgr])
        cv2.imshow(ventana, display)

        key = cv2.waitKey(50)
        if key == 27:
            break

    cv2.destroyAllWindows()


# ── Paso 3: Guardar en config.py ──────────────────────────────────────────────

def guardar_region(region: dict):
    """Reemplaza REGION_MINIMAP en src/config.py."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    nuevo = (
        f"REGION_MINIMAP = {{\n"
        f"    'left': {region['left']}, 'top': {region['top']}, "
        f"'width': {region['width']}, 'height': {region['height']},\n"
        f"}}"
    )
    content_nuevo = re.sub(
        r"REGION_MINIMAP\s*=\s*\{[^}]+\}",
        nuevo,
        content,
        flags=re.DOTALL,
    )
    if content_nuevo == content:
        print("  ADVERTENCIA: no se encontro REGION_MINIMAP en config.py para reemplazar.")
        print(f"  Agrega manualmente: {nuevo}")
        return

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content_nuevo)
    print(f"  config.py actualizado: {region}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    solo_debug = "--debug" in sys.argv
    no_guardar  = "--no-save" in sys.argv

    if solo_debug:
        from src.config import REGION_MINIMAP, MINIMAP_JUGADOR_LOW, MINIMAP_JUGADOR_HIGH
        print(f"Usando REGION_MINIMAP de config.py: {REGION_MINIMAP}")
        debug_region(REGION_MINIMAP, MINIMAP_JUGADOR_LOW, MINIMAP_JUGADOR_HIGH)
        return

    # Flujo completo: seleccion → debug → guardar automaticamente
    region = seleccionar_region()
    if region is None:
        sys.exit(0)

    low, high = _leer_colores_config()
    debug_region(region, low, high)

    if no_guardar:
        print(f"\nRegion (no guardada): {region}")
    else:
        guardar_region(region)
        print("\nListo. Corre 'python calibrar_minimap.py --debug' para verificar.")


if __name__ == "__main__":
    main()
