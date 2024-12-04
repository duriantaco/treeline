from typing import List, Tuple, Dict, Optional, Set
import ast
from pathlib import Path
from collections import defaultdict

class EnhancedCodeAnalyzer:
    """
    Enhanced analyzer for code quality and maintainability metrics.
    
    This analyzer implements industry-standard code quality checks and metrics
    following Clean Code principles, SOLID principles, and PEP 8 standards.
    """
    
    QUALITY_METRICS = {
        'MAX_FUNCTION_LINES': 20,       
        'MAX_PARAMS': 3,                 
        'MAX_RETURNS': 3,             
        'MAX_COGNITIVE_COMPLEXITY': 15,   
        'MAX_CYCLOMATIC_COMPLEXITY': 10,  
        'MAX_NESTED_DEPTH': 3,           
        'MAX_CLASS_LINES': 200,         
        'MAX_METHODS_PER_CLASS': 10,     
        'MAX_CLASS_COMPLEXITY': 50,      
        'MAX_FILE_LINES': 400,          
        'MAX_LINE_LENGTH': 79,           
        'MIN_DOCSTRING_COVERAGE': 0.8,   
        'MIN_COMMENT_RATIO': 0.15,       
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
    
    def _analyze_file_metrics(self, content: str, file_path: Path) -> None:
        """
        Analyze file-level metrics for code quality issues.
        
        Args:
            content: The file content as a string
            file_path: Path to the file being analyzed
        """
        lines = content.split('\n')
        total_lines = len(lines)
        file_path_str = str(file_path)
        
        if total_lines > self.QUALITY_METRICS['MAX_FILE_LINES']:
            self._add_issue('file', f"File exceeds maximum length ({total_lines} lines)", file_path_str)
        
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > self.QUALITY_METRICS['MAX_LINE_LENGTH']:
                self._add_issue('file', f"Line {i} exceeds maximum length ({len(line)} characters)", file_path_str, i)

        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
        
        if comment_ratio < self.QUALITY_METRICS['MIN_COMMENT_RATIO']:
            self._add_issue('documentation', f"Low comment ratio ({comment_ratio:.2%})", file_path_str)
        
        self.metrics_summary['file'][file_path_str] = {
            'total_lines': total_lines,
            'comment_lines': comment_lines,
            'comment_ratio': comment_ratio
        }

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read and return file content safely."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self._add_issue('file', f"Could not read file: {str(e)}")
            return None

    def _parse_content(self, content: str) -> Optional[ast.AST]:
        """Parse Python content into AST safely."""
        try:
            return ast.parse(content)
        except Exception as e:
            self._add_issue('parsing', f"Could not parse content: {str(e)}")
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
            'type': 'class',
            'name': node.name,
            'docstring': ast.get_docstring(node) or '',
            'metrics': self._calculate_class_metrics(node, content),
            'code_smells': []
        }
        
        self._check_class_metrics(metrics)
        return metrics

    def _calculate_class_metrics(self, node: ast.ClassDef, content: str) -> Dict:
        """Calculate comprehensive metrics for a class."""
        methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
        return {
            'lines': node.end_lineno - node.lineno + 1,
            'method_count': len(methods),
            'complexity': sum(self._calculate_complexity(m) for m in methods),
            'has_docstring': bool(ast.get_docstring(node)),
            'public_methods': len([m for m in methods if not m.name.startswith('_')]),
            'private_methods': len([m for m in methods if m.name.startswith('_')])
        }

    def _check_class_metrics(self, class_data: Dict) -> None:
        """Check class metrics against quality thresholds."""
        metrics = class_data['metrics']
        smells = class_data['code_smells']
        
        if metrics['lines'] > self.QUALITY_METRICS['MAX_CLASS_LINES']:
            smells.append('Class too long')
            
        if metrics['method_count'] > self.QUALITY_METRICS['MAX_METHODS_PER_CLASS']:
            smells.append('Too many methods')
            
        if metrics['complexity'] > self.QUALITY_METRICS['MAX_CLASS_COMPLEXITY']:
            smells.append('High class complexity')
            
        if not metrics['has_docstring']:
            smells.append('Missing class docstring')

    def format_structure(self, structure: List[Dict], indent: str = "") -> List[str]:
        """Format analysis results into a readable tree structure."""
        lines = []
        
        for item in structure:
            if lines:
                lines.append(indent)
            
            item_type = item.get('type', '')
            name = item.get('name', '')
            docstring = item.get('docstring', '')
            metrics = item.get('metrics', {})
            code_smells = item.get('code_smells', [])
            
            if item_type == 'class':
                lines.append(f"{indent}[CLASS] 🏛️ {name}")
                if metrics.get('method_count'):
                    lines.append(f"{indent}  └─ Methods: {metrics['method_count']}")
            elif item_type == 'function':
                lines.append(f"{indent}[FUNC] ⚡ {name}")
            else:
                lines.append(f"{indent}⚠️ {name}")
                continue
            
            if docstring:
                lines.append(f"{indent}  └─ # {docstring}")
            
            if 'lines' in metrics:
                lines.append(f"{indent}  └─ 📏 Lines: {metrics['lines']}")
            
            for smell in code_smells:
                lines.append(f"{indent}  └─ ⚠️ {smell}")
        
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
            'type': 'function',
            'name': node.name,
            'docstring': ast.get_docstring(node) or '',
            'metrics': self._calculate_function_metrics(node, content),
            'code_smells': []
        }
        
        self._check_function_metrics(metrics)
        return metrics

    def _calculate_function_metrics(self, node: ast.FunctionDef, content: str) -> Dict:
        """Calculate comprehensive metrics for a function."""
        return {
            'lines': node.end_lineno - node.lineno + 1,
            'params': len(node.args.args),
            'returns': len([n for n in ast.walk(node) if isinstance(n, ast.Return)]),
            'complexity': self._calculate_complexity(node),
            'nested_depth': self._calculate_nested_depth(node),
            'has_docstring': bool(ast.get_docstring(node))
        }

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

    def _check_function_metrics(self, func_data: Dict) -> None:
        """Check function metrics against quality thresholds."""
        metrics = func_data['metrics']
        smells = func_data['code_smells']
        
        if metrics['lines'] > self.QUALITY_METRICS['MAX_FUNCTION_LINES']:
            smells.append('Function too long')
            
        if metrics['params'] > self.QUALITY_METRICS['MAX_PARAMS']:
            smells.append('Too many parameters')
            
        if metrics['complexity'] > self.QUALITY_METRICS['MAX_CYCLOMATIC_COMPLEXITY']:
            smells.append('High complexity')
            
        if not metrics['has_docstring']:
            smells.append('Missing docstring')

    def _add_issue(self, category: str, description: str, file_path: str = None, line: int = None) -> None:
        """
        Add a quality issue to the collection.
        
        Args:
            category: The category of the issue
            description: Description of the issue
            file_path: Optional path to the file where the issue was found
            line: Optional line number where the issue was found
        """
        issue = {
            'description': description,
            'file_path': file_path,
            'line': line
        }
        self.quality_issues[category].append(issue)
        
    def generate_report(self) -> str:
        """Generate a formatted quality report."""
        return self._format_report_sections([
            self._format_overview_section(),
            self._format_issues_section(),
            self._format_metrics_section()
        ])

    def _format_report_sections(self, sections: List[str]) -> str:
        """Format and combine report sections."""
        return "\n\n".join(section for section in sections if section)

    def _format_overview_section(self) -> str:
        """Format the report overview section."""
        return "# Code Quality Analysis Report\n\n" + \
               "Analysis completed with the following results:"

    def _format_issues_section(self) -> str:
        """Format the quality issues section."""
        if not self.quality_issues:
            return "No quality issues found."
            
        lines = ["## Quality Issues"]
        for category, issues in self.quality_issues.items():
            lines.append(f"\n### {category.title()}")
            for issue in issues:
                lines.append(f"- {issue['description']}")
                if issue.get('line'):
                    lines.append(f"  Line: {issue['line']}")
        return "\n".join(lines)