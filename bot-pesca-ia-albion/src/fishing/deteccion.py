import cv2
import numpy as np
import pyautogui
import time

from src.config import (
    REGION_PIQUE, REGION_PUZZLE,
    BOBBER_ROJO_1_LOW, BOBBER_ROJO_1_HIGH,
    BOBBER_ROJO_2_LOW, BOBBER_ROJO_2_HIGH,
    PUZZLE_NARANJA_LOW, PUZZLE_NARANJA_HIGH,
    UMBRAL_BAJADA_BOBBER, FRAMES_SIN_BOBBER,
    AREA_MIN_BOBBER, AREA_MIN_PUZZLE,
    PUZZLE_ZONA_IZQ, PUZZLE_ZONA_DER,
)

_LOW1  = np.array(BOBBER_ROJO_1_LOW)
_HIGH1 = np.array(BOBBER_ROJO_1_HIGH)
_LOW2  = np.array(BOBBER_ROJO_2_LOW)
_HIGH2 = np.array(BOBBER_ROJO_2_HIGH)
_NARANJA_LOW  = np.array(PUZZLE_NARANJA_LOW)
_NARANJA_HIGH = np.array(PUZZLE_NARANJA_HIGH)


def _capturar(region: dict) -> np.ndarray:
    shot = pyautogui.screenshot(
        region=(region['left'], region['top'], region['width'], region['height'])
    )
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def detectar_hundimiento(log_callback=print) -> bool:
    log_callback("Esperando picada...")
    ventana = "Deteccion"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, REGION_PIQUE['width'], REGION_PIQUE['height'])
    cv2.moveWindow(ventana, 600, 50)

    bobber_detectado = False
    frames_sin_bobber = 0
    pos_y_anterior = None
    last_click_pos = None

    while True:
        frame = _capturar(REGION_PIQUE)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.bitwise_or(
            cv2.inRange(hsv, _LOW1, _HIGH1),
            cv2.inRange(hsv, _LOW2, _HIGH2),
        )
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best = max(contours, key=cv2.contourArea, default=None)

        if best is not None and cv2.contourArea(best) > AREA_MIN_BOBBER:
            x, y, w, h = cv2.boundingRect(best)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            last_click_pos = (
                REGION_PIQUE['left'] + x + w // 2,
                REGION_PIQUE['top']  + y + h // 2,
            )
            y_actual = y

            if not bobber_detectado:
                bobber_detectado = True
                pos_y_anterior = y_actual
                log_callback("Bobber a la vista.")
            elif (y_actual - pos_y_anterior) > UMBRAL_BAJADA_BOBBER:
                log_callback("PICO!")
                pyautogui.click(*last_click_pos)
                time.sleep(0.5)
                cv2.destroyWindow(ventana)
                return True
            else:
                pos_y_anterior = y_actual
                frames_sin_bobber = 0
        else:
            if bobber_detectado:
                frames_sin_bobber += 1
                if frames_sin_bobber >= FRAMES_SIN_BOBBER:
                    if last_click_pos:
                        pyautogui.click(*last_click_pos)
                    time.sleep(0.5)
                    cv2.destroyWindow(ventana)
                    return True

        cv2.imshow(ventana, frame)
        if cv2.waitKey(1) == 27:
            log_callback("Cancelado por el usuario.")
            cv2.destroyAllWindows()
            return False


def controlar_puzzle(log_callback=print):
    log_callback("Controlando puzzle...")
    ventana = "Puzzle"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, REGION_PUZZLE['width'], REGION_PUZZLE['height'])
    cv2.moveWindow(ventana, 600, 50)

    mouse_presionado = False

    while True:
        frame = _capturar(REGION_PUZZLE)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, _NARANJA_LOW, _NARANJA_HIGH)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bobber_x = None
        for cnt in contours:
            if cv2.contourArea(cnt) > AREA_MIN_PUZZLE:
                x, y, w, h = cv2.boundingRect(cnt)
                bobber_x = x + w // 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if bobber_x is not None:
            if PUZZLE_ZONA_IZQ <= bobber_x <= PUZZLE_ZONA_DER:
                if not mouse_presionado:
                    pyautogui.mouseDown()
                    mouse_presionado = True
            else:
                if mouse_presionado:
                    pyautogui.mouseUp()
                    mouse_presionado = False
                    pyautogui.mouseDown()
                    time.sleep(0.3)
                    pyautogui.mouseUp()
                    pyautogui.mouseDown()
                    time.sleep(0.3)
                    pyautogui.mouseUp()
        else:
            if mouse_presionado:
                pyautogui.mouseUp()
                mouse_presionado = False

        cv2.imshow(ventana, frame)
        key = cv2.waitKey(1)
        if key == 27:
            pyautogui.mouseUp()
            log_callback("Saliendo por ESC.")
            break
        if np.count_nonzero(mask) == 0:
            pyautogui.mouseUp()
            log_callback("Puzzle completado.")
            break

    cv2.destroyAllWindows()
    cv2.waitKey(1)
