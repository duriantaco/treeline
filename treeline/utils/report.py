from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict

class ReportGenerator:
    def __init__(self, target_dir: Path, output_dir: Path = None):
        self.target_dir = target_dir
        self.output_dir = output_dir or Path("treeline_reports")
        self.output_dir.mkdir(exist_ok=True)

        from treeline.dependency_analyzer import ModuleDependencyAnalyzer
        from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

        self.dependency_analyzer = ModuleDependencyAnalyzer()
        self.enhanced_analyzer = EnhancedCodeAnalyzer()

        self.analyzed_files = []
        self.quality_issues = defaultdict(list)
        self.complexity_metrics = {}
        self.dependency_graph = {}
        self.entry_points = []
        self.core_components = []
        self.code_smells_by_category = defaultdict(list)
        self.issues_by_file = defaultdict(list)
        self.issues_count = 0
        
        self.function_dependencies = {}
        self.function_docstrings = {}
        self.functions_by_complexity = []
        self.script_contents = defaultdict(lambda: {"classes": {}, "functions": []})
        self.script_links = defaultdict(set)
        self.function_usage = defaultdict(set)

    def analyze(self):
        print(f"Analyzing {self.target_dir}...")
        self.all_file_results = {}  
        for py_file in self.target_dir.rglob("*.py"):
            if not self._should_analyze_file(py_file):
                continue
            self.analyzed_files.append(py_file)
            try:
                file_results = self.enhanced_analyzer.analyze_file(py_file)
                self.all_file_results[str(py_file)] = file_results 
                for result in file_results:
                    if result["type"] == "function":
                        func_name = result["name"]
                        module_name = str(py_file.relative_to(self.target_dir)).replace('/', '.').replace('\\', '.').replace('.py', '')
                        full_name = f"{module_name}.{func_name}"
                        self.function_docstrings[full_name] = {
                            "has_docstring": result["docstring"] is not None,
                            "docstring": result["docstring"],
                            "file_path": str(py_file),
                            "line": result["line"]
                        }
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        self.quality_issues = self.enhanced_analyzer.quality_issues
        self.issues_count = sum(len(issues) for issues in self.quality_issues.values())

        for category, issues in self.quality_issues.items():
            for issue in issues:
                if isinstance(issue, dict) and 'file_path' in issue:
                    file_path = issue['file_path']
                    self.issues_by_file[file_path].append({
                        'category': category,
                        'description': issue.get('description', 'Unknown issue'),
                        'line': issue.get('line', 'Unknown')
                    })
                    self.code_smells_by_category[category].append(issue)

        self.dependency_analyzer.analyze_directory(self.target_dir)
        
        self.function_dependencies = self._collect_function_dependencies()
        self.functions_by_complexity = self._collect_complex_functions()
        self.entry_points = self.dependency_analyzer.get_entry_points()
        self.core_components = self.dependency_analyzer.get_core_components()
        
        self.complexity_metrics = {
            'complex_functions': self.dependency_analyzer.complex_functions,
            'thresholds': self.dependency_analyzer.QUALITY_METRICS
        }
        
        self._build_structure_data()

        print(f"Analysis complete! Found {self.issues_count} issues in {len(self.analyzed_files)} files.")
        
    def _collect_function_dependencies(self):
        function_deps = {}
        for func_name, calls in self.dependency_analyzer.function_calls.items():
            if func_name not in self.dependency_analyzer.function_locations:
                continue 
            function_deps[func_name] = {
                "called_by": [],
                "calls": []
            }
            for call_info in calls:
                caller = call_info.get("from_function", "unknown")
                module = call_info.get("from_module", "unknown")
                if caller != "unknown" and caller in self.dependency_analyzer.function_locations:
                    function_deps[func_name]["called_by"].append({
                        "function": caller,
                        "module": module,
                        "line": call_info.get("line", 0)
                    })
                    if caller not in function_deps:
                        function_deps[caller] = {"called_by": [], "calls": []}
                    function_deps[caller]["calls"].append({
                        "function": func_name,
                        "module": self.dependency_analyzer.function_locations.get(func_name, {}).get("module", "unknown"),
                        "line": call_info.get("line", 0)
                    })
        return function_deps
        
    def _collect_complex_functions(self):
        complex_funcs = []
        for file_path, file_results in self.all_file_results.items():
            for result in file_results:
                if result["type"] == "function" and "metrics" in result:
                    module_path = str(Path(file_path).relative_to(self.target_dir)).replace('/', '.').replace('\\', '.').replace('.py', '')
                    func_name = result["name"]
                    complexity = result["metrics"].get("complexity", 0)
                    if complexity > 5:
                        complex_funcs.append({
                            "module": module_path,
                            "function": func_name,
                            "complexity": complexity,
                            "cognitive_complexity": result["metrics"].get("cognitive_complexity", 0),
                            "lines": result["metrics"].get("lines", 0),
                            "params": result["metrics"].get("params", 0),
                            "has_docstring": result["docstring"] is not None,
                            "file_path": file_path,
                            "line": result["line"]
                        })
        return sorted(complex_funcs, key=lambda x: x["complexity"], reverse=True)
    
    def _build_structure_data(self):
        for module_name, classes in self.dependency_analyzer.class_info.items():
            for class_name, class_info in classes.items():
                if "file" in class_info:
                    file_path = class_info["file"]
                    self.script_contents[file_path]["classes"][class_name] = {
                        "methods": list(class_info.get("methods", {}).keys()),
                        "line": class_info.get("line", 0)
                    }
        
        for func_name, location in self.dependency_analyzer.function_locations.items():
            if "file" in location:
                file_path = location["file"]
                module = location.get("module", "")
                self.script_contents[file_path]["functions"].append({
                    "name": func_name,
                    "line": location.get("line", 0),
                    "module": module
                })
        
        for module, imports in self.dependency_analyzer.module_imports.items():
            source_path = self._module_to_file_path(module)
            if source_path:
                for imported in imports:
                    target_path = self._module_to_file_path(imported)
                    if target_path and source_path != target_path:
                        self.script_links[source_path].add(target_path)
        
        for func_name, calls in self.dependency_analyzer.function_calls.items():
            if func_name in self.dependency_analyzer.function_locations:
                func_file = self.dependency_analyzer.function_locations[func_name].get("file", "")
                
                for call_info in calls:
                    caller = call_info.get("from_function", "")
                    if caller in self.dependency_analyzer.function_locations:
                        caller_file = self.dependency_analyzer.function_locations[caller].get("file", "")
                        if caller_file and func_file and caller_file != func_file:
                            self.script_links[caller_file].add(func_file)
                            self.function_usage[func_name].add(caller_file)

    def _module_to_file_path(self, module_name):
        if not module_name:
            return None
            
        for func_name, location in self.dependency_analyzer.function_locations.items():
            if location.get("module") == module_name and "file" in location:
                return location["file"]
                
        for mod, classes in self.dependency_analyzer.class_info.items():
            if mod == module_name:
                for class_name, info in classes.items():
                    if "file" in info:
                        return info["file"]
        
        try:
            module_parts = module_name.split(".")
            path = self.target_dir.joinpath(*module_parts).with_suffix(".py")
            if path.exists():
                return str(path)
        except Exception:
            pass
        
        return None

    def generate_report(self) -> str:
        sections = []
        sections.append(f"# Treeline Code Analysis Report\n")
        sections.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append(f"**Project:** {self.target_dir.absolute()}")
        total_funcs = len(self.function_docstrings)
        categories = self.dependency_analyzer.categorize_functions(self.function_dependencies)
        sections.append(f"**Files Analyzed:** {len(self.analyzed_files)}")
        sections.append(f"**Functions:** {total_funcs} (Entry: {len(categories['entry_points'])}, Core: {len(categories['core_functions'])})")
        sections.append(f"**Issues Found:** {self.issues_count}\n")
        script_info = {}
        for file_path in self.analyzed_files:
            rel_path = str(file_path.relative_to(self.target_dir))
            script_info[str(file_path)] = {
                "path": rel_path,
                "classes": {},
                "functions": [],
                "imports": set(),
                "imported_by": set(),
                "calls_to": set(),
                "called_by": set()
            }
        for module_name, classes in self.dependency_analyzer.class_info.items():
            for class_name, class_info in classes.items():
                if "file" in class_info and "methods" in class_info:
                    file_path = class_info["file"]
                    if file_path in script_info:
                        script_info[file_path]["classes"][class_name] = {
                            "methods": list(class_info["methods"].keys()),
                            "line": class_info.get("line", 0)
                        }
        for func_name, location in self.dependency_analyzer.function_locations.items():
            if "file" in location:
                file_path = location["file"]
                if file_path in script_info:
                    script_info[file_path]["functions"].append({
                        "name": func_name,
                        "module": location.get("module", ""),
                        "line": location.get("line", 0)
                    })
        for module, imports in self.dependency_analyzer.module_imports.items():
            source_path = self._module_to_file_path(module)
            if source_path and source_path in script_info:
                for imported in imports:
                    imported_path = self._module_to_file_path(imported)
                    if imported_path and imported_path in script_info and imported_path != source_path:
                        script_info[source_path]["imports"].add(imported_path)
                        script_info[imported_path]["imported_by"].add(source_path)
        for func_name, calls in self.dependency_analyzer.function_calls.items():
            if func_name in self.dependency_analyzer.function_locations:
                func_file = self.dependency_analyzer.function_locations[func_name].get("file", "")
                if func_file in script_info:
                    for call_info in calls:
                        caller = call_info.get("from_function", "")
                        if caller in self.dependency_analyzer.function_locations:
                            caller_file = self.dependency_analyzer.function_locations[caller].get("file", "")
                            if caller_file in script_info and caller_file != func_file:
                                script_info[caller_file]["calls_to"].add(func_file)
                                script_info[func_file]["called_by"].add(caller_file)
        sections.append("## 📊 Code Structure Analysis\n")
        file_connections = {}
        for file_path, info in script_info.items():
            connections = (len(info["imports"]) + len(info["imported_by"]) + 
                        len(info["calls_to"]) + len(info["called_by"]))
            file_connections[file_path] = connections
        most_connected = sorted(file_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        sections.append("### Most Connected Files\n")
        sections.append("| File | Total Connections | Imports | Imported By | Calls To | Called By |")
        sections.append("|------|-------------------|---------|-------------|----------|-----------|")
        for file_path, connections in most_connected:
            info = script_info[file_path]
            sections.append(f"| {info['path']} | {connections} | {len(info['imports'])} | {len(info['imported_by'])} | {len(info['calls_to'])} | {len(info['called_by'])} |")
        
        sections.append("\n### Module Stability Analysis\n")
        sections.append("This analysis shows which modules are stable (many incoming, few outgoing dependencies) versus unstable (few incoming, many outgoing).\n")
        sections.append("| Module | Stability Index | Incoming | Outgoing | Rating |")
        sections.append("|--------|----------------|----------|----------|--------|")

        module_stability = []
        for module in self.dependency_analyzer.module_imports:
            incoming = len([1 for imports in self.dependency_analyzer.module_imports.values() if module in imports])
            outgoing = len(self.dependency_analyzer.module_imports[module])
            total_deps = incoming + outgoing
            stability = incoming / total_deps if total_deps > 0 else 0.5
            
            rating = "Very Stable ✓" if stability > 0.8 else "Stable" if stability > 0.6 else "Balanced" if stability > 0.4 else "Unstable" if stability > 0.2 else "Very Unstable ⚠"
            module_stability.append((module, stability, incoming, outgoing, rating))

        for module, stability, incoming, outgoing, rating in sorted(module_stability, key=lambda x: x[1], reverse=True)[:10]:
            sections.append(f"| {module} | {stability:.2f} | {incoming} | {outgoing} | {rating} |")
        

        sections.append("\n### Change Impact Analysis\n")
        sections.append("These modules would have the highest ripple effect if modified - changes here will impact many other parts of the codebase:\n")

        cascade_impact = []
        for module in self.dependency_analyzer.module_imports:
            impact_count = 0
            impacted = set()
            for other_mod, imports in self.dependency_analyzer.module_imports.items():
                if module in imports:
                    impact_count += 1
                    impacted.add(other_mod)
            cascade_impact.append((module, impact_count, impacted))

        for module, count, impacted in sorted(cascade_impact, key=lambda x: x[1], reverse=True)[:5]:
            sections.append(f"- **{module}**: Would affect {count} modules")
            if impacted:
                sections.append(f" -> Most notable dependents: {', '.join(sorted(list(impacted))[:3])}")
            if count > 3:
                sections.append(f" -> Impact risk: {'High ⚠' if count > 7 else 'Medium'}")

        sections.append("\n### Architectural Insights\n")

        entry_count = len(self.dependency_analyzer.get_entry_points())
        core_count = len(self.dependency_analyzer.get_core_components())
        utility_modules = [m for m, imports in self.dependency_analyzer.module_imports.items() 
                        if len(imports) < 3 and any(u in m.lower() for u in ['util', 'helper', 'common'])]

        avg_fanout = sum(len(imports) for imports in self.dependency_analyzer.module_imports.values()) / max(1, len(self.dependency_analyzer.module_imports))
        max_depth = 0
        for module in self.dependency_analyzer.module_imports:
            visited = set()
            def get_depth(mod, current_depth=0):
                if mod in visited or current_depth > 20:  # prevent infinite recursion
                    return current_depth
                visited.add(mod)
                if mod not in self.dependency_analyzer.module_imports:
                    return current_depth
                return max([get_depth(imp, current_depth + 1) for imp in self.dependency_analyzer.module_imports[mod]] or [current_depth])
            depth = get_depth(module)
            max_depth = max(max_depth, depth)

        arch_insights = []
        if entry_count > 5:
            arch_insights.append("- Multiple entry points detected - this appears to be a **multi-service architecture**")
        elif entry_count == 1:
            arch_insights.append("- Single clear entry point - this follows a **monolithic architecture** pattern")

        if core_count > 3:
            arch_insights.append("- Several core components identified - suggests a **modular design** with clear separation of concerns")
        elif core_count <= 1:
            arch_insights.append("- Few core components - may indicate **tightly coupled code** or early stage development")

        if avg_fanout > 5:
            arch_insights.append(f"- High average dependencies ({avg_fanout:.1f} per module) - consider **reducing coupling** between modules")
        else:
            arch_insights.append(f"- Healthy average dependencies ({avg_fanout:.1f} per module) - good **separation of concerns**")

        if max_depth > 5:
            arch_insights.append(f"- Deep dependency chain (depth of {max_depth}) - watch for **ripple effects** from lower-level changes")
        else:
            arch_insights.append(f"- Shallow dependency chains (max depth {max_depth}) - **resilient to changes**")

        if len(utility_modules) > 3:
            arch_insights.append(f"- Good use of utility modules ({len(utility_modules)} identified) - improves **code reusability**")

        sections.extend(arch_insights)

        sections.append("## Executive Summary\n")
        sections.append("This section provides a high-level overview of your codebase's health, highlighting key metrics and areas needing attention.\n")
        total_functions = len(self.function_docstrings)
        missing_docstrings_count = sum(1 for info in self.function_docstrings.values() if not info["has_docstring"])
        docstring_coverage = 100 - (missing_docstrings_count / max(1, total_functions) * 100)
        high_complexity_funcs = [f for f in self.functions_by_complexity if f["complexity"] > 10]
        security_issues = len(self.code_smells_by_category.get('security', []))
        top_issue_categories = sorted(
            [(category, len(issues)) for category, issues in self.code_smells_by_category.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        summary_items = [
            f"- **Overall Health**: {'⚠️ Needs attention' if self.issues_count > 50 else '✅ Generally good' if self.issues_count > 10 else '🎉 Excellent'}",
            f"- **Function Count**: {total_functions} functions across {len(self.analyzed_files)} files",
            f"- **Documentation Coverage**: {docstring_coverage:.1f}% ({total_functions - missing_docstrings_count}/{total_functions} functions have docstrings)",
            f"- **Complex Functions**: {len(high_complexity_funcs)} functions with complexity > 10",
            f"- **Security Issues**: {security_issues} potential security concerns",
            f"- **Top Issue Categories**: {', '.join([f'{cat.title()} ({count})' for cat, count in top_issue_categories]) if top_issue_categories else 'None'}"
        ]
        sections.extend(summary_items)
        recommendations = []
        if security_issues > 0:
            recommendations.append(f"- Address the {security_issues} security issues immediately")
        if high_complexity_funcs:
            recommendations.append(f"- Refactor the top {min(3, len(high_complexity_funcs))} complex functions")
        if missing_docstrings_count > 0:
            recommendations.append(f"- Add docstrings to {missing_docstrings_count} undocumented functions")
        if recommendations:
            sections.append("\n**Recommended Actions:**")
            sections.extend(recommendations)
        sections.append("")
        
        sections.append("## Quality Analysis\n")
        
        sections.append("## Configuration Thresholds\n")
        sections.append("This section lists the thresholds used to evaluate your code. These are the maximum allowed values for various metrics before an issue is flagged.\n")
        sections.append("| Threshold | Value |")
        sections.append("|-----------|-------|")
        config = self.enhanced_analyzer.config
        thresholds = [
            (f"Maximum parameters per function", config.get('MAX_PARAMS', 5)),
            (f"Maximum function length", f"{config.get('MAX_FUNCTION_LINES', 50)} lines"),
            (f"Maximum nested blocks", config.get('MAX_NESTED_BLOCKS', 3)),
            (f"Maximum cyclomatic complexity", config.get('MAX_CYCLOMATIC_COMPLEXITY', 10)),
            (f"Maximum cognitive complexity", config.get('MAX_COGNITIVE_COMPLEXITY', 15)),
            (f"Maximum line length", f"{config.get('MAX_LINE_LENGTH', 100)} characters"),
            (f"Maximum file length", f"{config.get('MAX_FILE_LINES', 1000)} lines"),
            (f"Maximum return statements", config.get('MAX_RETURNS', 4)),
            (f"Maximum duplicated lines", config.get('MAX_DUPLICATED_LINES', 5))
        ]
        for name, value in thresholds:
            sections.append(f"| {name} | {value} |")
        sections.append("")
        sections.append("## Priority Issues by Severity\n")
        sections.append("This section groups issues by their severity (critical, high, medium, low), helping you prioritize fixes based on their impact.\n")
        SEVERITY_ORDER = ["critical", "high", "medium", "low"]
        issues_by_severity = defaultdict(list)
        for category, issues in self.quality_issues.items():
            for issue in issues:
                severity = issue.get("severity", "medium").lower()
                issues_by_severity[severity].append(issue)
        sorted_severities = sorted(
            issues_by_severity.keys(),
            key=lambda s: SEVERITY_ORDER.index(s) if s in SEVERITY_ORDER else len(SEVERITY_ORDER)
        )
        for severity in sorted_severities:
            sections.append(f"### {severity.title()} Priority Issues\n")
            if not issues_by_severity[severity]:
                sections.append("None found.\n")
                continue
                
            display_limit = 10
            total_issues = len(issues_by_severity[severity])
            
            for issue in issues_by_severity[severity][:display_limit]:
                file_path = issue.get('file_path', 'Unknown')
                rel_path = Path(file_path).relative_to(self.target_dir) if Path(file_path).is_absolute() else file_path
                line = issue.get('line', 'Unknown')
                description = issue.get('description', 'Unknown issue')
                sections.append(f"- **{rel_path}:{line}**: {description}")
                
            if total_issues > display_limit:
                remaining = total_issues - display_limit
                collapsed_content = []
                for issue in issues_by_severity[severity][display_limit:]:
                    file_path = issue.get('file_path', 'Unknown')
                    rel_path = Path(file_path).relative_to(self.target_dir) if Path(file_path).is_absolute() else file_path
                    line = issue.get('line', 'Unknown')
                    description = issue.get('description', 'Unknown issue')
                    collapsed_content.append(f"- **{rel_path}:{line}**: {description}")
                
                sections.append(f'<details><summary>▼ - *...and {remaining} more {severity} priority issues*</summary>\n')
                sections.extend(collapsed_content)
                sections.append('</details>')
                
            sections.append(f"**Total: {total_issues} {severity} issues**\n")
            
        sections.append("## Most Complex Functions\n")
        sections.append("This section lists the functions with the highest complexity metrics, which may indicate areas that are hard to test, maintain, or understand.\n")
        sections.append("- **Cyclomatic Complexity**: Measures the number of independent paths through a function's code (e.g., branches from if/loop statements). A higher value means more complex logic and more test cases needed.\n")
        sections.append("- **Cognitive Complexity**: Assesses how difficult the code is for a human to understand, factoring in nesting, control flow, and logical complexity.\n")
        sections.append("\n")
        if self.functions_by_complexity:
            display_limit = 10
            total_complex_funcs = len(self.functions_by_complexity)
            
            sections.append("| Module | Function | Cyclomatic Complexity | Cognitive Complexity | Lines | Parameters | Has Docstring |")
            sections.append("|--------|----------|-----------------------|----------------------|-------|------------|---------------|")
            
            for func in self.functions_by_complexity[:display_limit]:
                has_doc = "✅" if func["has_docstring"] else "❌"
                sections.append(
                    f"| {func['module']} | {func['function']} | {func['complexity']} | {func.get('cognitive_complexity', 'N/A')} | {func['lines']} | {func['params']} | {has_doc} |"
                )
                
            if total_complex_funcs > display_limit:
                remaining = total_complex_funcs - display_limit
                
                sections.append(f'<details><summary>▼ *...and {remaining} more complex functions*</summary>\n')
                sections.append("| Module | Function | Cyclomatic Complexity | Cognitive Complexity | Lines | Parameters | Has Docstring |")
                sections.append("|--------|----------|-----------------------|----------------------|-------|------------|---------------|")
                
                for func in self.functions_by_complexity[display_limit:]:
                    has_doc = "✅" if func["has_docstring"] else "❌"
                    sections.append(
                        f"| {func['module']} | {func['function']} | {func['complexity']} | {func.get('cognitive_complexity', 'N/A')} | {func['lines']} | {func['params']} | {has_doc} |"
                    )
                sections.append('</details>')
        else:
            sections.append("No complex functions found.\n")
            
        sections.append("")
        sections.append("## Function Dependencies (Code Flow)\n")
        sections.append("This section details how functions interact, showing which functions depend on others and vice versa. If you change a function, its dependents (functions that call it) may be impacted. Understanding this helps predict the ripple effects of modifications.\n")
        sections.append("### Most Called Functions\n")
        sections.append("These functions are depended upon by many others. Changing them could affect multiple parts of your codebase.\n")
        
        top_called = sorted(
            self.function_dependencies.items(),
            key=lambda x: len(x[1]["called_by"]),
            reverse=True
        )[:5]
        
        for func_name, deps in top_called:
            if deps["called_by"]:
                module = self.dependency_analyzer.function_locations.get(func_name, {}).get("module", "unknown")
                sections.append(f"- `{func_name}` (in {module}): called by {len(deps['called_by'])} functions")
                
                display_limit = 3
                total_callers = len(deps["called_by"])
                
                if total_callers > 0:
                    caller_examples = ", ".join([f"`{caller['function']}` in {caller['module']}" for caller in deps["called_by"][:display_limit]])
                    sections.append(f"  - Examples of dependents: {caller_examples}")
                    
                    if total_callers > display_limit:
                        remaining = total_callers - display_limit
                        
                        sections.append(f'  <details><summary>▼ - *...and {remaining} more dependents*</summary>')
                        for caller in deps["called_by"][display_limit:]:
                            sections.append(f"  - `{caller['function']}` in {caller['module']}")
                        sections.append('  </details>')
                        
        if not any(deps["called_by"] for _, deps in top_called):
            sections.append("No significant call dependencies found within project code.\n")
            
        sections.append("")
        sections.append("### Functions with Most Dependencies\n")
        sections.append("These functions rely on many others. They might be complex hubs, and changes to their dependencies could affect them.\n")
        
        top_dependent = sorted(
            self.function_dependencies.items(),
            key=lambda x: len(x[1]["calls"]),
            reverse=True
        )[:5]
        
        for func_name, deps in top_dependent:
            if deps["calls"]:
                module = self.dependency_analyzer.function_locations.get(func_name, {}).get("module", "unknown")
                sections.append(f"- `{func_name}` (in {module}): calls {len(deps['calls'])} functions")
                
                display_limit = 3
                total_calls = len(deps["calls"])
                
                if total_calls > 0:
                    calls_examples = ", ".join([f"`{called['function']}` in {called['module']}" for called in deps["calls"][:display_limit]])
                    sections.append(f"  - Examples of dependencies: {calls_examples}")
                    
                    if total_calls > display_limit:
                        remaining = total_calls - display_limit
                        
                        sections.append(f'  <details><summary>▼ - *...and {remaining} more dependencies*</summary>')
                        for called in deps["calls"][display_limit:]:
                            sections.append(f"  - `{called['function']}` in {called['module']}")
                        sections.append('  </details>')
                        
        if not any(deps["calls"] for _, deps in top_dependent):
            sections.append("No significant dependencies found within project code.\n")
            
        sections.append("")
        sections.append("## Function Docstring Status\n")
        sections.append("This section lists all functions and indicates whether they have docstrings. Docstrings are critical for documentation, improving code readability and maintainability by explaining a function's purpose and usage.\n")
        sorted_functions = sorted(
            self.function_docstrings.items(),
            key=lambda x: (x[1]["file_path"], x[0])
        )
        display_limit = 15

        sections.append("| Module | Function | Has Docstring | Action Needed |")
        sections.append("|--------|----------|---------------|---------------|")
        for full_name, info in sorted_functions[:display_limit]:
            has_doc = "✅" if info["has_docstring"] else "❌"
            action = "Add docstring" if not info["has_docstring"] else "None"
            module = full_name.split('.')[0] if '.' in full_name else "unknown"
            func_name = full_name.split('.')[-1]
            sections.append(f"| {module} | {func_name} | {has_doc} | {action} |")
        
        if len(sorted_functions) > display_limit:
            remaining = len(sorted_functions) - display_limit
            sections.append("") 
            sections.append(f'<details><summary>▼ ...and {remaining} more functions</summary>\n')
            
            sections.append("| Module | Function | Has Docstring | Action Needed |")
            sections.append("|--------|----------|---------------|---------------|")
            for full_name, info in sorted_functions[display_limit:]:
                has_doc = "✅" if info["has_docstring"] else "❌"
                action = "Add docstring" if not info["has_docstring"] else "None"
                module = full_name.split('.')[0] if '.' in full_name else "unknown"
                func_name = full_name.split('.')[-1]
                sections.append(f"| {module} | {func_name} | {has_doc} | {action} |")
            sections.append('\n</details>')
        else:
            for full_name, info in sorted_functions:
                has_doc = "✅" if info["has_docstring"] else "❌"
                action = "Add docstring" if not info["has_docstring"] else "None"
                module = full_name.split('.')[0] if '.' in full_name else "unknown"
                func_name = full_name.split('.')[-1]
                sections.append(f"| {module} | {func_name} | {has_doc} | {action} |")
        
        missing_docstrings_count = sum(1 for info in self.function_docstrings.values() if not info["has_docstring"])
        sections.append(f"**Total Functions**: {len(self.function_docstrings)}, **Missing Docstrings**: {missing_docstrings_count}\n")
        sections.append("\n---\n")
        sections.append("Report generated by Treeline")
        return "\n".join(sections)

    def generate_report_json(self) -> Dict:
        total_functions = len(self.function_docstrings)
        missing_docstrings_count = sum(1 for info in self.function_docstrings.values() if not info["has_docstring"])
        docstring_coverage = 100 - (missing_docstrings_count / max(1, total_functions) * 100)
        
        high_complexity_funcs = [f for f in self.functions_by_complexity if f["complexity"] > 10]
        security_issues = len(self.code_smells_by_category.get('security', []))
        
        top_issue_categories = sorted(
            [(category, len(issues)) for category, issues in self.code_smells_by_category.items()],
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        missing_docstrings = []
        for full_name, info in self.function_docstrings.items():
            if not info["has_docstring"]:
                missing_docstrings.append({
                    "name": full_name,
                    "file_path": info["file_path"],
                    "line": info["line"]
                })
                
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project": str(self.target_dir.absolute()),
                "files_analyzed": len(self.analyzed_files),
                "issues_found": self.issues_count
            },
            "executive_summary": {
                "overall_health": "needs_attention" if self.issues_count > 50 else "good" if self.issues_count > 10 else "excellent",
                "function_count": total_functions,
                "documentation_coverage": round(docstring_coverage, 1),
                "complex_functions_count": len(high_complexity_funcs),
                "security_issues_count": security_issues,
                "top_issue_categories": dict(top_issue_categories)
            },
            "issues_by_category": {
                category: len(issues) for category, issues in self.code_smells_by_category.items()
            },
            "security_issues": [
                {
                    "file": str(Path(issue.get('file_path', '')).relative_to(self.target_dir) if Path(issue.get('file_path', '')).is_absolute() else issue.get('file_path', '')),
                    "line": issue.get('line'),
                    "description": issue.get('description'),
                    "severity": issue.get('severity', 'medium')
                }
                for issue in self.code_smells_by_category.get('security', [])
            ],
            "most_complex_functions": [
                {
                    "module": func["module"],
                    "function": func["function"],
                    "complexity": func["complexity"],
                    "cognitive_complexity": func.get("cognitive_complexity", 0),
                    "lines": func["lines"],
                    "parameters": func["params"],
                    "has_docstring": func["has_docstring"],
                    "file_path": str(Path(func["file_path"]).relative_to(self.target_dir) if Path(func["file_path"]).is_absolute() else func["file_path"]),
                    "line": func["line"]
                }
                for func in self.functions_by_complexity[:15]
            ],
            "function_dependencies": {
                "most_called": [
                    {
                        "function": func_name,
                        "module": self.dependency_analyzer.function_locations.get(func_name, {}).get("module", "unknown"),
                        "callers": [
                            {
                                "function": caller["function"],
                                "module": caller["module"],
                                "line": caller["line"]
                            }
                            for caller in deps["called_by"][:10]
                        ]
                    }
                    for func_name, deps in sorted(
                        self.function_dependencies.items(),
                        key=lambda x: len(x[1]["called_by"]) if "called_by" in x[1] else 0,
                        reverse=True
                    )[:10] if deps["called_by"]
                ],
                "most_dependent": [
                    {
                        "function": func_name,
                        "module": self.dependency_analyzer.function_locations.get(func_name, {}).get("module", "unknown"),
                        "calls": [
                            {
                                "function": called["function"],
                                "module": called["module"],
                                "line": called["line"]
                            }
                            for called in deps["calls"][:10]
                        ]
                    }
                    for func_name, deps in sorted(
                        self.function_dependencies.items(),
                        key=lambda x: len(x[1]["calls"]) if "calls" in x[1] else 0,
                        reverse=True
                    )[:10] if deps["calls"]
                ]
            },
            "missing_docstrings": [
                {
                    "name": func["name"],
                    "file": str(Path(func["file_path"]).relative_to(self.target_dir) if Path(func["file_path"]).is_absolute() else func["file_path"]),
                    "line": func["line"]
                }
                for func in missing_docstrings
            ],
            "issues_by_file": [
                {
                    "file": str(Path(file_path).relative_to(self.target_dir) if Path(file_path).is_absolute() else file_path),
                    "issues_count": len(issues),
                    "issues_by_category": defaultdict(list)
                }
                for file_path, issues in sorted(
                    self.issues_by_file.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:10]
            ],
            "core_components": [
                {
                    "name": comp["name"],
                    "incoming": comp["incoming"],
                    "outgoing": comp["outgoing"]
                }
                for comp in self.core_components
            ],
            "entry_points": self.entry_points
        }
        
        return report_data

    def save_report(self, filename: str = None, format: str = "md") -> Path:
        if format.lower() == "json":
            import json
            report_data = self.generate_report_json()
            content = json.dumps(report_data, indent=2, default=str)
            extension = ".json"
        else:
            content = self.generate_report()
            extension = ".md"
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"treeline_report_{timestamp}{extension}"
        elif not filename.endswith(extension):
            filename = f"{filename}{extension}"
        
        output_path = self.output_dir / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Report saved to {output_path}")
        return output_path

    def _should_analyze_file(self, file_path: Path) -> bool:
        if any(p in str(file_path) for p in ["venv", "site-packages", "__pycache__", ".git"]):
            return False
            
        return True