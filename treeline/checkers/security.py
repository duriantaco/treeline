import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

class SecurityAnalyzer:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        self.security_patterns = {
            "credential": {
                "patterns": [
                    (r'(?:password|passwd|pwd).*=.*[\'"][^\'"]{3,}[\'"]', "high"),
                    (r'(?:api_?key|apikey|secret|token).*=.*[\'"][^\'"]{8,}[\'"]', "high"),
                    (r'auth.*=.*[\'"][^\'"]{8,}[\'"]', "medium"),
                ],
                "exclude_patterns": [
                    r'example|sample|placeholder|default|fake|test',
                    r'password.*required|password.*field|password.*\(|password.*\)',
                    r'token.*required|token.*field|token.*\(|token.*\)',
                ],
                "message": "Possible hardcoded credential"
            },
            
            "sql_injection": {
                "patterns": [
                    (r'execute\(.*\+', "high"),
                    (r'execute\(.*\.format', "high"),
                    (r'execute\(.*%', "high"),
                    (r'execute\(.*f[\'"]', "high"),
                ],
                "exclude_patterns": [],
                "message": "Potential SQL injection risk"
            },
            
            "command_injection": {
                "patterns": [
                    (r'(?:os\.system|subprocess\.call|subprocess\.Popen|exec|eval)\(.*\+', "high"),
                    (r'(?:os\.system|subprocess\.call|subprocess\.Popen|exec|eval)\(.*\.format', "high"),
                    (r'(?:os\.system|subprocess\.call|subprocess\.Popen|exec|eval)\(.*%', "high"),
                    (r'(?:os\.system|subprocess\.call|subprocess\.Popen|exec|eval)\(.*f[\'"]', "high"),
                ],
                "exclude_patterns": [],
                "message": "Potential command injection risk"
            },
            
            "insecure_function": {
                "patterns": [
                    (r'pickle\.loads', "medium"),
                    (r'yaml\.load\s*\((?!.*Loader=yaml\.SafeLoader)', "medium"),
                    (r'hashlib\.md5\(', "low"),
                    (r'hashlib\.sha1\(', "low"),
                    (r'random\.(random|randint)', "low"),
                ],
                "exclude_patterns": [
                    r'test_',
                    r'example',
                ],
                "message": "Use of potentially insecure function"
            }
        }

    def check(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            self._check_regex_patterns(lines, file_path, quality_issues)
            self._check_dangerous_ast_patterns(tree, file_path, quality_issues)
            
        except Exception as e:
            quality_issues["security"].append({
                "description": f"Error during security analysis: {str(e)}",
                "file_path": str(file_path),
                "line": None,
                "severity": "low"
            })

    def _check_regex_patterns(self, lines: List[str], file_path: Path, quality_issues: defaultdict):
        for i, line in enumerate(lines, start=1):
            for category, config in self.security_patterns.items():
                if any(re.search(ex_pattern, line, re.IGNORECASE) for ex_pattern in config["exclude_patterns"]):
                    continue
                
                for pattern, severity in config["patterns"]:
                    if re.search(pattern, line, re.IGNORECASE):
                        if category == "credential" and self._is_credential_false_positive(line):
                            continue
                        
                        quality_issues["security"].append({
                            "description": f"{config['message']} ({category})",
                            "file_path": str(file_path),
                            "line": i,
                            "severity": severity
                        })
                        break

    def _is_credential_false_positive(self, line: str) -> bool:
        if re.search(r'[\'"].*\{.*\}.*[\'"]', line):
            return True
            
        if re.search(r'(?:password|apikey|secret|token).*=.*[\'"][^\'"]{1,7}[\'"]', line, re.IGNORECASE):
            return True
            
        if re.search(r'(?:password|apikey|secret|token).*=.*os\.environ', line, re.IGNORECASE):
            return True
            
        if re.search(r'(?:user|admin|test|example|dummy|foo|bar)', line, re.IGNORECASE):
            return True
            
        return False

    def _check_dangerous_ast_patterns(self, tree: ast.AST, file_path: Path, quality_issues: defaultdict):
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and
                ((isinstance(node.func, ast.Name) and node.func.id == 'open') or
                (isinstance(node.func, ast.Attribute) and node.func.attr in ['open', 'read', 'write']))):
                
                for arg in node.args:
                    if isinstance(arg, ast.BinOp) or (
                        isinstance(arg, ast.Call) and
                        isinstance(arg.func, ast.Attribute) and
                        arg.func.attr == 'format'
                    ):
                        quality_issues["security"].append({
                            "description": "Potential path traversal vulnerability in file operation",
                            "file_path": str(file_path),
                            "line": node.lineno,
                            "severity": "high"
                        })
                        break
            # Keep existing checks for eval, input, etc.
            if (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'eval'):
                quality_issues["security"].append({
                    "description": "Use of eval() function - potential security risk",
                    "file_path": str(file_path),
                    "line": node.lineno,
                    "severity": "high"
                })
            if (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'input'):
                parent = self._get_parent(node, tree)
                if parent and isinstance(parent, ast.Call) and hasattr(parent.func, 'id'):
                    if parent.func.id in ['eval', 'exec', 'os.system', 'subprocess.call']:
                        quality_issues["security"].append({
                            "description": f"User input passed directly to {parent.func.id} - critical security risk",
                            "file_path": str(file_path),
                            "line": node.lineno,
                            "severity": "critical"
                        })

    def _get_parent(self, node, tree):
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    return parent
        return None