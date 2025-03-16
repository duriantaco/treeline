import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from treeline.checkers.code_smells import CodeSmellChecker
from treeline.checkers.complexity import ComplexityAnalyzer
from treeline.checkers.duplication import DuplicationDetector
from treeline.checkers.security import SecurityAnalyzer
from treeline.models.enhanced_analyzer import QualityIssue
from treeline.checkers.sql_injection import SQLInjectionChecker
from treeline.checkers.style_checker import StyleChecker
from treeline.checkers.unused_code import UnusedCodeChecker
from treeline.utils.metrics import calculate_cyclomatic_complexity
from treeline.config_manager import get_config
from concurrent.futures import ProcessPoolExecutor

class EnhancedCodeAnalyzer:
    def __init__(self, show_params: bool = True, config: Dict = None):
        self.show_params = show_params
        self.quality_issues = defaultdict(list)
        self.metrics_summary = defaultdict(dict)
        
        self.config = config or get_config().as_dict()

        self.config = config or {}
        self.code_smell_checker = CodeSmellChecker(self.config)
        self.complexity_analyzer = ComplexityAnalyzer(self.config)
        self.security_analyzer = SecurityAnalyzer(self.config)
        self.duplication_detector = DuplicationDetector(self.config)
        self.sql_injection_checker = SQLInjectionChecker(self.config)
        self.style_checker = StyleChecker(self.config)
        self.unused_code_checker = UnusedCodeChecker(self.config) 

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
        file_issues = [
            {
                'type': category,
                'description': issue.get('description', 'Unknown issue'),
                'line': issue.get('line'),
                'severity': issue.get('severity', 'medium')
            }
            for category, issues in self.quality_issues.items()
            for issue in issues if isinstance(issue, dict) and issue.get('file_path') == str(file_path)
        ]
        if not file_issues:
            return

        elements.sort(key=lambda e: e.get('line', 0))
        file_issues.sort(key=lambda i: i.get('line', 0))

        element_idx = 0
        for issue in file_issues:
            issue_line = issue.get('line')
            if not issue_line:
                continue

            while element_idx < len(elements) and elements[element_idx].get('line', 0) < issue_line:
                element_idx += 1

            if element_idx > 0 and element_idx < len(elements):
                prev_line = elements[element_idx - 1].get('line', 0)
                curr_line = elements[element_idx].get('line', 0)
                if abs(issue_line - prev_line) < abs(issue_line - curr_line):
                    closest_element = elements[element_idx - 1]
                else:
                    closest_element = elements[element_idx]
            elif element_idx == 0 and elements:
                closest_element = elements[0]
            elif element_idx == len(elements) and elements:
                closest_element = elements[-1]
            else:
                continue

            if 'code_smells' not in closest_element:
                closest_element['code_smells'] = []
            if issue not in closest_element['code_smells']:
                closest_element['code_smells'].append(issue)

    def analyze_directory(self, directory: Path) -> List[Dict]:
        results = []
        python_files = list(directory.rglob("*.py"))

        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.analyze_file, file_path) for file_path in python_files]
            for future in futures:
                results.extend(future.result())

        self.duplication_detector.analyze_directory(directory, self.quality_issues)
        self.unused_code_checker.finalize_checks(self.quality_issues)

        return results

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
                    
                    new_issue = {
                        'type': category,
                        'description': issue.get('description', 'Unknown issue'),
                        'line': issue.get('line'),
                        'severity': issue.get('severity', 'medium')
                    }
                    if new_issue not in element_info['code_smells']:
                        element_info['code_smells'].append(new_issue)

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
        return calculate_cyclomatic_complexity(node)
    