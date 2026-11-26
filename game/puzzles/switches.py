"""Тумблеры щитка: нужно выставить нужное сочетание (1 = вверх).
JSON: {"puzzle": "switches", "count": 4, "target": [1,0,1,1], "labels": ["1","2","3","4"], "title": "...", "onWin": [...]}
target необязателен (тогда нужно включить все). Победа засчитывается, как только сочетание совпало."""
import pygame

from .. import assets
from ..settings import VIEW_W, COLOR_ACCENT, COLOR_TEXT
from .base import PuzzleTask
from .draw import draw_hint
from .logic import SwitchesLogic


class SwitchesPuzzle(PuzzleTask):
    def __init__(self, cfg):
        super().__init__(cfg)
        n = cfg.get("count") or len(cfg.get("target", [])) or 4
        self.logic = SwitchesLogic(n, cfg.get("target"), cfg.get("start"))
        self.labels = cfg.get("labels") or [str(i + 1) for i in range(n)]
        self.rects = [pygame.Rect(VIEW_W // 2 + int((i - (n - 1) / 2) * 150) - 40, 235, 80, 300) for i in range(n)]

    def click(self, pos):
        for i, r in enumerate(self.rects):
            if r.collidepoint(pos):
                self.logic.toggle(i)
                if self.logic.solved():
                    self.won = True
                return

    def draw_body(self, surf):
        draw_hint(surf, "Нажми на тумблер, чтобы переключить его: вверх или вниз")
        f = assets.font(30)
        for r, on, lab in zip(self.rects, self.logic.state, self.labels):
            pygame.draw.rect(surf, (36, 36, 42), r)
            pygame.draw.rect(surf, (110, 104, 90), r, 3)
            slot = pygame.Rect(r.centerx - 8, r.y + 20, 16, r.h - 40)
            pygame.draw.rect(surf, (12, 12, 14), slot)
            y = r.y + 60 if on else r.bottom - 60
            pygame.draw.line(surf, (200, 196, 180), r.center, (r.centerx, y), 10)
            pygame.draw.circle(surf, COLOR_ACCENT if on else (150, 146, 134), (r.centerx, y), 22)
            img = f.render(str(lab), True, COLOR_TEXT)
            surf.blit(img, img.get_rect(center=(r.centerx, r.bottom + 34)))
