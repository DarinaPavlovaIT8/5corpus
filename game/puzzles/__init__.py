"""Головоломки. Чтобы добавить новую: класс-наследник PuzzleTask в этой папке + строка в create().
Вызов из JSON (ключ "puzzle" ДОЛЖЕН идти первым в действии):
  {"puzzle": "code", "code": "3157", "title": "...", "onWin": [...]}
Типы: code (цифровой замок), symbols (барабаны с символами), order (перестановка книг/ключей/символов),
wires (соединение проводов), switches (тумблеры), sequence (кнопки по порядку).
Импорты внутри функции: так логику (logic.py) можно тестировать без pygame."""

NAMES = ("code", "symbols", "order", "wires", "switches", "sequence")


def create(name, cfg):
    if name == "code":                 # code: "3157"
        from .code import CodePuzzle
        return CodePuzzle(cfg)
    if name == "symbols":              # answer: ["triangle", "diamond", "circle"]
        from .symbols import SymbolsPuzzle
        return SymbolsPuzzle(cfg)
    if name == "order":                # style: books|keys|tiles, start: [...], answer: [...]
        from .order import OrderPuzzle
        return OrderPuzzle(cfg)
    if name == "wires":                # left: [...], right: [...], pairs: [[0, 1], ...]
        from .wires import WiresPuzzle
        return WiresPuzzle(cfg)
    if name == "switches":             # count: 4, target: [1, 0, 1, 1]
        from .switches import SwitchesPuzzle
        return SwitchesPuzzle(cfg)
    if name == "sequence":             # buttons: ["Красный", ...], order: [1, 0, 2]
        from .sequence import SequencePuzzle
        return SequencePuzzle(cfg)
    raise ValueError(f"Неизвестная головоломка: {name}")
