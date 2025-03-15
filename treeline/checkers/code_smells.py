import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict
from treeline.config_manager import get_config

class CodeSmellChecker:
    def __init__(self, config: Dict = None):
        self.config = config or get_config().as_dict()
        self.max_params = self.config.get("MAX_PARAMS", 5)
        self.max_function_lines = self.config.get("MAX_FUNCTION_LINES", 50)
        self.max_nested_blocks = self.config.get("MAX_NESTED_BLOCKS", 3)
        self.max_return_statements = self.config.get("MAX_RETURNS", 4)

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        self._check_long_parameter_lists(tree, file_path, quality_issues)
        self._check_long_functions(tree, file_path, quality_issues)
        self._check_nested_blocks(tree, file_path, quality_issues)
        self._check_multiple_returns(tree, file_path, quality_issues)
        self._check_too_many_branches(tree, file_path, quality_issues)
        self._check_empty_except_blocks(tree, file_path, quality_issues)
        self._check_too_broad_except(tree, file_path, quality_issues)

    def _check_long_parameter_lists(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.args.args) > self.max_params:
                quality_issues["code_smells"].append({
                    "description": f"Function has too many parameters ({len(node.args.args)} > {self.max_params})",
                    "file_path": str(file_path),
                    "line": node.lineno,
                    "severity": "medium"
                })

    def _check_long_functions(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and hasattr(node, 'end_lineno'):
                function_lines = node.end_lineno - node.lineno
                if function_lines > self.max_function_lines:
                    quality_issues["code_smells"].append({
                        "description": f"Function is too long ({function_lines} > {self.max_function_lines} lines)",
                        "file_path": str(file_path),
                        "line": node.lineno,
                        "severity": "medium"
                    })

    def _check_nested_blocks(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                max_nesting = self._get_max_nesting(node)
                if max_nesting > self.max_nested_blocks:
                    quality_issues["code_smells"].append({
                        "description": f"Function has deeply nested blocks ({max_nesting} > {self.max_nested_blocks} levels)",
                        "file_path": str(file_path),
                        "line": node.lineno,
                        "severity": "medium"
                    })

    def _get_max_nesting(self, node, current_depth=0):
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.AsyncFor, ast.AsyncWith)):
                child_depth = self._get_max_nesting(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._get_max_nesting(child, current_depth)
                max_depth = max(max_depth, child_depth)
                
        return max_depth

    def _check_multiple_returns(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return_count = sum(1 for _ in ast.walk(node) if isinstance(_, ast.Return))
                if return_count > self.max_return_statements:
                    quality_issues["code_smells"].append({
                        "description": f"Function has too many return statements ({return_count} > {self.max_return_statements})",
                        "file_path": str(file_path),
                        "line": node.lineno,
                        "severity": "medium"
                    })

    def _check_too_many_branches(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if_count = sum(1 for _ in ast.walk(node) if isinstance(_, ast.If))
                if if_count > 4:
                    quality_issues["code_smells"].append({
                        "description": f"Function has too many branches ({if_count} if statements)",
                        "file_path": str(file_path),
                        "line": node.lineno,
                        "severity": "medium"
                    })

    def _check_empty_except_blocks(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                    quality_issues["code_smells"].append({
                        "description": "Empty except block",
                        "file_path": str(file_path),
                        "line": node.lineno,
                        "severity": "medium"
                    })

    def _check_too_broad_except(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    quality_issues["code_smells"].append({
                        "description": "Too broad exception handler (bare except:)",
                        "file_path": str(file_path),
                        "line": node.lineno,
                        "severity": "high"
                    })
                elif isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                    quality_issues["code_smells"].append({
                        "description": "Too broad exception handler (except Exception:)",
                        "file_path": str(file_path),
                        "line": node.lineno,
                        "severity": "medium"
                    })