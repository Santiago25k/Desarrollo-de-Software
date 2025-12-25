import pyautogui
import time
from cebo import aplicar_cebo
from deteccion import detectar_hundimiento, controlar_puzzle
from alga import usar_alga
from comida import preparar_comida

def ejecutar_bot(log_callback=print, pause_event=None):
    log_callback("🔄 Ajustando cámara.")
    for _ in range(3):
        pyautogui.scroll(400)
        time.sleep(0.2)

    log_callback("🍽️ Usando comida...")
    preparar_comida()
    log_callback("😋Comida en la panza y lista para la acción.")


    log_callback("🛠️ Aplicando cebo..")
    aplicar_cebo()

    contador_peces = 1
    inicio_comida = time.time()
    TIEMPO_COMIDA = 1800  # 30 minutos

    try:
        while True:
            # Aquí chequeamos la pausa
            if pause_event is not None and pause_event.is_set():
                log_callback("⏸️ Bot en pausa, esperando reanudar...")
                while pause_event.is_set():
                    time.sleep(0.5)
                log_callback("▶️ Bot reanudado, continuando...")

            if time.time() - inicio_comida >= TIEMPO_COMIDA:
                log_callback("🔁 Tiempo de comida agotado. Usando comida nuevamente...")
                pyautogui.press('2')
                time.sleep(4)
                aplicar_cebo()
                inicio_comida = time.time()
                log_callback("✅ Comida y cebo reaplicados.")

            if contador_peces % 10 == 0:
                aplicar_cebo()
                log_callback("🛠️ Cebo reaplicado (cada 10 peces).")

            log_callback(f"🎣 Lanzando línea...")
            pyautogui.moveTo(300, 450, duration=0.5)
            pyautogui.mouseDown()
            time.sleep(2.7)
            pyautogui.mouseUp()

            hundio = detectar_hundimiento(log_callback)
            if not hundio:
                continue

            controlar_puzzle(log_callback)

            usar_alga()
            log_callback("🧼Limpiándonos las manos..")


            log_callback(f"🎉🐟 ¡Boom! Pez #{contador_peces} pescado como un campeón!!🌟🌟🌟")


            contador_peces += 1

    except KeyboardInterrupt:
        log_callback("🛑 Bot detenido por el usuario.")
        import cv2
        cv2.destroyAllWindows()
        exit()

def iniciar_desde_interfaz(log_callback=print, pause_event=None):
    ejecutar_bot(log_callback=log_callback, pause_event=pause_event)

if __name__ == "__main__":
    iniciar_desde_interfaz()
