"""Главный класс: окно, игровой цикл, клики"""
import json
import sys

import pygame

from . import ui
from .actions import ActionRunner
from .scene import Scene
from .settings import WIDTH, HEIGHT, FPS, TITLE, SCENES_PATH, ITEMS_PATH
from .state import GameState


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.data = json.loads(SCENES_PATH.read_text(encoding="utf-8"))
        self.items = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
        self.scenes = {sid: Scene(sid, d) for sid, d in self.data["scenes"].items()}

        self.state = GameState()
        self.runner = ActionRunner(self)
        self.debug = False
        self.fade = 0.0
        self.change_scene(self.data["start"])  # меню появится в следующих блоках

    # ---------- сцены ----------
    def change_scene(self, sid):
        if sid not in self.scenes:
            print(f"[!] Нет сцены: {sid}")
            return
        self.state.scene = sid
        self.state.selected = None
        self.fade = 1.0  # плавное появление
        actions = []
        for rule in self.scenes[sid].on_enter:
            if self.state.check(rule.get("if")):
                actions += rule["do"]
        self.runner.push_front(actions)

    @property
    def scene(self):
        return self.scenes[self.state.scene]

    # ---------- события ----------
    def handle(self, e):
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            self.quit()
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_F3:
                self.debug = not self.debug
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN) and self.runner.task:
                self.runner.task.on_click(None)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.click(e.pos)

    def click(self, pos):
        if self.runner.task:  # идёт текст/пауза
            self.runner.task.on_click(pos)
            return
        if self.runner.busy:
            return
        st = self.state
        for item_id, r in zip(st.inventory, ui.slot_rects(st)):
            if r.collidepoint(pos):  # выбрать / снять выбор с предмета
                st.selected = None if st.selected == item_id else item_id
                return
        hs = self.scene.hotspot_at(pos, st)
        if hs:
            rule = hs.first_rule(st)
            if rule:
                self.runner.start(rule["do"])
        else:
            st.selected = None

    # ---------- цикл ----------
    def update(self, dt):
        self.runner.update(dt)
        if self.fade > 0:
            self.fade = max(0.0, self.fade - dt * 2.5)

    def draw(self):
        s = self.screen
        self.scene.draw(s, self.state, self.debug)
        ui.draw_inventory(s, self.state, self.items)
        pos = pygame.mouse.get_pos()
        if not self.runner.busy:
            hs = self.scene.hotspot_at(pos, self.state)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hs else pygame.SYSTEM_CURSOR_ARROW)
            if hs and hs.label:
                ui.draw_tooltip(s, hs.label, pos)
        if self.runner.task:
            self.runner.task.draw(s)
        if self.fade > 0:
            veil = pygame.Surface((WIDTH, HEIGHT))
            veil.set_alpha(int(255 * self.fade))
            s.blit(veil, (0, 0))

    def quit(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000, 0.1)
            for e in pygame.event.get():
                self.handle(e)
            self.update(dt)
            self.draw()
            pygame.display.flip()
