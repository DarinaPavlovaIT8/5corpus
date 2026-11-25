"""Запуск: python -m unittest -v"""
import tempfile
import unittest
from pathlib import Path

from game.state import GameState


class TestSave(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "save.json"

    def tearDown(self):
        self.dir.cleanup()

    def test_roundtrip(self):
        a = GameState()
        a.scene = "hall"; a.flags = {"x", "y"}; a.inventory = ["key"]
        a.save(self.path)
        b = GameState()
        self.assertTrue(b.load(path=self.path))
        self.assertEqual((b.scene, b.flags, b.inventory), ("hall", {"x", "y"}, ["key"]))

    def test_missing_file(self):
        self.assertFalse(GameState().load(path=self.path))

    def test_corrupt_file(self):
        self.path.write_text("{ не json", encoding="utf-8")
        self.assertFalse(GameState().load(path=self.path))

    def test_unknown_scene_is_rejected(self):
        a = GameState(); a.scene = "deleted_scene"; a.save(self.path)
        self.assertFalse(GameState().load(valid_scenes={"room", "hall"}, path=self.path))

    def test_known_scene_is_accepted(self):
        a = GameState(); a.scene = "room"; a.save(self.path)
        self.assertTrue(GameState().load(valid_scenes={"room", "hall"}, path=self.path))

    def test_delete_save(self):
        a = GameState(); a.scene = "room"; a.save(self.path)
        self.assertTrue(GameState.has_save(self.path))
        GameState.delete_save(self.path)
        self.assertFalse(GameState.has_save(self.path))

    def test_delete_missing_is_safe(self):
        GameState.delete_save(self.path)  # не должно падать


if __name__ == "__main__":
    unittest.main()
