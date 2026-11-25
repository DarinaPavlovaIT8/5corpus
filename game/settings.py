from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Окно = сцена 16:9 слева + панель инвентаря справа (как в Rusty Lake)
VIEW_W, VIEW_H = 1280, 720
PANEL_W = 110
WIDTH, HEIGHT, FPS = VIEW_W + PANEL_W, VIEW_H, 60
TITLE = "Пятый корпус"

SCENES_PATH = ROOT / "data" / "scenes.json"
ITEMS_PATH = ROOT / "data" / "items.json"
RECIPES_PATH = ROOT / "data" / "recipes.json"
SAVE_PATH = ROOT / "savegame.json"  # в .gitignore, в репозиторий не попадает

COLOR_TEXT = (216, 210, 196)
COLOR_ACCENT = (138, 28, 28)
COLOR_PANEL = (14, 14, 18)
