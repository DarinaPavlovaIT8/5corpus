"""Сцена = фон + кликабельные зоны (хотспоты). Данные берутся из data/scenes.json."""
import pygame

from . import assets
from .settings import VIEW_W, VIEW_H


class Hotspot:
    def __init__(self, d):
        x, y, w, h = d["rect"]  # проценты от размера экрана
        self.rect = pygame.Rect(VIEW_W * x / 100, VIEW_H * y / 100, VIEW_W * w / 100, VIEW_H * h / 100)
        self.label = d.get("label", "")
        self.rules = d.get("rules", [])
        self.visible_if = d.get("visibleIf")
        self.img = d.get("img")  # отдельная картинка предмета, показывается пока зона видима

    def first_rule(self, state):
        """Первое правило, условия которого выполнены."""
        for r in self.rules:
            if state.check(r.get("if")):
                return r
        return None


class Scene:
    def __init__(self, sid, d):
        self.id = sid
        self.title = d.get("title", sid)
        self.bg = d.get("bg")
        self.color = pygame.Color(d.get("color", "#111111"))
        self.on_enter = d.get("onEnter", [])
        self.arrows = d.get("arrows", {})  # {"left": id, "right": id, "up": id, "down": id}
        self.hotspots = [Hotspot(h) for h in d.get("hotspots", [])]

    def visible_hotspots(self, state):
        return [h for h in self.hotspots if state.check(h.visible_if)]

    def hotspot_at(self, pos, state):
        for h in reversed(self.visible_hotspots(state)):
            if h.rect.collidepoint(pos):
                return h
        return None

    def draw(self, surf, state, debug=False):
        bg = assets.image(self.bg, (VIEW_W, VIEW_H)) if self.bg else None
        if bg:
            surf.blit(bg, (0, 0))
        else:  # заглушка, пока художник не нарисовал фон
            surf.fill(self.color, (0, 0, VIEW_W, VIEW_H))
            surf.blit(assets.font(20).render(self.title, True, (120, 120, 120)), (16, 12))
        for h in self.visible_hotspots(state):  # предметы-спрайты исчезают, когда их забрали
            sprite = assets.image(h.img, (h.rect.w, h.rect.h)) if h.img else None
            if sprite:
                surf.blit(sprite, h.rect.topleft)
        if debug:
            for h in self.visible_hotspots(state):
                pygame.draw.rect(surf, (0, 255, 0), h.rect, 1)
                surf.blit(assets.font(14).render(h.label, True, (0, 255, 0)), h.rect.topleft)
