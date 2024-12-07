import os
import unittest
from pathlib import Path

from treeline.core import generate_tree


class TestNestedDirectories(unittest.TestCase):
    def setUp(self):
        """Set up test directory"""
        self.test_dir = "test_temp_dir"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test directory"""
        if os.path.exists(self.test_dir):
            import shutil

            shutil.rmtree(self.test_dir)

    def test_nested_directories(self):
        """Test handling of nested directories"""
        nested_path = os.path.join(self.test_dir, "level1", "level2", "level3")
        os.makedirs(nested_path)
        Path(nested_path, "deep_file.txt").touch()

        result = generate_tree(self.test_dir)
        self.assertIn("level1", result)
        self.assertIn("level2", result)
        self.assertIn("level3", result)
        self.assertIn("deep_file.txt", result)


if __name__ == "__main__":
    unittest.main()
