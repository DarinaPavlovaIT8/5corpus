"""Цифровой замок. JSON: {"puzzle": "code", "code": "3157", "title": "...", "onWin": [...]}"""
import pygame

from .. import assets, ui
from ..settings import VIEW_W, COLOR_TEXT
from .base import PuzzleTask
from .draw import draw_msg
from .logic import CodeLogic

LABELS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "<", "0", "C"]  # < стереть, C сбросить


class CodePuzzle(PuzzleTask):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.logic = CodeLogic(cfg["code"])
        self.msg, self.msg_t = "", 0.0
        bw, bh, gap = 100, 72, 14
        x0 = VIEW_W // 2 - (3 * bw + 2 * gap) // 2
        self.keys = [(lab, pygame.Rect(x0 + (i % 3) * (bw + gap), 295 + (i // 3) * (bh + gap), bw, bh))
                     for i, lab in enumerate(LABELS)]

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)
        return super().update(dt)

    def click(self, pos):
        for lab, r in self.keys:
            if r.collidepoint(pos):
                if lab == "<":
                    self.logic.back()
                elif lab == "C":
                    self.logic.clear()
                else:
                    res = self.logic.press(lab)
                    if res == "win":
                        self.won = True
                    elif res == "wrong":
                        self.msg, self.msg_t = "Неверный код", 1.2
                return

    def draw_body(self, surf):
        n, w, gap = len(self.logic.code), 64, 12
        x0 = VIEW_W // 2 - (n * w + (n - 1) * gap) // 2
        f = assets.font(46)
        for i in range(n):
            r = pygame.Rect(x0 + i * (w + gap), 165, w, 84)
            pygame.draw.rect(surf, (26, 26, 30), r)
            pygame.draw.rect(surf, (90, 90, 90), r, 2)
            if i < len(self.logic.entered):
                img = f.render(self.logic.entered[i], True, COLOR_TEXT)
                surf.blit(img, img.get_rect(center=r.center))
        if self.won:
            draw_msg(surf, "Замок открыт", 275, ok=True)
        elif self.msg_t > 0:
            draw_msg(surf, self.msg, 275)
        pos = pygame.mouse.get_pos()
        for lab, r in self.keys:
            ui.draw_button(surf, r, lab, True, r.collidepoint(pos))
