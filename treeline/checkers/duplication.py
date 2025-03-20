from collections import defaultdict
from pathlib import Path
from typing import Dict
from treeline.config_manager import get_config
from treeline.models.enhanced_analyzer import QualityIssue

class DuplicationDetector:
    def __init__(self, config: Dict = None):
        """Initialize the DuplicationDetector with a configuration."""
        self.config = config or get_config().as_dict()
        self.min_block_size = self.config.get("MIN_DUPLICATED_BLOCK_SIZE", 5)

    def analyze_directory(self, directory: Path, quality_issues: defaultdict):
        """Analyze a directory for duplicated code blocks."""
        all_lines = {}
        for file_path in directory.rglob("*.py"):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().split("\n")
            all_lines[str(file_path)] = lines

        block_locations = defaultdict(list)
        for file_path, lines in all_lines.items():
            for i in range(len(lines) - self.min_block_size + 1):
                block = tuple(lines[i:i + self.min_block_size])
                if any(line.strip() for line in block):  
                    block_locations[block].append((file_path, i + 1))

        for block, locations in block_locations.items():
            if len(locations) > 1:  
                for file_path, start_line in locations:
                    quality_issues["duplication"].append(QualityIssue(
                        description=f"Duplicated code block of {self.min_block_size} lines starting at line {start_line}",
                        file_path=file_path,
                        line=start_line
                    ).__dict__)