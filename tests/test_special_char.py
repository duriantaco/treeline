import os
import unittest
from pathlib import Path

from treeline.core import generate_tree


def test_special_characters(self):
    """Test handling of special characters in names"""
    special_dir = os.path.join(self.test_dir, "special!@#$")
    os.makedirs(special_dir)
    Path(special_dir, "file with spaces.txt").touch()

    result = generate_tree(special_dir)
    self.assertIn("special!@#$", result)
    self.assertIn("file with spaces.txt", result)


if __name__ == "__main__":
    unittest.main()
