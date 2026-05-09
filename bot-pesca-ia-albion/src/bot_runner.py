"""
Bot runner: ejecuta el loop principal de la maquina de estados.
Se corre en un hilo separado desde la interfaz.
"""

import time
import threading

from src.state_machine import StateMachine, Estado
from src.mount.controller import montar, desmontar
from src.fishing.loop import ejecutar_ciclo_pesca
from src.perception.hp_reader import HpReader
from src.combat.handler import manejar_combate, huir


def _hilo_monitor_hp(sm: StateMachine, hp_reader: HpReader, stop_event: threading.Event):
    """Hilo de fondo que monitorea HP y dispara COMBATE si baja."""
    while not stop_event.is_set():
        if sm.es(Estado.PESCANDO, Estado.NAVEGANDO) and hp_reader.bajo():
            sm.log("HP bajo detectado — activando COMBATE.")
            sm.interrumpir_por_combate()
        time.sleep(0.5)


def ejecutar_bot(sm: StateMachine, pause_event: threading.Event, stop_event: threading.Event):
    """
    Loop principal de estados. Llamar en un hilo daemon desde la GUI.
    """
    hp_reader = HpReader()

    monitor = threading.Thread(
        target=_hilo_monitor_hp,
        args=(sm, hp_reader, stop_event),
        daemon=True,
    )
    monitor.start()

    sm.transicion(Estado.INICIO)

    while not stop_event.is_set():
        estado = sm.estado

        if estado == Estado.INICIO:
            sm.log("Iniciando... 5 segundos para abrir Albion.")
            time.sleep(5)
            sm.transicion(Estado.MONTANDO)

        elif estado == Estado.MONTANDO:
            montar(log_callback=sm.log)
            # Fase 2 agregara NAVEGANDO aqui
            sm.transicion(Estado.DESMONTANDO)

        elif estado == Estado.NAVEGANDO:
            # Placeholder Fase 2
            sm.log("[NAV] Navegacion no implementada (Fase 2).")
            sm.transicion(Estado.DESMONTANDO)

        elif estado == Estado.DESMONTANDO:
            desmontar(log_callback=sm.log)
            sm.transicion(Estado.PESCANDO)

        elif estado == Estado.PESCANDO:
            ejecutar_ciclo_pesca(sm, pause_event=pause_event, stop_event=stop_event)
            # Si salimos del loop sin stop, volvemos a montar para buscar otro spot
            if not stop_event.is_set() and sm.es(Estado.PESCANDO):
                sm.transicion(Estado.MONTANDO)

        elif estado == Estado.COMBATE:
            manejar_combate(sm, hp_reader, stop_event=stop_event)

        elif estado == Estado.HUYENDO:
            huir(sm, stop_event=stop_event)

        elif estado == Estado.MUERTO:
            sm.log("Personaje muerto. Esperando respawn (30s)...")
            time.sleep(30)
            sm.transicion(Estado.INICIO)

        elif estado == Estado.DETENIDO:
            break

        else:
            time.sleep(0.2)

    sm.transicion(Estado.DETENIDO)
    sm.log("Bot detenido.")
