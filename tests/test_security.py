import pytest
import ast
import re
from pathlib import Path
from collections import defaultdict
from unittest.mock import patch
from treeline.checkers.security import SecurityAnalyzer  

DEFAULT_CONFIG = {
    "SOME_CONFIG_KEY": "value"
}

@pytest.fixture
def mock_get_config():
    """Fixture to mock get_config with a controlled configuration."""
    with patch("your_module.get_config") as mock_get_config:
        mock_get_config.return_value.as_dict.return_value = DEFAULT_CONFIG
        yield mock_get_config

@pytest.fixture
def temp_file(tmp_path):
    """Fixture to create a temporary file for testing."""
    file_path = tmp_path / "test_file.py"
    file_path.write_text("password = 'mysecret'\n")
    return file_path

def test_init_default_config():
    """Test initialization with default configuration."""
    analyzer = SecurityAnalyzer()
    assert analyzer.config == {}
    assert isinstance(analyzer.security_patterns, dict)
    assert "credential" in analyzer.security_patterns

def test_init_custom_config():
    """Test initialization with custom configuration."""
    custom_config = {"CUSTOM_KEY": "custom_value"}
    analyzer = SecurityAnalyzer(config=custom_config)
    assert analyzer.config == custom_config

def test_check_regex_patterns_credential(temp_file):
    """Test detection of hardcoded credentials."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    with open(temp_file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    analyzer._check_regex_patterns(lines, temp_file, quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "Possible hardcoded credential" in quality_issues["security"][0]["description"]
    assert quality_issues["security"][0]["severity"] == "high"

def test_check_regex_patterns_sql_injection():
    """Test detection of potential SQL injection."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    lines = ["cursor.execute('SELECT * FROM users WHERE id = ' + user_id)"]
    analyzer._check_regex_patterns(lines, Path("test.py"), quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "Potential SQL injection risk" in quality_issues["security"][0]["description"]
    assert quality_issues["security"][0]["severity"] == "high"

def test_check_regex_patterns_command_injection():
    """Test detection of potential command injection."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    lines = ["os.system('ls ' + user_input)"]
    analyzer._check_regex_patterns(lines, Path("test.py"), quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "Potential command injection risk" in quality_issues["security"][0]["description"]

def test_check_regex_patterns_insecure_function():
    """Test detection of insecure function usage."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    lines = ["pickle.loads(data)"]
    analyzer._check_regex_patterns(lines, Path("test.py"), quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "Use of potentially insecure function" in quality_issues["security"][0]["description"]

def test_is_credential_false_positive_true():
    """Test false positive detection for credentials."""
    analyzer = SecurityAnalyzer()
    line = "password = 'example'"
    assert analyzer._is_credential_false_positive(line) == True

def test_is_credential_false_positive_short_value():
    """Test false positive for short credential values."""
    analyzer = SecurityAnalyzer()
    line = "password = 'short'"
    assert analyzer._is_credential_false_positive(line) == True

def test_is_credential_false_positive_env():
    """Test false positive for environment variable usage."""
    analyzer = SecurityAnalyzer()
    line = "password = os.environ['PASS']"
    assert analyzer._is_credential_false_positive(line) == True

def test_is_credential_false_positive_false():
    """Test true positive detection for credentials."""
    analyzer = SecurityAnalyzer()
    line = "password = 'mysecretpassword123'"
    assert analyzer._is_credential_false_positive(line) == False

def test_check_dangerous_ast_patterns_eval():
    """Test detection of eval() usage."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    tree = ast.parse("eval('some code')")
    analyzer._check_dangerous_ast_patterns(tree, Path("test.py"), quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "Use of eval() function" in quality_issues["security"][0]["description"]
    assert quality_issues["security"][0]["severity"] == "high"

def test_check_dangerous_ast_patterns_input_exec():
    """Test detection of user input passed to exec()."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    tree = ast.parse("exec(input('Enter code: '))")
    analyzer._check_dangerous_ast_patterns(tree, Path("test.py"), quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "User input passed directly to exec" in quality_issues["security"][0]["description"]
    assert quality_issues["security"][0]["severity"] == "critical"

def test_check_dangerous_ast_patterns_file_operation():
    """Test detection of potential path traversal in file operations."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    tree = ast.parse("open(user_input + '.txt', 'r')")
    analyzer._check_dangerous_ast_patterns(tree, Path("test.py"), quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "Potential path traversal vulnerability" in quality_issues["security"][0]["description"]
    assert quality_issues["security"][0]["severity"] == "high"

def test_get_parent():
    """Test getting the parent node in the AST."""
    analyzer = SecurityAnalyzer()
    tree = ast.parse("exec(input('Enter code: '))")
    call_node = tree.body[0].value
    parent = analyzer._get_parent(call_node, tree)
    assert isinstance(parent, ast.Expr)

def test_check_with_file(temp_file):
    """Integration test for check method with a file."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    tree = ast.parse(temp_file.read_text())
    analyzer.check(tree, temp_file, quality_issues)
    assert len(quality_issues["security"]) > 0
    assert "Possible hardcoded credential" in quality_issues["security"][0]["description"]

def test_check_with_exception(temp_file):
    """Test check method handles exceptions gracefully."""
    analyzer = SecurityAnalyzer()
    quality_issues = defaultdict(list)
    with patch("builtins.open", side_effect=Exception("Mocked exception")):
        analyzer.check(ast.parse(""), temp_file, quality_issues)
    assert len(quality_issues["security"]) == 1
    assert "Error during security analysis" in quality_issues["security"][0]["description"]
    assert quality_issues["security"][0]["severity"] == "low"

if __name__ == "__main__":
    pytest.main(["-v"])