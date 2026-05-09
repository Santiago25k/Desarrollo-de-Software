import json
from pathlib import Path

_DIR = Path(__file__).parent.parent.parent / "waypoints"


def cargar(nombre: str) -> list:
    """Carga lista de waypoints desde waypoints/<nombre>.json"""
    path = _DIR / f"{nombre}.json"
    if not path.exists():
        raise FileNotFoundError(f"Archivo de waypoints no encontrado: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def guardar(nombre: str, puntos: list) -> Path:
    """Guarda lista de waypoints en waypoints/<nombre>.json"""
    _DIR.mkdir(exist_ok=True)
    path = _DIR / f"{nombre}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(puntos, f, indent=2)
    return path


def listar() -> list:
    """Retorna nombres de rutas guardadas (sin extension)."""
    _DIR.mkdir(exist_ok=True)
    return [p.stem for p in _DIR.glob("*.json")]
