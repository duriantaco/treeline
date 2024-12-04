from typing import List, Tuple, Dict, Set, Optional
import ast
from pathlib import Path
from collections import defaultdict

class ModuleDependencyAnalyzer:
    """Analyzes module-level dependencies and generates summary reports."""
    
    def __init__(self):
        self.module_imports = defaultdict(set)
        self.module_metrics = defaultdict(dict)
        self.complex_functions = []
        self.function_locations = defaultdict(dict)   
        self.function_calls = defaultdict(list)       
        self.class_info = defaultdict(dict)           
        
    def analyze_directory(self, directory: Path):
        """Analyze all Python files in directory."""
        for file_path in directory.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                module_name = str(file_path.relative_to(directory)).replace('/', '.').replace('.py', '')
                self._analyze_module(tree, module_name, str(file_path))
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

    def _analyze_module(self, tree: ast.AST, module_name: str, file_path: str):
        """Analyze a single module's contents and relationships."""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                setattr(child, 'parent', parent)
                
        self._analyze_imports(tree, module_name)
        self._collect_metrics(tree, module_name)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                parent = getattr(node, 'parent', None)
                if isinstance(parent, ast.Module):
                    self.function_locations[node.name] = {
                        'module': module_name,
                        'file': file_path,
                        'line': node.lineno
                    }
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            self.function_calls[child.func.id].append({
                                'from_module': module_name,
                                'from_function': node.name,
                                'line': child.lineno
                            })
            
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'module': module_name,
                    'file': file_path,
                    'line': node.lineno,
                    'methods': {}
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = f"{node.name}.{item.name}"
                        class_info['methods'][item.name] = {
                            'line': item.lineno,
                            'calls': []
                        }
                        for child in ast.walk(item):
                            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                                class_info['methods'][item.name]['calls'].append(child.func.id)
                
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
                if complexity > 10:  # Threshold for complex functions
                    self.complex_functions.append((module_name, node.name, complexity))
                total_complexity += complexity
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        self.module_metrics[module_name] = {
            'functions': len(functions),
            'classes': len(classes),
            'complexity': total_complexity
        }
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def generate_mermaid_graph(self) -> str:
        """Generate detailed Mermaid graph showing module, function, and class relationships."""
        mermaid_lines = ['graph TD']
        mermaid_lines.append('    %% Styling')
        mermaid_lines.append('    classDef module fill:#b7e2d8,stroke:#333,stroke-width:2px;')
        mermaid_lines.append('    classDef function fill:#e4d1d1,stroke:#333;')
        mermaid_lines.append('    classDef class fill:#d1e0e4,stroke:#333;')
        
        for module in self.module_imports:
            clean_module = module.replace('.', '_')
            
            mermaid_lines.append(f'    subgraph {clean_module}["{module}"]')
            mermaid_lines.append(f'        {clean_module}_node["{module}"]:::module')
            
            for func_name, location in self.function_locations.items():
                if location['module'] == module:
                    if 'in_class' not in location:  
                        clean_func = f"{clean_module}_{func_name}"
                        mermaid_lines.append(f'        {clean_func}["⚡ {func_name}()"]:::function')
                        mermaid_lines.append(f'        {clean_module}_node --> {clean_func}')
            
            if module in self.class_info:
                for class_name, info in self.class_info[module].items():
                    clean_class = f"{clean_module}_{class_name}"
                    mermaid_lines.append(f'        {clean_class}["📦 {class_name}"]:::class')
                    mermaid_lines.append(f'        {clean_module}_node --> {clean_class}')
                    
                    for method_name in info['methods']:
                        clean_method = f"{clean_class}_{method_name}"
                        mermaid_lines.append(f'        {clean_method}["⚡ {method_name}()"]:::function')
                        mermaid_lines.append(f'        {clean_class} --> {clean_method}')
            
            mermaid_lines.append('    end')
        
        for func_name, calls in self.function_calls.items():
            for call in calls:
                from_module = call['from_module'].replace('.', '_')
                if func_name in self.function_locations:
                    to_module = self.function_locations[func_name]['module'].replace('.', '_')
                    from_func = f"{from_module}_{call['from_function']}"
                    to_func = f"{to_module}_{func_name}"
                    mermaid_lines.append(f'    {from_func} -.->|calls| {to_func}')
        
        for module, imports in self.module_imports.items():
            clean_module = module.replace('.', '_')
            for imp in imports:
                if imp in self.module_imports:  
                    clean_imp = imp.replace('.', '_')
                    mermaid_lines.append(f'    {clean_module}_node --> {clean_imp}_node')
        
        return '\n'.join(mermaid_lines)

    def generate_summary_report(self) -> str:
        """Generate a readable markdown report without tables."""
        lines = ["# Code Analysis Summary Report\n"]
        
        lines.append("## Module Metrics\n")
        for module, metrics in sorted(self.module_metrics.items()):
            lines.append(f"### {module}")
            lines.append(f"- Functions: **{metrics['functions']}**")
            lines.append(f"- Classes: **{metrics['classes']}**")
            lines.append(f"- Complexity: **{metrics['complexity']}**")
            
            if module in self.class_info:
                lines.append("\nClasses:")
                for class_name, info in self.class_info[module].items():
                    lines.append(f"\n#### 📦 {class_name}")
                    lines.append(f"- Defined at line {info['line']}")
                    if info['methods']:
                        lines.append("- Methods:")
                        for method_name, method_info in info['methods'].items():
                            lines.append(f"  - ⚡ {method_name} (line {method_info['line']})")
                            if method_info['calls']:
                                lines.append(f"    Calls: {', '.join(method_info['calls'])}")
            
            functions_in_module = [f for f, loc in self.function_locations.items() 
                                 if loc['module'] == module and 'in_class' not in loc]
            if functions_in_module:
                lines.append("\nFunctions:")
                for func in functions_in_module:
                    lines.append(f"\n#### ⚡ {func}")
                    if func in self.function_calls:
                        lines.append("Called by:")
                        for call in self.function_calls[func]:
                            lines.append(f"- {call['from_function']} in {call['from_module']} (line {call['line']})")
            
            lines.append("") 
        
        lines.append("## Complexity Hotspots\n")
        if self.complex_functions:
            sorted_hotspots = sorted(self.complex_functions, key=lambda x: x[2], reverse=True)
            for module, func, complexity in sorted_hotspots:
                lines.append(f"### {func}")
                lines.append(f"- **Module**: {module}")
                lines.append(f"- **Complexity**: {complexity}")
                lines.append("")
        else:
            lines.append("*No complex functions found.*\n")
        
        lines.extend([
            "## Module Dependencies\n",
            "```mermaid",
            self.generate_mermaid_graph(),
            "```"
        ])
        
        return "\n".join(lines)