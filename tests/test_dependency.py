import pytest
from pathlib import Path
from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from unittest.mock import Mock

@pytest.fixture
def sample_dir(tmp_path):
    dir_path = tmp_path / "sample_project"
    dir_path.mkdir()
    file1 = dir_path / "file1.py"
    file1.write_text("""
import file2
def func1():
    file2.func2()
""")
    file2 = dir_path / "file2.py"
    file2.write_text("""
def func2():
    pass
class Class1:
    def method1(self):
        pass
""")
    return dir_path

@pytest.fixture
def sample_dir_with_subdir(tmp_path):
    dir_path = tmp_path / "sample_project"
    dir_path.mkdir()
    sub_dir = dir_path / "sub"
    sub_dir.mkdir()
    file1 = dir_path / "file1.py"
    file1.write_text("""
from sub import file3
def func1():
    file3.func3()
""")
    file2 = dir_path / "file2.py"
    file2.write_text("""
def func2():
    pass
""")
    file3 = sub_dir / "file3.py"
    file3.write_text("""
def func3():
    pass
""")
    return dir_path

class MockEnhancedAnalyzer:
    def __init__(self, sample_dir):
        self.quality_issues = {
            "complexity": [
                {"file_path": str(sample_dir / "file2.py"), "description": "High complexity", "line": 1}
            ]
        }

def test_analyze_file(sample_dir):
    analyzer = ModuleDependencyAnalyzer()
    analyzer.directory = sample_dir
    file_path = sample_dir / "file1.py"
    result = analyzer._analyze_file(file_path)
    assert result is not None
    assert result["module_name"] == "file1"
    assert "file2" in result["imports"]
    assert "file1.func1" in result["function_locations"]
    assert any(
        call["to_function"] == "func2" and call["to_module"] == "file2"
        for call in result["function_calls"]
    )

def test_analyze_directory(sample_dir):
    analyzer = ModuleDependencyAnalyzer()
    analyzer.analyze_directory(sample_dir)
    assert "file1" in analyzer.module_imports
    assert "file2" in analyzer.module_imports
    assert analyzer.module_imports["file1"] == {"file2"}
    assert analyzer.module_imports["file2"] == set()
    assert "file1.func1" in analyzer.function_locations
    assert "file2.func2" in analyzer.function_locations
    assert "Class1" in analyzer.class_info["file2"]

def find_node_by_name(nodes, name):
    return next((node for node in nodes if node["name"] == name), None)

def test_get_graph_data(sample_dir):
    analyzer = ModuleDependencyAnalyzer()
    analyzer.analyze_directory(sample_dir)
    nodes, links = analyzer.get_graph_data()
    
    file1_node = find_node_by_name(nodes, "file1")
    assert file1_node is not None
    assert file1_node["type"] == "module"
    func1_node = find_node_by_name(nodes, "file1.func1")  # Updated to full identifier
    assert func1_node is not None
    assert func1_node["type"] == "function"
    file2_node = find_node_by_name(nodes, "file2")
    assert file2_node is not None
    class1_node = find_node_by_name(nodes, "Class1")
    assert class1_node is not None
    method1_node = find_node_by_name(nodes, "method1")
    assert method1_node is not None
    
    id_to_name = {node["id"]: node["name"] for node in nodes}
    contains_link = next(
        (link for link in links 
         if id_to_name[link["source"]] == "file1" and id_to_name[link["target"]] == "file1.func1"  # Updated
         and link["type"] == "contains"), 
        None
    )
    assert contains_link is not None
    calls_link = next(
        (link for link in links 
         if id_to_name[link["source"]] == "file1.func1" and id_to_name[link["target"]] == "file2.func2" 
         and link["type"] == "calls"), 
        None
    )
    assert calls_link is not None

def test_get_graph_data_with_quality(sample_dir):
    analyzer = ModuleDependencyAnalyzer()
    analyzer.analyze_directory(sample_dir)
    mock_analyzer = MockEnhancedAnalyzer(sample_dir)
    nodes, _ = analyzer.get_graph_data_with_quality(mock_analyzer)
    file2_node = find_node_by_name(nodes, "file2")
    assert "code_smells" in file2_node
    assert len(file2_node["code_smells"]) == 1
    assert file2_node["code_smells"][0]["description"] == "High complexity"

def test_get_entry_points(sample_dir):
    analyzer = ModuleDependencyAnalyzer()
    analyzer.analyze_directory(sample_dir)
    entry_points = analyzer.get_entry_points()
    assert "file1" in entry_points
    assert "file2" not in entry_points

def test_clean_for_markdown():
    analyzer = ModuleDependencyAnalyzer()
    input_line = "⚡ func1 # Docstring here"
    cleaned = analyzer.clean_for_markdown(input_line)
    assert '<i class="fas fa-bolt icon-function"></i>' in cleaned
    assert '<span class="docstring">Docstring here</span>' in cleaned

def test_analyze_directory_empty(tmp_path):
    analyzer = ModuleDependencyAnalyzer()
    analyzer.analyze_directory(tmp_path)
    assert analyzer.module_imports == {}
    assert analyzer.module_metrics == {}
    assert analyzer.function_locations == {}
    assert analyzer.function_calls == {}
    assert analyzer.class_info == {}

def test_analyze_file_with_syntax_error(tmp_path):
    file_path = tmp_path / "invalid.py"
    file_path.write_text("def func1(: pass")
    analyzer = ModuleDependencyAnalyzer()
    analyzer.directory = tmp_path
    result = analyzer._analyze_file(file_path)
    assert result is None

def test_analyze_directory_with_subdir(sample_dir_with_subdir):
    analyzer = ModuleDependencyAnalyzer()
    analyzer.analyze_directory(sample_dir_with_subdir)
    assert "file1" in analyzer.module_imports
    assert "sub.file3" in analyzer.module_imports
    assert "sub" in analyzer.module_imports["file1"]
    assert "sub.file3.func3" in analyzer.function_locations