import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

class SQLInjectionChecker:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        self.sql_functions = [
            'execute', 'executemany', 'executescript', 'query', 'raw', 
            'raw_query', 'cursor.execute', 'connection.execute'
        ]
        
        self.safe_patterns = [
            r'.*\?\s*(?:,|\))',
            r'.*%s\s*(?:,|\))',
            r'.*:\w+\s*(?:,|\))',
            r'.*\$\d+\s*(?:,|\))',
            r'.*VALUES\s*\(\s*%s\s*\)',
            r'.*\.format\(\s*sql.Literal',
            r'.*\.format\(\s*sql.Identifier',
            r'.*params\s*=\s*\{',
            r'.*query_params\s*=\s*\{',
            r'.*paramstyle\s*=',
        ]
        
        self.risk_patterns = [
            (r'.*\+\s*[\'"]\s*\+\s*', 'high'),
            (r'.*\+\s*(?:str\()?\s*\w+\s*(?:\))?\s*(?:\+|,)', 'high'),
            (r'.*\.format\(.*\)', 'medium'),
            (r'.*%.*%\s*(?:,|\))', 'medium'),
            (r'.*f[\'"].*\{.*\}', 'high'),
        ]

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            self._check_ast_for_sql_injection(tree, file_path, quality_issues, lines)
                
        except Exception as e:
            quality_issues["security"].append({
                "description": f"Error checking for SQL injection: {str(e)}",
                "file_path": str(file_path),
                "line": None,
                "severity": "low"
            })

    def _check_ast_for_sql_injection(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict, lines: List[str]):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_func_name(node)
                
                if func_name and any(sql_func in func_name for sql_func in self.sql_functions):
                    line_num = node.lineno
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    if any(re.match(pattern, line_content) for pattern in self.safe_patterns):
                        continue
                    
                    for pattern, severity in self.risk_patterns:
                        if re.match(pattern, line_content):
                            quality_issues["security"].append({
                                "description": f"Potential SQL injection: {func_name} with unsanitized input",
                                "file_path": str(file_path),
                                "line": line_num,
                                "severity": severity,
                                "code": line_content.strip()
                            })
                            break
                    
                    if node.args and self._has_injection_risk(node.args[0]):
                        quality_issues["security"].append({
                            "description": f"Potential SQL injection in {func_name}: Query contains dynamic values",
                            "file_path": str(file_path),
                            "line": line_num,
                            "severity": "high",
                            "code": line_content.strip()
                        })

    def _get_func_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            return node.func.attr
        return None

    def _has_injection_risk(self, arg_node: ast.AST) -> bool:
        if isinstance(arg_node, ast.BinOp) and isinstance(arg_node.op, (ast.Add)):
            return True
            
        if isinstance(arg_node, ast.Call):
            if (isinstance(arg_node.func, ast.Attribute) and 
                arg_node.func.attr in ['format', 'replace', 'join']):
                return True
                
            if (isinstance(arg_node.func, ast.Name) and 
                arg_node.func.id in ['format', 'f']):
                return True
                
        if isinstance(arg_node, ast.JoinedStr):
            return True
            
        if isinstance(arg_node, ast.FormattedValue):
            return True
            
        return False