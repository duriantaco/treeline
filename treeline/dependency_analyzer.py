import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict
from treeline.utils.metrics import calculate_cyclomatic_complexity
from concurrent.futures import ProcessPoolExecutor

from treeline.ignore import read_ignore_patterns, should_ignore
from treeline.models.dependency_analyzer import (
    FunctionCallInfo,
    FunctionLocation,
    MethodInfo,
    ModuleMetrics,
)

def default_call_graph():
    return {
        "callers": defaultdict(int),
        "callees": defaultdict(int),
        "module": "",
        "total_calls": 0,
        "entry_point": False,
        "terminal": False,
        "recursive": False,
        "call_depth": 0,
    }

class ModuleDependencyAnalyzer:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.module_imports = {}
        self.module_metrics = {}
        self.complex_functions = {}
        self.function_locations = {}
        self.function_calls = defaultdict(list)  
        self.class_info = {}
        self.call_graph = defaultdict(default_call_graph)
        
        self.QUALITY_METRICS = {
            "MAX_LINE_LENGTH": self.config.get("MAX_LINE_LENGTH", 100),
            "MAX_DOC_LENGTH": self.config.get("MAX_DOC_LENGTH", 80),
            "MAX_CYCLOMATIC_COMPLEXITY": self.config.get("MAX_CYCLOMATIC_COMPLEXITY", 10),
            "MAX_COGNITIVE_COMPLEXITY": self.config.get("MAX_COGNITIVE_COMPLEXITY", 15),
            "MAX_NESTED_DEPTH": self.config.get("MAX_NESTED_DEPTH", 4),
            "MAX_FUNCTION_LINES": self.config.get("MAX_FUNCTION_LINES", 50),
            "MAX_PARAMS": self.config.get("MAX_PARAMS", 5),
            "MAX_RETURNS": self.config.get("MAX_RETURNS", 4),
            "MAX_ARGUMENTS_PER_LINE": self.config.get("MAX_ARGUMENTS_PER_LINE", 5),
            "MIN_MAINTAINABILITY_INDEX": self.config.get("MIN_MAINTAINABILITY_INDEX", 20),
            "MAX_FUNC_COGNITIVE_LOAD": self.config.get("MAX_FUNC_COGNITIVE_LOAD", 15),
            "MIN_PUBLIC_METHODS": self.config.get("MIN_PUBLIC_METHODS", 1),
            "MAX_IMPORT_STATEMENTS": self.config.get("MAX_IMPORT_STATEMENTS", 15),
            "MAX_MODULE_DEPENDENCIES": self.config.get("MAX_MODULE_DEPENDENCIES", 10),
            "MAX_INHERITANCE_DEPTH": self.config.get("MAX_INHERITANCE_DEPTH", 3),
            "MAX_DUPLICATED_LINES": self.config.get("MAX_DUPLICATED_LINES", 6),
            "MAX_DUPLICATED_BLOCKS": self.config.get("MAX_DUPLICATED_BLOCKS", 2),
            "MAX_CLASS_LINES": self.config.get("MAX_CLASS_LINES", 300),
            "MAX_METHODS_PER_CLASS": self.config.get("MAX_METHODS_PER_CLASS", 20),
            "MAX_CLASS_COMPLEXITY": self.config.get("MAX_CLASS_COMPLEXITY", 50),
        }
        self.entry_patterns = {
            "fastapi_route": r"@(?:app|router)\.(?:get|post|put|delete|patch)",
            "cli_command": r"@click\.command|@app\.command|def main\(",
            "django_view": r"class \w+View\(|@api_view",
            "test_file": r"test_.*\.py$|.*_test\.py$",
            "main_guard": r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:',
        }

    def analyze_directory(self, directory: Path):
        self.directory = directory
        ignore_patterns = read_ignore_patterns()
        python_files = [fp for fp in directory.rglob("*.py") if not should_ignore(fp, ignore_patterns)]
        
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._analyze_file, fp) for fp in python_files]
            for future in futures:
                result = future.result()
                if result:
                    module_name = result["module_name"]
                    if module_name not in self.module_imports:
                        self.module_imports[module_name] = set()
                    self.module_imports[module_name].update(result["imports"])
                    self.module_metrics[module_name] = result["metrics"]
                    self.function_locations.update(result["function_locations"])

                    for call in result["function_calls"]:
                        to_func_id = f"{call['to_module']}.{call['to_function']}"
                        self.function_calls[to_func_id].append(call)

                    if module_name not in self.class_info:
                        self.class_info[module_name] = {}

                    self.class_info[module_name].update(result["class_info"])

    def _analyze_module(self, tree: ast.AST, module_name: str, file_path: str) -> dict:
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                setattr(child, "parent", parent)

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        functions = []
        classes = []
        total_complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                total_complexity += complexity
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        metrics = ModuleMetrics(functions=len(functions), classes=len(classes), complexity=total_complexity)

        function_locations = {}
        function_calls = []
        local_functions = set()
        imported_functions = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if isinstance(getattr(node, "parent", None), ast.Module):
                    local_functions.add(node.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for name in node.names:
                        alias = name.asname or name.name
                        imported_functions[alias] = f"{node.module}.{name.name}"

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                parent = getattr(node, "parent", None)
                if isinstance(parent, ast.Module):
                    func_id = f"{module_name}.{node.name}"
                    location = FunctionLocation(module=module_name, file=file_path, line=node.lineno)
                    function_locations[func_id] = location.__dict__

                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            called_func = child.func.id
                            if called_func in local_functions:
                                target_module = module_name
                                target_func = called_func
                            elif called_func in imported_functions:
                                target_module, target_func = imported_functions[called_func].rsplit(".", 1)
                            else:
                                continue  
                            call_info = FunctionCallInfo(
                                from_module=module_name,
                                from_function=node.name,
                                to_module=target_module,
                                to_function=target_func,
                                line=child.lineno
                            )
                            function_calls.append(call_info.__dict__)

        class_info = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_data = {
                    "module": module_name,
                    "file": file_path,
                    "line": node.lineno,
                    "methods": {},
                }
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        calls = []
                        for child in ast.walk(item):
                            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                                calls.append(child.func.id)
                        method_info = MethodInfo(line=item.lineno, calls=calls)
                        class_data["methods"][item.name] = method_info.__dict__
                class_info[node.name] = class_data

        return {
            "imports": imports,
            "metrics": metrics.__dict__,
            "function_locations": function_locations,
            "function_calls": function_calls,
            "class_info": class_info,
            "module_name": module_name
        }
    
    def _analyze_file(self, file_path: Path) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
            module_name = str(file_path.relative_to(self.directory)).replace("/", ".").replace(".py", "")
            analysis = self._analyze_module(tree, module_name, str(file_path))
            return analysis
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _analyze_imports(self, tree: ast.AST, module_name: str):
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.module_imports[module_name].add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.module_imports[module_name].add(node.module)

    def _collect_metrics(self, tree: ast.AST, module_name: str):
        functions = []
        classes = []
        total_complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                total_complexity += complexity
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        metrics = ModuleMetrics(functions=len(functions), classes=len(classes), complexity=total_complexity)
        self.module_metrics[module_name] = metrics.__dict__

    def _calculate_complexity(self, node: ast.AST) -> int:
        return calculate_cyclomatic_complexity(node)

    def get_graph_data(self):

        nodes = []
        links = []
        node_lookup = {}
        all_modules = set(self.module_imports.keys())

        for module in all_modules:
            node_id = len(nodes)
            node_lookup[module] = node_id
            is_entry = not any(module in imports for imports in self.module_imports.values())
            file_path = str(self.directory / (module.replace('.', '/') + '.py'))
            nodes.append({
                "id": node_id,
                "name": module,
                "type": "module",
                "is_entry": is_entry,
                "file_path": file_path,  
                "metrics": self.module_metrics.get(module, {}),
                "code_smells": [],
            })

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
                    {"source": node_lookup[module], "target": class_node_id, "type": "contains"}
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
                        {"source": class_node_id, "target": method_node_id, "type": "contains"}
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

        for to_func_id, calls in self.function_calls.items():
            if to_func_id not in self.function_locations:
                continue
            target_module = self.function_locations[to_func_id]["module"]
            target_key = to_func_id  
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
                            {"source": node_lookup[module], "target": node_lookup[imp], "type": "imports"}
                        )

        return nodes, links

    def get_entry_points(self):
        entry_points = []
        for module, metrics in self.module_metrics.items():
            if not any(module in imports for imports in self.module_imports.values()):
                entry_points.append(module)
        return entry_points
    
    def categorize_functions(self):
        categories = {'entry_points': [], 'core_functions': [], 'leaf_functions': []}
        for func, calls in self.function_calls.items():
            fan_in = len(calls)
            fan_out = len(self.function_dependencies.get(func, {}).get('calls', []))
            if fan_in == 0:
                categories['entry_points'].append(func)
            elif fan_in > 5 or fan_out > 5:
                categories['core_functions'].append(func)
            elif fan_out == 0 and fan_in > 0:
                categories['leaf_functions'].append(func)
        return categories

    def get_core_components(self):
        components = []
        for module in self.module_imports:
            incoming = len(
                [1 for imports in self.module_imports.values() if module in imports]
            )
            outgoing = len(self.module_imports[module])
            if (
                incoming > 2 and outgoing > 2
            ):
                components.append(
                    {"name": module, "incoming": incoming, "outgoing": outgoing}
                )
        return sorted(
            components, key=lambda x: x["incoming"] + x["outgoing"], reverse=True
        )
    
    def get_graph_data_with_quality(self, enhanced_analyzer=None):
        nodes, links = self.get_graph_data()
        
        if enhanced_analyzer and hasattr(enhanced_analyzer, 'quality_issues') and enhanced_analyzer.quality_issues:
            file_to_module = {}
            
            for node in nodes:
                if node['type'] == 'module':
                    for func_name, location in self.function_locations.items():
                        if location.get('module') == node['name'] and 'file' in location:
                            file_to_module[location.get('file')] = node['name']
                    
                    for module_name, classes in self.class_info.items():
                        if module_name == node['name']:
                            for class_name, info in classes.items():
                                if 'file' in info:
                                    file_to_module[info.get('file')] = node['name']
            
            file_basenames = {Path(file_path).name: module_name for file_path, module_name in file_to_module.items()}
            
            for category, issues in enhanced_analyzer.quality_issues.items():
                for issue in issues:
                    if isinstance(issue, dict) and 'file_path' in issue:
                        file_path = issue['file_path']
                        module_name = file_to_module.get(file_path) or file_basenames.get(Path(file_path).name)
                        
                        if not module_name:
                            for path, mod in file_to_module.items():
                                if path.endswith(file_path) or file_path.endswith(path):
                                    module_name = mod
                                    break
                        
                        if module_name:
                            for node in nodes:
                                if node['type'] == 'module' and node['name'] == module_name:
                                    if 'code_smells' not in node:
                                        node['code_smells'] = []
                                    new_issue = {
                                        'type': category,
                                        'description': issue.get('description', 'Unknown issue'),
                                        'line': issue.get('line'),
                                        'severity': issue.get('severity', 'medium')
                                    }
                                    if new_issue not in node['code_smells']:
                                        node['code_smells'].append(new_issue)
                                    break
        
        return nodes, links

    def get_common_flows(self):
        flows = []
        for func, calls in self.function_calls.items():
            if len(calls) > 2:
                flows.append(
                    {"function": func, "calls": calls, "call_count": len(calls)}
                )
        return sorted(flows, key=lambda x: x["call_count"], reverse=True)

    def clean_for_markdown(self, line: str) -> str:
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