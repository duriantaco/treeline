import ast
import re

class CodeAnalyzer:
    
    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []
        self.components = []
    
    def analyze_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ext = file_path.suffix.lower()
            if ext == '.py':
                return self._analyze_python(content)
            elif ext in ['.js', '.jsx', '.ts', '.tsx', '.mjs']:
                return self._analyze_javascript(content, ext)
            else:
                return False
                
        except (UnicodeDecodeError, PermissionError):
            return False
    
    def _analyze_python(self, content):
        try:
            tree = ast.parse(content)
            self._extract_python_structure(tree)
            return True
        except SyntaxError:
            return False
    
    def _analyze_javascript(self, content, ext):
        self.classes = []
        self.functions = []
        self.imports = []
        self.components = []
        
        class_component_pattern = r'class\s+([A-Za-z_$][A-Za-z0-9_$]*)\s+extends\s+(?:React\.)?Component'
        for match in re.finditer(class_component_pattern, content):
            self.components.append({
                'name': match.group(1),
                'type': 'class',
                'methods': self._extract_class_methods(content, match.start())
            })
        
        func_component_patterns = [
            r'(?:export\s+)?(?:default\s+)?function\s+([A-Z][A-Za-z0-9_$]*)\s*\([^)]*\)\s*{[^}]*return\s*(?:\(|<)',
            r'const\s+([A-Z][A-Za-z0-9_$]*)\s*=\s*\([^)]*\)\s*=>\s*{[^}]*return\s*(?:\(|<)',
            r'const\s+([A-Z][A-Za-z0-9_$]*)\s*=\s*\([^)]*\)\s*=>\s*(?:\(|<)',
            r'export\s+(?:default\s+)?const\s+([A-Z][A-Za-z0-9_$]*)\s*=\s*\([^)]*\)\s*=>'
        ]
        
        component_names = set()
        for comp in self.components:
            component_names.add(comp['name'])
        
        for pattern in func_component_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                comp_name = match.group(1)
                if comp_name not in component_names:
                    self.components.append({
                        'name': comp_name,
                        'type': 'functional',
                        'methods': [] 
                    })
                    component_names.add(comp_name)
        
        class_pattern = r'class\s+([A-Za-z_$][A-Za-z0-9_$]*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            if class_name not in component_names:
                self.classes.append({
                    'name': class_name,
                    'methods': self._extract_class_methods(content, match.start())
                })
        
        func_patterns = [
            r'function\s+([a-z][A-Za-z0-9_$]*)\s*\(',
            r'const\s+([a-z][A-Za-z0-9_$]*)\s*=\s*\([^)]*\)\s*=>', 
            r'let\s+([a-z][A-Za-z0-9_$]*)\s*=\s*\([^)]*\)\s*=>',
            r'export\s+function\s+([a-z][A-Za-z0-9_$]*)\s*\(',
            r'async\s+function\s+([a-z][A-Za-z0-9_$]*)\s*\('
        ]
        
        used_names = set()
        for comp in self.components:
            used_names.add(comp['name'])
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                if func_name not in used_names:
                    self.functions.append({'name': func_name})
                    used_names.add(func_name)
                
        import_patterns = [
            r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+.*?=\s*require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                import_path = match.group(1)
                if not import_path.startswith('.'):
                    self.imports.append(import_path)
        
        return True
    
    def _extract_class_methods(self, content, class_start):
        methods = []
        class_content = content[class_start:class_start + 2000]
        method_pattern = r'^\s*([a-zA-Z_$][A-Za-z0-9_$]*)\s*\([^)]*\)\s*{'
        
        for line in class_content.split('\n'):
            method_match = re.match(method_pattern, line)
            if method_match:
                method_name = method_match.group(1)
                if method_name not in ['if', 'for', 'while', 'switch', 'constructor', 'render']:
                    methods.append(method_name)
                elif method_name == 'render':
                    methods.append('render')
        
        return methods[:8]
    
    def _extract_python_structure(self, tree):
        self.classes = []
        self.functions = []
        self.imports = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = []
                for n in node.body:
                    if isinstance(n, ast.FunctionDef):
                        methods.append(n.name)
                
                self.classes.append({
                    'name': node.name,
                    'methods': methods,
                    'line': node.lineno
                })
            elif isinstance(node, ast.FunctionDef):
                args = []
                for arg in node.args.args:
                    args.append(arg.arg)
                
                self.functions.append({
                    'name': node.name,
                    'args': args
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(alias.name)
                    
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    if module:
                        self.imports.append(f"{module}.{alias.name}")
                    else:
                        self.imports.append(alias.name)