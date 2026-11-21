"""Рисование интерфейса: текстбокс, инвентарь, подсказка."""
import pygame

from . import assets
from .settings import WIDTH, HEIGHT, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL

SLOT = 64


def wrap(text, font, max_w):
    """Разбивает текст на строки по ширине."""
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if font.size(test)[0] <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def draw_textbox(surf, text, visible_chars=None):
    """Рисует рамку с текстом; visible_chars — сколько символов уже «напечатано»."""
    rect = pygame.Rect(60, HEIGHT - 230, WIDTH - 120, 130)
    box = pygame.Surface(rect.size, pygame.SRCALPHA)
    box.fill((0, 0, 0, 215))
    surf.blit(box, rect)
    pygame.draw.rect(surf, (70, 70, 70), rect, 1)
    f = assets.font(26)
    left = len(text) if visible_chars is None else visible_chars
    for i, line in enumerate(wrap(text, f, rect.w - 40)[:3]):
        part = line[:max(left, 0)]
        left -= len(line) + 1
        surf.blit(f.render(part, True, COLOR_TEXT), (rect.x + 20, rect.y + 16 + i * 34))


def slot_rects(state):
    return [pygame.Rect(16 + i * (SLOT + 8), HEIGHT - SLOT - 16, SLOT, SLOT) for i in range(len(state.inventory))]


def draw_inventory(surf, state, items):
    for item_id, r in zip(state.inventory, slot_rects(state)):
        pygame.draw.rect(surf, COLOR_PANEL, r)
        info = items.get(item_id, {})
        icon = assets.image(info["icon"], (SLOT - 8, SLOT - 8)) if info.get("icon") else None
        if icon:
            surf.blit(icon, (r.x + 4, r.y + 4))
        else:  # заглушка: первая буква названия
            letter = assets.font(32).render(info.get("name", "?")[:1], True, COLOR_TEXT)
            surf.blit(letter, letter.get_rect(center=r.center))
        selected = state.selected == item_id
        pygame.draw.rect(surf, COLOR_ACCENT if selected else (60, 60, 60), r, 3 if selected else 1)


def draw_tooltip(surf, text, pos):
    img = assets.font(20).render(text, True, COLOR_TEXT)
    r = img.get_rect(topleft=(pos[0] + 16, pos[1] + 18)).inflate(12, 6)
    r.clamp_ip(surf.get_rect())
    pygame.draw.rect(surf, (0, 0, 0), r)
    surf.blit(img, img.get_rect(center=r.center))
