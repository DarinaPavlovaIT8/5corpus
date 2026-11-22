"""Выполнение действий из JSON по очереди.
Мгновенные: give, take, setFlag, clearFlag, randomFlag, goto, ending.
Блокирующие (ждём игрока/время): say, wait."""
import random
from collections import deque

from . import ui


class Task:
    """Блокирующее действие: пока оно идёт, игрок не может кликать по сцене."""
    def update(self, dt):
        return True  # True = закончено

    def draw(self, surf):
        pass

    def on_click(self, pos=None):
        pass


class SayTask(Task):
    SPEED = 45  # символов в секунду

    def __init__(self, text):
        self.text, self.t, self.done = text, 0.0, False

    def update(self, dt):
        self.t += dt
        return self.done

    def on_click(self, pos=None):
        if self.t * self.SPEED < len(self.text):  # первый клик — показать весь текст
            self.t = len(self.text) / self.SPEED
        else:
            self.done = True

    def draw(self, surf):
        ui.draw_textbox(surf, self.text, int(self.t * self.SPEED))


class WaitTask(Task):
    def __init__(self, seconds):
        self.left = seconds

    def update(self, dt):
        self.left -= dt
        return self.left <= 0


class ActionRunner:
    def __init__(self, game):
        self.game = game
        self.queue = deque()
        self.task = None

    @property
    def busy(self):
        return self.task is not None or bool(self.queue)

    def start(self, actions):
        self.queue.extend(actions)

    def push_front(self, actions):
        self.queue.extendleft(reversed(actions))

    def clear(self):
        self.queue.clear()
        self.task = None

    def update(self, dt):
        while True:
            if self.task:
                if not self.task.update(dt):
                    return
                self.task = None
            if not self.queue:
                return
            self.task = self._exec(self.queue.popleft())

    def _exec(self, a):
        """Выполняет одно действие. Возвращает Task, если нужно подождать, иначе None."""
        g, st = self.game, self.game.state
        key, val = next(iter(a.items()))
        if key == "say":
            return SayTask(val)
        if key == "wait":
            return WaitTask(val / 1000)
        if key == "give":
            if val not in st.inventory:
                st.inventory.append(val)
        elif key == "take":
            if val in st.inventory:
                st.inventory.remove(val)
            st.selected = None
        elif key == "setFlag":
            st.flags.add(val)
        elif key == "clearFlag":
            st.flags.discard(val)
        elif key == "randomFlag":
            (st.flags.add if random.random() < 0.5 else st.flags.discard)(val)
        elif key == "goto":
            g.change_scene(val)
        elif key == "ending":  # конец игры: остальные действия отменяются
            self.clear()
            g.show_ending(val)
        else:
            print(f"[!] Неизвестное действие: {key}")
        return None
