# app/logic/replay.py
import time
import random
from app.input import mouse, keyboard


class ReplayRunner:
    def __init__(self, grid, recording):
        self.grid = grid
        self.recording = recording
        self.running = False

        # 🔧 Parámetros de velocidad ajustables
        self.hold_time_default = (
            0.04  # tiempo mínimo que el click se mantiene presionado
        )
        self.delta_factor = (
            0.2  # multiplicador de delta para ajustar espera entre clicks
        )

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
            hold = step.get("hold", self.hold_time_default)
            delta = step.get("delta", 0) * self.delta_factor

            cell = self.grid[cell_index]

            print(f"Click cell {cell_index} | hold={hold:.3f}s | delta={delta:.3f}")

            # Click estable, rápido y seguro
            mouse.click_cell(cell, hold_time=hold)

            # Espera delta ajustable con micro-jitter
            if delta > 0:
                time.sleep(delta + random.uniform(-0.02, 0.02))

        print("\nReplay finalizado")
        self.running = False
