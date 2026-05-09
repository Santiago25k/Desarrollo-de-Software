import threading
from enum import Enum, auto


class Estado(Enum):
    DETENIDO   = auto()
    INICIO     = auto()
    MONTANDO   = auto()
    NAVEGANDO  = auto()   # Fase 2
    DESMONTANDO = auto()
    PESCANDO   = auto()
    COMBATE    = auto()
    HUYENDO    = auto()
    MUERTO     = auto()


class StateMachine:
    def __init__(self, log_callback=print):
        self.estado = Estado.DETENIDO
        self.log = log_callback
        self._estado_anterior = None
        self._lock = threading.Lock()

    def transicion(self, nuevo: Estado):
        with self._lock:
            anterior = self.estado
            self._estado_anterior = anterior
            self.estado = nuevo
            self.log(f"[BOT] {anterior.name} → {nuevo.name}")

    def es(self, *estados: Estado) -> bool:
        return self.estado in estados

    @property
    def activo(self) -> bool:
        return not self.es(Estado.DETENIDO)

    def interrumpir_por_combate(self):
        """Llamado desde cualquier modulo que detecte un ataque."""
        if not self.es(Estado.COMBATE, Estado.HUYENDO, Estado.DETENIDO):
            self.transicion(Estado.COMBATE)

    def volver(self):
        """Retorna al estado anterior despues de combate."""
        if self._estado_anterior and self._estado_anterior not in (
            Estado.COMBATE, Estado.HUYENDO, Estado.MUERTO
        ):
            self.transicion(self._estado_anterior)
        else:
            self.transicion(Estado.INICIO)
