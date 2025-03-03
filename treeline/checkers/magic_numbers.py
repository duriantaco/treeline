from collections import defaultdict
from pathlib import Path
import ast
from typing import Dict

class MagicNumberChecker:
    def __init__(self, config: Dict = None):
        self.config = config or {}

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value in [0, 1, -1]:
                    continue
                parent = self._get_parent(node, tree)
                if isinstance(parent, ast.Assign) and len(parent.targets) == 1 and isinstance(parent.targets[0], ast.Name):
                    continue
                quality_issues["code_smells"].append({
                    "description": "Magic number detected",
                    "file_path": str(file_path),
                    "line": node.lineno
                })

    def _get_parent(self, node, tree):
        """Find the parent node in the AST."""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    return parent
        return None