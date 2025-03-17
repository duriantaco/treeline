import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict

from treeline.config_manager import get_config

class UnusedCodeChecker:
    def __init__(self, config: Dict = None):
        self.config = config or get_config().as_dict()
        self.imported_names = defaultdict(set)
        self.used_names = defaultdict(set)
        self.defined_functions = {}
        self.called_functions = set()
        self.globally_used_imports = set()

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        """Check for unused imports and functions in a single file"""
        str_path = str(file_path)
        
        self._collect_imports_and_functions(tree, str_path)
        self._check_name_usage(tree, str_path)
        self._report_unused_imports(str_path, quality_issues)

    def finalize_checks(self, quality_issues: defaultdict):
        self._report_unused_functions(quality_issues)

    def _collect_imports_and_functions(self, tree: ast.AST, file_path: str):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
            if isinstance(node, ast.Import):
                for name in node.names:
                    alias = name.asname or name.name
                    self.imported_names[file_path].add(alias)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for name in node.names:
                        alias = name.asname or name.name
                        self.imported_names[file_path].add(alias)
            elif isinstance(node, ast.FunctionDef):
                module_name = Path(file_path).stem
                parent = getattr(node, "parent", None)
                if isinstance(parent, ast.ClassDef):
                    class_name = parent.name
                    func_name = f"{module_name}.{class_name}.{node.name}"
                else:
                    func_name = f"{module_name}.{node.name}"
                self.defined_functions[func_name] = {
                    "file_path": file_path,
                    "line": node.lineno,
                    "name": node.name
                }

    def _check_name_usage(self, tree: ast.AST, file_path: str):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                self.used_names[file_path].add(node.id)
                self.globally_used_imports.add(node.id)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    module_name = Path(file_path).stem
                    self.called_functions.add(f"{module_name}.{func_name}")
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'self':
                            parent = node
                            while parent and not isinstance(parent, ast.ClassDef):
                                parent = getattr(parent, "parent", None)
                            if parent and isinstance(parent, ast.ClassDef):
                                module_name = Path(file_path).stem
                                class_name = parent.name
                                method_name = node.func.attr
                                self.called_functions.add(f"{module_name}.{class_name}.{method_name}")
                        else:
                            self.used_names[file_path].add(node.func.value.id)
                            self.globally_used_imports.add(node.func.value.id)

    def _report_unused_imports(self, file_path: str, quality_issues: defaultdict):
        imported = self.imported_names.get(file_path, set())
        used = self.used_names.get(file_path, set())
        
        unused_imports = imported - used
        
        for name in unused_imports:
            quality_issues["unused_code"].append({
                "description": f"Unused import: {name}",
                "file_path": file_path,
                "line": self._find_import_line(file_path, name),
                "severity": "low"
            })

    def _report_unused_functions(self, quality_issues: defaultdict):
        special_patterns = {"__init__", "main", "test_", "setup", "teardown"}
        
        for func_name, info in self.defined_functions.items():
            if any(pattern in func_name.split(".")[-1] for pattern in special_patterns):
                continue
                
            if func_name not in self.called_functions:
                quality_issues["unused_code"].append({
                    "description": f"Unused function: {info['name']}",
                    "file_path": info["file_path"],
                    "line": info["line"],
                    "severity": "medium"
                })

    def _find_import_line(self, file_path: str, name: str) -> int:
        """Find the line number where a name is imported"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                if f"import {name}" in line or f"as {name}" in line:
                    return i
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except PermissionError:
            print(f"Permission denied when reading: {file_path}")
        except UnicodeDecodeError:
            print(f"Unicode decode error when reading: {file_path}")
        except IOError as e:
            print(f"IO error when reading {file_path}: {str(e)}")
            
        return 1   