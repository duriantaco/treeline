
from pathlib import Path
from typing import Dict, Union
import os
import ast
import logging
from collections import defaultdict, Counter
import ast
from collections import Counter
    
from fastapi import APIRouter, Query, HTTPException, Path as FastAPIPath, Depends
from treeline.models.graphing import DetailedAnalysisResponse, FileMetricsDetail, ComplexityBreakdown

detailed_metrics_router = APIRouter(prefix="/api/detailed-metrics", tags=["detailed_metrics"])
files_router = APIRouter(prefix="/api/file-metrics", tags=["file_metrics"])

logger = logging.getLogger(__name__)

@detailed_metrics_router.get("/", response_model=DetailedAnalysisResponse)
async def get_detailed_metrics(
    directory: str = Query(".", description="Directory to analyze"),
    max_depth: int = Query(1, description="Maximum depth for dependency analysis")
):
    """
    Get comprehensive detailed metrics for the entire codebase.
    Returns raw metrics for all files, functions, classes, and dependencies.
    """
    target_dir = Path(directory).resolve()
    
    from treeline.dependency_analyzer import ModuleDependencyAnalyzer
    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
    
    dep_analyzer = ModuleDependencyAnalyzer()
    code_analyzer = EnhancedCodeAnalyzer()
    
    dep_analyzer.analyze_directory(target_dir)
    file_results = code_analyzer.analyze_directory(target_dir)
    
    files_data = {}
    issues_summary = defaultdict(int)
    
    for category, issues in code_analyzer.quality_issues.items():
        for issue in issues:
            if isinstance(issue, dict) and 'file_path' in issue:
                file_path = issue['file_path']
                if file_path not in files_data:
                    files_data[file_path] = {
                        "path": file_path,
                        "lines": 0,
                        "functions": [],
                        "classes": [],
                        "imports": [],
                        "issues_by_category": defaultdict(list),
                        "metrics_summary": {}
                    }
                
                files_data[file_path]["issues_by_category"][category].append(issue)
                issues_summary[category] += 1
    
    for result in file_results:
        if result["type"] == "function":
            file_path = result.get("file_path")

            if not file_path or file_path == "unknown":
                continue        
        
            if file_path not in files_data:
                files_data[file_path] = {
                    "path": file_path,
                    "lines": 0,
                    "functions": [],
                    "classes": [],
                    "imports": [],
                    "issues_by_category": defaultdict(list),
                    "metrics_summary": {}
                }
            
            function_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "params": result["metrics"].get("params", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "cognitive_complexity": result["metrics"].get("cognitive_complexity", 0),
                "nested_depth": result["metrics"].get("nested_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "maintainability_index": result["metrics"].get("maintainability_index", 0),
                "cognitive_load": result["metrics"].get("cognitive_load", 0),
                "code_smells": result.get("code_smells", [])
            }
            
            files_data[file_path]["functions"].append(function_detail)
            
        elif result["type"] == "class":
            file_path = result.get("file_path", "unknown")
            if file_path not in files_data:
                files_data[file_path] = {
                    "path": file_path,
                    "lines": 0,
                    "functions": [],
                    "classes": [],
                    "imports": [],
                    "issues_by_category": defaultdict(list),
                    "metrics_summary": {}
                }
            
            class_methods = []
            if "methods" in result:
                for method_name, method_info in result["methods"].items():
                    method_detail = {
                        "name": method_name,
                        "line": method_info.get("line", 0),
                        "lines": method_info.get("lines", 0),
                        "params": method_info.get("params", 0),
                        "complexity": method_info.get("complexity", 0),
                        "code_smells": []
                    }
                    class_methods.append(method_detail)
            
            class_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "method_count": result["metrics"].get("methods", 0),
                "public_methods": result["metrics"].get("public_methods", 0),
                "private_methods": result["metrics"].get("private_methods", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "inheritance_depth": result["metrics"].get("inheritance_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "code_smells": result.get("code_smells", []),
                "methods": class_methods
            }
            
            files_data[file_path]["classes"].append(class_detail)
    
    for file_path in files_data:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                files_data[file_path]["lines"] = len(f.readlines())
        except (UnicodeDecodeError, IOError, FileNotFoundError) as e:
            files_data[file_path]["lines"] = 0
            if "issues_by_category" not in files_data[file_path]:
                files_data[file_path]["issues_by_category"] = {}
            if "file" not in files_data[file_path]["issues_by_category"]:
                files_data[file_path]["issues_by_category"]["file"] = []
            
            files_data[file_path]["issues_by_category"]["file"].append({
                "description": f"Could not read file: {str(e)}",
                "file_path": file_path,
                "line": None
            })
    
    nodes, links = dep_analyzer.get_graph_data()
    
    entry_points = dep_analyzer.get_entry_points()
    core_components = dep_analyzer.get_core_components()
    
    for module, imports in dep_analyzer.module_imports.items():
        for file_path, file_data in files_data.items():
            if module in file_path or os.path.basename(file_path).replace('.py', '') == module:
                file_data["imports"] = list(imports)
    
    total_functions = sum(len(file_data["functions"]) for file_data in files_data.values())
    total_classes = sum(len(file_data["classes"]) for file_data in files_data.values())
    total_lines = sum(file_data["lines"] for file_data in files_data.values())
    
    complexity_values = [func["complexity"] for file_data in files_data.values()
                         for func in file_data["functions"] if "complexity" in func]
    
    avg_complexity = sum(complexity_values) / len(complexity_values) if complexity_values else 0
    max_complexity = max(complexity_values) if complexity_values else 0
    
    project_metrics = {
        "total_files": len(files_data),
        "total_functions": total_functions,
        "total_classes": total_classes,
        "total_lines": total_lines,
        "avg_complexity": round(avg_complexity, 2),
        "complex_functions_count": len(dep_analyzer.complex_functions),
        "max_complexity": max_complexity
    }
    
    dependency_counts = [len(deps) for deps in dep_analyzer.module_imports.values()]
    avg_dependencies = sum(dependency_counts) / len(dependency_counts) if dependency_counts else 0
    max_dependencies = max(dependency_counts) if dependency_counts else 0
    
    dependency_metrics = {
        "entry_points": entry_points,
        "core_components": core_components,
        "nodes": len(nodes),
        "links": len(links),
        "avg_dependencies": round(avg_dependencies, 2),
        "max_dependencies": max_dependencies
    }
    
    for file_path, file_data in files_data.items():
        if isinstance(file_data["issues_by_category"], defaultdict):
            file_data["issues_by_category"] = dict(file_data["issues_by_category"])
    
    return {
        "files": files_data,
        "project_metrics": project_metrics,
        "dependency_metrics": dependency_metrics,
        "issues_summary": dict(issues_summary)
    }

@detailed_metrics_router.get("/file/{file_path:path}", response_model=FileMetricsDetail)
async def get_file_detailed_metrics(file_path: str = FastAPIPath(...)):
    try:
        with open(".treeline_dir", "r") as f:
            base_dir = Path(f.read().strip()).resolve()
    except FileNotFoundError:
        base_dir = Path(".").resolve()
    
    target_file = (base_dir / file_path).resolve()
    
    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
    
    code_analyzer = EnhancedCodeAnalyzer()
    
    file_results = code_analyzer.analyze_file(target_file)
    
    functions = []
    classes = []
    issues_by_category = defaultdict(list)
    
    file_path_str = str(target_file)
    for category, issues in code_analyzer.quality_issues.items():
        for issue in issues:
            if isinstance(issue, dict) and issue.get('file_path') == file_path_str:
                issues_by_category[category].append(issue)
    
    for result in file_results:
        if result["type"] == "function":
            function_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "params": result["metrics"].get("params", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "cognitive_complexity": result["metrics"].get("cognitive_complexity", 0),
                "nested_depth": result["metrics"].get("nested_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "maintainability_index": result["metrics"].get("maintainability_index", 0),
                "cognitive_load": result["metrics"].get("cognitive_load", 0),
                "code_smells": result.get("code_smells", [])
            }
            functions.append(function_detail)
            
        elif result["type"] == "class":
            class_methods = []
            if "methods" in result:
                for method_name, method_info in result["methods"].items():
                    method_detail = {
                        "name": method_name,
                        "line": method_info.get("line", 0),
                        "lines": method_info.get("lines", 0),
                        "params": method_info.get("params", 0),
                        "complexity": method_info.get("complexity", 0),
                        "code_smells": []
                    }
                    class_methods.append(method_detail)
            
            class_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "method_count": result["metrics"].get("methods", 0),
                "public_methods": result["metrics"].get("public_methods", 0),
                "private_methods": result["metrics"].get("private_methods", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "inheritance_depth": result["metrics"].get("inheritance_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "code_smells": result.get("code_smells", []),
                "methods": class_methods
            }
            classes.append(class_detail)
    
    line_count = 0
    imports = []
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
            line_count = len(content)
            
            for line in content:
                if line.strip().startswith(('import ', 'from ')):
                    imports.append(line.strip())
    except Exception as e:
        issues_by_category["file"].append({
            "description": f"Could not read file: {str(e)}",
            "file_path": file_path_str,
            "line": None
        })
    
    metrics_summary = {
        "lines": line_count,
        "functions": len(functions),
        "classes": len(classes),
        "imports": len(imports),
        "issues": sum(len(issues) for issues in issues_by_category.values()),
        "complexity": sum(func["complexity"] for func in functions),
        "avg_function_complexity": sum(func["complexity"] for func in functions) / len(functions) if functions else 0,
    }
    
    return {
        "path": file_path_str,
        "lines": line_count,
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "issues_by_category": dict(issues_by_category),
        "metrics_summary": metrics_summary
    }

@detailed_metrics_router.get("/complexity-breakdown", response_model=Dict[str, Union[ComplexityBreakdown, Dict[str, ComplexityBreakdown]]])
async def get_complexity_breakdown(
    directory: str = Query(".", description="Directory to analyze"),
    by_file: bool = Query(False, description="Break down complexity by file")
):
    """
    Get a detailed breakdown of what contributes to complexity in the codebase.
    """
    target_dir = Path(directory).resolve()

    class ComplexityBreakdownAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.breakdown = Counter()
            
        def visit_If(self, node):
            self.breakdown['if_statements'] += 1
            self.generic_visit(node)
            
        def visit_For(self, node):
            self.breakdown['for_loops'] += 1
            self.generic_visit(node)
            
        def visit_While(self, node):
            self.breakdown['while_loops'] += 1
            self.generic_visit(node)
            
        def visit_Try(self, node):
            self.breakdown['try_blocks'] += 1
            self.generic_visit(node)
            
        def visit_ExceptHandler(self, node):
            self.breakdown['except_blocks'] += 1
            self.generic_visit(node)
            
        def visit_BoolOp(self, node):
            if isinstance(node.op, ast.And):
                self.breakdown['and_operations'] += len(node.values) - 1
                self.breakdown['boolean_operations'] += len(node.values) - 1
            elif isinstance(node.op, ast.Or):
                self.breakdown['or_operations'] += len(node.values) - 1
                self.breakdown['boolean_operations'] += len(node.values) - 1
            self.generic_visit(node)
            
        def visit_ListComp(self, node):
            self.breakdown['list_comprehensions'] += 1
            self.breakdown['comprehensions'] += 1
            self.generic_visit(node)
            
        def visit_DictComp(self, node):
            self.breakdown['dict_comprehensions'] += 1
            self.breakdown['comprehensions'] += 1
            self.generic_visit(node)
            
        def visit_SetComp(self, node):
            self.breakdown['set_comprehensions'] += 1
            self.breakdown['comprehensions'] += 1
            self.generic_visit(node)
            
        def visit_GeneratorExp(self, node):
            self.breakdown['generator_expressions'] += 1
            self.generic_visit(node)
            
        def visit_Lambda(self, node):
            self.breakdown['lambda_functions'] += 1
            self.generic_visit(node)
            
        def visit_FunctionDef(self, node):
            parent = getattr(node, 'parent', None)
            if parent and isinstance(parent, ast.FunctionDef):
                self.breakdown['nested_functions'] += 1
            self.generic_visit(node)
            
        def visit_ClassDef(self, node):
            parent = getattr(node, 'parent', None)
            if parent and isinstance(parent, ast.ClassDef):
                self.breakdown['nested_classes'] += 1
            self.generic_visit(node)
    
    total_breakdown = Counter()
    file_breakdowns = {}
    
    for file_path in target_dir.rglob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    child.parent = parent
            
            analyzer = ComplexityBreakdownAnalyzer()
            analyzer.visit(tree)
            
            total_breakdown.update(analyzer.breakdown)
            
            if by_file:
                rel_path = file_path.relative_to(target_dir)
                file_breakdowns[str(rel_path)] = dict(analyzer.breakdown)
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    if by_file:
        return {
            "total": dict(total_breakdown),
            "by_file": file_breakdowns
        }
    
    return {"total": dict(total_breakdown)}

@detailed_metrics_router.get("/dependency-graph")
async def get_detailed_dependency_graph(
    directory: str = Query(".", description="Directory to analyze"),
    include_details: bool = Query(False, description="Include detailed node information")
):
    """
    Get detailed dependency graph including all connections between modules, classes, and functions.
    """
    target_dir = Path(directory).resolve()
    
    from treeline.dependency_analyzer import ModuleDependencyAnalyzer
    
    dep_analyzer = ModuleDependencyAnalyzer()
    
    dep_analyzer.analyze_directory(target_dir)
    
    nodes, links = dep_analyzer.get_graph_data()
    
    if include_details:
        for node in nodes:
            if node["type"] == "module":
                node["metrics"] = dep_analyzer.module_metrics.get(node["name"], {})
                
                node["functions"] = []
                node["classes"] = []
                
                for func_name, location in dep_analyzer.function_locations.items():
                    if isinstance(location, dict) and location.get("module") == node["name"]:
                        node["functions"].append({
                            "name": func_name,
                            "line": location.get("line", 0),
                            "file": location.get("file", "")
                        })
                
                for module_name, classes in dep_analyzer.class_info.items():
                    if module_name == node["name"]:
                        for class_name, info in classes.items():
                            node["classes"].append({
                                "name": class_name,
                                "line": info.get("line", 0),
                                "file": info.get("file", ""),
                                "methods": list(info.get("methods", {}).keys())
                            })
    
    return {
        "nodes": nodes,
        "links": links,
        "entry_points": dep_analyzer.get_entry_points(),
        "core_components": dep_analyzer.get_core_components(),
        # Cycles detection would require additional code
        "cycles": [],
        "module_metrics": dep_analyzer.module_metrics
    }

@detailed_metrics_router.get("/issues-by-category")
async def get_issues_by_category(
    directory: str = Query(".", description="Directory to analyze")
):
    """
    Get all quality issues grouped by category with detailed information.
    """
    target_dir = Path(directory).resolve()
    
    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
    
    code_analyzer = EnhancedCodeAnalyzer()
    
    code_analyzer.analyze_directory(target_dir)
    
    issues_by_category = {}
    
    for category, issues in code_analyzer.quality_issues.items():
        if issues:
            issues_by_category[category] = issues
    
    file_issues_count = {}
    
    for category, issues in code_analyzer.quality_issues.items():
        for issue in issues:
            if isinstance(issue, dict) and 'file_path' in issue:
                file_path = issue['file_path']
                if file_path not in file_issues_count:
                    file_issues_count[file_path] = defaultdict(int)
                file_issues_count[file_path][category] += 1
    
    files_with_most_issues = sorted(
        [(file_path, sum(counts.values())) for file_path, counts in file_issues_count.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return {
        "issues_by_category": issues_by_category,
        "total_issues": sum(len(issues) for issues in code_analyzer.quality_issues.values()),
        "files_with_most_issues": [
            {"file_path": file_path, "issue_count": count}
            for file_path, count in files_with_most_issues
        ],
        "category_counts": {
            category: len(issues) for category, issues in code_analyzer.quality_issues.items()
        }
    }
