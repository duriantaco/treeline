import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from treeline.models.security_analyzer import (
    SecurityIssue,
    SecurityPattern,
    SecurityPatterns,
)


class TreelineSecurity:
    def __init__(self):
        self.security_issues: Dict[str, List[SecurityIssue]] = defaultdict(list)
        self.imports: Dict[str, str] = {}
        self.tree: ast.AST = None

        self.RISKY_PATTERNS = SecurityPatterns(
            sql_injection=SecurityPattern(
                patterns={"execute", "executemany", "raw", "raw_query"},
                safe_patterns={"parameterize", "execute_params"},
            ),
            command_injection=SecurityPattern(
                patterns={"system", "popen", "run", "shell", "spawn", "call"},
                modules={"os", "subprocess", "commands"},
            ),
            deserialization=SecurityPattern(
                patterns={"loads", "load", "parse"},
                risky_modules={"pickle", "yaml", "marshal"},
                safe_modules={"json"},
            ),
            file_operations=SecurityPattern(
                patterns={
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
            ),
        )

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
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            print(f"Method call: {func_name}")

            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                orig_module = self.imports.get(module_name, module_name)
                print(f"Module: {module_name} -> {orig_module}")

                if (
                    orig_module in self.RISKY_PATTERNS.command_injection.modules
                    and func_name in self.RISKY_PATTERNS.command_injection.patterns
                ):
                    self._add_issue(
                        "command_injection",
                        f"Possible command injection in {orig_module}.{func_name}()",
                        filename,
                        node.lineno,
                    )

                if (
                    orig_module in {"os", "pathlib", "shutil"}
                    and func_name in self.RISKY_PATTERNS.file_operations.patterns
                ):
                    if any(isinstance(arg, ast.BinOp) for arg in node.args):
                        self._add_issue(
                            "file_operations",
                            f"Insecure file operation in {orig_module}.{func_name}()",
                            filename,
                            node.lineno,
                        )

                if (
                    orig_module in self.RISKY_PATTERNS.deserialization.risky_modules
                    and func_name in self.RISKY_PATTERNS.deserialization.patterns
                ):
                    self._add_issue(
                        "deserialization",
                        f"Unsafe deserialization using {orig_module}.{func_name}()",
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
            print("Checking SQL keywords")
            if any(
                keyword in str(node.left.value).lower()
                for keyword in sql_keywords
                if hasattr(node.left, "value")
            ):
                print("Found SQL keyword in left operand")
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
        issue = SecurityIssue(description=description, file=filename, line=line)
        self.security_issues[category].append(issue.__dict__)
