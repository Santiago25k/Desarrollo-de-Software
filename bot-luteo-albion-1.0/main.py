# main.py
import json
import time
import os

from app.logic.replay import ReplayRunner


def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROFILE_FILE = os.path.join(BASE_DIR, "app", "data", "click_profile.json")

    print("Cargando perfil...")

    if not os.path.exists(PROFILE_FILE):
        print("ERROR: No se encontró el archivo click_profile.json")
        return

    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 🔑 EXTRAEMOS SOLO LAS CELDAS
    grid = data["grid"]["cells"]
    recording = data["recording"]

    print(f"Celdas cargadas: {len(grid)}")
    print(f"Eventos grabados: {len(recording)}")

    runner = ReplayRunner(grid, recording)

    time.sleep(0.5)

    runner.wait_for_shift()
    runner.run()


if __name__ == "__main__":
    main()
