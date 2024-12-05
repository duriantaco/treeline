import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


class TreelineSecurity:
    def __init__(self):
        self.security_issues = defaultdict(list)
        self.imports = {}
        self.tree = None

        self.RISKY_PATTERNS = {
            "sql_injection": {
                "patterns": {"execute", "executemany", "raw", "raw_query"},
                "safe_patterns": {"parameterize", "execute_params"},
            },
            "command_injection": {
                "patterns": {"system", "popen", "run", "shell", "spawn", "call"},
                "modules": {"os", "subprocess", "commands"},
            },
            "deserialization": {
                "patterns": {"loads", "load", "parse"},
                "risky_modules": {"pickle", "yaml", "marshal"},
                "safe_modules": {"json"},
            },
            "file_operations": {
                "patterns": {
                    "open",
                    "read",
                    "write",
                    "save",
                    "load",
                    "exec",
                    "eval",
                    "remove",
                    "unlink",
                }
            },
        }

    def analyze_file(self, file_path: Path) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.tree = ast.parse(content)
            self._collect_imports(self.tree)
            self._scan_security_issues(self.tree, str(file_path))
        except Exception as e:
            self.security_issues["errors"].append(
                {
                    "description": f"Security scan failed: {str(e)}",
                    "file": str(file_path),
                    "line": 0,
                }
            )

    def _collect_imports(self, tree: ast.AST) -> None:
        self.imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    self.imports[alias.asname or alias.name] = full_name

    def _scan_security_issues(self, tree: ast.AST, filename: str) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._check_all_dangerous_calls(node, filename)
            elif isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.Add):
                    self._check_string_concat(node, filename)
            elif isinstance(node, ast.Assign):
                self._check_hardcoded_secrets(node, filename)

    def _check_all_dangerous_calls(self, node: ast.Call, filename: str) -> None:
        """
        Check for dangerous function calls that may lead to security vulnerabilities.
        """

        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            if func_name in self.RISKY_PATTERNS["command_injection"]["patterns"]:
                print(f"Found command injection pattern: {func_name}")
                self._add_issue(
                    "command_injection",
                    f"Possible command injection using {func_name}()",
                    filename,
                    node.lineno,
                )

        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            print(f"Method call: {func_name}")

            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                orig_module = self.imports.get(module_name, module_name)
                print(f"Module: {module_name} -> {orig_module}")

                if func_name in self.RISKY_PATTERNS["sql_injection"]["patterns"]:
                    print(f"Checking SQL injection for {func_name}")
                    print(f"Args: {[ast.dump(arg) for arg in node.args]}")
                    if any(
                        isinstance(arg, (ast.BinOp, ast.JoinedStr)) for arg in node.args
                    ):
                        self._add_issue(
                            "sql_injection",
                            f"Possible SQL injection in {func_name}()",
                            filename,
                            node.lineno,
                        )

                if orig_module in self.RISKY_PATTERNS["command_injection"]["modules"]:
                    print(f"Found command injection module: {orig_module}")
                    if (
                        func_name
                        in self.RISKY_PATTERNS["command_injection"]["patterns"]
                    ):
                        print(f"Found command injection function: {func_name}")
                        self._add_issue(
                            "command_injection",
                            f"Possible command injection in {orig_module}.{func_name}()",
                            filename,
                            node.lineno,
                        )

                if (
                    orig_module
                    in self.RISKY_PATTERNS["deserialization"]["risky_modules"]
                ):
                    print(f"Found risky deserialization module: {orig_module}")
                    if func_name in self.RISKY_PATTERNS["deserialization"]["patterns"]:
                        print(f"Found risky deserialization function: {func_name}")
                        self._add_issue(
                            "deserialization",
                            f"Unsafe deserialization using {orig_module}.{func_name}()",
                            filename,
                            node.lineno,
                        )

                if func_name in self.RISKY_PATTERNS["file_operations"]["patterns"]:
                    print(f"Checking file operation for {func_name}")
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp):
                            print(
                                f"Found string concatenation in argument of {func_name}"
                            )
                            self._add_issue(
                                "file_operations",
                                f"Insecure file operation in {orig_module}.{func_name}()",
                                filename,
                                node.lineno,
                            )

    def _check_string_concat(self, node: ast.BinOp, filename: str) -> None:
        """
        Check for string concatenation with SQL-like commands.
        """

        if isinstance(node.left, ast.Constant):
            print(f"Left operand: {node.left.value}")
        if isinstance(node.right, ast.Constant):
            print(f"Right operand: {node.right.value}")

        if (
            isinstance(node.left, ast.Constant) and isinstance(node.left.value, str)
        ) or (
            isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)
        ):
            sql_keywords = ["select", "insert", "update", "delete", "exec", "eval"]
            print(f"Checking SQL keywords")
            if any(
                keyword in str(node.left.value).lower()
                for keyword in sql_keywords
                if hasattr(node.left, "value")
            ):
                print(f"Found SQL keyword in left operand")
                self._add_issue(
                    "sql_injection",
                    "String concatenation with SQL-like commands detected",
                    filename,
                    node.lineno,
                )

    def _check_hardcoded_secrets(self, node: ast.Assign, filename: str) -> None:
        print(f"\nChecking hardcoded secrets: {ast.dump(node, indent=2)}")

        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                print(f"Checking variable name: {name}")
                if any(
                    word in name
                    for word in ["password", "secret", "key", "token", "api"]
                ):
                    print(f"Found secret-like name: {name}")
                    if isinstance(node.value, ast.Constant):
                        print(f"Found hardcoded value: {node.value.value}")
                        self._add_issue(
                            "hardcoded_secret",
                            f"Hardcoded secret found in variable '{target.id}'",
                            filename,
                            node.lineno,
                        )

    def _add_issue(
        self, category: str, description: str, filename: str, line: int
    ) -> None:
        self.security_issues[category].append(
            {"description": description, "file": filename, "line": line}
        )
