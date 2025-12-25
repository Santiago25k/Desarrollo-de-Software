import os
import time
import pyautogui
import cv2
import numpy as np

# Ruta absoluta a la carpeta con imágenes
ruta_img = r"C:\Users\Aquiles\Desktop\portada\bot-pesca-albion-1.0copy\img"

def listar_archivos(ruta):
    print(f"📁 Listando archivos en: {ruta}")
    if not os.path.exists(ruta):
        print("❌ La carpeta no existe.")
        return []
    archivos = os.listdir(ruta)
    if archivos:
        for archivo in archivos:
            print(" -", archivo)
        return archivos
    else:
        print("⚠️ La carpeta está vacía.")
        return []

def mostrar_y_buscar(imagen_nombre, confidence=0.7):
    ruta_imagen = os.path.join(ruta_img, imagen_nombre)
    print(f"\n🔍 Probando imagen: {ruta_imagen}")

    if not os.path.isfile(ruta_imagen):
        print(f"❌ Archivo no encontrado: {ruta_imagen}")
        return False

    # Abrir la imagen en ventana para simular que está en pantalla (como en el juego)
    img = cv2.imread(ruta_imagen)
    if img is None:
        print(f"❌ No se pudo cargar la imagen con OpenCV: {ruta_imagen}")
        return False

    cv2.imshow("Imagen para detección (cerrar ventana para continuar)", img)
    print("⌛ Tenés 5 segundos para que la ventana esté visible en pantalla...")
    cv2.waitKey(5000)
    cv2.destroyAllWindows()

    # Ahora busca la imagen en la pantalla con pyautogui
    ubicacion = pyautogui.locateCenterOnScreen(ruta_imagen, confidence=confidence)
    if ubicacion:
        print(f"✅ Imagen encontrada en pantalla en: {ubicacion}")
        return True
    else:
        print("❌ Imagen NO encontrada en pantalla.")
        return False


if __name__ == "__main__":
    archivos = listar_archivos(ruta_img)

    # Ajustá los nombres según los archivos que te aparecen listados
    imagenes_a_probar = ["alga.png"]

    time.sleep(3)  # Un pequeño tiempo para prepararte

    for imagen in imagenes_a_probar:
        mostrar_y_buscar(imagen, confidence=0.6)
