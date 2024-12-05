import ast
import os
import unittest
from pathlib import Path

from treeline.security_analyzer import TreelineSecurity


class TestTreelineSecurity(unittest.TestCase):
    def setUp(self):
        self.analyzer = TreelineSecurity()
        self.test_files = []

    def create_test_file(self, code: str, filename: str) -> Path:
        """Helper method to create a temporary test file."""
        path = Path(filename)
        with open(path, "w") as f:
            f.write(code)
        self.test_files.append(path)
        return path

    def debug_ast(self, code: str):
        """Helper to print AST for debugging"""
        tree = ast.parse(code)
        return tree

    def test_sql_injection_detection(self):
        code = """def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)"""
        tree = self.debug_ast(code)
        path = self.create_test_file(code, "test_sql_injection.py")
        self.analyzer.analyze_file(path)
        issues = self.analyzer.security_issues.get("sql_injection", [])
        self.assertTrue(
            len(issues) > 0, "SQL injection vulnerability was not detected."
        )

    def test_command_injection_detection(self):
        code = """import os

def execute_command(cmd):
    os.system("ls " + cmd)"""
        path = self.create_test_file(code, "test_command_injection.py")
        self.analyzer.analyze_file(path)
        issues = self.analyzer.security_issues.get("command_injection", [])
        self.assertTrue(
            len(issues) > 0, "Command injection vulnerability was not detected."
        )

    def test_unsafe_deserialization_detection(self):
        code = """import pickle

def load_data(data):
    obj = pickle.loads(data)
    return obj"""
        path = self.create_test_file(code, "test_deserialization.py")
        self.analyzer.analyze_file(path)
        issues = self.analyzer.security_issues.get("deserialization", [])

        self.assertTrue(
            len(issues) > 0, "Unsafe deserialization vulnerability was not detected."
        )

    def test_hardcoded_secret_detection(self):
        code = """def connect_to_db():
    password = "super_secret_password"
    # Use password to connect to the database"""
        path = self.create_test_file(code, "test_hardcoded_secret.py")
        self.analyzer.analyze_file(path)
        issues = self.analyzer.security_issues.get("hardcoded_secret", [])
        self.assertTrue(len(issues) > 0, "Hardcoded secret was not detected.")

    def test_file_operation_detection(self):
        code = """def delete_file(filename):
    os.remove("/var/www/" + filename)"""
        path = self.create_test_file(code, "test_file_operation.py")
        self.analyzer.analyze_file(path)
        issues = self.analyzer.security_issues.get("file_operations", [])

        self.assertTrue(len(issues) > 0, "Insecure file operation was not detected.")

    def tearDown(self):
        for file in self.test_files:
            if file.exists():
                os.remove(file)


if __name__ == "__main__":
    unittest.main()
