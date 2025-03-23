import ast
from collections import defaultdict
from pathlib import Path
import pytest
from unittest.mock import patch
from treeline.checkers.code_smells import CodeSmellChecker 

DEFAULT_CONFIG = {
    "MAX_PARAMS": 5,
    "MAX_FUNCTION_LINES": 50,
    "MAX_NESTED_BLOCKS": 3,
    "MAX_RETURNS": 4
}

@pytest.fixture
def checker():
    """Fixture to create a CodeSmellChecker instance with mocked config."""
    with patch("treeline.checkers.code_smells.get_config") as mock_config:
        mock_config.return_value.as_dict.return_value = DEFAULT_CONFIG
        return CodeSmellChecker()

@pytest.fixture
def file_path():
    """Fixture to provide a consistent file path for tests."""
    return Path("test_file.py")

@pytest.fixture
def quality_issues():
    """Fixture to initialize an empty defaultdict for collecting quality issues."""
    return defaultdict(list)

def run_check(code, checker, file_path, quality_issues):
    """Helper function to parse code and run the check method."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            node.end_lineno = node.lineno + len(code.splitlines()) - 1
    checker.check(tree, file_path, quality_issues)

def test_long_parameter_list_detected(checker, file_path, quality_issues):
    """Test detection of functions with too many parameters."""
    code = """
def my_function(a, b, c, d, e, f):
    pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    issue = quality_issues["code_smells"][0]
    assert "too many parameters (6 > 5)" in issue["description"]
    assert issue["file_path"] == "test_file.py"
    assert issue["line"] == 2
    assert issue["severity"] == "medium"

def test_short_parameter_list_ok(checker, file_path, quality_issues):
    """Test that functions with acceptable parameter counts pass."""
    code = """
def my_function(a, b, c):
    pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 0

def test_long_function_detected(checker, file_path, quality_issues):
    """Test detection of functions exceeding the line limit."""
    code = "def my_function():\n" + "    pass\n" * 51
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    assert "too long (51 > 50 lines)" in quality_issues["code_smells"][0]["description"]

def test_short_function_ok(checker, file_path, quality_issues):
    """Test that short functions pass without issues."""
    code = """
def my_function():
    x = 1
    return x
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 0

def test_deep_nesting_detected(checker, file_path, quality_issues):
    """Test detection of deeply nested blocks."""
    code = """
def my_function():
    if True:
        if True:
            if True:
                if True:
                    pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    assert "deeply nested blocks (4 > 3 levels)" in quality_issues["code_smells"][0]["description"]

def test_shallow_nesting_ok(checker, file_path, quality_issues):
    """Test that shallow nesting passes without issues."""
    code = """
def my_function():
    if True:
        pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 0

def test_multiple_returns_detected(checker, file_path, quality_issues):
    """Test detection of functions with too many return statements."""
    code = """
def my_function():
    if True:
        return 1
    if False:
        return 2
    return 3
    return 4
    return 5
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    assert "too many return statements (5 > 4)" in quality_issues["code_smells"][0]["description"]

def test_few_returns_ok(checker, file_path, quality_issues):
    """Test that functions with few returns pass."""
    code = """
def my_function():
    return 1
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 0

def test_too_many_branches_detected(checker, file_path, quality_issues):
    """Test detection of functions with too many branches."""
    code = """
def my_function():
    if True:
        pass
    if True:
        pass
    if True:
        pass
    if True:
        pass
    if True:
        pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    assert "too many branches (5 if statements)" in quality_issues["code_smells"][0]["description"]

def test_few_branches_ok(checker, file_path, quality_issues):
    """Test that functions with few branches pass."""
    code = """
def my_function():
    if True:
        pass
    if True:
        pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 0

def test_empty_except_detected(checker, file_path, quality_issues):
    """Test detection of empty except blocks."""
    code = """
try:
    x = 1
except:
    pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 2
    descriptions = [issue["description"] for issue in quality_issues["code_smells"]]
    assert "Empty except block" in descriptions
    assert "Too broad exception handler (bare except:)" in descriptions

def test_non_empty_except_ok(checker, file_path, quality_issues):
    """Test that non-empty except blocks pass."""
    code = """
try:
    x = 1
except:
    print("Error")
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    issue = quality_issues["code_smells"][0]
    assert "Too broad exception handler (bare except:)" in issue["description"]

def test_broad_except_detected(checker, file_path, quality_issues):
    """Test detection of overly broad exception handlers."""
    code = """
try:
    x = 1
except:
    pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 2
    descriptions = [issue["description"] for issue in quality_issues["code_smells"]]
    assert "Empty except block" in descriptions
    assert "Too broad exception handler (bare except:)" in descriptions

def test_specific_except_ok(checker, file_path, quality_issues):
    """Test that specific exception handlers pass."""
    code = """
try:
    x = 1
except ValueError:
    pass
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    assert "Empty except block" in quality_issues["code_smells"][0]["description"]

def test_minimal_code(checker, file_path, quality_issues):
    """Test that minimal code passes without issues."""
    code = "def f(): pass"
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 0

def test_multiple_smells(checker, file_path, quality_issues):
    """Test detection of multiple code smells in one function."""
    code = """
def my_function(a, b, c, d, e, f):
    if True:
        if True:
            if True:
                if True:
                    return 1
    return 2
    return 3
    return 4
    return 5
"""
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) >= 3 

def test_custom_max_params(file_path, quality_issues):
    """Test behavior with a custom configuration."""
    custom_config = DEFAULT_CONFIG.copy()
    custom_config["MAX_PARAMS"] = 2
    checker = CodeSmellChecker(config=custom_config)
    code = "def my_function(a, b, c): pass"
    run_check(code, checker, file_path, quality_issues)
    assert len(quality_issues["code_smells"]) == 1
    assert "too many parameters (3 > 2)" in quality_issues["code_smells"][0]["description"]