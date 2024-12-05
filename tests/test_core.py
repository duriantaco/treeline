import os
import shutil
import tempfile
import unittest
from pathlib import Path

from treeline.core import generate_tree


class TestTreeGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        os.makedirs(os.path.join(self.test_dir, "folder1"))
        os.makedirs(os.path.join(self.test_dir, "folder2"))
        Path(self.test_dir, "test.txt").touch()
        Path(self.test_dir, "folder1", "file1.txt").touch()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_tree_structure(self):
        """Test if the tree structure is generated correctly"""
        result = generate_tree(self.test_dir)

        self.assertIn("folder1", result)
        self.assertIn("folder2", result)
        self.assertIn("test.txt", result)
        self.assertIn("file1.txt", result)

        self.assertIn("├──", result)
        self.assertIn("└──", result)

    def test_markdown_creation(self):
        """Test if markdown file is created when flag is True"""
        generate_tree(self.test_dir, create_md=True)

        self.assertTrue(os.path.exists("tree.md"))

        if os.path.exists("tree.md"):
            os.remove("tree.md")


if __name__ == "__main__":
    unittest.main()
