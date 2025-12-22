import cv2
import json
import time
import os

from app.screen.capture import ScreenCapture
from app.screen.roi_selector import ROISelector

WINDOW_NAME = "Albion Online Client"
ROI_FILE = "popup_roi.json"
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

    # Abrimos snapshot para seleccionar ROI (sin bucle)
    cv2.namedWindow("Calibracion Popup", cv2.WINDOW_NORMAL)
    selector = ROISelector("Calibracion Popup")
    roi = selector.select_static(frame)  # selección única

    if roi:
        data = {"x": roi[0], "y": roi[1], "w": roi[2], "h": roi[3]}
        with open(ROI_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("ROI guardado:", data)
    else:
        print("ROI no seleccionado")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
