# app/recorder/recorder.py
import time
from pynput import mouse, keyboard

GRID_CELLS = [
    (55, 314, 100, 100),
    (155, 314, 100, 100),
    (255, 314, 100, 100),
    (355, 314, 100, 100),
    (455, 314, 100, 100),
    (55, 414, 100, 100),
    (155, 414, 100, 100),
    (255, 414, 100, 100),
    (355, 414, 100, 100),
    (455, 414, 100, 100),
    (55, 514, 100, 100),
    (155, 514, 100, 100),
    (255, 514, 100, 100),
    (355, 514, 100, 100),
    (455, 514, 100, 100),
    (55, 614, 100, 100),
    (155, 614, 100, 100),
    (255, 614, 100, 100),
    (355, 614, 100, 100),
    (455, 614, 100, 100),
    (55, 714, 100, 100),
    (155, 714, 100, 100),
    (255, 714, 100, 100),
    (355, 714, 100, 100),
    (455, 714, 100, 100),
]

recording = False
click_down_time = None
last_click_time = None
data = []


def get_cell_index(x, y):
    for i, (cx, cy, w, h) in enumerate(GRID_CELLS):
        if cx <= x <= cx + w and cy <= y <= cy + h:
            return i
    return None


def on_mouse_click(x, y, button, pressed):
    global click_down_time, last_click_time

    if not recording or button != mouse.Button.left:
        return

    if pressed:
        click_down_time = time.time()
    else:
        now = time.time()
        hold = now - click_down_time
        delta = None if last_click_time is None else now - last_click_time
        cell = get_cell_index(x, y)

        data.append(
            {
                "cell": cell,
                "hold": round(hold, 3),
                "delta": None if delta is None else round(delta, 3),
            }
        )

        last_click_time = now
        print(f"Cell {cell} | hold={hold:.3f}s | delta={delta}")


def on_key_press(key):
    global recording
    if key == keyboard.Key.shift_l and not recording:
        recording = True
        print("\n[SHIFT DOWN] Grabacion iniciada\n")


def on_key_release(key):
    global recording
    if key == keyboard.Key.shift_l:
        recording = False
        print("\n[SHIFT UP] Grabacion finalizada\n")
        print(data)
