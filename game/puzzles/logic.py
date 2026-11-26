"""Чистая логика головоломок без pygame — её можно проверять обычными тестами."""

SYMBOLS = ("square", "circle", "diamond", "triangle")  # квадрат, круг, ромб, треугольник


class CodeLogic:
    """Цифровой замок: набираем цифры, на последней сразу проверка."""
    def __init__(self, code):
        self.code, self.entered = str(code), ""

    def press(self, ch):
        """Возвращает "win", "wrong" или None (ввод продолжается)."""
        if len(self.entered) < len(self.code):
            self.entered += ch
        if len(self.entered) == len(self.code):
            if self.entered == self.code:
                return "win"
            self.entered = ""
            return "wrong"
        return None

    def back(self):
        self.entered = self.entered[:-1]

    def clear(self):
        self.entered = ""


class SymbolsLogic:
    """Механический замок с барабанами-символами."""
    def __init__(self, answer, symbols=SYMBOLS, start=None):
        self.symbols = list(symbols)
        self.answer = list(answer)
        self.pos = [self.symbols.index(s) for s in start] if start else [0] * len(self.answer)
        if self.current() == self.answer:  # чтобы замок не был открыт с самого начала
            self.pos[0] = (self.pos[0] + 1) % len(self.symbols)

    def current(self):
        return [self.symbols[p] for p in self.pos]

    def turn(self, i, step=1):
        self.pos[i] = (self.pos[i] + step) % len(self.symbols)

    def solved(self):
        return self.current() == self.answer


class OrderLogic:
    """Перестановка предметов (книги, ключи, символы). None = пустое место (крючок).
    Клик по предмету выбирает его, клик по другому месту меняет их местами."""
    def __init__(self, start, answer):
        self.slots, self.answer, self.sel = list(start), list(answer), None

    def click(self, i):
        if self.sel is None:
            if self.slots[i] is not None:
                self.sel = i
            return
        if self.sel != i:
            self.slots[self.sel], self.slots[i] = self.slots[i], self.slots[self.sel]
        self.sel = None

    def solved(self):
        return self.slots == self.answer


class WiresLogic:
    """Соединение проводов: слева n клемм, справа n клемм; pairs = [[левая, правая], ...]."""
    def __init__(self, n, pairs):
        self.n, self.want = n, {a: b for a, b in pairs}
        self.conn, self.sel = {}, None  # conn: левая -> правая

    def click_left(self, i):
        if i in self.conn and self.sel is None:
            del self.conn[i]  # клик по занятой клемме отсоединяет провод
        else:
            self.sel = None if self.sel == i else i

    def click_right(self, j):
        for a in [a for a, b in self.conn.items() if b == j]:
            del self.conn[a]
        if self.sel is not None:
            self.conn[self.sel], self.sel = j, None

    def full(self):
        return len(self.conn) == self.n

    def solved(self):
        return self.conn == self.want


class SwitchesLogic:
    """Тумблеры: нужно выставить target (1 = вверх)."""
    def __init__(self, count, target=None, start=None):
        self.target = list(target) if target else [1] * count
        self.state = list(start) if start else [0] * count
        if self.state == self.target:
            self.state[0] ^= 1

    def toggle(self, i):
        self.state[i] ^= 1

    def solved(self):
        return self.state == self.target


class SequenceLogic:
    """Кнопки нужно нажать по порядку; ошибка сбрасывает ввод."""
    def __init__(self, order):
        self.order, self.pressed = list(order), []

    def press(self, i):
        """Возвращает "win", "wrong" или None."""
        if i != self.order[len(self.pressed)]:
            self.pressed = []
            return "wrong"
        self.pressed.append(i)
        return "win" if len(self.pressed) == len(self.order) else None
