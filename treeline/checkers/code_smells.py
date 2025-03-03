import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict

from treeline.models.enhanced_analyzer import QualityIssue

class CodeSmellChecker:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_params = self.config.get("MAX_PARAMS", 5)

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        self._check_magic_numbers(tree, file_path, quality_issues)
        self._check_long_parameter_lists(tree, file_path, quality_issues)

    def _check_magic_numbers(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                quality_issues["code_smells"].append(QualityIssue(
                    description="Magic number detected",
                    file_path=str(file_path),
                    line=node.lineno
                ).__dict__)

    def _check_long_parameter_lists(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.args.args) > self.max_params:
                quality_issues["code_smells"].append(QualityIssue(
                    description=f"Function has too many parameters (>{self.max_params})",
                    file_path=str(file_path),
                    line=node.lineno
                ).__dict__)