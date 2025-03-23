import pytest
import ast
from collections import defaultdict
from unittest.mock import patch
from treeline.checkers.unused_code import UnusedCodeChecker

DEFAULT_CONFIG = {"SOME_CONFIG_KEY": "value"}

@pytest.fixture
def mock_get_config():
    """Fixture to mock get_config with a controlled configuration."""
    with patch("treeline.checkers.unused_code.get_config") as mock_get_config:
        mock_get_config.return_value.as_dict.return_value = DEFAULT_CONFIG
        yield mock_get_config

@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test_file.py"
    file_path.write_text("import os\n\ndef func1():\n    pass\n\nclass MyClass:\n    def method1(self):\n        pass\n")
    return file_path

def test_init_default_config(mock_get_config):
    checker = UnusedCodeChecker()
    assert checker.config == DEFAULT_CONFIG

def test_init_custom_config():
    """Test initialization with custom configuration."""
    custom_config = {"CUSTOM_KEY": "custom_value"}
    checker = UnusedCodeChecker(config=custom_config)
    assert checker.config == custom_config

def test_collect_imports_and_functions_basic(temp_file):
    checker = UnusedCodeChecker()
    tree = ast.parse(temp_file.read_text())
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    checker._collect_imports_and_functions(tree, str(temp_file))
    assert "os" in checker.imported_names[str(temp_file)]
    assert "test_file.func1" in checker.defined_functions
    assert "test_file.MyClass.method1" in checker.defined_functions

def test_collect_imports_and_functions_with_alias():
    """Test collecting imports with aliases."""
    checker = UnusedCodeChecker()
    tree = ast.parse("import os as operating_system\nfrom sys import version as ver")
    checker._collect_imports_and_functions(tree, "test.py")
    assert "operating_system" in checker.imported_names["test.py"]
    assert "ver" in checker.imported_names["test.py"]

def test_check_name_usage_basic(temp_file):
    checker = UnusedCodeChecker()
    tree = ast.parse("import os\nos.path.join('a', 'b')\nfunc1()\n")
    checker._check_name_usage(tree, str(temp_file))
    assert "os" in checker.used_names[str(temp_file)]
    assert "test_file.func1" in checker.called_functions
    assert "os" in checker.globally_used_imports

def test_check_name_usage_self_method():
    checker = UnusedCodeChecker()
    tree = ast.parse("class MyClass:\n    def method1(self):\n        self.method2()\n    def method2(self):\n        pass")
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    checker._check_name_usage(tree, "test.py")
    assert "test.MyClass.method2" in checker.called_functions

def test_report_unused_imports(temp_file):
    """Test reporting unused imports."""
    checker = UnusedCodeChecker()
    checker.imported_names[str(temp_file)] = {"os", "sys"}
    checker.used_names[str(temp_file)] = {"os"}
    quality_issues = defaultdict(list)
    checker._report_unused_imports(str(temp_file), quality_issues)
    assert len(quality_issues["unused_code"]) == 1
    assert quality_issues["unused_code"][0]["description"] == "Unused import: sys"
    assert quality_issues["unused_code"][0]["file_path"] == str(temp_file)
    assert quality_issues["unused_code"][0]["severity"] == "low"

def test_report_unused_functions():
    """Test reporting unused functions."""
    checker = UnusedCodeChecker()
    checker.defined_functions = {
        "module.func1": {"file_path": "module.py", "line": 1, "name": "func1"},
        "module.func2": {"file_path": "module.py", "line": 2, "name": "func2"},
        "module.__init__": {"file_path": "module.py", "line": 3, "name": "__init__"}
    }
    checker.called_functions = {"module.func1"}
    quality_issues = defaultdict(list)
    checker._report_unused_functions(quality_issues)
    assert len(quality_issues["unused_code"]) == 1
    assert quality_issues["unused_code"][0]["description"] == "Unused function: func2"
    assert quality_issues["unused_code"][0]["severity"] == "medium"

def test_find_import_line_basic(temp_file):
    """Test finding the line number of an import."""
    checker = UnusedCodeChecker()
    line = checker._find_import_line(str(temp_file), "os")
    assert line == 1

def test_find_import_line_file_not_found():
    """Test handling file not found error."""
    checker = UnusedCodeChecker()
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("builtins.print") as mock_print:
            line = checker._find_import_line("nonexistent.py", "os")
            assert line == 1
            mock_print.assert_called_with("File not found: nonexistent.py")

def test_find_import_line_permission_error():
    """Test handling permission error."""
    checker = UnusedCodeChecker()
    with patch("builtins.open", side_effect=PermissionError):
        with patch("builtins.print") as mock_print:
            line = checker._find_import_line("test.py", "os")
            assert line == 1
            mock_print.assert_called_with("Permission denied when reading: test.py")

def test_find_import_line_unicode_error():
    """Test handling Unicode decode error."""
    checker = UnusedCodeChecker()
    with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")):
        with patch("builtins.print") as mock_print:
            line = checker._find_import_line("test.py", "os")
            assert line == 1
            mock_print.assert_called_with("Unicode decode error when reading: test.py")

def test_find_import_line_io_error():
    """Test handling generic IO error."""
    checker = UnusedCodeChecker()
    with patch("builtins.open", side_effect=IOError("IO error")):
        with patch("builtins.print") as mock_print:
            line = checker._find_import_line("test.py", "os")
            assert line == 1
            mock_print.assert_called_with("IO error when reading test.py: IO error")

def test_check_and_finalize(temp_file):
    """Integration test for check and finalize_checks methods."""
    checker = UnusedCodeChecker()
    tree = ast.parse("import os\ndef func1():\n    pass")
    quality_issues = defaultdict(list)
    checker.check(tree, temp_file, quality_issues)
    checker.finalize_checks(quality_issues)
    assert len(quality_issues["unused_code"]) == 2
    assert "Unused import: os" in [issue["description"] for issue in quality_issues["unused_code"]]
    assert "Unused function: func1" in [issue["description"] for issue in quality_issues["unused_code"]]

if __name__ == "__main__":
    pytest.main(["-v"])