import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from treeline.models.enhanced_analyzer import QualityIssue

class ComplexityAnalyzer:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_cyclomatic = self.config.get("MAX_CYCLOMATIC_COMPLEXITY", 10)
        self.max_cognitive = self.config.get("MAX_COGNITIVE_COMPLEXITY", 15)

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                cc = self._calculate_cyclomatic_complexity(node)
                cog = self._calculate_cognitive_complexity(node)
                if cc > self.max_cyclomatic:
                    quality_issues["complexity"].append(QualityIssue(
                        description=f"High cyclomatic complexity ({cc} > {self.max_cyclomatic})",
                        file_path=str(file_path),
                        line=node.lineno
                    ).__dict__)
                if cog > self.max_cognitive:
                    quality_issues["complexity"].append(QualityIssue(
                        description=f"High cognitive complexity ({cog} > {self.max_cognitive})",
                        file_path=str(file_path),
                        line=node.lineno
                    ).__dict__)

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_cognitive_complexity(self, node: ast.AST) -> int:
        def walk_cognitive(node: ast.AST, nesting: int = 0) -> int:
            complexity = 0
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For)):
                    complexity += 1 + nesting
                    complexity += walk_cognitive(child, nesting + 1)
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1
                else:
                    complexity += walk_cognitive(child, nesting)
            return complexity
        return walk_cognitive(node)