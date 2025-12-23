# app/logic/replay.py
import time
import random
from app.input import mouse, keyboard


class ReplayRunner:
    def __init__(self, grid, recording):
        self.grid = grid
        self.recording = recording
        self.running = False

    def wait_for_shift(self):
        print("Mantene Shift izquierdo para iniciar...")
        while not keyboard.is_shift_pressed():
            time.sleep(0.05)

    def run(self):
        if self.running:
            print("Replay ya en ejecución, ignorado.")
            return

        self.running = True
        print("\n[SHIFT DOWN] Reproduciendo...\n")

        for step in self.recording:
            if not keyboard.is_shift_pressed():
                print("\n[SHIFT UP] Replay abortado")
                break

            cell_index = step["cell"]
            hold = step["hold"]
            delta = step["delta"]

            cell = self.grid[cell_index]

            print(f"Click cell {cell_index} | hold={hold:.3f}s | delta={delta}")

            mouse.click_cell(cell, hold_time=hold)

            if delta:
                time.sleep(delta + random.uniform(-0.02, 0.02))

        print("\nReplay finalizado")
        self.running = False
