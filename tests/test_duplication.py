import pytest
from pathlib import Path
from collections import defaultdict
from unittest.mock import patch
from treeline.checkers.duplication import DuplicationDetector
from treeline.models.enhanced_analyzer import QualityIssue

@pytest.fixture
def temp_dir(tmp_path):
    """Fixture to create a temporary directory for test files."""
    dir_path = tmp_path / "sample_project"
    dir_path.mkdir()
    return dir_path

@pytest.fixture
def mock_config():
    """Fixture to mock get_config with a controlled configuration."""
    config = {"MAX_DUPLICATED_LINES": 2} 
    with patch("treeline.config_manager.get_config") as mock_get_config:
        mock_get_config.return_value.as_dict.return_value = config
        yield config

def test_no_duplication(temp_dir, mock_config):
    """Test that no duplication issues are logged when there are no duplicates."""
    file1 = temp_dir / "file1.py"
    file1.write_text("unique line 1\nunique line 2")
    file2 = temp_dir / "file2.py"
    file2.write_text("unique line 3\nunique line 4")

    quality_issues = defaultdict(list)
    detector = DuplicationDetector()
    detector.analyze_directory(temp_dir, quality_issues)

    assert len(quality_issues["duplication"]) == 0, "No duplication issues should be logged."

def test_single_duplication(temp_dir, mock_config):
    """Test detection of a single duplicated line across files."""
    duplicated_line = "print('Hello, World!')"
    file1 = temp_dir / "file1.py"
    file1.write_text(f"{duplicated_line}\nunique line 1")
    file2 = temp_dir / "file2.py"
    file2.write_text(f"{duplicated_line}\nunique line 2")

    quality_issues = defaultdict(list)
    detector = DuplicationDetector()
    detector.analyze_directory(temp_dir, quality_issues)

    assert len(quality_issues["duplication"]) == 0, "Single duplication should not exceed threshold of 2."

def test_multiple_duplications_exceeding_threshold(temp_dir, mock_config):
    duplicated_line = "print('Hello')"
    file1 = temp_dir / "file1.py"
    file1.write_text(f"{duplicated_line}\nunique line 1")
    file2 = temp_dir / "file2.py"
    file2.write_text(f"{duplicated_line}\nunique line 2")
    file3 = temp_dir / "file3.py"
    file3.write_text(f"{duplicated_line}\nunique line 3")

    quality_issues = defaultdict(list)
    detector = DuplicationDetector(config=mock_config)
    detector.analyze_directory(temp_dir, quality_issues)

    assert len(quality_issues["duplication"]) == 3, "Issues should be logged for all three occurrences."
    paths = {issue["file_path"] for issue in quality_issues["duplication"]}
    assert paths == {str(file1), str(file2), str(file3)}

def test_multiple_lines_duplicated(temp_dir, mock_config):
    duplicated_line1 = "print('Hello')"
    duplicated_line2 = "print('World')"
    file1 = temp_dir / "file1.py"
    file1.write_text(f"{duplicated_line1}\n{duplicated_line2}")
    file2 = temp_dir / "file2.py"
    file2.write_text(f"{duplicated_line1}\n{duplicated_line2}")
    file3 = temp_dir / "file3.py"
    file3.write_text(f"{duplicated_line1}\n{duplicated_line2}")

    quality_issues = defaultdict(list)
    detector = DuplicationDetector(config=mock_config)  
    detector.analyze_directory(temp_dir, quality_issues)

    assert len(quality_issues["duplication"]) == 6, "Issues should be logged for all occurrences of both lines."
    paths = {issue["file_path"] for issue in quality_issues["duplication"]}
    assert paths == {str(file1), str(file2), str(file3)}

def test_threshold_handling_below_threshold(temp_dir, mock_config):
    """Test that no issues are logged when duplication is below threshold."""
    duplicated_line = "print('Hello')"
    file1 = temp_dir / "file1.py"
    file1.write_text(f"{duplicated_line}\nunique line 1")
    file2 = temp_dir / "file2.py"
    file2.write_text(f"{duplicated_line}\nunique line 2") 

    quality_issues = defaultdict(list)
    detector = DuplicationDetector()
    detector.analyze_directory(temp_dir, quality_issues)

    assert len(quality_issues["duplication"]) == 0, "No issues should be logged when below threshold."

def test_edge_cases(temp_dir, mock_config):
    """Test handling of empty files, whitespace-only files, and non-Python files."""
    empty_file = temp_dir / "empty.py"
    empty_file.write_text("")
    whitespace_file = temp_dir / "whitespace.py"
    whitespace_file.write_text("   \n   ")
    non_py_file = temp_dir / "script.sh"
    non_py_file.write_text("#!/bin/bash\necho 'Hello'")

    quality_issues = defaultdict(list)
    detector = DuplicationDetector()
    detector.analyze_directory(temp_dir, quality_issues)

    assert len(quality_issues["duplication"]) == 0, "No issues should be logged for edge cases."

def test_custom_config(temp_dir):
    duplicated_line = "print('Test')"
    file1 = temp_dir / "file1.py"
    file1.write_text(f"{duplicated_line}\nunique line 1")
    file2 = temp_dir / "file2.py"
    file2.write_text(f"{duplicated_line}\nunique line 2")
    file3 = temp_dir / "file3.py"
    file3.write_text(f"{duplicated_line}\nunique line 3")

    quality_issues = defaultdict(list)
    custom_config = {"MAX_DUPLICATED_LINES": 1}
    detector = DuplicationDetector(config=custom_config)
    detector.analyze_directory(temp_dir, quality_issues)

    assert len(quality_issues["duplication"]) == 3, "Issues should be logged for all three occurrences."
    paths = {issue["file_path"] for issue in quality_issues["duplication"]}
    assert paths == {str(file1), str(file2), str(file3)}