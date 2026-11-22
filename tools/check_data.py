"""Проверка data/*.json без запуска игры:  python tools/check_data.py
Ловит опечатки: несуществующие сцены/предметы, неизвестные действия, кривые rect."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Когда в движок добавляется новое действие, допиши его сюда
KNOWN_ACTIONS = {"say", "wait", "give", "take", "setFlag", "clearFlag", "randomFlag", "goto", "ending"}
COND_KEYS = {"flag", "notFlag", "has", "selected"}

errors, warnings = [], []
endings = {}
set_flags, used_flags = set(), set()


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
        elif key == "goto" and val not in scenes:
            err(f"{where}[{i}]: goto на несуществующую сцену '{val}'")
        elif key in ("give", "take") and val not in items:
            err(f"{where}[{i}]: предмет '{val}' нет в items.json")
        elif key in ("setFlag", "randomFlag"):
            set_flags.add(val)
        elif key == "clearFlag":
            used_flags.add(val)


def main():
    data = json.loads((ROOT / "data" / "scenes.json").read_text(encoding="utf-8"))
    items = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))
    scenes = data.get("scenes", {})
    endings.update(data.get("endings", {}))
    for eid, e in endings.items():
        if not e.get("title") or not e.get("text"):
            err(f"концовка '{eid}': нужны поля title и text")
    if data.get("start") not in scenes:
        err(f"start='{data.get('start')}' — такой сцены нет")
    for sid, sc in scenes.items():
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
            check_cond(h.get("visibleIf"), w + ".visibleIf", items)
            for j, rule in enumerate(h.get("rules", [])):
                check_cond(rule.get("if"), f"{w}.rules[{j}]", items)
                check_actions(rule.get("do", []), f"{w}.rules[{j}].do", scenes, items)
    for f in sorted(used_flags - set_flags):
        warnings.append(f"флаг '{f}' проверяется, но нигде не ставится")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ОШИБКА", e)
    print(f"Сцен: {len(scenes)}, предметов: {len(items)}. Ошибок: {len(errors)}, предупреждений: {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
