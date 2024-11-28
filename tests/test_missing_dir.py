import unittest
from treeline.core import generate_tree 


def test_non_existent_directory(self):
    """Test handling of non-existent directory"""
    with self.assertRaises(FileNotFoundError):
        generate_tree("/path/that/does/not/exist")
    
if __name__ == '__main__':
    unittest.main()