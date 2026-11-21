"""Состояние игры: текущая сцена, флаги, инвентарь. Не зависит от pygame (поэтому легко тестируется)."""


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.scene = None
        self.flags = set()
        self.inventory = []
        self.selected = None  #выбранный предмет из инвентаря

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
