"""Интерфейс: текстбокс, инвентарь справа, стрелки навигации, подпись предмета сверху."""
import pygame

from . import assets
from .settings import VIEW_W, VIEW_H, PANEL_W, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL

SLOT, GAP, TOP = 90, 8, 12
VISIBLE = (VIEW_H - TOP * 2 + GAP) // (SLOT + GAP)  # сколько ячеек помещается в панель


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
    """Рамка с текстом внизу сцены; visible_chars — сколько символов уже «напечатано»."""
    rect = pygame.Rect(60, VIEW_H - 230, VIEW_W - 120, 130)
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


# ---------- стрелки навигации ----------
_CX, _CY = VIEW_W // 2, VIEW_H // 2
ARROW_ZONES = {
    "left": pygame.Rect(0, _CY - 110, 90, 220),
    "right": pygame.Rect(VIEW_W - 90, _CY - 110, 90, 220),
    "up": pygame.Rect(_CX - 110, 0, 220, 80),
    "down": pygame.Rect(_CX - 110, VIEW_H - 80, 220, 80),
}


def _triangle(d):
    return {
        "left": [(18, _CY), (52, _CY - 26), (52, _CY + 26)],
        "right": [(VIEW_W - 18, _CY), (VIEW_W - 52, _CY - 26), (VIEW_W - 52, _CY + 26)],
        "up": [(_CX, 16), (_CX - 26, 50), (_CX + 26, 50)],
        "down": [(_CX, VIEW_H - 16), (_CX - 26, VIEW_H - 50), (_CX + 26, VIEW_H - 50)],
    }[d]


def draw_arrows(surf, arrows, hover=None):
    for d in arrows:
        if d in ARROW_ZONES:
            pts = _triangle(d)
            pygame.draw.polygon(surf, (190, 40, 40) if d == hover else (236, 232, 214), pts)
            pygame.draw.polygon(surf, (15, 15, 15), pts, 3)


def arrow_at(pos, arrows):
    for d in arrows:
        if d in ARROW_ZONES and ARROW_ZONES[d].collidepoint(pos):
            return d
    return None


# ---------- инвентарь справа ----------
def slot_rect(i):
    return pygame.Rect(VIEW_W + (PANEL_W - SLOT) // 2, TOP + i * (SLOT + GAP), SLOT, SLOT)


def max_scroll(state):
    return max(0, len(state.inventory) - VISIBLE)


def visible_items(state, scroll):
    return state.inventory[scroll:scroll + VISIBLE]


def item_at(pos, state, scroll=0):
    for i, item in enumerate(visible_items(state, scroll)):
        if slot_rect(i).collidepoint(pos):
            return item
    return None


def draw_inventory(surf, state, items, scroll=0):
    pygame.draw.rect(surf, COLOR_PANEL, pygame.Rect(VIEW_W, 0, PANEL_W, VIEW_H))
    pygame.draw.line(surf, (60, 60, 60), (VIEW_W, 0), (VIEW_W, VIEW_H), 2)
    for i, item_id in enumerate(visible_items(state, scroll)):
        r = slot_rect(i)
        selected = state.selected == item_id
        pygame.draw.rect(surf, (222, 214, 186), r)
        info = items.get(item_id, {})
        icon = assets.image(info["icon"], (SLOT - 16, SLOT - 16)) if info.get("icon") else None
        if icon:
            surf.blit(icon, (r.x + 8, r.y + 8))
        else:  # заглушка: первая буква названия
            letter = assets.font(36).render(info.get("name", "?")[:1], True, (40, 40, 40))
            surf.blit(letter, letter.get_rect(center=r.center))
        pygame.draw.rect(surf, COLOR_ACCENT if selected else (30, 30, 30), r, 5 if selected else 3)
    cx = VIEW_W + PANEL_W // 2
    if scroll > 0:  # есть предметы выше
        pygame.draw.polygon(surf, COLOR_TEXT, [(cx, 2), (cx - 8, 10), (cx + 8, 10)])
    if scroll < max_scroll(state):  # есть предметы ниже
        pygame.draw.polygon(surf, COLOR_TEXT, [(cx, VIEW_H - 2), (cx - 8, VIEW_H - 10), (cx + 8, VIEW_H - 10)])


def draw_label(surf, text):
    """Подпись сверху по центру сцены (название предмета, «Получено: …»)."""
    img = assets.font(26).render(text, True, (240, 236, 224))
    r = img.get_rect(center=(VIEW_W // 2, 36)).inflate(40, 18)
    pygame.draw.rect(surf, (0, 0, 0), r, border_radius=14)
    pygame.draw.rect(surf, (90, 90, 90), r, 1, border_radius=14)
    surf.blit(img, img.get_rect(center=r.center))


def draw_tooltip(surf, text, pos):
    img = assets.font(20).render(text, True, COLOR_TEXT)
    r = img.get_rect(topleft=(pos[0] + 16, pos[1] + 18)).inflate(12, 6)
    r.clamp_ip(surf.get_rect())
    pygame.draw.rect(surf, (0, 0, 0), r)
    surf.blit(img, img.get_rect(center=r.center))


def draw_button(surf, rect, text, enabled=True, hover=False):
    """Кнопка для меню."""
    border = COLOR_ACCENT if (hover and enabled) else (70, 70, 70)
    pygame.draw.rect(surf, (26, 26, 30), rect)
    pygame.draw.rect(surf, border, rect, 2)
    img = assets.font(28).render(text, True, COLOR_TEXT if enabled else (90, 90, 90))
    surf.blit(img, img.get_rect(center=rect.center))
