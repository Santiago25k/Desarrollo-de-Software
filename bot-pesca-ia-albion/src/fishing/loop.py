import time
import pyautogui

from .deteccion import detectar_hundimiento, controlar_puzzle
from .cebo import aplicar_cebo
from .alga import usar_alga
from .comida import preparar_comida
from src.config import TIEMPO_COMIDA, TECLA_COMIDA, CEBO_CADA_N_PECES, TIEMPO_LANZO, SPOT_X, SPOT_Y
from src.state_machine import Estado


def ejecutar_ciclo_pesca(sm, pause_event=None, stop_event=None):
    """
    Bucle principal de pesca. Se ejecuta mientras sm.estado == PESCANDO.
    sm: instancia de StateMachine
    pause_event: threading.Event — si set, el bot se pausa
    stop_event: threading.Event — si set, el bot se detiene
    """
    log = sm.log

    preparar_comida(log_callback=log)
    aplicar_cebo(log_callback=log)

    contador_peces = 0
    inicio_comida = time.time()

    while sm.es(Estado.PESCANDO):
        if stop_event and stop_event.is_set():
            log("Bot detenido.")
            break

        if pause_event and pause_event.is_set():
            log("En pausa...")
            while pause_event.is_set():
                if stop_event and stop_event.is_set():
                    return
                time.sleep(0.5)
            log("Reanudado.")

        # Si el estado cambia a COMBATE desde otro hilo (hp_reader), salimos del loop
        if not sm.es(Estado.PESCANDO):
            break

        if time.time() - inicio_comida >= TIEMPO_COMIDA:
            log("Reaplicando comida...")
            pyautogui.press(TECLA_COMIDA)
            time.sleep(4)
            aplicar_cebo(log_callback=log)
            inicio_comida = time.time()

        if contador_peces > 0 and contador_peces % CEBO_CADA_N_PECES == 0:
            aplicar_cebo(log_callback=log)

        log(f"Lanzando linea #{contador_peces + 1}...")
        pyautogui.moveTo(SPOT_X, SPOT_Y, duration=0.5)
        pyautogui.mouseDown()
        time.sleep(TIEMPO_LANZO)
        pyautogui.mouseUp()

        if not sm.es(Estado.PESCANDO):
            break

        hundio = detectar_hundimiento(log_callback=log)
        if not hundio:
            continue

        if not sm.es(Estado.PESCANDO):
            break

        controlar_puzzle(log_callback=log)
        usar_alga(log_callback=log)

        contador_peces += 1
        log(f"Pez #{contador_peces} pescado.")
