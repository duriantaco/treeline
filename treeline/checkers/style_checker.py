from collections import defaultdict
import re
from pathlib import Path
from typing import Dict
from treeline.config_manager import get_config

class StyleChecker:
    def __init__(self, config: Dict = None):
        self.config = config or get_config().as_dict()
        self.max_line_length = self.config.get("MAX_LINE_LENGTH", 100)
        self.max_file_lines = self.config.get("MAX_FILE_LINES", 500)
        self.max_function_length = self.config.get("MAX_FUNCTION_LINES", 50)
        
        self.exception_patterns = [
            r'^(\s*#|\s*"""|\s*\'\'\')',
            r'https?://',
            r'file://',
            r'(\s*import|\s*from)',
            r'^\s*return\s+\{',
            r'^\s*[\'"][^\'"]{40,}[\'"]',
            r'^\s*raise\s+\w+\([\'"]',
        ]
        self.exception_regexes = [re.compile(pattern) for pattern in self.exception_patterns]

    def check(self, file_path: Path, quality_issues: defaultdict):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            if len(lines) > self.max_file_lines:
                quality_issues["style"].append({
                    "description": f"File has {len(lines)} lines (over {self.max_file_lines})",
                    "file_path": str(file_path),
                    "line": None,
                    "severity": "low"
                })
            
            for i, line in enumerate(lines, start=1):
                stripped = line.rstrip()
                if len(stripped) > self.max_line_length and not self._is_exception(stripped):
                    quality_issues["style"].append({
                        "description": f"Line is too long ({len(stripped)} > {self.max_line_length} chars)",
                        "file_path": str(file_path),
                        "line": i,
                        "severity": "low"
                    })
            
            for i, line in enumerate(lines, start=1):
                if line.strip() == "":
                    continue
                if line.rstrip('\n').endswith((' ', '\t')):
                    quality_issues["style"].append({
                        "description": "Line has trailing whitespace",
                        "file_path": str(file_path),
                        "line": i,
                        "severity": "low"
                    })
            
            has_tabs = False
            has_spaces = False
            
            for line in lines:
                if line.startswith('\t'):
                    has_tabs = True
                elif line.startswith(' '):
                    has_spaces = True
                    
            if has_tabs and has_spaces:
                quality_issues["style"].append({
                    "description": "File mixes tabs and spaces for indentation",
                    "file_path": str(file_path),
                    "line": None,
                    "severity": "medium"
                })
                
            if lines and not lines[-1].endswith('\n'):
                quality_issues["style"].append({
                    "description": "File does not end with a newline",
                    "file_path": str(file_path),
                    "line": len(lines),
                    "severity": "low"
                })
                
            trailing_blank_count = 0
            for line in reversed(lines):
                if line.strip() == '':
                    trailing_blank_count += 1
                else:
                    break
                    
            if trailing_blank_count > 1:
                quality_issues["style"].append({
                    "description": f"File has {trailing_blank_count} blank lines at the end",
                    "file_path": str(file_path),
                    "line": len(lines),
                    "severity": "low"
                })
                
        except Exception as e:
            quality_issues["style"].append({
                "description": f"Error checking file style: {str(e)}",
                "file_path": str(file_path),
                "line": None,
                "severity": "low"
            })
            
    def _is_exception(self, line: str) -> bool:
        return any(regex.search(line) for regex in self.exception_regexes)