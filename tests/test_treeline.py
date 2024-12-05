import os
import shutil
import tempfile
import unittest

import treeline


class TestTreeLine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        os.makedirs(os.path.join(self.test_dir, "folder1"))
        os.makedirs(os.path.join(self.test_dir, "folder2"))
        open(os.path.join(self.test_dir, "test.txt"), "w").close()
        open(os.path.join(self.test_dir, "folder1", "file1.txt"), "w").close()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_basic_tree(self):
        """Test if tree structure is generated correctly"""
        result = treeline(str(self.test_dir))

        self.assertIn("folder1", result)
        self.assertIn("folder2", result)
        self.assertIn("test.txt", result)
        self.assertIn("file1.txt", result)


if __name__ == "__main__":
    unittest.main()
