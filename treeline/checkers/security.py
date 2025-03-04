import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict

from treeline.models.enhanced_analyzer import QualityIssue

class SecurityAnalyzer:
    def __init__(self, config: Dict = None):
        self.config = config or {}

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        self._check_hardcoded_credentials(tree, file_path, quality_issues)

    def _check_hardcoded_credentials(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and any(kw in node.value.lower() for kw in ["password", "key", "secret"]):
                quality_issues["security"].append(QualityIssue(
                    description="Possible hardcoded credential",
                    file_path=str(file_path),
                    line=node.lineno
                ).__dict__)