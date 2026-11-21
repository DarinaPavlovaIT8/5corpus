"""Сцена = фон + кликабельные зоны (хотспоты). Данные берутся из data/scenes.json."""
import pygame

from . import assets
from .settings import WIDTH, HEIGHT


class Hotspot:
    def __init__(self, d):
        x, y, w, h = d["rect"]  #проценты от размера экрана
        self.rect = pygame.Rect(WIDTH * x / 100, HEIGHT * y / 100, WIDTH * w / 100, HEIGHT * h / 100)
        self.label = d.get("label", "")
        self.rules = d.get("rules", [])
        self.visible_if = d.get("visibleIf")

    def first_rule(self, state):
        """Первое правило, условия которого выполнены"""
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
        self.hotspots = [Hotspot(h) for h in d.get("hotspots", [])]

    def visible_hotspots(self, state):
        return [h for h in self.hotspots if state.check(h.visible_if)]

    def hotspot_at(self, pos, state):
        for h in reversed(self.visible_hotspots(state)):
            if h.rect.collidepoint(pos):
                return h
        return None

    def draw(self, surf, state, debug=False):
        bg = assets.image(self.bg, (WIDTH, HEIGHT)) if self.bg else None
        if bg:
            surf.blit(bg, (0, 0))
        else:#пока художник не нарисовал фон
            surf.fill(self.color)
            surf.blit(assets.font(20).render(self.title, True, (120, 120, 120)), (16, 12))
        if debug:
            for h in self.visible_hotspots(state):
                pygame.draw.rect(surf, (0, 255, 0), h.rect, 1)
                surf.blit(assets.font(14).render(h.label, True, (0, 255, 0)), h.rect.topleft)
