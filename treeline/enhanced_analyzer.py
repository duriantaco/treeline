from typing import List, Tuple, Dict, Optional
import ast
from pathlib import Path
from collections import defaultdict
from .analyzer import CodeAnalyzer

class EnhancedCodeAnalyzer(CodeAnalyzer):
    """Enhanced analyzer focused on code quality metrics."""
    
    COMPLEXITY_THRESHOLD = 10
    MAX_PARAMS = 5
    MAX_LINES = 30
    
    def __init__(self, show_params=True, show_relationships=True):
        super().__init__(show_params, show_relationships)
        self.COLORS.update({
            'RED': '\033[91m',       # Warnings
            'GRAY': '\033[90m',      # Stats
        })
    
    def analyze_file(self, file_path: Path) -> List[Tuple[str, str, str, Optional[str], Optional[str], Dict]]:
        """Analyzes Python files with additional code quality metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            structure = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    name = node.name
                    doc = ast.get_docstring(node) or ''
                    params = self._get_function_params(node) if self.show_params else ''
                    metrics = self._analyze_function_metrics(node, content)
                    
                    structure.append(('function', name, doc, params, '', metrics))
                
                elif isinstance(node, ast.ClassDef):
                    name = node.name
                    doc = ast.get_docstring(node) or ''
                    metrics = self._analyze_class_metrics(node, content)
                    
                    structure.append(('class', name, doc, '', '', metrics))
            
            return structure
            
        except Exception as e:
            return [('error', f"Could not parse file: {str(e)}", '', '', '', {})]

    def format_structure(self, structure: List[Tuple[str, str, str, str, str, Dict]], indent: str = "") -> List[str]:
        """Formats the code structure with metrics on separate lines."""
        lines = []
        
        for item_type, name, doc, params, relationship, metrics in structure:
            if lines:
                vertical_line = "│" if "│" in indent else " "
                lines.append(f"{indent}")
            
            symbol = self.get_symbol(item_type)
            
            if item_type == 'class':
                prefix = f"{self.COLORS['PURPLE']}{self.COLORS['BOLD']}[CLASS]{self.COLORS['END']}"
                name_colored = f"{self.COLORS['PURPLE']}{name}{self.COLORS['END']}"
            else:
                prefix = f"{self.COLORS['BLUE']}{self.COLORS['BOLD']}[FUNC]{self.COLORS['END']}"
                name_colored = f"{self.COLORS['BLUE']}{name}{self.COLORS['END']}"
            
            if params:
                params_colored = f"{self.COLORS['YELLOW']}{params}{self.COLORS['END']}"
                lines.append(f"{indent}{prefix} {symbol} {name_colored}{params_colored}")
            else:
                lines.append(f"{indent}{prefix} {symbol} {name_colored}")
            
            if doc:
                doc_clean = ' '.join(line.strip() for line in doc.split('\n') if line.strip())
                lines.append(f"{indent}  └─ {self.COLORS['GREEN']}# {doc_clean}{self.COLORS['END']}")
            
            if metrics:
                if 'complexity' in metrics and metrics['complexity'] > self.COMPLEXITY_THRESHOLD:
                    lines.append(f"{indent}  └─ {self.COLORS['RED']}⚠️ High complexity ({metrics['complexity']}){self.COLORS['END']}")
                
                if 'code_smells' in metrics and metrics['code_smells']:
                    for smell in metrics['code_smells']:
                        lines.append(f"{indent}  └─ {self.COLORS['RED']}{smell}{self.COLORS['END']}")
                
                if 'lines' in metrics:
                    lines.append(f"{indent}  └─ {self.COLORS['GRAY']}📏 Lines: {metrics['lines']}{self.COLORS['END']}")
                
                if 'method_count' in metrics and metrics['method_count'] > 10:
                    lines.append(f"{indent}  └─ {self.COLORS['RED']}⚠️ Large class ({metrics['method_count']} methods){self.COLORS['END']}")
            
        return lines

    def _analyze_function_metrics(self, node: ast.FunctionDef, content: str) -> Dict:
        """Calculate function metrics."""
        complexity = self._calculate_complexity(node)
        code_smells = []
        
        if len(node.args.args) > self.MAX_PARAMS:
            code_smells.append(f"⚠️ Too many parameters ({len(node.args.args)})")
        
        lines = len(content.splitlines()[node.lineno-1:node.end_lineno])
        if lines > self.MAX_LINES:
            code_smells.append(f"⚠️ Long function ({lines} lines)")
        
        return {
            'complexity': complexity,
            'code_smells': code_smells,
            'lines': lines
        }
    
    def _analyze_class_metrics(self, node: ast.ClassDef, content: str) -> Dict:
        """Calculate class metrics."""
        return {
            'method_count': len([n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]),
            'lines': len(content.splitlines()[node.lineno-1:node.end_lineno])
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