"""Загрузка картинок и шрифтов. Нет файла то возвращается None/запасной шрифт, игра не падает"""
import pygame

from .settings import ROOT

_images, _fonts = {}, {}


def image(path, size=None):
    """Surface или None, если файла нет"""
    key = (path, size)
    if key not in _images:
        surf, p = None, ROOT / path
        if p.exists():
            try:
                surf = pygame.image.load(str(p)).convert_alpha()
                if size:
                    surf = pygame.transform.smoothscale(surf, size)
            except pygame.error:
                surf = None
        _images[key] = surf
    return _images[key]


def font(size):
    if size not in _fonts:
        custom = ROOT / "assets" / "fonts" / "main.ttf"  #сюда положить свой шрифт
        if custom.exists():
            _fonts[size] = pygame.font.Font(str(custom), size)
        else:
            name = pygame.font.match_font("dejavusans,liberationsans,notosans,arial")
            _fonts[size] = pygame.font.Font(name, size)  #None шрифт по умолчанию
    return _fonts[size]
