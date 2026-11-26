"""Основа головоломки: затемнённая сцена, заголовок, стрелка «назад», победа."""
import pygame

from .. import assets, ui
from ..actions import Task
from ..settings import VIEW_W, VIEW_H, COLOR_TEXT


class PuzzleTask(Task):
    cancelable = True  # Esc или стрелка вниз закрывают головоломку без победы

    def __init__(self, cfg):
        self.title = cfg.get("title", "")
        self.on_win = cfg.get("onWin", [])  # действия, которые выполнятся при победе
        self.won = False
        self.done = False
        self.win_t = 0.0

    def cancel(self):
        self.done = True

    def update(self, dt):
        if self.won:
            self.win_t += dt
            if self.win_t > 0.8:  # короткая пауза, чтобы успеть увидеть победу
                self.done = True
        return self.done

    def on_click(self, pos=None):
        if pos is None or pos[0] >= VIEW_W or self.won:
            return
        if ui.ARROW_ZONES["down"].collidepoint(pos):
            self.cancel()
            return
        self.click(pos)

    def click(self, pos):  # переопределяется в конкретной головоломке
        pass

    def draw_body(self, surf):  # переопределяется в конкретной головоломке
        pass

    def draw(self, surf):
        veil = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 225))
        surf.blit(veil, (0, 0))
        if self.title:
            img = assets.font(34).render(self.title, True, COLOR_TEXT)
            surf.blit(img, img.get_rect(center=(VIEW_W // 2, 90)))
        self.draw_body(surf)
        ui.draw_arrows(surf, {"down": 1})
