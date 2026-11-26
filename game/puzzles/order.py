"""Перестановка предметов: книги, ключи, плитки с символами. Клик по предмету, затем клик по другому месту — меняются.
JSON: {"puzzle": "order", "style": "books"|"keys"|"tiles", "start": [...], "answer": [...], "title": "...", "onWin": [...]}
Предмет — имя символа (square/circle/diamond/triangle) или любая строка (номер ключа). null = пустое место (крючок).
Необязательно: "labels": {"id": "подпись"}."""
import pygame

from .. import assets
from ..settings import VIEW_W, COLOR_ACCENT
from .base import PuzzleTask
from .draw import draw_token, draw_hint
from .logic import OrderLogic

BOOK_COLORS = [(92, 52, 40), (44, 66, 92), (62, 84, 52), (88, 62, 96), (110, 86, 40), (70, 70, 70)]
SIZES = {"books": (96, 270, 18), "keys": (110, 210, 20), "tiles": (130, 130, 20)}  # ширина, высота, зазор


class OrderPuzzle(PuzzleTask):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.style = cfg.get("style", "tiles")
        self.logic = OrderLogic(cfg["start"], cfg["answer"])
        self.labels = cfg.get("labels", {})
        self.kinds = list(dict.fromkeys(t for t in cfg["answer"] if t is not None))
        n = len(cfg["answer"])
        w, h, gap = SIZES.get(self.style, SIZES["tiles"])
        x0 = VIEW_W // 2 - (n * w + (n - 1) * gap) // 2
        top = 400 - h // 2
        self.rects = [pygame.Rect(x0 + i * (w + gap), top, w, h) for i in range(n)]

    def click(self, pos):
        for i, r in enumerate(self.rects):
            if r.collidepoint(pos):
                self.logic.click(i)
                if self.logic.solved():
                    self.won = True
                return

    def _text(self, tok):
        return self.labels.get(tok, tok)

    def _draw_item(self, surf, r, tok):
        if self.style == "books":
            col = BOOK_COLORS[self.kinds.index(tok) % len(BOOK_COLORS)]
            pygame.draw.rect(surf, col, r)
            pygame.draw.rect(surf, (20, 16, 14), r, 3)
            pygame.draw.line(surf, (200, 180, 120), (r.x + 8, r.y + 22), (r.right - 8, r.y + 22), 2)
            pygame.draw.line(surf, (200, 180, 120), (r.x + 8, r.bottom - 22), (r.right - 8, r.bottom - 22), 2)
            draw_token(surf, self._text(tok), (r.centerx, r.y + 110), 50, (236, 224, 190))
        elif self.style == "keys":
            head = (r.centerx, r.y + 56)
            pygame.draw.circle(surf, (210, 190, 120), head, 38, 5)
            pygame.draw.rect(surf, (210, 190, 120), (r.centerx - 7, r.y + 94, 14, 90))
            pygame.draw.rect(surf, (210, 190, 120), (r.centerx + 7, r.y + 150, 18, 10))
            pygame.draw.rect(surf, (210, 190, 120), (r.centerx + 7, r.y + 170, 14, 10))
            draw_token(surf, self._text(tok), head, 36, (236, 232, 214))
        else:
            pygame.draw.rect(surf, (30, 30, 36), r)
            pygame.draw.rect(surf, (120, 112, 90), r, 3)
            draw_token(surf, self._text(tok), r.center, 70)

    def draw_body(self, surf):
        draw_hint(surf, "Нажми на предмет, затем на другое место — они поменяются")
        if self.style == "keys":  # планка с крючками
            pygame.draw.rect(surf, (60, 46, 34), (self.rects[0].x - 30, self.rects[0].y - 14,
                                                  self.rects[-1].right - self.rects[0].x + 60, 16))
        for i, (r, tok) in enumerate(zip(self.rects, self.logic.slots)):
            if tok is None:
                if self.style == "keys":
                    pygame.draw.circle(surf, (120, 112, 90), (r.centerx, r.y + 12), 9, 3)  # пустой крючок
                else:
                    pygame.draw.rect(surf, (60, 60, 60), r, 2)
            else:
                self._draw_item(surf, r, tok)
            if self.logic.sel == i:
                pygame.draw.rect(surf, COLOR_ACCENT, r.inflate(10, 10), 5)
