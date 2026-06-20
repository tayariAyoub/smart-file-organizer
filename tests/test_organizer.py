import tempfile
import unittest
from pathlib import Path

from organizer import build_plan, category_for, organize, undo


class OrganizerTests(unittest.TestCase):
    def test_categories_are_case_insensitive(self):
        self.assertEqual(category_for(Path("photo.JPG")), "Images")
        self.assertEqual(category_for(Path("report.pdf")), "Documents")
        self.assertEqual(category_for(Path("unknown.custom")), "Other")

    def test_dry_run_does_not_move_files(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "photo.jpg"
            source.write_text("image", encoding="utf-8")

            result = organize(folder, dry_run=True)

            self.assertEqual(result, [])
            self.assertTrue(source.exists())
            self.assertFalse((folder / "Images").exists())

    def test_organize_and_undo(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "notes.txt").write_text("hello", encoding="utf-8")
            (folder / "script.py").write_text("print('hello')", encoding="utf-8")

            moves = organize(folder)

            self.assertEqual(len(moves), 2)
            self.assertTrue((folder / "Documents" / "notes.txt").exists())
            self.assertTrue((folder / "Code" / "script.py").exists())

            restored = undo(folder)

            self.assertEqual(restored, 2)
            self.assertTrue((folder / "notes.txt").exists())
            self.assertTrue((folder / "script.py").exists())
            self.assertFalse((folder / "Documents").exists())
            self.assertFalse((folder / "Code").exists())

    def test_existing_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            images = folder / "Images"
            images.mkdir()
            (images / "photo.jpg").write_text("old", encoding="utf-8")
            (folder / "photo.jpg").write_text("new", encoding="utf-8")

            plan = build_plan(folder)
            self.assertEqual(plan[0][1].name, "photo_1.jpg")

            organize(folder)
            self.assertEqual((images / "photo.jpg").read_text(encoding="utf-8"), "old")
            self.assertEqual((images / "photo_1.jpg").read_text(encoding="utf-8"), "new")


if __name__ == "__main__":
    unittest.main()
