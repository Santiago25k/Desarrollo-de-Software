import time
import pyautogui

from src.config import REGION_MINIMAP, WAYPOINT_RADIO, WAYPOINT_TIMEOUT
from src.state_machine import Estado
from .minimap import get_player_pos, distancia

_MM_LEFT = REGION_MINIMAP['left']
_MM_TOP  = REGION_MINIMAP['top']


def navegar_por_waypoints(sm, waypoints: list, stop_event=None):
    """
    Navega por la lista de waypoints haciendo click en el minimapa.
    Cada waypoint: {"x": int, "y": int} en pixeles dentro de REGION_MINIMAP.
    Transicion de estado la maneja bot_runner al retornar.
    """
    log = sm.log

    if not waypoints:
        log("[NAV] Lista de waypoints vacia.")
        return

    for i, wp in enumerate(waypoints):
        if stop_event and stop_event.is_set():
            return
        if not sm.es(Estado.NAVEGANDO):
            return

        wp_x, wp_y = wp["x"], wp["y"]
        destino = (_MM_LEFT + wp_x, _MM_TOP + wp_y)
        log(f"[NAV] Waypoint {i + 1}/{len(waypoints)} → minimap ({wp_x}, {wp_y})")

        inicio = time.time()
        while sm.es(Estado.NAVEGANDO):
            if stop_event and stop_event.is_set():
                return

            if time.time() - inicio > WAYPOINT_TIMEOUT:
                log(f"[NAV] Timeout en waypoint {i + 1}, continuando.")
                break

            player = get_player_pos()
            if player and distancia(player, (wp_x, wp_y)) <= WAYPOINT_RADIO:
                log(f"[NAV] Waypoint {i + 1} alcanzado.")
                break

            # Click en el minimapa para mover al personaje
            pyautogui.click(*destino)
            time.sleep(1.5)

    log("[NAV] Ruta completada.")
