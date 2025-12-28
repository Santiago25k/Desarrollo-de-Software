import os

# Carpeta donde están las imágenes
FOLDER_PATH = "out"

# Extensiones permitidas
VALID_EXTENSIONS = (".png", ".jpg", ".jpeg")


def rename_images():
    files = sorted(
        [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith(VALID_EXTENSIONS)]
    )

    for index, filename in enumerate(files, start=1):
        old_path = os.path.join(FOLDER_PATH, filename)
        new_name = f"img_{index:03}.png"
        new_path = os.path.join(FOLDER_PATH, new_name)

        os.rename(old_path, new_path)
        print(f"Renombrado: {filename} → {new_name}")

    print("✔ Renombrado completado.")


if __name__ == "__main__":
    rename_images()
