"""Главный класс: окно, режимы (меню / игра / концовка), навигация стрелками, инвентарь, скрещивание."""
import json
import sys

import pygame

from . import assets, ui
from .actions import ActionRunner
from .flash import FLASH_TIME, alpha as flash_alpha
from .scene import Scene
from .settings import (ROOT, WIDTH, HEIGHT, VIEW_W, VIEW_H, FPS, TITLE, SCENES_PATH, ITEMS_PATH,
                       RECIPES_PATH, COLOR_TEXT, COLOR_ACCENT)
from .state import GameState, find_recipe


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.data = json.loads(SCENES_PATH.read_text(encoding="utf-8"))
        self.items = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
        self.recipes = json.loads(RECIPES_PATH.read_text(encoding="utf-8"))
        self.scenes = {sid: Scene(sid, d) for sid, d in self.data["scenes"].items()}

        self.state = GameState()
        self.runner = ActionRunner(self)
        self.mode = "menu"  # menu | play | ending
        self.ending = None
        self.debug = False
        self.fade = 0.0
        self.was_busy = False
        self.inv_scroll = 0
        self.label, self.label_t = "", 0.0
        self.flash = None  # [картинка, время] идущего мерцания
        cx = WIDTH // 2 - 150
        self.menu_buttons = {
            "new": pygame.Rect(cx, 330, 300, 56),
            "continue": pygame.Rect(cx, 400, 300, 56),
            "quit": pygame.Rect(cx, 470, 300, 56),
        }

    # ---------- подпись сверху ----------
    def show_label(self, text, seconds=2.2):
        self.label, self.label_t = text, seconds

    # ---------- мерцание силуэта ----------
    def start_flash(self, name):
        """Запускает одноразовое мерцание: assets/bg/<name>.png (с прозрачностью) поверх сцены.
        Нет файла: просто короткое затемнение. Повторов не допускает actions (метка во флагах)."""
        try:
            img = pygame.image.load(str(ROOT / "assets" / "bg" / f"{name}.png")).convert_alpha()
            img = pygame.transform.smoothscale(img, (VIEW_W, VIEW_H))
        except (OSError, pygame.error):
            img = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
            img.fill((0, 0, 0, 255))
        self.flash = [img, 0.0]

    # ---------- сохранение ----------
    def can_continue(self):
        """Есть ли рабочее сохранение (битое или со старой сценой считается отсутствующим)."""
        return GameState().load(valid_scenes=self.scenes)

    # ---------- управление игрой ----------
    def new_game(self):
        self.state.reset()
        self.runner.clear()
        self.inv_scroll, self.label_t, self.flash = 0, 0.0, None
        self.mode = "play"
        self.change_scene(self.data["start"])

    def continue_game(self):
        if not self.state.load(valid_scenes=self.scenes):
            return
        self.runner.clear()
        self.inv_scroll, self.label_t, self.flash = 0, 0.0, None
        self.mode = "play"
        self.change_scene(self.state.scene, run_enter=False)

    def to_menu(self):
        if self.mode == "play":
            self.state.save()
        self.runner.clear()
        self.flash = None
        self.mode = "menu"

    def change_scene(self, sid, run_enter=True):
        if sid not in self.scenes:
            print(f"[!] Нет сцены: {sid}")
            return
        self.state.scene = sid  # выбранный предмет сохраняется при переходах, как в Rusty Lake
        self.fade = 1.0  # плавное появление
        if run_enter:
            actions = []
            for rule in self.scenes[sid].on_enter:
                if self.state.check(rule.get("if")):
                    actions += rule["do"]
            self.runner.push_front(actions)
        if self.mode == "play":
            self.state.save()

    def show_ending(self, eid):
        self.ending = self.data["endings"][eid]
        self.mode = "ending"
        GameState.delete_save()  # игра пройдена, «Продолжить» больше не нужно

    @property
    def scene(self):
        return self.scenes[self.state.scene]

    # ---------- события ----------
    def handle(self, e):
        if e.type == pygame.QUIT:
            self.quit()
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_F3:
                self.debug = not self.debug
            elif e.key == pygame.K_ESCAPE and self.mode == "play":
                self.to_menu()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN) and self.mode == "play" and self.runner.task:
                self.runner.task.on_click(None)
        elif e.type == pygame.MOUSEWHEEL and self.mode == "play":
            if pygame.mouse.get_pos()[0] >= VIEW_W:  # крутим только над панелью инвентаря
                self.inv_scroll -= e.y
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button in (1, 3):
            if self.mode == "play":
                self.click_play(e.pos, e.button)
            elif e.button == 1:
                {"menu": self.click_menu, "ending": self.click_ending}[self.mode](e.pos)

    def click_menu(self, pos):
        b = self.menu_buttons
        if b["new"].collidepoint(pos):
            self.new_game()
        elif b["continue"].collidepoint(pos) and self.can_continue():
            self.continue_game()
        elif b["quit"].collidepoint(pos):
            self.quit()

    def click_ending(self, pos):
        self.mode = "menu"

    def click_play(self, pos, button=1):
        if self.runner.task:  # идёт текст / пауза / головоломка
            if button == 1:
                self.runner.task.on_click(pos)
            return
        if self.runner.busy:
            return
        if pos[0] >= VIEW_W:  # панель инвентаря справа
            self.click_inventory(pos, button)
            return
        if button != 1:
            return
        st = self.state
        d = ui.arrow_at(pos, self.scene.arrows)  # стрелка: поворот, приближение, возврат
        if d:
            self.change_scene(self.scene.arrows[d])
            return
        hs = self.scene.hotspot_at(pos, st)
        if hs:
            rule = hs.first_rule(st)
            if rule:
                self.runner.start(rule["do"])
        else:
            st.selected = None

    def click_inventory(self, pos, button):
        st = self.state
        item = ui.item_at(pos, st, self.inv_scroll)
        if not item:
            return
        info = self.items.get(item, {})
        if button == 3:  # правая кнопка: осмотреть предмет
            self.runner.start([{"say": info.get("desc", "Ничего особенного.")}])
            return
        if st.selected == item:  # повторный клик снимает выбор
            st.selected = None
        elif st.selected:  # выбран другой предмет: пробуем скрестить
            recipe = find_recipe(self.recipes, st.selected, item)
            if recipe and st.combine(recipe):
                result = recipe["result"]
                self.show_label("Получено: " + self.items.get(result, {}).get("name", result))
                self.runner.start(recipe.get("do", []))
            else:
                self.show_label("Эти предметы не сочетаются")
                st.selected = item
        else:
            st.selected = item
            self.show_label(info.get("name", item))

    # ---------- цикл ----------
    def update(self, dt):
        if self.mode != "play":
            return
        self.runner.update(dt)
        if self.flash:
            self.flash[1] += dt
            if self.flash[1] >= FLASH_TIME:
                self.flash = None
        if not self.runner.busy:  # отработавшие предметы (dropWhen в items.json) убираем из инвентаря
            removed = self.state.prune_inventory(self.items)
            if removed:
                names = ", ".join(self.items.get(i, {}).get("name", i) for i in removed)
                self.show_label("Использовано: " + names)
                self.state.save()
        if self.fade > 0:
            self.fade = max(0.0, self.fade - dt * 2.5)
        if self.label_t > 0:
            self.label_t -= dt
        self.inv_scroll = max(0, min(self.inv_scroll, ui.max_scroll(self.state)))
        if self.mode == "play" and self.was_busy and not self.runner.busy:
            self.state.save()  # автосохранение после каждого действия
        self.was_busy = self.runner.busy

    def draw(self):
        if self.mode == "menu":
            self.draw_menu()
        elif self.mode == "ending":
            self.draw_ending()
        else:
            self.draw_play()

    def draw_play(self):
        s = self.screen
        self.scene.draw(s, self.state, self.debug)
        if self.flash:  # мерцание силуэта поверх сцены, но под стрелками и инвентарём
            img, t = self.flash
            a = flash_alpha(t)
            if a:
                img.set_alpha(a)
                s.blit(img, (0, 0))
        pos = pygame.mouse.get_pos()
        free = not self.runner.busy
        arrows = self.scene.arrows if free else {}
        hover_arrow = ui.arrow_at(pos, arrows)
        ui.draw_arrows(s, arrows, hover_arrow)
        ui.draw_inventory(s, self.state, self.items, self.inv_scroll)
        cursor = pygame.SYSTEM_CURSOR_ARROW
        if free:
            hs = self.scene.hotspot_at(pos, self.state) if pos[0] < VIEW_W else None
            if hover_arrow or hs or ui.item_at(pos, self.state, self.inv_scroll):
                cursor = pygame.SYSTEM_CURSOR_HAND
            if self.debug and hs and hs.label:
                ui.draw_tooltip(s, hs.label, pos)  # названия зон видны только по F3
        pygame.mouse.set_cursor(cursor)
        if self.label_t > 0:
            ui.draw_label(s, self.label)
        if self.runner.task:
            self.runner.task.draw(s)
        if self.fade > 0:
            veil = pygame.Surface((VIEW_W, VIEW_H))
            veil.set_alpha(int(255 * self.fade))
            s.blit(veil, (0, 0))

    def draw_menu(self):
        s = self.screen
        s.fill((8, 8, 10))
        title = assets.font(64).render("ПЯТЫЙ КОРПУС", True, COLOR_TEXT)
        s.blit(title, title.get_rect(center=(WIDTH // 2, 220)))
        pos = pygame.mouse.get_pos()
        enabled = {"new": True, "continue": self.can_continue(), "quit": True}
        labels = {"new": "Новая игра", "continue": "Продолжить", "quit": "Выход"}
        for key, r in self.menu_buttons.items():
            ui.draw_button(s, r, labels[key], enabled[key], r.collidepoint(pos))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        hint = assets.font(18).render("Esc в игре: в меню · F3: показать зоны клика · ПКМ по предмету: осмотреть", True, (90, 90, 90))
        s.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

    def draw_ending(self):
        s = self.screen
        s.fill((0, 0, 0))
        t = assets.font(60).render(self.ending["title"], True, COLOR_ACCENT)
        s.blit(t, t.get_rect(center=(WIDTH // 2, 260)))
        f = assets.font(28)
        for i, line in enumerate(ui.wrap(self.ending["text"], f, 800)):
            img = f.render(line, True, COLOR_TEXT)
            s.blit(img, img.get_rect(center=(WIDTH // 2, 340 + i * 38)))
        hint = assets.font(18).render("Клик: в главное меню", True, (90, 90, 90))
        s.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 60)))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

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
