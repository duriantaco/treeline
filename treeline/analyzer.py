import ast
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Set, Tuple

from treeline.models.analyzer import CodeStructure, FunctionCall
from treeline.type_checker import ValidationError


class CodeAnalyzer:
    """Simple analyzer for extracting functions and classes from Python files."""

    COLORS = {
        "BLUE": "\033[94m",  # Functions
        "PURPLE": "\033[95m",  # Classes
        "GREEN": "\033[92m",  # Docstrings
        "YELLOW": "\033[93m",  # Parameters
        "CYAN": "\033[96m",  # Relationships
        "BOLD": "\033[1m",
        "END": "\033[0m",
    }

    def __init__(self, show_params=True, show_relationships=True):
        self.show_params = show_params
        self.show_relationships = show_relationships
        self.function_calls = defaultdict(set) if show_relationships else None

    def analyze_file(
        self, file_path: Path
    ) -> List[Tuple[str, str, str, Optional[str], Optional[str]]]:
        """Extracts functions and classes with optional params and relationships."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            structure = []

            for node in ast.walk(tree):
                try:
                    if isinstance(node, ast.FunctionDef):
                        name = node.name
                        doc = ast.get_docstring(node) or ""

                        params = (
                            self._get_function_params(node) if self.show_params else ""
                        )

                        relationship = ""
                        if self.show_relationships:
                            calls = self._find_function_calls(node)
                            if calls:
                                relationship = f"Calls: {', '.join(calls)}"

                        item = CodeStructure(
                            type="function",
                            name=name,
                            docstring=doc,
                            params=params,
                            relationship=relationship,
                        )

                        structure.append(
                            (
                                item.type,
                                item.name,
                                item.docstring,
                                item.params,
                                item.relationship,
                            )
                        )

                    elif isinstance(node, ast.ClassDef):
                        name = node.name
                        doc = ast.get_docstring(node) or ""

                        relationship = ""
                        if self.show_relationships:
                            bases = [
                                base.id
                                for base in node.bases
                                if isinstance(base, ast.Name)
                            ]
                            if bases:
                                relationship = f"Inherits: {', '.join(bases)}"

                        item = CodeStructure(
                            type="class",
                            name=name,
                            docstring=doc,
                            params="",
                            relationship=relationship,
                        )

                        structure.append(
                            (
                                item.type,
                                item.name,
                                item.docstring,
                                item.params,
                                item.relationship,
                            )
                        )

                except ValidationError as e:
                    print(f"Validation error for {name}: {e}")
                    continue

            return structure

        except Exception as e:
            error_item = CodeStructure(
                type="error",
                name=f"Could not parse file: {str(e)}",
                docstring="",
                params="",
                relationship="",
            )
            return [
                (
                    error_item.type,
                    error_item.name,
                    error_item.docstring,
                    error_item.params,
                    error_item.relationship,
                )
            ]

    def _get_function_params(self, node: ast.FunctionDef) -> str:
        """Extract function parameters with type hints."""
        params = []

        for arg in node.args.args:
            param = arg.arg
            if arg.annotation and hasattr(arg.annotation, "id"):
                param += f": {arg.annotation.id}"
            params.append(param)

        if node.args.vararg:
            params.append(f"*{node.args.vararg.arg}")

        if node.args.kwarg:
            params.append(f"**{node.args.kwarg.arg}")

        returns = ""
        if hasattr(node, "returns") and hasattr(node.returns, "id"):
            returns = f" -> {node.returns.id}"

        return f"({', '.join(params)}){returns}"

    def _find_function_calls(self, node: ast.AST) -> Set[str]:
        calls = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                try:
                    call = FunctionCall(caller=node.name, called=child.func.id)
                    calls.add(call.called)
                except ValidationError as e:
                    print(f"Invalid function call: {e}")
        return calls

    @staticmethod
    def get_symbol(item_type: str) -> str:
        """Maps item types to their display symbols."""
        symbols = {"function": "⚡", "class": "🏛️", "error": "⚠️"}
        return symbols.get(item_type, "•")

    def format_structure(
        self, structure: List[Tuple[str, str, str, str, str]], indent: str = ""
    ) -> List[str]:
        """Formats the code structure into displayable lines with colors and prefixes."""
        lines = []

        for item_type, name, doc, params, relationship in structure:
            if lines:
                lines.append(f"{indent}")

            symbol = self.get_symbol(item_type)

            if item_type == "class":
                prefix = (
                    f"{self.COLORS['PURPLE']}{self.COLORS['BOLD']}"
                    f"[CLASS]{self.COLORS['END']}"
                )
                name_colored = f"{self.COLORS['PURPLE']}{name}{self.COLORS['END']}"
            else:
                prefix = (
                    f"{self.COLORS['BLUE']}{self.COLORS['BOLD']}"
                    f"[FUNC]{self.COLORS['END']}"
                )
                name_colored = f"{self.COLORS['BLUE']}{name}{self.COLORS['END']}"

            if params:
                params_colored = f"{self.COLORS['YELLOW']}{params}{self.COLORS['END']}"
                line = f"{indent}{prefix} {symbol} {name_colored}{params_colored}"
                lines.append(line)
            else:
                lines.append(f"{indent}{prefix} {symbol} {name_colored}")

            if doc:
                doc_clean = " ".join(
                    line.strip() for line in doc.split("\n") if line.strip()
                )
                doc_line = (
                    f"{indent}  └─ {self.COLORS['GREEN']}"
                    f"# {doc_clean}{self.COLORS['END']}"
                )
                lines.append(doc_line)

            if relationship:
                rel_line = (
                    f"{indent}  └─ {self.COLORS['CYAN']}"
                    f"$ {relationship}{self.COLORS['END']}"
                )
                lines.append(rel_line)

        return lines
