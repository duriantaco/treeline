from collections import defaultdict
from pathlib import Path
from typing import Dict
from treeline.config_manager import get_config
from treeline.models.enhanced_analyzer import QualityIssue

class DuplicationDetector:
    def __init__(self, config: Dict = None):
        self.config = config or get_config().as_dict()
        self.max_duplicated_lines = self.config.get("MAX_DUPLICATED_LINES", 6)

    def analyze_directory(self, directory: Path, quality_issues: defaultdict):
        all_lines = {}
        for file_path in directory.rglob("*.py"):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().split("\n")
                all_lines[str(file_path)] = lines

        seen = defaultdict(lambda: {"count": 0, "files": []})
        for file1, lines1 in all_lines.items():
            for i, line in enumerate(lines1):
                if line.strip(): 
                    seen[line]["count"] += 1
                    seen[line]["files"].append({"file": file1, "line": i + 1})
                    if seen[line]["count"] > self.max_duplicated_lines:
                        for occurrence in seen[line]["files"]:
                            quality_issues["duplication"].append(QualityIssue(
                                description="Duplicated code block detected",
                                file_path=occurrence["file"],
                                line=occurrence["line"]
                            ).__dict__)
                        seen[line]["files"] = []