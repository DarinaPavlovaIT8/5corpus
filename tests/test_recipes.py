"""Запуск: python -m unittest -v"""
import unittest

from game.state import GameState, find_recipe

RECIPES = [
    {"a": "lamp", "b": "battery", "result": "lamp_on"},
    {"a": "rope", "b": "hook", "result": "grapple", "keep": ["hook"]},
]


class TestRecipes(unittest.TestCase):
    def test_find_in_any_order(self):
        self.assertIsNotNone(find_recipe(RECIPES, "lamp", "battery"))
        self.assertIsNotNone(find_recipe(RECIPES, "battery", "lamp"))

    def test_find_missing(self):
        self.assertIsNone(find_recipe(RECIPES, "lamp", "rope"))

    def test_combine_replaces_items(self):
        st = GameState()
        st.inventory = ["key", "lamp", "coin", "battery"]
        st.selected = "lamp"
        self.assertTrue(st.combine(RECIPES[0]))
        self.assertEqual(st.inventory, ["key", "lamp_on", "coin"])
        self.assertIsNone(st.selected)

    def test_combine_keep(self):
        st = GameState()
        st.inventory = ["rope", "hook"]
        self.assertTrue(st.combine(RECIPES[1]))
        self.assertEqual(sorted(st.inventory), ["grapple", "hook"])

    def test_combine_requires_both_items(self):
        st = GameState()
        st.inventory = ["lamp"]
        self.assertFalse(st.combine(RECIPES[0]))
        self.assertEqual(st.inventory, ["lamp"])

    def test_no_duplicate_result(self):
        st = GameState()
        st.inventory = ["lamp", "battery", "lamp_on"]
        st.combine(RECIPES[0])
        self.assertEqual(st.inventory.count("lamp_on"), 1)


if __name__ == "__main__":
    unittest.main()
