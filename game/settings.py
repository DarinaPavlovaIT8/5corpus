from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT, FPS = 1280, 720, 60
TITLE = "Пятый корпус"

SCENES_PATH = ROOT / "data" / "scenes.json"
ITEMS_PATH = ROOT / "data" / "items.json"
SAVE_PATH = ROOT / "savegame.json"  # в .gitignore, в репозиторий не попадает

COLOR_TEXT = (216, 210, 196)
COLOR_ACCENT = (138, 28, 28)
COLOR_PANEL = (14, 14, 18)
