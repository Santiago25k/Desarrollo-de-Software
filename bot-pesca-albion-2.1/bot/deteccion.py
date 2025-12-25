import cv2
import numpy as np
import pyautogui
import time

# Región de pique
region_pique_left = 100
region_pique_top = 350
region_pique_width = 400
region_pique_height = 300

# Región del puzzle
region_puzzle_width = 400
region_puzzle_height = 200
region_puzzle_left = (1920 - region_puzzle_width) // 2
region_puzzle_top = (1080 - region_puzzle_height) // 2 + 50

# Color naranja del bobber
lower_orange = np.array([15, 180, 200])
upper_orange = np.array([25, 255, 255])


def detectar_hundimiento(log_callback=print):
    log_callback("Eso.. muerde el cebo 👀")

    ventana = "Detección"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, region_pique_width, region_pique_height)
    cv2.moveWindow(ventana, 600, 50)

    lower_red1 = np.array([0, 100, 80])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 80])
    upper_red2 = np.array([179, 255, 255])

    bobber_detectado = False
    frames_sin_bobber = 0
    pos_y_anterior = None
    umbral_bajada = 4
    last_click_pos = None

    while True:
        screenshot = pyautogui.screenshot(
            region=(
                region_pique_left,
                region_pique_top,
                region_pique_width,
                region_pique_height,
            )
        )
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_cnt = max(contours, key=cv2.contourArea, default=None)
        if best_cnt is not None and cv2.contourArea(best_cnt) > 50:
            x, y, w, h = cv2.boundingRect(best_cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            last_click_pos = (
                region_pique_left + x + w // 2,
                region_pique_top + y + h // 2,
            )
            y_actual = y

            if not bobber_detectado:
                bobber_detectado = True
                pos_y_anterior = y_actual
                log_callback("🧐 A la vista.")
            elif (y_actual - pos_y_anterior) > umbral_bajada:
                log_callback("🐟 Mordio el cebo 🥵🥵!")
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
                if frames_sin_bobber >= 5:
                    # log_callback("⚠️ Bobber perdido de vista. Click por seguridad.")
                    if last_click_pos:
                        pyautogui.click(*last_click_pos)
                    time.sleep(0.5)
                    cv2.destroyWindow(ventana)
                    return True

        cv2.imshow(ventana, frame)
        if cv2.waitKey(1) == 27:
            log_callback("⛔ Cancelado por el usuario.")
            cv2.destroyAllWindows()
            exit()


def controlar_puzzle(log_callback=print):
    log_callback("🎣🐟 Pescando al maldito... 😎😎")
    ventana = "Puzzle"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, region_puzzle_width, region_puzzle_height)
    cv2.moveWindow(ventana, 600, 50)

    mouse_pressed = False
    zona_segura_izq = 25
    zona_segura_der = 215

    while True:
        screenshot = pyautogui.screenshot(
            region=(
                region_puzzle_left,
                region_puzzle_top,
                region_puzzle_width,
                region_puzzle_height,
            )
        )
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bobber_x = None
        for cnt in contours:
            if cv2.contourArea(cnt) > 78:
                x, y, w, h = cv2.boundingRect(cnt)
                bobber_x = x + w // 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if bobber_x is not None:
            if zona_segura_izq <= bobber_x <= zona_segura_der:
                if not mouse_pressed:
                    pyautogui.mouseDown()
                    mouse_pressed = True
                    # log_callback("🎯 Bobber en zona segura. Manteniendo clic.")
            else:
                if mouse_pressed:
                    pyautogui.mouseUp()
                    mouse_pressed = False
                    # log_callback("↩️ Bobber fuera de zona. Reiniciando clic.")
                    pyautogui.mouseDown()
                    time.sleep(0.3)
                    pyautogui.mouseUp()
                    pyautogui.mouseDown()
                    time.sleep(0.3)
                    pyautogui.mouseUp()
        else:
            if mouse_pressed:
                pyautogui.mouseUp()
                mouse_pressed = False
                # log_callback("❓ Bobber no detectado. Soltando clic.")

        cv2.imshow(ventana, frame)
        key = cv2.waitKey(1)
        if key == 27:
            pyautogui.mouseUp()
            log_callback("🚪 Saliendo por ESC.")
            break
        if np.count_nonzero(mask) == 0:
            pyautogui.mouseUp()
            # log_callback("✅ Puzzle completado.")
            break

    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    time.sleep(5)
    if detectar_hundimiento():
        controlar_puzzle()
