import cv2
import numpy as np
import pyautogui
import time

region_pique_left = 100
region_pique_top = 350
region_pique_width = 400
region_pique_height = 300

region_puzzle_width = 400
region_puzzle_height = 200
region_puzzle_left = (1920 - region_puzzle_width) // 2
region_puzzle_top = (1080 - region_puzzle_height) // 2 + 50

lower_pink = np.array([160, 100, 200])
upper_pink = np.array([180, 255, 255])

lower_orange = np.array([15, 180, 200])
upper_orange = np.array([25, 255, 255])

frames_para_confirmar = 4

def detectar_hundimiento():
    print("Esperando hundimiento del bobber rosa...")
    cv2.namedWindow("Deteccion Bobber Rosa", cv2.WINDOW_GUI_EXPANDED)
    cv2.setWindowProperty("Deteccion Bobber Rosa", cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow("Deteccion Bobber Rosa", 600, 50)

    bobber_detectado = False
    frames_sin_bobber = 0
    hundio = False

    while True:
        screenshot = pyautogui.screenshot(region=(region_pique_left, region_pique_top, region_pique_width, region_pique_height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_pink, upper_pink)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        pequeño_rojo = False
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 5 < area < 50:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
                cv2.putText(frame, "BOBBER ROSA", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                pequeño_rojo = True
                break

        if not bobber_detectado and pequeño_rojo:
            bobber_detectado = True
            print("Bobber rosa detectado...")

        elif bobber_detectado:
            if not pequeño_rojo:
                frames_sin_bobber += 1
                print(f"Bobber desaparecido (frame {frames_sin_bobber})")
                if frames_sin_bobber >= frames_para_confirmar:
                    print("¡Bobber desapareció! Haciendo clic...")
                    pyautogui.click(region_pique_left + region_pique_width // 2, region_pique_top + region_pique_height // 2)
                    time.sleep(0.5)
                    hundio = True
                    break
            else:
                frames_sin_bobber = 0

        cv2.imshow("Deteccion Bobber Rosa", frame)
        if cv2.waitKey(1) == 27:
            print("Cancelado por usuario.")
            cv2.destroyAllWindows()
            exit()

    cv2.destroyWindow("Deteccion Bobber Rosa")
    return hundio

def controlar_puzzle():
    print("Controlando el puzzle.")
    cv2.namedWindow("Puzzle", cv2.WINDOW_GUI_EXPANDED)
    cv2.setWindowProperty("Puzzle", cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow("Puzzle", 600, 50)

    mouse_pressed = False
    zona_segura_izq = 50
    zona_segura_centro_der = region_puzzle_width // 2 + 30

    while True:
        screenshot = pyautogui.screenshot(region=(region_puzzle_left, region_puzzle_top, region_puzzle_width, region_puzzle_height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_orange, upper_orange)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bobber_x = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 78:
                x, y, w, h = cv2.boundingRect(cnt)
                bobber_x = x + w // 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "BOBBER", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if bobber_x is not None:
            if (zona_segura_izq <= bobber_x <= zona_segura_centro_der):
                if not mouse_pressed:
                    pyautogui.mouseDown()
                    mouse_pressed = True
                    print("Manteniendo clic.")
            else:
                if mouse_pressed:
                    pyautogui.mouseUp()
                    mouse_pressed = False
                    print("Soltando clic.")
        else:
            if mouse_pressed:
                pyautogui.mouseUp()
                mouse_pressed = False
                print("Bobber no detectado, soltando clic.")

        cv2.imshow("Puzzle", frame)
        if cv2.waitKey(1) == 27:
            pyautogui.mouseUp()
            print("Saliendo por ESC.")
            cv2.destroyAllWindows()
            exit()

        if np.count_nonzero(mask) == 0:
            pyautogui.mouseUp()
            print("Puzzle terminado.")
            break

    cv2.destroyWindow("Puzzle")
