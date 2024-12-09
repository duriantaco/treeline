import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from treeline.models.enhanced_analyzer import (
    ClassMetrics,
    FunctionMetrics,
    QualityIssue,
)


class EnhancedCodeAnalyzer:
    """
    Enhanced analyzer for code quality and maintainability metrics.

    This analyzer implements industry-standard code quality checks and metrics
    following Clean Code principles, SOLID principles, and PEP 8 standards.
    """

    QUALITY_METRICS = {
        "MAX_LINE_LENGTH": 150,
        "MAX_DOC_LENGTH": 72,
        "MAX_CYCLOMATIC_COMPLEXITY": 10,
        "MAX_COGNITIVE_COMPLEXITY": 15,
        "MAX_NESTED_DEPTH": 4,
        "MAX_FUNCTION_LINES": 50,
        "MAX_PARAMS": 5,
        "MAX_RETURNS": 3,
        "MAX_ARGUMENTS_PER_LINE": 2,
        "MIN_MAINTAINABILITY_INDEX": 20,
        "MAX_FUNC_COGNITIVE_LOAD": 7,
        "MIN_PUBLIC_METHODS": 1,
        "MAX_IMPORT_STATEMENTS": 15,
        "MAX_MODULE_DEPENDENCIES": 10,
        "MAX_INHERITANCE_DEPTH": 3,
        "MAX_DUPLICATED_LINES": 5,
        "MAX_DUPLICATED_BLOCKS": 3,
        "MAX_CLASS_LINES": 200,
        "MAX_METHODS_PER_CLASS": 10,
        "MAX_CLASS_COMPLEXITY": 50,
    }

    def __init__(self, show_params: bool = True):
        """
        Initialize the code analyzer.

        Args:
            show_params: Whether to show function parameters in analysis
        """
        self.show_params = show_params
        self.quality_issues = defaultdict(list)
        self.metrics_summary = defaultdict(dict)

    def analyze_file(self, file_path: Path) -> List[Dict]:
        """
        Analyze a Python file for code quality metrics.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            List of analysis results for each code element
        """
        content = self._read_file(file_path)
        if not content:
            return []

        tree = self._parse_content(content)
        if not tree:
            return []

        self._analyze_file_metrics(content, file_path)
        return self._analyze_code_elements(tree, content)

    def _calculate_maintainability_index(self, node: ast.AST, content: str) -> float:
        """
        Calculate Maintainability Index (MI) following Microsoft's formula.

        MI = max(0, (171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
        where:
        - HV = Halstead Volume
        - CC = Cyclomatic Complexity
        - LOC = Lines of Code
        """
        import math

        loc = node.end_lineno - node.lineno + 1
        cc = self._calculate_cyclomatic_complexity(node)

        operators = len(
            [
                n
                for n in ast.walk(node)
                if isinstance(n, (ast.operator, ast.BoolOp, ast.Compare))
            ]
        )
        operands = len(
            [n for n in ast.walk(node) if isinstance(n, (ast.Name, ast.Num, ast.Str))]
        )
        hv = (
            (operators + operands) * math.log(len(set([operators, operands])), 2)
            if operators + operands > 0
            else 1
        )

        mi = 171 - 5.2 * math.log(hv) - 0.23 * cc - 16.2 * math.log(loc)
        return max(0, (mi * 100 / 171))

    def _calculate_cognitive_load(self, node: ast.FunctionDef) -> int:
        """
        Counts control structures and parameters as cognitive items.
        """
        control_structures = sum(
            1
            for n in ast.walk(node)
            if isinstance(n, (ast.If, ast.While, ast.For, ast.Try))
        )
        parameters = len(node.args.args)
        return control_structures + parameters

    def _check_function_metrics(self, func_data: Dict) -> None:
        """Check function metrics against quality thresholds."""
        metrics = func_data["metrics"]
        smells = func_data["code_smells"]

        if metrics["lines"] > self.QUALITY_METRICS["MAX_FUNCTION_LINES"]:
            smells.append(
                f"Function exceeds {self.QUALITY_METRICS['MAX_FUNCTION_LINES']} lines"
            )

        if metrics["params"] > self.QUALITY_METRICS["MAX_PARAMS"]:
            smells.append(
                f"Too many parameters (> {self.QUALITY_METRICS['MAX_PARAMS']})"
            )

        if metrics["complexity"] > self.QUALITY_METRICS["MAX_CYCLOMATIC_COMPLEXITY"]:
            smells.append(
                f"High cyclomatic complexity(> {self.QUALITY_METRICS['MAX_CYCLOMATIC_COMPLEXITY']})"
            )

        if (
            metrics["cognitive_complexity"]
            > self.QUALITY_METRICS["MAX_COGNITIVE_COMPLEXITY"]
        ):
            smells.append(
                f"High cognitive complexity (> {self.QUALITY_METRICS['MAX_COGNITIVE_COMPLEXITY']})"
            )

        if metrics["nested_depth"] > self.QUALITY_METRICS["MAX_NESTED_DEPTH"]:
            smells.append(
                f"Excessive nesting depth (> {self.QUALITY_METRICS['MAX_NESTED_DEPTH']})"
            )

        if (
            metrics.get("maintainability_index", 0)
            < self.QUALITY_METRICS["MIN_MAINTAINABILITY_INDEX"]
        ):
            smells.append(
                f"Low maintainability index (< {self.QUALITY_METRICS['MIN_MAINTAINABILITY_INDEX']})"
            )

        if (
            metrics.get("cognitive_load", 0)
            > self.QUALITY_METRICS["MAX_FUNC_COGNITIVE_LOAD"]
        ):
            smells.append(
                f"High cognitive load (> {self.QUALITY_METRICS['MAX_FUNC_COGNITIVE_LOAD']} items)"
            )

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate McCabe's cyclomatic complexity.

        Based on McCabe, 1976 and implementation in Radon/SonarQube.
        """
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_cognitive_complexity(self, node: ast.AST) -> int:
        """
        Calculate cognitive complexity based on SonarQube's metric.

        Implements SonarSource's cognitive complexity calculation.
        """

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

    def _analyze_file_metrics(self, content: str, file_path: Path) -> None:
        """
        Analyze file-level metrics including style, duplication, imports, and documentation.

        Args:
            content: File content as string
            file_path: Path to the file being analyzed
        """
        lines = content.split("\n")
        tree = self._parse_content(content)
        if not tree:
            return

        for i, line in enumerate(lines, 1):
            stripped_line = line.rstrip()
            if len(stripped_line) > self.QUALITY_METRICS["MAX_LINE_LENGTH"]:
                self._add_issue(
                    "style",
                    f"Line {i} exceeds PEP 8 maximum length of {self.QUALITY_METRICS['MAX_LINE_LENGTH']} characters",
                    str(file_path),
                    i,
                )

            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                if len(stripped_line) > self.QUALITY_METRICS["MAX_DOC_LENGTH"]:
                    self._add_issue(
                        "style",
                        f"Docstring line {i} exceeds maximum length of {self.QUALITY_METRICS['MAX_DOC_LENGTH']} characters",
                        str(file_path),
                        i,
                    )

        duplication = self._analyze_code_duplication(content)
        if (
            duplication["duplicated_blocks"]
            > self.QUALITY_METRICS["MAX_DUPLICATED_BLOCKS"]
        ):
            self._add_issue(
                "duplication",
                f"Too many duplicated blocks ({duplication['duplicated_blocks']} found)",
                str(file_path),
            )

        imports = self._analyze_imports(tree)
        if imports["import_count"] > self.QUALITY_METRICS["MAX_IMPORT_STATEMENTS"]:
            self._add_issue(
                "imports",
                f"Too many import statements ({imports['import_count']})",
                str(file_path),
            )
        if imports["dependencies"] > self.QUALITY_METRICS["MAX_MODULE_DEPENDENCIES"]:
            self._add_issue(
                "dependencies",
                f"Too many module dependencies ({imports['dependencies']})",
                str(file_path),
            )

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if len(node.args) > self.QUALITY_METRICS["MAX_ARGUMENTS_PER_LINE"]:
                    self._add_issue(
                        "style",
                        f"Too many arguments in single line call ({len(node.args)})",
                        str(file_path),
                        node.lineno,
                    )

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read and return file content safely."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self._add_issue("file", f"Could not read file: {str(e)}")
            return None

    def _parse_content(self, content: str) -> Optional[ast.AST]:
        """Parse Python content into AST safely."""
        try:
            return ast.parse(content)
        except Exception as e:
            self._add_issue("parsing", f"Could not parse content: {str(e)}")
            return None

    def _analyze_code_elements(self, tree: ast.AST, content: str) -> List[Dict]:
        """Analyze individual code elements in the AST."""
        results = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                results.append(self._analyze_function(node, content))
            elif isinstance(node, ast.ClassDef):
                results.append(self._analyze_class(node, content))

        return results

    def _analyze_class(self, node: ast.ClassDef, content: str) -> Dict:
        """Analyze a class's quality metrics."""
        metrics = {
            "type": "class",
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "metrics": self._calculate_class_metrics(node, content),
            "code_smells": [],
        }

        self._check_class_metrics(metrics)
        return metrics

    def _check_class_metrics(self, class_data: Dict) -> None:
        """Check class metrics against quality thresholds."""
        metrics = class_data["metrics"]
        smells = class_data["code_smells"]

        if metrics["lines"] > self.QUALITY_METRICS["MAX_CLASS_LINES"]:
            smells.append("Class too long")

        if metrics["method_count"] > self.QUALITY_METRICS["MAX_METHODS_PER_CLASS"]:
            smells.append("Too many methods")

        if metrics["complexity"] > self.QUALITY_METRICS["MAX_CLASS_COMPLEXITY"]:
            smells.append("High class complexity")

        if not metrics["has_docstring"]:
            smells.append("Missing class docstring")

        if (
            metrics.get("public_methods", 0)
            < self.QUALITY_METRICS["MIN_PUBLIC_METHODS"]
        ):
            smells.append(
                f"Too few public method (< {self.QUALITY_METRICS['MIN_PUBLIC_METHODS']}, SOLID-ISP)"
            )

        if (
            metrics.get("inheritance_depth", 0)
            > self.QUALITY_METRICS["MAX_INHERITANCE_DEPTH"]
        ):
            smells.append(
                f"Deep inheritance (> {self.QUALITY_METRICS['MAX_INHERITANCE_DEPTH']} levels)"
            )

        imports = metrics.get("imports", {})
        if (
            imports.get("import_count", 0)
            > self.QUALITY_METRICS["MAX_IMPORT_STATEMENTS"]
        ):
            smells.append(
                f"Too many imports (> {self.QUALITY_METRICS['MAX_IMPORT_STATEMENTS']})"
            )

        if (
            imports.get("dependencies", 0)
            > self.QUALITY_METRICS["MAX_MODULE_DEPENDENCIES"]
        ):
            smells.append(
                f"Too many dependencies (> {self.QUALITY_METRICS['MAX_MODULE_DEPENDENCIES']})"
            )

    def format_structure(self, structure: List[Dict], indent: str = "") -> List[str]:
        """Format the analysis results into a tree structure."""
        if not structure:
            return []

        lines = []
        for item in structure:
            if not isinstance(item, dict):
                continue

            item_type = item.get("type", "")
            name = item.get("name", "")
            docstring = item.get("docstring", "")
            metrics = item.get("metrics", {})
            code_smells = item.get("code_smells", [])

            if item_type == "class":
                lines.append(f"{indent}[CLASS] 🏛️ {name}")
            elif item_type == "function":
                lines.append(f"{indent}[FUNC] ⚡ {name}")
            elif item_type == "error":
                lines.append(f"{indent}⚠️ {name}")
                continue

            child_indent = indent + "  "
            if docstring:
                doc_lines = docstring.split("\n")
                lines.append(f"{child_indent}└─ # {doc_lines[0]}")
                for doc_line in doc_lines[1:]:
                    if doc_line.strip():
                        lines.append(f"{child_indent}   {doc_line.strip()}")

            if metrics:
                if (
                    metrics.get("complexity", 0)
                    > self.QUALITY_METRICS["MAX_CYCLOMATIC_COMPLEXITY"]
                ):
                    lines.append(
                        f"{child_indent}└─ ⚠️ High complexity ({metrics['complexity']})"
                    )
                if metrics.get("lines", 0) > self.QUALITY_METRICS["MAX_FUNCTION_LINES"]:
                    lines.append(
                        f"{child_indent}└─ ⚠️ Too long ({metrics['lines']} lines)"
                    )
                if (
                    metrics.get("nested_depth", 0)
                    > self.QUALITY_METRICS["MAX_NESTED_DEPTH"]
                ):
                    lines.append(
                        f"{child_indent}└─ ⚠️ Deep nesting (depth {metrics['nested_depth']})"
                    )

            for smell in code_smells:
                lines.append(f"{child_indent}└─ ⚠️ {smell}")

        return lines

    def _format_metrics_section(self) -> str:
        """Format the metrics section of the report."""
        if not self.metrics_summary:
            return "No metrics collected."

        lines = ["## Metrics Summary"]

        for category, items in self.metrics_summary.items():
            lines.append(f"\n### {category.title()}")
            for item, metrics in items.items():
                lines.append(f"\n#### {item}")
                for metric, value in metrics.items():
                    if isinstance(value, float):
                        lines.append(f"- {metric}: {value:.2%}")
                    else:
                        lines.append(f"- {metric}: {value}")

        return "\n".join(lines)

    def _analyze_function(self, node: ast.FunctionDef, content: str) -> Dict:
        """Analyze a function's quality metrics."""
        metrics = {
            "type": "function",
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "metrics": self._calculate_function_metrics(node, content),
            "code_smells": [],
        }

        self._check_function_metrics(metrics)
        return metrics

    def _calculate_class_metrics(self, node: ast.ClassDef, content: str) -> Dict:
        methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
        inheritance = self._analyze_inheritance(node)

        metrics = ClassMetrics(
            lines=node.end_lineno - node.lineno + 1,
            method_count=len(methods),
            complexity=sum(self._calculate_cyclomatic_complexity(m) for m in methods),
            has_docstring=bool(ast.get_docstring(node)),
            public_methods=len([m for m in methods if not m.name.startswith("_")]),
            private_methods=len([m for m in methods if m.name.startswith("_")]),
            inheritance_depth=inheritance["inheritance_depth"],
            imports=self._analyze_imports(node),
            docstring_length=len(ast.get_docstring(node) or ""),
        )
        return metrics.__dict__

    def _calculate_function_metrics(self, node: ast.FunctionDef, content: str) -> Dict:
        metrics = FunctionMetrics(
            lines=node.end_lineno - node.lineno + 1,
            params=len(node.args.args),
            returns=len([n for n in ast.walk(node) if isinstance(n, ast.Return)]),
            complexity=self._calculate_cyclomatic_complexity(node),
            cognitive_complexity=self._calculate_cognitive_complexity(node),
            nested_depth=self._calculate_nested_depth(node),
            has_docstring=bool(ast.get_docstring(node)),
            maintainability_index=self._calculate_maintainability_index(node, content),
            cognitive_load=self._calculate_cognitive_load(node),
            docstring_length=len(ast.get_docstring(node) or ""),
        )
        return metrics.__dict__

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of code."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_nested_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth in code."""

        def get_depth(node: ast.AST, current: int = 0) -> int:
            max_depth = current
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                    child_depth = get_depth(child, current + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    max_depth = max(max_depth, get_depth(child, current))
            return max_depth

        return get_depth(node)

    def _analyze_code_duplication(self, content: str) -> Dict[str, int]:
        """Analyze code for duplication using line-based comparison."""
        lines = content.split("\n")
        duplicated_blocks = []
        duplicated_lines = set()

        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                consecutive_matches = 0
                while (
                    i + consecutive_matches < len(lines)
                    and j + consecutive_matches < len(lines)
                    and lines[i + consecutive_matches].strip()
                    == lines[j + consecutive_matches].strip()
                ):
                    consecutive_matches += 1

                if consecutive_matches >= self.QUALITY_METRICS["MAX_DUPLICATED_LINES"]:
                    duplicated_blocks.append((i, j, consecutive_matches))
                    duplicated_lines.update(range(i, i + consecutive_matches))
                    duplicated_lines.update(range(j, j + consecutive_matches))

        return {
            "duplicated_blocks": len(duplicated_blocks),
            "duplicated_lines": len(duplicated_lines),
        }

    def _analyze_imports(self, tree: ast.AST) -> Dict[str, int]:
        """Analyze import statements and module dependencies."""
        import_count = 0
        dependencies = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_count += 1
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name.split(".")[0])
                else:
                    if node.module:
                        dependencies.add(node.module.split(".")[0])

        return {"import_count": import_count, "dependencies": len(dependencies)}

    def _analyze_inheritance(self, node: ast.ClassDef) -> Dict[str, int]:
        """Analyze class inheritance depth and hierarchy."""

        def get_inheritance_depth(cls_node: ast.ClassDef) -> int:
            max_depth = 0
            for base in cls_node.bases:
                if isinstance(base, ast.Name):
                    max_depth = max(max_depth, 1)
            return max_depth + 1

        depth = get_inheritance_depth(node)
        return {"inheritance_depth": depth}

    def _add_issue(
        self, category: str, description: str, file_path: str = None, line: int = None
    ) -> None:
        """
        Add a quality issue to the collection.

        Args:
            category: The category of the issue
            description: Description of the issue
            file_path: Optional path to the file where the issue was found
            line: Optional line number where the issue was found
        """
        issue = QualityIssue(description=description, file_path=file_path, line=line)
        self.quality_issues[category].append(issue.__dict__)

    def generate_report(self) -> str:
        """Generate a formatted quality report."""
        return self._format_report_sections(
            [
                self._format_overview_section(),
                self._format_issues_section(),
                self._format_metrics_section(),
            ]
        )

    def _format_report_sections(self, sections: List[str]) -> str:
        """Format and combine report sections."""
        return "\n\n".join(section for section in sections if section)

    def _format_overview_section(self) -> str:
        """Format the report overview section."""
        return (
            "# Code Quality Analysis Report\n\n"
            + "Analysis completed with the following results:"
        )

    def _format_issues_section(self) -> str:
        """Format the quality issues section."""
        if not self.quality_issues:
            return "No quality issues found."

        lines = ["## Quality Issues"]
        for category, issues in self.quality_issues.items():
            lines.append(f"\n### {category.title()}")
            for issue in issues:
                lines.append(f"- {issue['description']}")
                if issue.get("line"):
                    lines.append(f"  Line: {issue['line']}")
        return "\n".join(lines)
