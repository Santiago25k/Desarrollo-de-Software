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

lower_orange = np.array([15, 180, 200])
upper_orange = np.array([25, 255, 255])

frames_para_confirmar = 2

def detectar_hundimiento():
    print("🎣 Preparando caña... esperando picar el pez.")
    ventana = "Detectando Bobber"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(ventana, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(ventana, region_pique_width, region_pique_height)
    cv2.moveWindow(ventana, 600, 50)

    bobber_detectado = False
    frames_sin_bobber = 0
    tiempo_detectado = 0
    last_click_pos = None
    pos_y_anterior = None
    umbral_bajada = 10

    lower_red1 = np.array([0, 100, 80])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 80])
    upper_red2 = np.array([179, 255, 255])

    while True:
        screenshot = pyautogui.screenshot(region=(region_pique_left, region_pique_top, region_pique_width, region_pique_height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        pluma_presente = False
        max_area = 0
        best_cnt = None
        y_actual = None

        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            if area > 50:
                if area > max_area:
                    max_area = area
                    best_cnt = cnt
                    y_actual = y

        if best_cnt is not None:
            x, y, w, h = cv2.boundingRect(best_cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "PLUMA ROJA", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            pluma_presente = True
            last_click_pos = (region_pique_left + x + w // 2, region_pique_top + y + h // 2)

        if not bobber_detectado and pluma_presente:
            bobber_detectado = True
            tiempo_detectado = time.time()
            pos_y_anterior = y_actual
            print("👀 Bobber detectada. Esperando movimiento...")

        elif bobber_detectado:
            if not pluma_presente:
                frames_sin_bobber += 1
                print(f"⚠️ Pluma desaparecida (frame {frames_sin_bobber})")
            else:
                if y_actual is not None and pos_y_anterior is not None:
                    if (y_actual - pos_y_anterior) > umbral_bajada:
                        print("💥 ¡Pez enganchado! Click para atraparlo.")
                        pyautogui.click(*last_click_pos)
                        time.sleep(0.5)
                        cv2.destroyWindow(ventana)
                        return True
                frames_sin_bobber = 0
                pos_y_anterior = y_actual

            if frames_sin_bobber >= 5:
                print("❓ Pluma perdida... lanzando click por seguridad.")
                if last_click_pos is not None:
                    pyautogui.click(*last_click_pos)
                time.sleep(0.5)
                cv2.destroyWindow(ventana)
                return True

        cv2.imshow(ventana, frame)
        if cv2.waitKey(1) == 27:
            print("⛔ Cancelado por usuario.")
            cv2.destroyAllWindows()
            exit()

def controlar_puzzle():
    print("🧩 Entrando al minijuego de pesca...")
    ventana = "Puzzle"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(ventana, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(ventana, region_puzzle_width, region_puzzle_height)
    cv2.moveWindow(ventana, 600, 50)

    mouse_pressed = False
    zona_segura_izq = 25
    zona_segura_centro_der = 215

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
            if zona_segura_izq <= bobber_x <= zona_segura_centro_der:
                if not mouse_pressed:
                    pyautogui.mouseDown()
                    mouse_pressed = True
                  
            else:
                if mouse_pressed:
                    pyautogui.mouseUp()
                    mouse_pressed = False
                    

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
                print("🔎 Bobber no detectado, soltando clic.")

        cv2.imshow(ventana, frame)
        key = cv2.waitKey(1)
        if key == 27:
            pyautogui.mouseUp()
            print("⛔ Saliendo por ESC.")
            break

        if np.count_nonzero(mask) == 0:
            pyautogui.mouseUp()
            print("✅ Puzzle terminado, pez capturado con éxito.")
            break

    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == "__main__":
    time.sleep(5)
    if detectar_hundimiento():
        controlar_puzzle()
