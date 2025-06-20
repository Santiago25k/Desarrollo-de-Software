import pyautogui
import time
from cebo import aplicar_cebo
from deteccion import detectar_hundimiento, controlar_puzzle
from alga import usar_alga
from comida import preparar_comida

def ejecutar_bot():
    print("Tenés 10 segundos para posicionar Albion con el bobber visible...")
    time.sleep(10)

    # --- Paso 1: Scroll inicial ---
    print("Haciendo scroll hacia adelante 5 veces...")
    for _ in range(5):
        pyautogui.scroll(500)
        time.sleep(0.2)

    # --- Paso 2 y 3: Equipar y usar comida (inicio) ---
    preparar_comida()

    # --- Paso 4: Aplicar cebo (inicio) ---
    aplicar_cebo()

    # --- Iniciar ciclo de pesca ---
    contador_peces = 1
    inicio_comida = time.time()
    TIEMPO_COMIDA = 1800  # 1800 segundos = 30 minutos

    try:
        while True:
            # ⏱️ Verificar si pasaron 30 minutos
            tiempo_actual = time.time()
            if tiempo_actual - inicio_comida >= TIEMPO_COMIDA:
                print("⏸️ Pausando bot por 30 segundos para usar comida...")
                time.sleep(5)
                print("🍽️ Usando comida (presionando '2')...")
                pyautogui.press('2')
                time.sleep(4)

                for i in range(20, 0, -1):
                    print(f"⏳ Reanudando bot en {i} segundos...", end='\r')
                    time.sleep(1)

                print("\n✅ Comida usada, reanudando bot.")
                aplicar_cebo()
                inicio_comida = time.time()

            # 🐟 Proceso normal de pesca
            if contador_peces % 10 == 0:
                aplicar_cebo()

            print("🎣 Lanzando bobber...")
            pyautogui.moveTo(200, 500, duration=0.5)
            pyautogui.mouseDown()
            time.sleep(3)
            pyautogui.mouseUp()

            hundio = detectar_hundimiento()
            if not hundio:
                continue

            controlar_puzzle()
            usar_alga()

            contador_peces += 1
            print(f"🐟 Peces pescados: {contador_peces}")

    except KeyboardInterrupt:
        print("\n🛑 Programa detenido por el usuario.")
        import cv2
        cv2.destroyAllWindows()
        exit()

# ✅ Este se usará desde interfaz.py
def iniciar_desde_interfaz():
    ejecutar_bot()

# ✅ Este solo se ejecuta si se corre desde consola (no desde interfaz)
if __name__ == "__main__":
    iniciar_desde_interfaz()
