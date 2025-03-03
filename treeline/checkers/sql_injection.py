from collections import defaultdict
from pathlib import Path
import ast
from typing import Dict

class SQLInjectionChecker:
    def __init__(self, config: Dict = None):
        self.config = config or {}

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Attribute) and 
                node.func.attr == "execute"):
                if any(isinstance(arg, ast.Constant) and isinstance(arg.value, str) for arg in node.args):
                    quality_issues["security"].append({
                        "description": "Potential SQL injection risk",
                        "file_path": str(file_path),
                        "line": node.lineno
                    })