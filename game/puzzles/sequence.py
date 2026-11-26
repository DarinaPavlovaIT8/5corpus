"""Кнопки по порядку. JSON: {"puzzle": "sequence", "buttons": ["Красный","Синий","Зелёный"], "order": [1,0,2], "title": "...", "onWin": [...]}
order — номера кнопок (с нуля) в том порядке, в котором их надо нажать. Ошибка сбрасывает ввод."""
import pygame

from .. import ui
from ..settings import VIEW_W, COLOR_ACCENT
from .base import PuzzleTask
from .draw import draw_hint, draw_msg
from .logic import SequenceLogic


class SequencePuzzle(PuzzleTask):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.buttons = cfg["buttons"]
        self.logic = SequenceLogic(cfg["order"])
        n, w, gap = len(self.buttons), 170, 18
        x0 = VIEW_W // 2 - (n * w + (n - 1) * gap) // 2
        self.rects = [pygame.Rect(x0 + i * (w + gap), 330, w, 90) for i in range(n)]
        self.msg, self.msg_t = "", 0.0

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)
        return super().update(dt)

    def click(self, pos):
        for i, r in enumerate(self.rects):
            if r.collidepoint(pos):
                res = self.logic.press(i)
                if res == "win":
                    self.won = True
                elif res == "wrong":
                    self.msg, self.msg_t = "Не то. Всё сначала", 1.2
                return

    def draw_body(self, surf):
        draw_hint(surf, "Нажимай кнопки в правильном порядке")
        pos = pygame.mouse.get_pos()
        for i, (r, text) in enumerate(zip(self.rects, self.buttons)):
            ui.draw_button(surf, r, text, True, r.collidepoint(pos))
        n = len(self.logic.order)
        for k in range(n):  # индикатор прогресса
            c = (VIEW_W // 2 + int((k - (n - 1) / 2) * 34), 500)
            pygame.draw.circle(surf, COLOR_ACCENT if k < len(self.logic.pressed) else (60, 60, 60), c, 11)
        if self.won:
            draw_msg(surf, "Готово", 560, ok=True)
        elif self.msg_t > 0:
            draw_msg(surf, self.msg, 560)
