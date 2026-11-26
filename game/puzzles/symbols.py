"""Механический замок с барабанами-символами.
JSON: {"puzzle": "symbols", "answer": ["triangle", "diamond", "circle"], "title": "...", "onWin": [...]}
Необязательно: "symbols" (набор на барабане, по умолчанию 4 фигуры), "start" (стартовые символы)."""
import pygame

from .. import ui
from ..settings import VIEW_W
from .base import PuzzleTask
from .draw import draw_symbol, draw_msg, draw_hint
from .logic import SymbolsLogic, SYMBOLS


class SymbolsPuzzle(PuzzleTask):
    CY = 350

    def __init__(self, cfg):
        super().__init__(cfg)
        self.logic = SymbolsLogic(cfg["answer"], cfg.get("symbols", SYMBOLS), cfg.get("start"))
        n = len(cfg["answer"])
        self.cx = [VIEW_W // 2 + int((i - (n - 1) / 2) * 220) for i in range(n)]
        self.open_btn = pygame.Rect(VIEW_W // 2 - 110, 565, 220, 60)
        self.msg, self.msg_t = "", 0.0

    def _rects(self, cx):
        cy = self.CY
        return (pygame.Rect(cx - 50, cy - 150, 100, 46),   # вверх (назад по кругу)
                pygame.Rect(cx - 80, cy - 80, 160, 160),   # окошко барабана
                pygame.Rect(cx - 50, cy + 104, 100, 46))   # вниз (вперёд)

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)
        return super().update(dt)

    def click(self, pos):
        for i, cx in enumerate(self.cx):
            up, box, down = self._rects(cx)
            if up.collidepoint(pos):
                self.logic.turn(i, -1)
                return
            if down.collidepoint(pos) or box.collidepoint(pos):
                self.logic.turn(i, 1)
                return
        if self.open_btn.collidepoint(pos):
            if self.logic.solved():
                self.won = True
            else:
                self.msg, self.msg_t = "Замок не поддаётся", 1.2

    def draw_body(self, surf):
        draw_hint(surf, "Крути барабаны, пока символы не совпадут, и жми «Открыть»")
        pos = pygame.mouse.get_pos()
        for i, cx in enumerate(self.cx):
            up, box, down = self._rects(cx)
            pygame.draw.rect(surf, (30, 30, 34), box)
            pygame.draw.rect(surf, (120, 112, 90), box, 4)
            draw_symbol(surf, self.logic.current()[i], box.center, 80)
            c = up.center
            pygame.draw.polygon(surf, (190, 40, 40) if up.collidepoint(pos) else (236, 232, 214),
                                [(c[0], c[1] - 14), (c[0] - 26, c[1] + 12), (c[0] + 26, c[1] + 12)])
            c = down.center
            pygame.draw.polygon(surf, (190, 40, 40) if down.collidepoint(pos) else (236, 232, 214),
                                [(c[0], c[1] + 14), (c[0] - 26, c[1] - 12), (c[0] + 26, c[1] - 12)])
        ui.draw_button(surf, self.open_btn, "Открыть", True, self.open_btn.collidepoint(pos))
        if self.won:
            draw_msg(surf, "Замок щёлкнул", 530, ok=True)
        elif self.msg_t > 0:
            draw_msg(surf, self.msg, 530)
