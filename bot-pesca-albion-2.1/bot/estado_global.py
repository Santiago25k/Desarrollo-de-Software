# estado_global.py
estado_callback = None

def registrar_callback(callback):
    global estado_callback
    estado_callback = callback

def actualizar_estado(texto):
    if estado_callback:
        estado_callback(texto)
