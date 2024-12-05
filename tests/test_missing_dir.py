import unittest
from treeline.core import generate_tree


class TestMissingDirectory(unittest.TestCase):
    def test_non_existent_directory(self):
        """Test handling of non-existent directory"""
        result = generate_tree("/path/that/does/not/exist")
        self.assertIn("⚠️", result)  
        self.assertIn("Error", result)  


if __name__ == "__main__":
    unittest.main()