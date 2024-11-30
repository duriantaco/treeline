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
        
    def analyze_directory(self, directory: Path):
        """Analyze all Python files in directory."""
        for file_path in directory.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                module_name = str(file_path.relative_to(directory)).replace('/', '.').replace('.py', '')
                self._analyze_imports(tree, module_name)
                self._collect_metrics(tree, module_name)
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
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
        """Generate Mermaid graph representation of module dependencies."""
        mermaid_lines = ['graph LR']
        
        for module in self.module_imports:
            clean_name = module.replace('.', '_')
            mermaid_lines.append(f'    {clean_name}["{module}"]')
        
        for module, imports in self.module_imports.items():
            clean_module = module.replace('.', '_')
            for imp in imports:
                if imp in self.module_imports:
                    clean_imp = imp.replace('.', '_')
                    mermaid_lines.append(f'    {clean_module} --> {clean_imp}')
        
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
            "%%{init: {'theme': 'neutral', 'flowchart': {'curve': 'monotoneX'}}}%%",
            self.generate_mermaid_graph(),
            "```"
        ])
        
        return "\n".join(lines)