"""Запуск: python -m unittest -v"""
import unittest

from game.state import GameState


class TestState(unittest.TestCase):
    def setUp(self):
        self.st = GameState()

    def test_empty_condition_is_true(self):
        self.assertTrue(self.st.check(None))
        self.assertTrue(self.st.check({}))

    def test_flag_and_notflag(self):
        self.assertFalse(self.st.check({"flag": "a"}))
        self.assertTrue(self.st.check({"notFlag": "a"}))
        self.st.flags.add("a")
        self.assertTrue(self.st.check({"flag": "a"}))
        self.assertFalse(self.st.check({"notFlag": "a"}))

    def test_has_item(self):
        self.assertFalse(self.st.check({"has": "key"}))
        self.st.inventory.append("key")
        self.assertTrue(self.st.check({"has": "key"}))

    def test_selected(self):
        self.st.inventory.append("key")
        self.assertFalse(self.st.check({"selected": "key"}))
        self.st.selected = "key"
        self.assertTrue(self.st.check({"selected": "key"}))

    def test_all_conditions_must_hold(self):
        self.st.flags.add("locked")
        self.assertFalse(self.st.check({"flag": "locked", "selected": "key"}))
        self.st.selected = "key"
        self.assertTrue(self.st.check({"flag": "locked", "selected": "key"}))

    def test_reset(self):
        self.st.flags.add("x"); self.st.inventory.append("k"); self.st.selected = "k"
        self.st.reset()
        self.assertEqual((self.st.flags, self.st.inventory, self.st.selected), (set(), [], None))


if __name__ == "__main__":
    unittest.main()
