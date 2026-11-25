"""Проверка data/*.json без запуска игры:  python tools/check_data.py
Ловит опечатки: несуществующие сцены/предметы, неизвестные действия, кривые rect, битые стрелки и рецепты."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Когда в движок добавляется новое действие, допиши его сюда
KNOWN_ACTIONS = {"say", "wait", "give", "take", "setFlag", "clearFlag", "randomFlag", "goto", "ending", "label"}
COND_KEYS = {"flag", "notFlag", "has", "selected"}
ARROW_KEYS = {"left", "right", "up", "down"}

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


def check_actions(actions, where, scenes, items):
    for i, a in enumerate(actions):
        if len(a) != 1:
            err(f"{where}[{i}]: в одном действии должен быть один ключ, а тут {list(a)}")
        key, val = next(iter(a.items()))
        if key not in KNOWN_ACTIONS:
            err(f"{where}[{i}]: неизвестное действие '{key}'")
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
            warnings.append(f"{sid}: нет файла фона {bg} (будет цветная заглушка)")
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
            for j, rule in enumerate(h.get("rules", [])):
                check_cond(rule.get("if"), f"{w}.rules[{j}]", items)
                check_actions(rule.get("do", []), f"{w}.rules[{j}].do", scenes, items)

    for iid, it in items.items():
        if it.get("icon") and not (ROOT / it["icon"]).exists():
            warnings.append(f"предмет '{iid}': нет файла иконки {it['icon']} (будет буква)")
    for j, r in enumerate(recipes):
        w = f"recipes[{j}]"
        for k in ("a", "b", "result"):
            if r.get(k) not in items:
                err(f"{w}.{k}: предмета '{r.get(k)}' нет в items.json")
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
