import keyboard  # pip install keyboard


def is_shift_pressed():
    """Devuelve True si Shift izquierdo está presionado"""
    return keyboard.is_pressed("shift")
