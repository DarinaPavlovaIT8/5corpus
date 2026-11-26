"""Общие функции рисования для головоломок: символы, цветные жетоны, подсказки."""
import pygame

from .. import assets
from ..settings import VIEW_W
from .logic import SYMBOLS

INK = (236, 232, 214)
COLORS = {
    "red": (190, 50, 50), "green": (60, 150, 80), "blue": (60, 100, 200),
    "yellow": (220, 190, 60), "white": (230, 230, 230), "black": (40, 40, 40),
}


def draw_symbol(surf, name, center, size, color=INK, width=5):
    cx, cy = center
    r = size // 2
    if name == "square":
        pygame.draw.rect(surf, color, (cx - r, cy - r, size, size), width)
    elif name == "circle":
        pygame.draw.circle(surf, color, center, r, width)
    elif name == "diamond":
        pygame.draw.polygon(surf, color, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], width)
    elif name == "triangle":
        pygame.draw.polygon(surf, color, [(cx, cy - r), (cx + r, cy + r), (cx - r, cy + r)], width)


def draw_token(surf, token, center, size, color=INK):
    """Символ (square/circle/diamond/triangle), цвет (red/blue/...) или просто текст/число."""
    if token in SYMBOLS:
        draw_symbol(surf, token, center, size, color)
    elif token in COLORS:
        pygame.draw.circle(surf, COLORS[token], center, size // 2)
        pygame.draw.circle(surf, (15, 15, 15), center, size // 2, 3)
    else:
        img = assets.font(max(20, int(size * 0.7))).render(str(token), True, color)
        surf.blit(img, img.get_rect(center=center))


def draw_hint(surf, text, y=150):
    img = assets.font(22).render(text, True, (150, 146, 134))
    surf.blit(img, img.get_rect(center=(VIEW_W // 2, y)))


def draw_msg(surf, text, y, ok=False):
    img = assets.font(26).render(text, True, (110, 190, 120) if ok else (200, 70, 70))
    surf.blit(img, img.get_rect(center=(VIEW_W // 2, y)))
