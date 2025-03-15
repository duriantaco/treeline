import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict

from treeline.models.enhanced_analyzer import QualityIssue
from treeline.utils.metrics import calculate_cyclomatic_complexity, calculate_cognitive_complexity
from treeline.config_manager import get_config

class ComplexityAnalyzer:
    def __init__(self, config: Dict = None):
        self.config = config or get_config().as_dict()
        self.max_cyclomatic = self.config.get("MAX_CYCLOMATIC_COMPLEXITY", 10)
        self.max_cognitive = self.config.get("MAX_COGNITIVE_COMPLEXITY", 15)

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                cc = self._calculate_cyclomatic_complexity(node)
                cog = self._calculate_cognitive_complexity(node)
                element_type = "function" if isinstance(node, ast.FunctionDef) else "class"
                if cc > self.max_cyclomatic:
                    quality_issues["complexity"].append(QualityIssue(
                        description=f"High cyclomatic complexity ({cc} > {self.max_cyclomatic}) in {element_type} '{node.name}'",
                        file_path=str(file_path),
                        line=node.lineno
                    ).__dict__)
                if cog > self.max_cognitive:
                    quality_issues["complexity"].append(QualityIssue(
                        description=f"High cognitive complexity ({cog} > {self.max_cognitive}) in {element_type} '{node.name}'",
                        file_path=str(file_path),
                        line=node.lineno
                    ).__dict__)

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        return calculate_cyclomatic_complexity(node)

    def _calculate_cognitive_complexity(self, node: ast.AST) -> int:
        return calculate_cognitive_complexity(node)