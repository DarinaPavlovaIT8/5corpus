"""Проверка data/*.json без запуска игры:  python tools/check_data.py
Ловит опечатки: несуществующие сцены/предметы, неизвестные действия, кривые rect, битые стрелки и рецепты,
а также ошибки в настройках головоломок (code, symbols, order, wires, switches, sequence)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Когда в движок добавляется новое действие, допиши его сюда
KNOWN_ACTIONS = {"say", "wait", "give", "take", "setFlag", "clearFlag", "randomFlag", "goto", "ending", "label", "puzzle", "flash"}
COND_KEYS = {"flag", "notFlag", "has", "selected"}
ARROW_KEYS = {"left", "right", "up", "down"}
# Когда в game/puzzles добавляется новая головоломка, допиши её сюда (держи в синхроне с game/puzzles/__init__.py)
PUZZLE_NAMES = {"code", "symbols", "order", "wires", "switches", "sequence"}
SYMBOLS = {"square", "circle", "diamond", "triangle"}
MAX_SAY = 200  # в текстбоксе помещается 3 строки, длинный текст обрежется

errors, warnings = [], []
set_flags, used_flags = set(), set()
endings = {}
edges = {}          # сцена -> куда из неё можно попасть
current = [None]    # сцена, которую проверяем сейчас


def err(msg): errors.append(msg)


def check_cond(cond, where, items):
    for k, v in (cond or {}).items():
        if k not in COND_KEYS:
            err(f"{where}: неизвестное условие '{k}'")
        if k in ("flag", "notFlag"):
            used_flags.add(v)
        if k in ("has", "selected") and v not in items:
            err(f"{where}: предмет '{v}' нет в items.json")


def is_list(v, n=None):
    return isinstance(v, list) and (n is None or len(v) == n)


def check_puzzle(a, name, where):
    """Проверка настроек головоломки (a — всё действие целиком)."""
    if name not in PUZZLE_NAMES:
        err(f"{where}: неизвестная головоломка '{name}' (есть {', '.join(sorted(PUZZLE_NAMES))})")
        return
    if name == "code":
        code = a.get("code")
        if not (isinstance(code, str) and code.isdigit()):
            err(f"{where}: для code нужно поле code — строка из цифр, например \"3157\"")
    elif name == "symbols":
        ans = a.get("answer")
        pool = a.get("symbols", sorted(SYMBOLS))
        if not (is_list(ans) and ans):
            err(f"{where}: для symbols нужно поле answer — список символов")
        else:
            for s in ans + list(a.get("start", [])):
                if s not in pool:
                    err(f"{where}: символа '{s}' нет в наборе барабана {pool}")
    elif name == "order":
        start, ans = a.get("start"), a.get("answer")
        if not (is_list(start) and is_list(ans)) or len(start) != len(ans):
            err(f"{where}: для order нужны списки start и answer одинаковой длины")
        elif sorted(map(str, start)) != sorted(map(str, ans)):
            err(f"{where}: start и answer должны состоять из одних и тех же предметов")
        elif start == ans:
            err(f"{where}: start совпадает с answer — головоломка решена с самого начала")
        if a.get("style", "tiles") not in ("books", "keys", "tiles"):
            err(f"{where}: style должен быть books, keys или tiles")
    elif name == "wires":
        left, right, pairs = a.get("left"), a.get("right"), a.get("pairs")
        if not (is_list(left) and is_list(right) and is_list(pairs)) or len(left) != len(right):
            err(f"{where}: для wires нужны списки left, right одинаковой длины и pairs")
        else:
            n = len(left)
            ok = all(is_list(p, 2) and all(isinstance(x, int) and 0 <= x < n for x in p) for p in pairs)
            if not ok or len(pairs) != n or len({p[0] for p in pairs}) != n or len({p[1] for p in pairs}) != n:
                err(f"{where}: pairs должны быть [[левая, правая], ...] — по одной паре на каждую клемму, номера с нуля")
    elif name == "switches":
        target, count = a.get("target"), a.get("count")
        n = count or (len(target) if is_list(target) else 0)
        if not n:
            err(f"{where}: для switches нужно count или target")
        if target is not None and (not is_list(target) or len(target) != n or any(t not in (0, 1) for t in target)):
            err(f"{where}: target — список из {n} чисел 0/1")
        if a.get("labels") is not None and len(a["labels"]) != n:
            err(f"{where}: labels должно быть {n} штук")
    elif name == "sequence":
        buttons, order = a.get("buttons"), a.get("order")
        if not (is_list(buttons) and is_list(order) and order):
            err(f"{where}: для sequence нужны списки buttons и order")
        elif any(not isinstance(o, int) or not 0 <= o < len(buttons) for o in order):
            err(f"{where}: order содержит номер кнопки, которой нет (номера с нуля)")


def check_actions(actions, where, scenes, items):
    for i, a in enumerate(actions):
        key, val = next(iter(a.items()))
        if key == "puzzle":
            check_puzzle(a, val, f"{where}[{i}]")
            check_actions(a.get("onWin", []), f"{where}[{i}].onWin", scenes, items)
            continue
        if len(a) != 1:
            err(f"{where}[{i}]: в одном действии должен быть один ключ, а тут {list(a)}")
        if key not in KNOWN_ACTIONS:
            err(f"{where}[{i}]: неизвестное действие '{key}'")
        elif key == "say":
            if len(val) > MAX_SAY:
                warnings.append(f"{where}[{i}]: реплика на {len(val)} символов, в рамку влезет около {MAX_SAY}: «{val[:40]}…»")
        elif key == "flash":
            img = str(val).split(":")[0]
            if ":" not in str(val):
                err(f"{where}[{i}]: flash должен быть вида \"картинка:метка\", например ghost_flash:cor2")
            elif not (ROOT / "assets" / "bg" / f"{img}.png").exists():
                warnings.append(f"{where}[{i}]: нет файла assets/bg/{img}.png (будет короткое затемнение без силуэта)")
        elif key == "ending" and val not in endings:
            err(f"{where}[{i}]: концовки '{val}' нет в блоке endings")
        elif key == "goto":
            if val not in scenes:
                err(f"{where}[{i}]: goto на несуществующую сцену '{val}'")
            else:
                edges.setdefault(current[0], set()).add(val)
        elif key in ("give", "take") and val not in items:
            err(f"{where}[{i}]: предмет '{val}' нет в items.json")
        elif key in ("setFlag", "randomFlag"):
            set_flags.add(val)
        elif key == "clearFlag":
            used_flags.add(val)


def main():
    data = json.loads((ROOT / "data" / "scenes.json").read_text(encoding="utf-8"))
    items = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))
    recipes = json.loads((ROOT / "data" / "recipes.json").read_text(encoding="utf-8"))
    scenes = data.get("scenes", {})
    endings.update(data.get("endings", {}))
    for eid, e in endings.items():
        if not e.get("title") or not e.get("text"):
            err(f"концовка '{eid}': нужны поля title и text")
    if data.get("start") not in scenes:
        err(f"start='{data.get('start')}': такой сцены нет")

    for sid, sc in scenes.items():
        current[0] = sid
        bg = sc.get("bg")
        if bg and not (ROOT / bg).exists():
            warnings.append(f"{sid}: нет файла фона {bg} (будет цветная заглушка; tools/make_placeholders.py создаст png)")
        for d, target in sc.get("arrows", {}).items():
            if d not in ARROW_KEYS:
                err(f"{sid}.arrows: неизвестное направление '{d}' (есть left, right, up, down)")
            elif target not in scenes:
                err(f"{sid}.arrows.{d}: сцены '{target}' нет")
            else:
                edges.setdefault(sid, set()).add(target)
        for j, rule in enumerate(sc.get("onEnter", [])):
            w = f"{sid}.onEnter[{j}]"
            check_cond(rule.get("if"), w, items)
            check_actions(rule.get("do", []), w + ".do", scenes, items)
        for h in sc.get("hotspots", []):
            w = f"{sid}.'{h.get('label', '?')}'"
            r = h.get("rect")
            if not (isinstance(r, list) and len(r) == 4 and all(isinstance(n, (int, float)) for n in r)):
                err(f"{w}: rect должен быть [x, y, w, h]")
            elif r[0] + r[2] > 100 or r[1] + r[3] > 100 or min(r) < 0:
                err(f"{w}: rect {r} выходит за экран (проценты 0..100)")
            if h.get("img") and not (ROOT / h["img"]).exists():
                warnings.append(f"{w}: нет файла спрайта {h['img']}")
            check_cond(h.get("visibleIf"), w + ".visibleIf", items)
            for prev in sc["hotspots"][:sc["hotspots"].index(h)]:
                a, b = prev.get("rect"), h.get("rect")
                va, vb = prev.get("visibleIf") or {}, h.get("visibleIf") or {}
                if (va.get("flag") and va.get("flag") == vb.get("notFlag")) or \
                        (vb.get("flag") and vb.get("flag") == va.get("notFlag")):
                    continue  # зоны никогда не видны одновременно
                if is_list(a, 4) and is_list(b, 4) and a[0] < b[0] + b[2] and b[0] < a[0] + a[2] \
                        and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                    warnings.append(f"{sid}: зоны '{prev.get('label')}' и '{h.get('label')}' перекрываются, "
                                    f"клик может уйти не туда (верх: та, что ниже в списке)")
            for j, rule in enumerate(h.get("rules", [])):
                check_cond(rule.get("if"), f"{w}.rules[{j}]", items)
                check_actions(rule.get("do", []), f"{w}.rules[{j}].do", scenes, items)

    for iid, it in items.items():
        if it.get("icon") and not (ROOT / it["icon"]).exists():
            warnings.append(f"предмет '{iid}': нет файла иконки {it['icon']} (будет буква)")
        if len(it.get("desc", "")) > MAX_SAY:
            warnings.append(f"предмет '{iid}': описание длиннее {MAX_SAY} символов, в рамку не влезет")
    for iid, it in items.items():
        drop = it.get("dropWhen")
        if drop is not None and not (is_list(drop) and drop):
            err(f"предмет '{iid}': dropWhen — непустой список флагов")
        for f in drop or []:
            used_flags.add(f)
    for j, r in enumerate(recipes):
        w = f"recipes[{j}]"
        for k in ("a", "b", "result"):
            if r.get(k) not in items:
                err(f"{w}.{k}: предмета '{r.get(k)}' нет в items.json")
        for k in r.get("keep", []):
            if k not in (r.get("a"), r.get("b")):
                err(f"{w}.keep: '{k}' должен быть одним из a или b")
        if r.get("a") == r.get("b"):
            err(f"{w}: a и b совпадают")
        check_actions(r.get("do", []), w + ".do", scenes, items)

    # недостижимые сцены
    seen, todo = set(), [data.get("start")]
    while todo:
        s = todo.pop()
        if s in seen or s not in scenes:
            continue
        seen.add(s)
        todo += list(edges.get(s, ()))
    for sid in scenes:
        if sid not in seen:
            warnings.append(f"сцена '{sid}' недостижима: в неё не ведёт ни стрелка, ни goto")
    for f in sorted(used_flags - set_flags):
        warnings.append(f"флаг '{f}' проверяется, но нигде не ставится")

    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ОШИБКА", e)
    print(f"Сцен: {len(scenes)}, предметов: {len(items)}, рецептов: {len(recipes)}. "
          f"Ошибок: {len(errors)}, предупреждений: {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
