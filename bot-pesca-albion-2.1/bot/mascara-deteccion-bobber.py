import cv2
import numpy as np
import pyautogui
import time

print("Tenes 5 segundos para posicionar Albion con las plumas visibles...")
time.sleep(5)

region_left = 100
region_top = 300   # Subí un poco la región para incluir bien las plumas
region_width = 400
region_height = 200

def nothing(x):
    pass

cv2.namedWindow("Calibracion Plumas Rojas")
cv2.namedWindow("Mascara Rojas")

# Más espacio horizontal
cv2.resizeWindow("Calibracion Plumas Rojas", 1200, 400)
cv2.resizeWindow("Mascara Rojas", 600, 400)

cv2.setWindowProperty("Calibracion Plumas Rojas", cv2.WND_PROP_TOPMOST, 1)
cv2.setWindowProperty("Mascara Rojas", cv2.WND_PROP_TOPMOST, 1)

cv2.moveWindow("Calibracion Plumas Rojas", 10, 50)
cv2.moveWindow("Mascara Rojas", 1230, 50)

# Trackbars para calibrar rojo (recordá que rojo puede estar en dos rangos de H)
cv2.createTrackbar("H Low", "Calibracion Plumas Rojas", 0, 179, nothing)
cv2.createTrackbar("H High", "Calibracion Plumas Rojas", 10, 179, nothing)
cv2.createTrackbar("S Low", "Calibracion Plumas Rojas", 150, 255, nothing)
cv2.createTrackbar("S High", "Calibracion Plumas Rojas", 255, 255, nothing)
cv2.createTrackbar("V Low", "Calibracion Plumas Rojas", 150, 255, nothing)
cv2.createTrackbar("V High", "Calibracion Plumas Rojas", 255, 255, nothing)

while True:
    screenshot = pyautogui.screenshot(region=(region_left, region_top, region_width, region_height))
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_low = cv2.getTrackbarPos("H Low", "Calibracion Plumas Rojas")
    h_high = cv2.getTrackbarPos("H High", "Calibracion Plumas Rojas")
    s_low = cv2.getTrackbarPos("S Low", "Calibracion Plumas Rojas")
    s_high = cv2.getTrackbarPos("S High", "Calibracion Plumas Rojas")
    v_low = cv2.getTrackbarPos("V Low", "Calibracion Plumas Rojas")
    v_high = cv2.getTrackbarPos("V High", "Calibracion Plumas Rojas")

    lower = np.array([h_low, s_low, v_low])
    upper = np.array([h_high, s_high, v_high])

    mask = cv2.inRange(hsv, lower, upper)

    cv2.imshow("Calibracion Plumas Rojas", frame)
    cv2.imshow("Mascara Rojas", mask)

    key = cv2.waitKey(1)
    if key == 27:
        print(f"\nValores seleccionados:")
        print(f"H Low: {h_low}")
        print(f"H High: {h_high}")
        print(f"S Low: {s_low}")
        print(f"S High: {s_high}")
        print(f"V Low: {v_low}")
        print(f"V High: {v_high}")
        break

cv2.destroyAllWindows()
