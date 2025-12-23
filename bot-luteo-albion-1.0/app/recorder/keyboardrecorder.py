# app/input/keyboardinput.py
from pynput import keyboard

keyboard_listener = None


def start_keyboard_listener(on_press, on_release):
    global keyboard_listener
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()


def stop_keyboard_listener():
    global keyboard_listener
    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None
