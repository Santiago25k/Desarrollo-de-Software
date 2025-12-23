# app/input/mouseinput.py
from pynput import mouse

mouse_listener = None


def start_mouse_listener(on_click):
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()


def stop_mouse_listener():
    global mouse_listener
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None
