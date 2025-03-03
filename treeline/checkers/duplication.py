import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict

from treeline.models.enhanced_analyzer import QualityIssue

class DuplicationDetector:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_duplicated_lines = self.config.get("MAX_DUPLICATED_LINES", 5)

    def analyze_directory(self, directory: Path, quality_issues: defaultdict):
        all_lines = {}
        for file_path in directory.rglob("*.py"):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().split("\n")
                all_lines[str(file_path)] = lines

        seen = {}
        for file1, lines1 in all_lines.items():
            for i, line in enumerate(lines1):
                if line.strip():
                    if line in seen and seen[line]["count"] >= self.max_duplicated_lines:
                        quality_issues["duplication"].append(QualityIssue(
                            description=f"Duplicated code block detected",
                            file_path=file1,
                            line=i + 1
                        ).__dict__)
                    else:
                        seen[line] = {"file": file1, "line": i + 1, "count": seen.get(line, {}).get("count", 0) + 1}