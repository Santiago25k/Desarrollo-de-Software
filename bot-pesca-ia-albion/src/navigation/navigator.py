import math
import time
import threading
import pyautogui
import pydirectinput

# Segundos de espera tras moverse para que la camara se estabilice
_PAUSA_CAMARA = 0.4

from src.config import (
    WAYPOINT_TIMEOUT, NAV_CLICK_DISTANCIA, NAV_DURACION_HOLD,
    NAV_STUCK_INTENTOS, SCREEN_WIDTH, SCREEN_HEIGHT,
)
from src.state_machine import Estado
from .minimap import get_water_direction, is_at_water

_CENTRO_X = SCREEN_WIDTH  // 2
_CENTRO_Y = SCREEN_HEIGHT // 2
_TIMEOUT  = WAYPOINT_TIMEOUT * 6


def _pos_destino(dx: float, dy: float) -> tuple:
    return (int(_CENTRO_X + dx * NAV_CLICK_DISTANCIA),
            int(_CENTRO_Y + dy * NAV_CLICK_DISTANCIA))


def _mover_hold(dx: float, dy: float):
    """Mueve el cursor al destino y mantiene el boton derecho presionado."""
    cx, cy = _pos_destino(dx, dy)
    pyautogui.moveTo(cx, cy)
    pydirectinput.mouseDown(button='right')
    time.sleep(NAV_DURACION_HOLD)
    pydirectinput.mouseUp(button='right')


def _rotar(dx: float, dy: float, grados: float) -> tuple:
    rad = math.radians(grados)
    return (dx * math.cos(rad) - dy * math.sin(rad),
            dx * math.sin(rad) + dy * math.cos(rad))


def _esta_atascado(historial: list, dx: float, dy: float) -> bool:
    historial.append((dx, dy))
    if len(historial) > NAV_STUCK_INTENTOS:
        historial.pop(0)
    if len(historial) < NAV_STUCK_INTENTOS:
        return False
    for hx, hy in historial[:-1]:
        if hx * dx + hy * dy < 0.92:
            return False
    return True


def navegar_al_agua(sm, stop_event: threading.Event = None):
    """
    Navega hacia el agua manteniendo el boton izquierdo presionado.
    - Cuando el agua no es visible, sigue la ultima direccion conocida.
    - Detecta atasco y rota 90° para esquivar obstaculos.
    """
    log = sm.log

    if is_at_water():
        log("[NAV] Jugador ya esta en el agua.")
        return

    log("[NAV] Navegando hacia el agua...")
    inicio     = time.time()
    historial  = []
    evasion    = 0
    ultima_dir = None

    try:
        while sm.es(Estado.NAVEGANDO):
            if stop_event and stop_event.is_set():
                return
            if time.time() - inicio > _TIMEOUT:
                log("[NAV] Timeout buscando agua.")
                return
            if is_at_water():
                log("[NAV] Agua alcanzada.")
                return

            direccion = get_water_direction()

            if direccion is None:
                if ultima_dir:
                    _mover_hold(*ultima_dir)
                else:
                    time.sleep(0.3)
                continue

            dx, dy = direccion
            if dx == 0.0 and dy == 0.0:
                log("[NAV] Jugador en el agua.")
                return

            ultima_dir = (dx, dy)

            if evasion > 0:
                dx, dy = _rotar(dx, dy, 90)
                evasion -= 1
            elif _esta_atascado(historial, dx, dy):
                evasion = 4
                historial.clear()
                log("[NAV] Atascado — evasion activada.")
                continue

            _mover_hold(dx, dy)
    finally:
        pydirectinput.mouseUp(button='right')


def recorrer_orilla(sm, stop_event: threading.Event = None, timeout: int = 120):
    """
    Recorre la orilla del agua buscando un spot de pesca.
    Arranca SpotWatcher en segundo plano — deteccion continua sin detenerse.
    Retorna True cuando se confirme un spot, False si agota el timeout.
    """
    from .spot_detector import iniciar_busqueda, detener_busqueda

    log = sm.log
    log("[NAV] Recorriendo orilla — deteccion de spots en segundo plano...")
    iniciar_busqueda()

    inicio   = time.time()
    sentido  = 1
    sin_agua = 0

    try:
        while sm.es(Estado.NAVEGANDO):
            if stop_event and stop_event.is_set():
                return False
            if time.time() - inicio > timeout:
                log("[NAV] Timeout recorriendo orilla.")
                return False

            from .spot_detector import get_spot
            spot = get_spot()
            if spot:
                log(f"[NAV] Spot encontrado: {spot['tipo']} en ({spot['screen_x']}, {spot['screen_y']})")
                return True

            direccion = get_water_direction()

            if direccion is None or (direccion[0] == 0.0 and direccion[1] == 0.0):
                _mover_hold(sentido * 1.0, 0.0)
                sin_agua = 0
                continue

            dx, dy = direccion
            sin_agua += 1

            if sin_agua > 3:
                _mover_hold(dx, dy)
                sin_agua = 0
            else:
                perp_x, perp_y = _rotar(dx, dy, 90 * sentido)
                _mover_hold(perp_x, perp_y)
    finally:
        detener_busqueda()
        pydirectinput.mouseUp(button='right')

    return False
