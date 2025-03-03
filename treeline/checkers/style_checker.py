from collections import defaultdict
from pathlib import Path
from typing import Dict
from treeline.models.enhanced_analyzer import QualityIssue

class StyleChecker:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_line_length = self.config.get("MAX_LINE_LENGTH", 80)
        self.max_file_lines = self.config.get("MAX_FILE_LINES", 500)

    def check(self, file_path: Path, quality_issues: defaultdict):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > self.max_file_lines:
            quality_issues["style"].append(QualityIssue(
                description=f"File has {len(lines)} lines (over {self.max_file_lines})",
                file_path=str(file_path),
                line=None
            ).__dict__)
        for i, line in enumerate(lines, start=1):
            if len(line.rstrip()) > self.max_line_length:
                quality_issues["style"].append(QualityIssue(
                    description="Line is too long",
                    file_path=str(file_path),
                    line=i
                ).__dict__)