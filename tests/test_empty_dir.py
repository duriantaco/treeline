import unittest
import os
from treeline.core import generate_tree 

def test_empty_directory(self):
    """Test handling of empty directory"""
    empty_dir = os.path.join(self.test_dir, "empty_folder")
    os.makedirs(empty_dir)
    result = generate_tree(empty_dir)
    self.assertEqual(result.count('\n'), 0)

if __name__ == '__main__':
    unittest.main()