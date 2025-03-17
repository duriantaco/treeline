import pytest
import ast
from pathlib import Path
from unittest.mock import Mock, patch
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

@pytest.fixture
def sample_dir(tmp_path):
    dir_path = tmp_path / "sample_project"
    dir_path.mkdir()
    file1 = dir_path / "file1.py"
    file1.write_text("""
def func1():
    pass
""")
    file2 = dir_path / "file2.py"
    file2.write_text("""
class Class1:
    def method1(self):
        pass
""")
    return dir_path

@pytest.fixture
def syntax_error_dir(tmp_path):
    dir_path = tmp_path / "syntax_error_project"
    dir_path.mkdir()
    file1 = dir_path / "file1.py"
    file1.write_text("def func1(: pass") 
    return dir_path

class MockChecker:
    def check(self, *args, **kwargs):
        pass

class MockDuplicationDetector:
    def analyze_directory(self, *args, **kwargs):
        pass

class MockUnusedCodeChecker:
    def finalize_checks(self, *args, **kwargs):
        pass

@pytest.fixture
def mock_dependencies():
    with patch('treeline.enhanced_analyzer.CodeSmellChecker', MockChecker), \
         patch('treeline.enhanced_analyzer.ComplexityAnalyzer', MockChecker), \
         patch('treeline.enhanced_analyzer.SecurityAnalyzer', MockChecker), \
         patch('treeline.enhanced_analyzer.SQLInjectionChecker', MockChecker), \
         patch('treeline.enhanced_analyzer.StyleChecker', MockChecker), \
         patch('treeline.enhanced_analyzer.DuplicationDetector', MockDuplicationDetector), \
         patch('treeline.enhanced_analyzer.UnusedCodeChecker', MockUnusedCodeChecker), \
         patch('treeline.enhanced_analyzer.get_config', return_value={'MAX_LINE_LENGTH': 80}):
        yield

def test_initialization(mock_dependencies):
    analyzer = EnhancedCodeAnalyzer()
    assert analyzer.show_params is True
    assert analyzer.config == {'MAX_LINE_LENGTH': 80}
    assert isinstance(analyzer.quality_issues, dict)
    assert isinstance(analyzer.metrics_summary, dict)

def test_initialization_with_config(mock_dependencies):
    custom_config = {"MAX_LINE_LENGTH": 120}
    analyzer = EnhancedCodeAnalyzer(config=custom_config)
    assert analyzer.config == custom_config

def test_read_file_success(mock_dependencies, tmp_path):
    file_path = tmp_path / "test.py"
    file_path.write_text("def test():\n    pass")
    analyzer = EnhancedCodeAnalyzer()
    content = analyzer._read_file(file_path)
    assert content == "def test():\n    pass"

def test_read_file_failure(mock_dependencies, tmp_path):
    file_path = tmp_path / "nonexistent.py"
    analyzer = EnhancedCodeAnalyzer()
    content = analyzer._read_file(file_path)
    assert content is None
    assert "file" in analyzer.quality_issues
    assert any("Could not read file" in issue["description"] for issue in analyzer.quality_issues["file"])

def test_parse_content_success(mock_dependencies):
    analyzer = EnhancedCodeAnalyzer()
    content = "def func():\n    pass"
    tree = analyzer._parse_content(content)
    assert isinstance(tree, ast.AST)

def test_parse_content_syntax_error(mock_dependencies):
    analyzer = EnhancedCodeAnalyzer()
    content = "def func(: pass"
    tree = analyzer._parse_content(content)
    assert tree is None
    assert "parsing" in analyzer.quality_issues
    assert any("Could not parse content" in issue["description"] for issue in analyzer.quality_issues["parsing"])

def test_analyze_file_valid(mock_dependencies, sample_dir):
    analyzer = EnhancedCodeAnalyzer()
    file_path = sample_dir / "file1.py"
    results = analyzer.analyze_file(file_path)
    assert len(results) == 1
    assert results[0]["type"] == "function"
    assert results[0]["name"] == "func1"

def test_analyze_file_syntax_error(mock_dependencies, syntax_error_dir):
    analyzer = EnhancedCodeAnalyzer()
    file_path = syntax_error_dir / "file1.py"
    results = analyzer.analyze_file(file_path)
    assert len(results) == 0

def test_analyze_file_read_error(mock_dependencies, sample_dir):
    analyzer = EnhancedCodeAnalyzer()
    file_path = sample_dir / "nonexistent.py"
    results = analyzer.analyze_file(file_path)
    assert len(results) == 0

def test_analyze_directory(mock_dependencies, sample_dir):
    analyzer = EnhancedCodeAnalyzer()
    results = analyzer.analyze_directory(sample_dir)
    assert len(results) == 2  
    assert any(r["type"] == "function" for r in results)
    assert any(r["type"] == "class" for r in results)

def test_analyze_function(mock_dependencies):
    analyzer = EnhancedCodeAnalyzer()
    tree = ast.parse("def func1():\n    pass")
    func_node = tree.body[0]
    func_info = analyzer._analyze_function(func_node, "def func1():\n    pass")
    assert func_info["type"] == "function"
    assert func_info["name"] == "func1"
    assert func_info["metrics"]["lines"] == 1
    assert func_info["metrics"]["params"] == 0
    assert func_info["metrics"]["complexity"] == 1

def test_analyze_class(mock_dependencies):
    analyzer = EnhancedCodeAnalyzer()
    tree = ast.parse("class Class1:\n    def method1(self):\n        pass")
    class_node = tree.body[0]
    class_info = analyzer._analyze_class(class_node, "class Class1:\n    def method1(self):\n        pass")
    assert class_info["type"] == "class"
    assert class_info["name"] == "Class1"
    assert class_info["metrics"]["lines"] == 2
    assert class_info["metrics"]["methods"] == 1

def test_calculate_complexity(mock_dependencies):
    analyzer = EnhancedCodeAnalyzer()
    tree = ast.parse("def func1():\n    if True:\n        pass")
    func_node = tree.body[0]
    complexity = analyzer._calculate_complexity(func_node)
    assert complexity == 2  

def test_issue_handling(mock_dependencies, sample_dir):
    analyzer = EnhancedCodeAnalyzer()
    file_path = sample_dir / "file1.py"
    analyzer.quality_issues["complexity"].append({
        "file_path": str(file_path),
        "description": "High complexity",
        "line": 1,
        "severity": "medium"
    })
    results = analyzer.analyze_file(file_path)
    assert len(results) == 1
    assert "code_smells" in results[0]
    assert len(results[0]["code_smells"]) == 1
    assert results[0]["code_smells"][0]["description"] == "High complexity"

def test_checker_error_handling(mock_dependencies, sample_dir):
    analyzer = EnhancedCodeAnalyzer()
    analyzer.code_smell_checker.check = Mock(side_effect=Exception("Mock error"))
    file_path = sample_dir / "file1.py"
    results = analyzer.analyze_file(file_path)
    assert len(results) == 1  