"""Соединение проводов. Клик по левой клемме, затем по правой — провод. Клик по занятой клемме снимает провод.
JSON: {"puzzle": "wires", "left": ["red","blue","yellow"], "right": ["triangle","circle","square"],
       "pairs": [[0,1],[1,2],[2,0]], "title": "...", "onWin": [...]}
pairs: [номер левой клеммы, номер правой клеммы] (с нуля). Клемма — цвет, символ или текст."""
import math

import pygame

from ..settings import VIEW_W, COLOR_ACCENT
from .base import PuzzleTask
from .draw import COLORS, INK, draw_token, draw_hint, draw_msg
from .logic import WiresLogic

R = 34  # радиус клеммы


class WiresPuzzle(PuzzleTask):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.left, self.right = cfg["left"], cfg["right"]
        self.logic = WiresLogic(len(self.left), cfg["pairs"])
        n = len(self.left)
        ys = [370 + int((i - (n - 1) / 2) * 110) for i in range(n)]
        self.lp = [(300, y) for y in ys]
        self.rp = [(VIEW_W - 300, y) for y in ys]
        self.msg, self.msg_t = "", 0.0

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)
        return super().update(dt)

    @staticmethod
    def _hit(pts, pos):
        for i, (x, y) in enumerate(pts):
            if math.hypot(pos[0] - x, pos[1] - y) <= R + 6:
                return i
        return None

    def click(self, pos):
        i = self._hit(self.lp, pos)
        if i is not None:
            self.logic.click_left(i)
            return
        j = self._hit(self.rp, pos)
        if j is not None:
            self.logic.click_right(j)
            if self.logic.full():
                if self.logic.solved():
                    self.won = True
                else:
                    self.msg, self.msg_t = "Схема не сходится — переставь провода", 1.6

    def _terminal(self, surf, token, pos, selected=False):
        pygame.draw.circle(surf, (30, 30, 36), pos, R + 6)
        pygame.draw.circle(surf, COLOR_ACCENT if selected else (120, 112, 90), pos, R + 6, 4)
        draw_token(surf, token, pos, 44)

    def draw_body(self, surf):
        draw_hint(surf, "Нажми на левую клемму, затем на правую — получится провод. Клик по занятой клемме снимает провод")
        for a, b in self.logic.conn.items():
            col = COLORS.get(self.left[a], INK)
            pygame.draw.line(surf, col, self.lp[a], self.rp[b], 9)
        for i, p in enumerate(self.lp):
            self._terminal(surf, self.left[i], p, self.logic.sel == i)
        for j, p in enumerate(self.rp):
            self._terminal(surf, self.right[j], p)
        if self.won:
            draw_msg(surf, "Контакт есть", 600, ok=True)
        elif self.msg_t > 0:
            draw_msg(surf, self.msg, 600)
