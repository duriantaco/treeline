import pytest
from pathlib import Path
from treeline.utils.report import ReportGenerator  
from unittest.mock import patch, MagicMock

@pytest.fixture
def target_dir(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    return target

@pytest.fixture
def output_dir(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    return output

def test_initialization(target_dir, output_dir):
    """Test that ReportGenerator initializes correctly with target and output directories."""
    generator = ReportGenerator(target_dir, output_dir)
    assert generator.target_dir == target_dir
    assert generator.output_dir == output_dir
    assert hasattr(generator, "dependency_analyzer")
    assert hasattr(generator, "enhanced_analyzer")

def test_analyze(target_dir, mocker):
    """Test the analyze method processes files in the target directory."""
    (target_dir / "file1.py").write_text("def func1(): pass")
    generator = ReportGenerator(target_dir)
    mocker.patch.object(generator.enhanced_analyzer, "analyze_directory")
    mocker.patch.object(generator.dependency_analyzer, "analyze_directory")
    generator.analyze()
    assert len(generator.analyzed_files) == 1
    assert str(generator.analyzed_files[0]) == str(target_dir / "file1.py")

def test_collect_function_dependencies(target_dir, mocker):
    """Test that function dependencies are collected correctly."""
    (target_dir / "file1.py").write_text("def func1(): func2()")
    (target_dir / "file2.py").write_text("def func2(): pass")
    generator = ReportGenerator(target_dir)
    mocker.patch.object(generator.enhanced_analyzer, "analyze_directory")
    mocker.patch.object(generator.dependency_analyzer, "analyze_directory")
    generator.dependency_analyzer.function_calls = {
        "file2.func2": [{"from_function": "file1.func1", "from_module": "file1", "line": 1}],
        "file1.func1": []
    }
    generator.dependency_analyzer.function_locations = {
        "file1.func1": {"module": "file1", "file": str(target_dir / "file1.py")},
        "file2.func2": {"module": "file2", "file": str(target_dir / "file2.py")}
    }
    generator.analyze()
    assert "file1.func1" in generator.function_dependencies
    assert any(call["function"] == "file2.func2" for call in generator.function_dependencies["file1.func1"]["calls"])

def test_detect_circular_dependencies(target_dir, mocker):
    """Test detection of circular dependencies between functions."""
    (target_dir / "file1.py").write_text("def func1(): func2()")
    (target_dir / "file2.py").write_text("def func2(): func1()")
    generator = ReportGenerator(target_dir)
    mocker.patch.object(generator.enhanced_analyzer, "analyze_directory")
    mocker.patch.object(generator.dependency_analyzer, "analyze_directory")
    generator.analyze()
    generator.function_dependencies = {
        "file1.func1": {"calls": [{"function": "file2.func2", "module": "file2", "line": 1}], "called_by": []},
        "file2.func2": {"calls": [{"function": "file1.func1", "module": "file1", "line": 1}], "called_by": []}
    }
    circular_deps = generator.detect_circular_dependencies()
    assert len(circular_deps["function_level"]) == 1
    assert circular_deps["function_level"][0] == ["file1.func1", "file2.func2", "file1.func1"]

def test_generate_report(target_dir, mocker):
    """Test that the generate_report method produces expected content."""
    (target_dir / "file1.py").write_text("def func1(): pass")
    generator = ReportGenerator(target_dir)
    mocker.patch.object(generator.enhanced_analyzer, "analyze_directory")
    mocker.patch.object(generator.dependency_analyzer, "analyze_directory")
    generator.dependency_analyzer.function_locations = {
        "file1.func1": {"module": "file1", "file": str(target_dir / "file1.py")}
    }
    generator.dependency_analyzer.function_calls = {"file1.func1": []}
    generator.analyze()
    report = generator.generate_report()
    assert "# Treeline Code Analysis Report" in report
    assert "## 📊 Code Structure Analysis" in report
    assert "## Executive Summary" in report

def test_save_report(target_dir, output_dir, mocker):
    """Test that reports are saved correctly in the output directory."""
    (target_dir / "file1.py").write_text("def func1(): pass")
    generator = ReportGenerator(target_dir, output_dir)
    mocker.patch.object(generator.enhanced_analyzer, "analyze_directory")
    mocker.patch.object(generator.dependency_analyzer, "analyze_directory")
    generator.dependency_analyzer.function_locations = {
        "file1.func1": {"module": "file1", "file": str(target_dir / "file1.py")}
    }
    generator.dependency_analyzer.function_calls = {"file1.func1": []}
    generator.analyze()
    report_path = generator.save_report(format="md")
    assert report_path.exists()
    assert report_path.suffix == ".md"

def test_single_file_no_dependencies(target_dir, mocker):
    """Test analysis of a single file with no dependencies."""
    (target_dir / "file1.py").write_text("def func1(): pass")
    generator = ReportGenerator(target_dir)
    mocker.patch.object(generator.enhanced_analyzer, "analyze_directory")
    mocker.patch.object(generator.dependency_analyzer, "analyze_directory")
    generator.dependency_analyzer.function_locations = {
        "file1.func1": {"module": "file1", "file": str(target_dir / "file1.py"), "line": 1}
    }
    generator.dependency_analyzer.function_calls = {"file1.func1": []}
    generator.analyze()
    assert len(generator.analyzed_files) == 1
    assert len(generator.function_dependencies) >= 1
    assert not generator.function_dependencies.get("file1.func1", {}).get("calls", [])

def test_empty_directory(target_dir, mocker):
    """Test behavior with an empty target directory."""
    generator = ReportGenerator(target_dir)
    mocker.patch.object(generator.enhanced_analyzer, "analyze_directory")
    mocker.patch.object(generator.dependency_analyzer, "analyze_directory")
    generator.analyze()
    assert len(generator.analyzed_files) == 0
    assert generator.issues_count == 0