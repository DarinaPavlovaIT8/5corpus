from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT, FPS = 1280, 720, 60
TITLE = "Пятый корпус"

# Раскладка экрана: слева игровая зона, справа панель инвентаря на всю высоту
# (ширина слота в ui.py = 90, поэтому панель 140)
PANEL_W = 140
VIEW_W = WIDTH - PANEL_W   # игровая зона: x от 0 до VIEW_W
VIEW_H = HEIGHT            # игровая зона: y от 0 до VIEW_H

SCENES_PATH = ROOT / "data" / "scenes.json"
ITEMS_PATH = ROOT / "data" / "items.json"
RECIPES_PATH = ROOT / "data" / "recipes.json"
SAVE_PATH = ROOT / "savegame.json"  # в .gitignore, в репозиторий не попадает

COLOR_TEXT = (216, 210, 196)
COLOR_ACCENT = (138, 28, 28)
COLOR_PANEL = (14, 14, 18)
