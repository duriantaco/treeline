import os
import shutil
import unittest
from treeline.core import generate_tree

class TestEmptyDirectory(unittest.TestCase):
    def setUp(self):
        """Set up test directory"""
        self.test_dir = "test_temp_dir"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir) 

    def test_empty_directory(self):
        """Test handling of empty directory"""
        empty_dir = os.path.join(self.test_dir, "empty_folder")
        os.makedirs(empty_dir)
        result = generate_tree(empty_dir)
        self.assertEqual(result.count("\n"), 0)


if __name__ == "__main__":
    unittest.main()