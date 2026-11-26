"""Запуск: python -m unittest -v"""
import itertools
import random
import unittest

from game.puzzles.logic import CodeLogic, SequenceLogic, SwitchLogic


class TestCode(unittest.TestCase):
    def test_solve(self):
        c = CodeLogic("1447")
        self.assertFalse(c.solved())
        for i, d in enumerate([1, 4, 4, 7]):
            for _ in range(d):
                c.bump(i, +1)
        self.assertTrue(c.solved())

    def test_wraps_around(self):
        c = CodeLogic("90")
        c.bump(0, -1)   # 0 -> 9
        self.assertEqual(c.digits[0], 9)
        c.bump(1, +10)  # 0 -> 0
        self.assertEqual(c.digits[1], 0)
        self.assertTrue(c.solved())


class TestSwitches(unittest.TestCase):
    def test_never_starts_solved(self):
        for seed in range(50):
            self.assertFalse(SwitchLogic(5, rng=random.Random(seed)).solved())

    def test_toggle_affects_neighbours(self):
        s = SwitchLogic(5, rng=random.Random(1))
        s.states = [False] * 5
        s.toggle(0)
        self.assertEqual(s.states, [True, True, False, False, False])
        s.toggle(2)
        self.assertEqual(s.states, [True, False, True, True, False])

    def test_always_solvable(self):
        for seed in range(30):
            s = SwitchLogic(5, rng=random.Random(seed))
            start = list(s.states)
            found = False
            for mask in itertools.product([0, 1], repeat=5):  # порядок кликов неважен
                s.states = list(start)
                for i, m in enumerate(mask):
                    if m:
                        s.toggle(i)
                if s.solved():
                    found = True
                    break
            self.assertTrue(found, f"seed {seed} нерешаем")


class TestSequence(unittest.TestCase):
    def test_correct_order(self):
        s = SequenceLogic([1, 0, 2])
        self.assertEqual([s.press(1), s.press(0), s.press(2)], ["ok", "ok", "done"])

    def test_wrong_resets(self):
        s = SequenceLogic([1, 0, 2])
        self.assertEqual(s.press(1), "ok")
        self.assertEqual(s.press(2), "wrong")
        self.assertEqual(s.progress, 0)
        self.assertEqual(s.press(1), "ok")


if __name__ == "__main__":
    unittest.main()
