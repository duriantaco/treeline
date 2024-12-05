import os
import unittest
from pathlib import Path

from treeline.core import generate_tree


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
