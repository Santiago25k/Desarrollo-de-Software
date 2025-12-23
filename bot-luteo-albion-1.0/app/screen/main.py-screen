import cv2
import json
import time
import os

from app.screen.capture import ScreenCapture
from app.screen.roi_selector import ROISelector

WINDOW_NAME = "Albion Online Client"
ROI_FILE = "popup_roi.json"
GRID_FILE = "popup_grid.json"
SNAPSHOT_FILE = "snapshot.png"


def main():
    print("El bot se iniciará en 5 segundos...")
    print("Abri Albion y mostra el popup")
    time.sleep(5)

    # Captura un frame de Albion
    capture = ScreenCapture(WINDOW_NAME)
    frame = capture.grab()
    capture.release()

    # Guardamos snapshot temporal
    cv2.imwrite(SNAPSHOT_FILE, frame)
    print(f"Snapshot guardado: {os.path.abspath(SNAPSHOT_FILE)}")

    # Abrimos snapshot para seleccionar ROI
    cv2.namedWindow("Calibracion Popup", cv2.WINDOW_NORMAL)
    selector = ROISelector("Calibracion Popup")
    roi = selector.select_static(frame)  # selección única

    if not roi:
        print("ROI no seleccionado")
        cv2.destroyAllWindows()
        return

    # Guardar ROI
    roi_data = {"x": roi[0], "y": roi[1], "w": roi[2], "h": roi[3]}
    with open(ROI_FILE, "w") as f:
        json.dump(roi_data, f, indent=4)
    print("ROI guardado:", roi_data)

    # Pedir filas y columnas de la grilla
    rows = int(input("Cantidad de filas en la grilla: "))
    cols = int(input("Cantidad de columnas en la grilla: "))

    # Generar celdas de la grilla
    cells = selector.generate_grid(roi, rows, cols)
    grid_data = {"rows": rows, "cols": cols, "cells": cells}

    # Guardar grilla en JSON
    with open(GRID_FILE, "w") as f:
        json.dump(grid_data, f, indent=4)
    print(f"Grilla guardada en {GRID_FILE}")

    # Mostrar la grilla sobre la imagen
    cv2.namedWindow("Popup con grilla", cv2.WINDOW_NORMAL)
    selector.draw_grid(frame, cells)  # dibuja todas las celdas
    print("La grilla se muestra sobre el popup. Presiona cualquier tecla para cerrar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
