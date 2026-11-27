"""Состояние игры: текущая сцена, флаги, инвентарь + сохранение. Не зависит от pygame (легко тестируется)."""
import json

from .settings import SAVE_PATH


def find_recipe(recipes, a, b):
    """Ищет рецепт для пары предметов (порядок не важен). Нет рецепта -> None."""
    if not a or not b:
        return None
    pair = {a, b}
    for r in recipes:
        if {r.get("a"), r.get("b")} == pair:
            return r
    return None


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.scene = None
        self.flags = set()
        self.inventory = []
        self.selected = None  # выбранный предмет из инвентаря

    def check(self, cond):
        """Условие из JSON: flag, notFlag, has, selected (все указанные должны выполняться)."""
        if not cond:
            return True
        if "flag" in cond and cond["flag"] not in self.flags:
            return False
        if "notFlag" in cond and cond["notFlag"] in self.flags:
            return False
        if "has" in cond and cond["has"] not in self.inventory:
            return False
        if "selected" in cond and self.selected != cond["selected"]:
            return False
        return True

    # ---------- скрещивание предметов ----------
    def combine(self, recipe):
        """Применяет рецепт: убирает исходные предметы, добавляет result. True = получилось, False = нет.
        Необязательное поле рецепта "keep": ["id", ...] — предметы, которые НЕ расходуются
        (повторное использование, например карандаш). Действия recipe["do"] запускает game.py."""
        if not recipe:
            return False
        a, b = recipe.get("a"), recipe.get("b")
        if a == b or a not in self.inventory or b not in self.inventory:
            return False
        keep = set(recipe.get("keep", []))
        for item in (a, b):
            if item not in keep and item in self.inventory:
                self.inventory.remove(item)
        result = recipe.get("result")
        if result and result not in self.inventory:
            self.inventory.append(result)
        self.selected = None
        return True

    def prune_inventory(self, items):
        """Убирает из инвентаря предметы, которые уже отработали. В items.json у предмета может быть
        "dropWhen": ["флаг", ...]: когда выставлены ВСЕ эти флаги, предмет больше не нужен по сюжету.
        Предметы без dropWhen остаются навсегда. Возвращает список id убранных предметов."""
        gone = [i for i in self.inventory
                if items.get(i, {}).get("dropWhen") and all(f in self.flags for f in items[i]["dropWhen"])]
        for i in gone:
            self.inventory.remove(i)
        if self.selected in gone:
            self.selected = None
        return gone

    # ---------- сохранение ----------
    def save(self, path=SAVE_PATH):
        """Пишем через временный файл, чтобы при сбое не испортить старое сохранение."""
        data = {"version": 1, "scene": self.scene, "flags": sorted(self.flags), "inventory": self.inventory}
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    def load(self, valid_scenes=None, path=SAVE_PATH):
        """True, если сохранение прочитано. Битый файл или сцена, которой уже нет, дают False."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        if not isinstance(data, dict) or not isinstance(data.get("scene"), str):
            return False
        if valid_scenes is not None and data["scene"] not in valid_scenes:
            return False  # например, сцену переименовали или удалили
        self.reset()
        self.scene = data["scene"]
        self.flags = set(data.get("flags", []))
        self.inventory = list(data.get("inventory", []))
        return True

    @staticmethod
    def has_save(path=SAVE_PATH):
        return path.exists()

    @staticmethod
    def delete_save(path=SAVE_PATH):
        try:
            path.unlink()
        except OSError:
            pass
