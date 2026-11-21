"""Создаёт ТЕСТОВЫЕ картинки для всех фонов и иконок из data/*.json, которых ещё нет.
Запуск:  python tools/make_placeholders.py
Существующие файлы НЕ перезаписываются, так что рисунки художника в безопасности.
На тестовом фоне обведены зоны клика с подписями, видно, где что будет."""
import json
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # окно не нужно
import pygame

ROOT = Path(__file__).resolve().parent.parent
pygame.init()
FONT = pygame.font.match_font("dejavusans,liberationsans,notosans,arial")


def save(surf, rel_path):
    p = ROOT / rel_path
    if p.exists():
        print("есть, пропускаю:", rel_path)
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(p))
    print("создан:", rel_path)


def make_bg(sc):
    W, H = 1920, 1080
    surf = pygame.Surface((W, H))
    surf.fill(pygame.Color(sc.get("color", "#222222")))
    big, small = pygame.font.Font(FONT, 56), pygame.font.Font(FONT, 30)
    surf.blit(big.render(sc.get("title", ""), True, (150, 150, 150)), (30, 20))
    for h in sc.get("hotspots", []):
        x, y, w, hh = h["rect"]
        r = pygame.Rect(W * x / 100, H * y / 100, W * w / 100, H * hh / 100)
        pygame.draw.rect(surf, (100, 100, 110), r, 4)
        surf.blit(small.render(h.get("label", ""), True, (170, 170, 180)), (r.x + 8, r.y + 8))
    return surf


def make_icon(name):
    surf = pygame.Surface((256, 256), pygame.SRCALPHA)
    pygame.draw.circle(surf, (90, 70, 40), (128, 128), 120)
    letter = pygame.font.Font(FONT, 140).render(name[:1], True, (230, 220, 200))
    surf.blit(letter, letter.get_rect(center=(128, 128)))
    return surf


def main():
    scenes = json.loads((ROOT / "data" / "scenes.json").read_text(encoding="utf-8"))["scenes"]
    items = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))
    for sc in scenes.values():
        if sc.get("bg"):
            save(make_bg(sc), sc["bg"])
    for it in items.values():
        if it.get("icon"):
            save(make_icon(it.get("name", "?")), it["icon"])


if __name__ == "__main__":
    main()
