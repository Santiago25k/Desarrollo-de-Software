"""
Lector de barra de HP basado en deteccion de color.

La barra de HP de Albion Online es roja y esta en posicion fija en pantalla.
Calibrar REGION_HP en src/config.py segun tu resolucion y UI.

Uso:
    reader = HpReader()
    porcentaje = reader.leer()   # 0.0 a 1.0
"""

import cv2
import numpy as np
import pyautogui

from src.config import REGION_HP, UMBRAL_HP_BAJO

# Rango HSV del color rojo de la barra de HP de Albion
_HP_LOW1  = np.array([0,   120, 80])
_HP_HIGH1 = np.array([10,  255, 255])
_HP_LOW2  = np.array([170, 120, 80])
_HP_HIGH2 = np.array([179, 255, 255])


class HpReader:
    def __init__(self):
        self._hp_max_pixeles = None

    def leer(self) -> float:
        """
        Captura la region de HP y retorna el porcentaje actual (0.0 - 1.0).
        En el primer llamado calibra el maximo automaticamente (asume HP lleno).
        """
        shot = pyautogui.screenshot(
            region=(
                REGION_HP['left'],
                REGION_HP['top'],
                REGION_HP['width'],
                REGION_HP['height'],
            )
        )
        frame = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.bitwise_or(
            cv2.inRange(hsv, _HP_LOW1, _HP_HIGH1),
            cv2.inRange(hsv, _HP_LOW2, _HP_HIGH2),
        )
        pixeles_rojos = np.count_nonzero(mask)

        if self._hp_max_pixeles is None or pixeles_rojos > self._hp_max_pixeles:
            self._hp_max_pixeles = max(pixeles_rojos, 1)

        return pixeles_rojos / self._hp_max_pixeles

    def bajo(self) -> bool:
        return self.leer() < UMBRAL_HP_BAJO
