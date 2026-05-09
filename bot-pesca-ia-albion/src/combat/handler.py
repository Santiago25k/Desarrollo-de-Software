"""
Manejador de combate basico (Fase 1).
Targeting completo con YOLO se implementa en Fase 4.

Flujo actual:
  1. Presiona Tab para auto-seleccionar enemigo mas cercano
  2. Cicla habilidades 1 → 2 → 3
  3. Monitorea HP; si sube de vuelta, el enemigo murio
  4. Si HP sigue bajo despues de CICLOS_COMBATE_MAX → HUYENDO
"""

import time
import pyautogui

from src.config import (
    TECLA_AUTO_TARGET, TECLAS_HABILIDADES,
    DELAY_HABILIDAD, CICLOS_COMBATE_MAX,
)
from src.state_machine import Estado


def manejar_combate(sm, hp_reader, stop_event=None):
    log = sm.log
    log("COMBATE: auto-targeting...")
    pyautogui.press(TECLA_AUTO_TARGET)
    time.sleep(0.3)

    hp_inicial = hp_reader.leer()

    for ciclo in range(CICLOS_COMBATE_MAX):
        if stop_event and stop_event.is_set():
            return

        for tecla in TECLAS_HABILIDADES:
            pyautogui.press(tecla)
            time.sleep(DELAY_HABILIDAD)

        hp_actual = hp_reader.leer()

        # Si el HP esta recuperandose o el enemigo murio (sin mas dano), salimos
        if hp_actual > hp_inicial + 0.05:
            log("COMBATE: HP recuperado, volviendo.")
            sm.volver()
            return

        # Actualizar referencia para detectar recuperacion en proximo ciclo
        if hp_actual < hp_inicial:
            hp_inicial = hp_actual

    # Demasiados ciclos sin mejorar → huir
    log("COMBATE: no se pudo eliminar al enemigo, huyendo...")
    sm.transicion(Estado.HUYENDO)


def huir(sm, stop_event=None):
    """Monta e intenta alejarse. Fase 1: solo monta y espera."""
    from src.mount.controller import montar
    from src.config import TIEMPO_HUIDA

    log = sm.log
    pyautogui.mouseUp()  # soltar si estaba pescando

    log("HUYENDO: intentando montar...")
    montar(log_callback=log)

    log(f"HUYENDO: corriendo {TIEMPO_HUIDA}s...")
    time.sleep(TIEMPO_HUIDA)

    log("HUYENDO: zona despejada, reiniciando.")
    sm.transicion(Estado.INICIO)
