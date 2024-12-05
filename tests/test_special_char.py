import os
import unittest
from pathlib import Path
from treeline.core import generate_tree

class TestSpecialCharacters(unittest.TestCase):
    def setUp(self):
        """Set up test directory"""
        self.test_dir = "test_temp_dir"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test directory"""
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

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