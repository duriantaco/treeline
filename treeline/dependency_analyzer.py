import ast
import re
from collections import defaultdict
from pathlib import Path

from treeline.ignore import read_ignore_patterns, should_ignore
from treeline.models.dependency_analyzer import (
    ComplexFunction,
    FunctionCallInfo,
    FunctionLocation,
    MethodInfo,
    ModuleMetrics,
)
from treeline.visualizers.mermaid import MermaidVisualizer


class ModuleDependencyAnalyzer:
    """Analyzes module-level dependencies and generates summary reports."""

    def __init__(self):
        self.module_imports = defaultdict(set)
        self.module_metrics = defaultdict(dict)
        self.complex_functions = []
        self.function_locations = defaultdict(dict)
        self.function_calls = defaultdict(list)
        self.class_info = defaultdict(dict)
        self.call_graph = defaultdict(
            lambda: {
                "callers": defaultdict(int),
                "callees": defaultdict(int),
                "module": "",
                "total_calls": 0,
                "entry_point": False,
                "terminal": False,
                "recursive": False,
                "call_depth": 0,
            }
        )

        self.QUALITY_METRICS = {
            "MAX_LINE_LENGTH": 100,
            "MAX_DOC_LENGTH": 80,
            "MAX_CYCLOMATIC_COMPLEXITY": 10,
            "MAX_COGNITIVE_COMPLEXITY": 15,
            "MAX_NESTED_DEPTH": 4,
            "MAX_FUNCTION_LINES": 50,
            "MAX_PARAMS": 5,
            "MAX_RETURNS": 4,
            "MAX_ARGUMENTS_PER_LINE": 5,
            "MIN_MAINTAINABILITY_INDEX": 20,
            "MAX_FUNC_COGNITIVE_LOAD": 15,
            "MIN_PUBLIC_METHODS": 1,
            "MAX_IMPORT_STATEMENTS": 15,
            "MAX_MODULE_DEPENDENCIES": 10,
            "MAX_INHERITANCE_DEPTH": 3,
            "MAX_DUPLICATED_LINES": 6,
            "MAX_DUPLICATED_BLOCKS": 2,
            "MAX_CLASS_LINES": 300,
            "MAX_METHODS_PER_CLASS": 20,
            "MAX_CLASS_COMPLEXITY": 50,
        }

        self.entry_patterns = {
            "fastapi_route": r"@(?:app|router)\.(?:get|post|put|delete|patch)",
            "cli_command": r"@click\.command|@app\.command|def main\(",
            "django_view": r"class \w+View\(|@api_view",
            "test_file": r"test_.*\.py$|.*_test\.py$",
            "main_guard": r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:',
        }

    def analyze_directory(self, directory: Path):
        """Analyze all Python files in directory."""
        ignore_patterns = read_ignore_patterns()

        def should_skip_module(module_path: str) -> bool:
            """Check if a module path should be skipped."""
            if any(
                indicator in module_path
                for indicator in ["site-packages", "venv", ".venv"]
            ):
                return True
            return False

        for file_path in directory.rglob("*.py"):
            try:
                if should_ignore(file_path, ignore_patterns):
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                module_path = str(file_path.relative_to(directory))

                if should_skip_module(module_path):
                    continue

                module_name = module_path.replace("/", ".").replace(".py", "")

                if should_skip_module(module_name):
                    continue

                self._analyze_module(tree, module_name, str(file_path))

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        for module in list(self.module_imports.keys()):
            if should_skip_module(module):
                del self.module_imports[module]
            else:
                self.module_imports[module] = {
                    imp
                    for imp in self.module_imports[module]
                    if not should_skip_module(imp)
                }

    def _analyze_module(self, tree: ast.AST, module_name: str, file_path: str):
        """Analyze a single module's contents and relationships."""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                setattr(child, "parent", parent)

        self._analyze_imports(tree, module_name)
        self._collect_metrics(tree, module_name)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                parent = getattr(node, "parent", None)
                if isinstance(parent, ast.Module):
                    location = FunctionLocation(
                        module=module_name, file=file_path, line=node.lineno
                    )
                    self.function_locations[node.name] = location.__dict__

                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(
                            child.func, ast.Name
                        ):
                            call_info = FunctionCallInfo(
                                from_module=module_name,
                                from_function=node.name,
                                line=child.lineno,
                            )
                            self.function_calls[child.func.id].append(
                                call_info.__dict__
                            )

            elif isinstance(node, ast.ClassDef):
                class_info = {
                    "module": module_name,
                    "file": file_path,
                    "line": node.lineno,
                    "methods": {},
                }

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        calls = []
                        for child in ast.walk(item):
                            if isinstance(child, ast.Call) and isinstance(
                                child.func, ast.Name
                            ):
                                calls.append(child.func.id)

                        method_info = MethodInfo(line=item.lineno, calls=calls)
                        class_info["methods"][item.name] = method_info.__dict__

                self.class_info[module_name][node.name] = class_info

    def _analyze_imports(self, tree: ast.AST, module_name: str):
        """Collect import information from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.module_imports[module_name].add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.module_imports[module_name].add(node.module)

    def _collect_metrics(self, tree: ast.AST, module_name: str):
        """Collect code metrics for the module."""
        functions = []
        classes = []
        total_complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    complex_func = ComplexFunction(
                        module=module_name, name=node.name, complexity=complexity
                    )
                    self.complex_functions.append(
                        (
                            complex_func.module,
                            complex_func.name,
                            complex_func.complexity,
                        )
                    )
                total_complexity += complexity
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        metrics = ModuleMetrics(
            functions=len(functions), classes=len(classes), complexity=total_complexity
        )
        self.module_metrics[module_name] = metrics.__dict__

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def get_mermaid_diagrams(self) -> str:
        visualizer = MermaidVisualizer()

        module_diagram = visualizer.generate_module_overview_diagram(
            self.module_imports
        )

        module_details = []
        for module in sorted(self.module_imports.keys()):
            if module.startswith("treeline."):
                detail_diagram = visualizer.generate_module_detail_diagram(
                    module=module,
                    class_info=self.class_info,
                    function_locations=self.function_locations,
                    function_calls=self.function_calls,
                )
                module_details.append(
                    f"### {module}\n```mermaid\n{detail_diagram}\n```\n"
                )

        return f"```mermaid\n{module_diagram}\n```\n" + "\n".join(module_details)

    def get_graph_data(self):
        """Get graph data for visualization"""
        all_modules = set()
        all_modules.update(self.module_imports.keys())
        all_modules.update(self.module_metrics.keys())
        all_modules.update(
            m.get("module", "") for m in self.function_locations.values()
        )
        all_modules.update(self.class_info.keys())
        all_modules.discard("")

        nodes = []
        links = []
        node_lookup = {}

        for module in all_modules:
            node_id = len(nodes)
            node_lookup[module] = node_id
            is_entry = not any(
                module in imports for imports in self.module_imports.values()
            )

            nodes.append(
                {
                    "id": node_id,
                    "name": module,
                    "type": "module",
                    "is_entry": is_entry,
                    "metrics": self.module_metrics.get(module, {}),
                    "code_smells": [],
                }
            )

        for module, classes in self.class_info.items():
            if module not in node_lookup:
                continue

            for class_name, info in classes.items():
                node_id = len(nodes)
                node_key = f"{module}.{class_name}"
                node_lookup[node_key] = node_id
                class_node_id = len(nodes)
                nodes.append(
                    {
                        "id": class_node_id,
                        "name": class_name,
                        "type": "class",
                        "metrics": info,
                        "methods": info["methods"],
                        "docstring": None,
                        "code_smells": [],
                    }
                )

                links.append(
                    {
                        "source": node_lookup[module],
                        "target": class_node_id,
                        "type": "contains",
                    }
                )

                for method_name, method_info in info["methods"].items():
                    method_node_id = len(nodes)
                    method_key = f"{node_key}.{method_name}"
                    node_lookup[method_key] = method_node_id

                    nodes.append(
                        {
                            "id": method_node_id,
                            "name": method_name,
                            "type": "method",
                            "parent_class": class_name,
                            "metrics": method_info,
                            "docstring": None,
                        }
                    )

                    links.append(
                        {
                            "source": class_node_id,
                            "target": method_node_id,
                            "type": "contains",
                        }
                    )

        for func_name, location in self.function_locations.items():
            if "module" not in location:
                continue

            module = location["module"]
            func_id = f"{module}.{func_name}"
            node_id = len(nodes)
            node_lookup[func_id] = node_id

            nodes.append(
                {
                    "id": node_id,
                    "name": func_name,
                    "type": "function",
                    "metrics": location,
                    "code_smells": [],
                }
            )

            links.append(
                {"source": node_lookup[module], "target": node_id, "type": "contains"}
            )

        for func_name, calls in self.function_calls.items():
            if func_name not in self.function_locations:
                continue

            target_module = self.function_locations[func_name]["module"]
            target_key = f"{target_module}.{func_name}"

            for call in calls:
                source_key = f"{call['from_module']}.{call['from_function']}"
                if source_key in node_lookup and target_key in node_lookup:
                    links.append(
                        {
                            "source": node_lookup[source_key],
                            "target": node_lookup[target_key],
                            "type": "calls",
                        }
                    )

        for module, imports in self.module_imports.items():
            if module in node_lookup:
                for imp in imports:
                    if imp in node_lookup:
                        links.append(
                            {
                                "source": node_lookup[module],
                                "target": node_lookup[imp],
                                "type": "imports",
                            }
                        )

        return nodes, links

    def get_entry_points(self):
        """Get potential entry points of the codebase"""
        entry_points = []
        for module, metrics in self.module_metrics.items():
            if not any(module in imports for imports in self.module_imports.values()):
                entry_points.append(module)
        return entry_points

    def get_core_components(self):
        """Identify core components based on usage and dependencies"""
        components = []
        for module in self.module_imports:
            incoming = len(
                [1 for imports in self.module_imports.values() if module in imports]
            )
            outgoing = len(self.module_imports[module])
            if (
                incoming > 2 and outgoing > 2
            ):  # some arbitrary threshold for core components
                components.append(
                    {"name": module, "incoming": incoming, "outgoing": outgoing}
                )
        return sorted(
            components, key=lambda x: x["incoming"] + x["outgoing"], reverse=True
        )

    def get_common_flows(self):
        """Identify common code flows based on function calls"""
        flows = []
        for func, calls in self.function_calls.items():
            if len(calls) > 2:
                flows.append(
                    {"function": func, "calls": calls, "call_count": len(calls)}
                )
        return sorted(flows, key=lambda x: x["call_count"], reverse=True)

    def clean_for_markdown(self, line: str) -> str:
        """Remove ANSI colors and simplify symbols for markdown."""
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_line = ansi_escape.sub("", line)

        if "# " in clean_line:
            parts = clean_line.split("# ", 1)
            prefix = parts[0]
            docstring = parts[1]
            clean_line = f'{prefix}<span class="docstring">{docstring}</span>'

        replacements = {
            "⚡": '<i class="fas fa-bolt icon-function"></i>',
            "🏛️": '<i class="fas fa-cube icon-class"></i>',
            "⚠️": "!",
            "📏": "▸",
            "[FUNC]": "<span class='function-label'>Function:</span>",
            "[CLASS]": "<span class='class-label'>Class:</span>",
            "├── ": "├─ ",
            "└── ": "└─ ",
            "│   ": "│ ",
            "    ": "  ",
        }

        for old, new in replacements.items():
            clean_line = clean_line.replace(old, new)

        return clean_line.rstrip()
