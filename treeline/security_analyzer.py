from typing import List, Dict, Optional, Set
import ast
from pathlib import Path
import re
from collections import defaultdict

class SecurityAnalyzer:
    """
    Security analyzer for Python code to detect potential vulnerabilities and risks.
    Follows OWASP guidelines and common security best practices.
    """
    
    VULNERABILITY_PATTERNS = {
        'sql_injection': {
            'patterns': [
                r'execute\s*\(.*[\%\+].*\)',
                r'cursor\.execute\s*\(.*[\%\+].*\)',
                r'raw_input\s*\(.*\)'
            ],
            'severity': 'HIGH',
            'description': 'Potential SQL injection vulnerability'
        },
        'command_injection': {
            'patterns': [
                r'subprocess\.call',
                r'subprocess\.Popen',
                r'os\.system',
                r'os\.popen',
                r'eval\(',
                r'exec\(',
            ],
            'severity': 'HIGH',
            'description': 'Potential command injection vulnerability'
        },
        'path_traversal': {
            'patterns': [
                r'\.\./',
                r'\.\.\\',
                r'open\s*\([^)]*[\+]',
            ],
            'severity': 'HIGH',
            'description': 'Potential path traversal vulnerability'
        },
        'hardcoded_secrets': {
            'patterns': [
                r'password\s*=\s*[\'"][^\'"]+[\'"]',
                r'secret\s*=\s*[\'"][^\'"]+[\'"]',
                r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]',
                r'token\s*=\s*[\'"][^\'"]+[\'"]',
            ],
            'severity': 'HIGH',
            'description': 'Hardcoded secret detected'
        },
        'insecure_crypto': {
            'patterns': [
                r'md5',
                r'sha1',
                r'hashlib\.md5',
                r'hashlib\.sha1',
            ],
            'severity': 'MEDIUM',
            'description': 'Use of weak cryptographic algorithm'
        },
        'insecure_deserialization': {
            'patterns': [
                r'pickle\.loads?',
                r'yaml\.load(?!s)',
                r'marshal\.loads?',
            ],
            'severity': 'HIGH',
            'description': 'Unsafe deserialization detected'
        },
        'insecure_random': {
            'patterns': [
                r'random\.',
                r'randint',
            ],
            'severity': 'LOW',
            'description': 'Use of insecure random number generator'
        },
        'info_exposure': {
            'patterns': [
                r'print\s*\([^)]*exception',
                r'traceback\.print_exc',
                r'debug\s*=\s*True',
            ],
            'severity': 'MEDIUM',
            'description': 'Potential information exposure'
        }
    }
    
    def __init__(self):
        """Initialize the security analyzer."""
        self.security_issues = defaultdict(list)
        self.stats = defaultdict(int)
        
    def analyze_file(self, file_path: Path) -> Dict:
        """
        Analyze a Python file for security vulnerabilities.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            Dictionary containing security analysis results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            self._scan_patterns(content, file_path)
            self._analyze_ast_security(tree, file_path)
            
            return {
                'issues': dict(self.security_issues),
                'stats': dict(self.stats)
            }
                
        except Exception as e:
            return {'error': f"Could not analyze file: {str(e)}"}

    def _scan_patterns(self, content: str, file_path: Path) -> None:
        """Scan code for vulnerable patterns using regex."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for vuln_type, config in self.VULNERABILITY_PATTERNS.items():
                for pattern in config['patterns']:
                    if re.search(pattern, line, re.IGNORECASE):
                        self._add_security_issue(
                            vuln_type=vuln_type,
                            file_path=file_path,
                            line_number=i,
                            line_content=line.strip(),
                            severity=config['severity'],
                            description=config['description']
                        )
                        self.stats[vuln_type] += 1

    def _analyze_ast_security(self, tree: ast.AST, file_path: Path) -> None:
        """Analyze AST for security issues."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                self._check_dangerous_attributes(node, file_path)
            
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self._check_dangerous_imports(node, file_path)
            
            elif isinstance(node, ast.Call):
                self._check_dangerous_calls(node, file_path)

    def _check_dangerous_attributes(self, node: ast.Attribute, file_path: Path) -> None:
        """Check for access to dangerous attributes."""
        dangerous_attrs = {
            '__globals__': 'Access to global namespace',
            '__builtins__': 'Access to builtin namespace',
            '__code__': 'Access to code object',
            '__reduce__': 'Potential deserialization vulnerability'
        }
        
        attr_name = node.attr
        if attr_name in dangerous_attrs:
            self._add_security_issue(
                vuln_type='dangerous_attribute',
                file_path=file_path,
                line_number=node.lineno,
                line_content=f'Access to {attr_name}',
                severity='HIGH',
                description=dangerous_attrs[attr_name]
            )

    def _check_dangerous_imports(self, node: ast.AST, file_path: Path) -> None:
        """Check for potentially dangerous imports."""
        dangerous_imports = {
            'telnetlib': 'Use of insecure Telnet protocol',
            'ftplib': 'Use of insecure FTP protocol',
            'pickle': 'Use of unsafe serialization',
            'marshal': 'Use of unsafe serialization',
            'tempfile': 'Potential temp file vulnerability'
        }
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in dangerous_imports:
                    self._add_security_issue(
                        vuln_type='dangerous_import',
                        file_path=file_path,
                        line_number=node.lineno,
                        line_content=f'Import {alias.name}',
                        severity='MEDIUM',
                        description=dangerous_imports[alias.name]
                    )

    def _add_security_issue(self, vuln_type: str, file_path: Path, 
                          line_number: int, line_content: str,
                          severity: str, description: str) -> None:
        """Add a security issue to the collection."""
        self.security_issues[vuln_type].append({
            'file': str(file_path),
            'line': line_number,
            'code': line_content,
            'severity': severity,
            'description': description
        })

    def generate_security_report(self) -> str:
        """Generate a comprehensive security analysis report."""
        report = ["# Security Analysis Report\n"]
        
        report.append("## Summary\n")
        total_issues = sum(len(issues) for issues in self.security_issues.values())
        report.append(f"Total security issues found: {total_issues}\n")
        
        severity_groups = defaultdict(list)
        for vuln_type, issues in self.security_issues.items():
            for issue in issues:
                severity_groups[issue['severity']].append((vuln_type, issue))
        
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            if severity in severity_groups:
                report.append(f"\n## {severity} Severity Issues\n")
                for vuln_type, issue in severity_groups[severity]:
                    report.append(f"### {vuln_type.replace('_', ' ').title()}")
                    report.append(f"- File: {issue['file']}")
                    report.append(f"- Line: {issue['line']}")
                    report.append(f"- Description: {issue['description']}")
                    report.append(f"- Code: `{issue['code']}`\n")
        
        return "\n".join(report)