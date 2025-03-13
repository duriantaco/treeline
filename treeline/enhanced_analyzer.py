import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from treeline.checkers.code_smells import CodeSmellChecker
from treeline.checkers.complexity import ComplexityAnalyzer
from treeline.checkers.duplication import DuplicationDetector
from treeline.checkers.security import SecurityAnalyzer
from treeline.models.enhanced_analyzer import QualityIssue
from treeline.checkers.magic_numbers import MagicNumberChecker
from treeline.checkers.sql_injection import SQLInjectionChecker
from treeline.checkers.style_checker import StyleChecker

class EnhancedCodeAnalyzer:
    def __init__(self, show_params: bool = True, config: Dict = None):
        self.show_params = show_params
        self.quality_issues = defaultdict(list)
        self.metrics_summary = defaultdict(dict)
        self.config = config or {}
        self.code_smell_checker = CodeSmellChecker(self.config)
        self.complexity_analyzer = ComplexityAnalyzer(self.config)
        self.security_analyzer = SecurityAnalyzer(self.config)
        self.duplication_detector = DuplicationDetector(self.config)
        self.magic_number_checker = MagicNumberChecker(self.config)
        self.sql_injection_checker = SQLInjectionChecker(self.config)
        self.style_checker = StyleChecker(self.config)

    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a file for code quality issues and structure"""
        try:
            content = self._read_file(file_path)
            if not content:
                return []
                
            tree = self._parse_content(content)
            if not tree:
                return []

            try:
                self.code_smell_checker.check(tree, file_path, self.quality_issues)
            except Exception as e:
                print(f"Error in code smell checker for {file_path}: {e}")
                
            try:
                self.complexity_analyzer.check(tree, file_path, self.quality_issues)
            except Exception as e:
                print(f"Error in complexity analyzer for {file_path}: {e}")
                
            try:
                self.security_analyzer.check(tree, file_path, self.quality_issues)
            except Exception as e:
                print(f"Error in security analyzer for {file_path}: {e}")
                
            try:
                self.magic_number_checker.check(tree, file_path, self.quality_issues)
            except Exception as e:
                print(f"Error in magic number checker for {file_path}: {e}")
                
            try:
                self.sql_injection_checker.check(tree, file_path, self.quality_issues)
            except Exception as e:
                print(f"Error in SQL injection checker for {file_path}: {e}")

            try:
                self.style_checker.check(file_path, self.quality_issues)
            except Exception as e:
                print(f"Error in style checker for {file_path}: {e}")

            results = self._analyze_code_elements(tree, content, file_path)
            
            for result in results:
                if 'code_smells' not in result:
                    result['code_smells'] = []
            
            self._add_file_issues_to_elements(results, file_path)
            
            return results
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return []

    def _add_file_issues_to_elements(self, elements: List[Dict], file_path: Path):
        """Add file-specific issues to the corresponding code elements"""
        file_path_str = str(file_path)
        
        file_issues = []
        for category, issues in self.quality_issues.items():
            for issue in issues:
                if isinstance(issue, dict) and issue.get('file_path') == file_path_str:
                    issue_with_category = issue.copy()
                    issue_with_category['category'] = category
                    file_issues.append(issue_with_category)
        
        if not file_issues:
            return
            
        elements_by_line = {}
        for element in elements:
            if 'line' in element:
                elements_by_line[element['line']] = element
        
        for issue in file_issues:
            issue_line = issue.get('line')
            if not issue_line:
                continue
                
            closest_element = None
            closest_distance = float('inf')
            
            for element_line, element in elements_by_line.items():
                if element_line <= issue_line:
                    distance = issue_line - element_line
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_element = element
            
            if closest_element and closest_distance <= 100:
                issue_text = f"[{issue['category']}] {issue.get('description', 'Unknown issue')}"
                if issue_line:
                    issue_text += f" (Line {issue_line})"
                    
                closest_element['code_smells'].append(issue_text)

    def analyze_directory(self, directory: Path) -> List[Dict]:
        results = []
        for file_path in directory.rglob("*.py"):
            results.extend(self.analyze_file(file_path))
        self.duplication_detector.analyze_directory(directory, self.quality_issues)
        return results

    def generate_report(self) -> str:
        report = ["# Code Quality Analysis Report"]
        for category, issues in self.quality_issues.items():
            report.append(f"## {category.title()}")
            for issue in issues:
                line_info = f" (Line {issue['line']})" if issue.get('line') else ""
                report.append(f"- {issue['description']}{line_info}")
        return "\n".join(report)

    def _read_file(self, file_path: Path) -> Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self._add_issue("file", f"Could not read file: {str(e)}")
            return None

    def _parse_content(self, content: str) -> Optional[ast.AST]:
        try:
            return ast.parse(content)
        except Exception as e:
            self._add_issue("parsing", f"Could not parse content: {str(e)}")
            return None

    def _add_issue(self, category: str, description: str, file_path: str = None, line: int = None):
        issue = QualityIssue(description=description, file_path=file_path, line=line)
        self.quality_issues[category].append(issue.__dict__)

    def _analyze_code_elements(self, tree: ast.AST, content: str, file_path: Path) -> List[Dict]:
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._analyze_function(node, content)
                self._add_quality_issues_to_element(func_info, node.lineno, file_path) 
                results.append(func_info)
                
            elif isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node, content)
                self._add_quality_issues_to_element(class_info, node.lineno, file_path)
                results.append(class_info)
    
        return results

    def _add_quality_issues_to_element(self, element_info: Dict, line_number: int, file_path: Path):
        if 'code_smells' not in element_info:
            element_info['code_smells'] = []
            
        file_path_str = str(file_path)
        
        for category, issues in self.quality_issues.items():
            for issue in issues:
                if (isinstance(issue, dict) and 
                    issue.get('file_path') == file_path_str and 
                    issue.get('line') is not None and
                    abs(issue.get('line') - line_number) <= 10):
                    
                    issue_text = f"[{category}] {issue.get('description')}"
                    if issue.get('line'):
                        issue_text += f" (Line {issue.get('line')})"
                    element_info['code_smells'].append(issue_text)

    def _analyze_function(self, node: ast.FunctionDef, content: str) -> Dict:
        func_lines = content.splitlines()[node.lineno-1:node.end_lineno]
        line_count = len(func_lines)
        docstring = ast.get_docstring(node)
        param_count = len(node.args.args)
        complexity = self._calculate_complexity(node)
        
        return {
            "type": "function",
            "name": node.name,
            "line": node.lineno,
            "docstring": docstring,
            "metrics": {
                "lines": line_count,
                "params": param_count,
                "complexity": complexity
            },
            "code_smells": []  
        }

    def _analyze_class(self, node: ast.ClassDef, content: str) -> Dict:
        class_lines = content.splitlines()[node.lineno-1:node.end_lineno]
        line_count = len(class_lines)
        docstring = ast.get_docstring(node)
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        
        return {
            "type": "class",
            "name": node.name,
            "line": node.lineno,
            "docstring": docstring,
            "metrics": {
                "lines": line_count,
                "methods": len(methods),
            },
            "code_smells": []  
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