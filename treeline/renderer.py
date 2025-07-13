from pathlib import Path
from rich.console import Console
from rich.text import Text
from treeline.utils import format_size
from treeline.analyzer import CodeAnalyzer

class TreeRenderer:
    def __init__(self, max_depth=None, show_size=True, show_all=False, 
                 include_patterns=None, exclude_patterns=None, show_file_count=False,
                 show_extensions=False, output_file=None, show_code_structure=False):
        self.max_depth = max_depth
        self.show_size = show_size
        self.show_all = show_all
        self.include_patterns = include_patterns or set()
        self.exclude_patterns = exclude_patterns or set()
        self.show_file_count = show_file_count
        self.show_extensions = show_extensions
        self.show_code_structure = show_code_structure
        self.output_file = output_file
        self.permission_errors = []
        self.file_extensions = {}
        self.total_files = 0
        self.total_dirs = 0
        self.output_lines = []
        self.console = Console() if not output_file else None
        
        self.default_exclusions = {
            '.git', '.gitignore', '.gitmodules',
            '__pycache__', '.pytest_cache',
            '.venv', 'venv', 'env', '.env',
            'node_modules', '.npm', '.yarn',
            '.DS_Store', '.localized', 'Thumbs.db',
            '.idea', '.vscode', '.vs',
            'dist', 'build', '.next', '.nuxt',
            '.cache', '.tmp', '.temp',
            '.coverage', '.nyc_output',
            '.mypy_cache', '.tox'
        }
    
    def should_skip(self, path):
        if self.show_all:
            return False
        
        name = path.name
        
        if self.include_patterns:
            match_found = False
            for pattern in self.include_patterns:
                if pattern in name:
                    match_found = True
            if not match_found:
                return True
        
        for pattern in self.exclude_patterns:
            if pattern in name:
                return True
        
        if name.startswith('.'):
            return True
        
        if name in self.default_exclusions:
            return True
        
        return False
    
    def _print(self, text, style=None):
        if self.output_file:
            if isinstance(text, Text):
                self.output_lines.append(text.plain)
            else:
                self.output_lines.append(str(text))
        else:
            if self.console and style:
                self.console.print(text, style=style)
            elif self.console:
                self.console.print(text)
            else:
                print(text)
    
    def count_items(self, path):
        if not path.is_dir():
            return 0, 0
        
        files, dirs = 0, 0
        try:
            for item in path.iterdir():
                if self.should_skip(item):
                    continue
                if item.is_file():
                    files += 1
                else:
                    dirs += 1
        except:
            pass
        return files, dirs
    
    def get_file_size(self, file_path):
        try:
            return file_path.stat().st_size
        except PermissionError:
            self.permission_errors.append(str(file_path))
            return None
        except:
            return 0
    
    def track_extension(self, file_path):
        ext = file_path.suffix.lower()
        if not ext:
            ext = "(no extension)"
        self.file_extensions[ext] = self.file_extensions.get(ext, 0) + 1
    
    def get_file_summary(self, file_path):
        if not self.show_code_structure:
            return ""
        
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.jsx': 'React/JSX', 
            '.ts': 'TypeScript', 
            '.tsx': 'React/TSX',
            '.mjs': 'JavaScript'
        }
        
        ext = file_path.suffix.lower()
        if ext not in extensions:
            return ""
        
        analyzer = CodeAnalyzer()
        if not analyzer.analyze_file(file_path):
            return ""
                
        counts = []
        if analyzer.components:
            n = len(analyzer.components)
            counts.append(f"{n} component{'s' if n != 1 else ''}")
        if analyzer.classes:
            n = len(analyzer.classes)
            counts.append(f"{n} class{'es' if n != 1 else ''}")
        if analyzer.functions:
            n = len(analyzer.functions)
            counts.append(f"{n} function{'s' if n != 1 else ''}")

        if counts:
            return f" ({', '.join(counts)})"
        return ""
    
    def analyze_code_file(self, file_path, prefix):
        if not self.show_code_structure:
            return
        
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.jsx': 'React/JSX', 
            '.ts': 'TypeScript', 
            '.tsx': 'React/TSX',
            '.mjs': 'JavaScript'
        }
        
        ext = file_path.suffix.lower()
        if ext not in extensions:
            return
        
        analyzer = CodeAnalyzer()
        if analyzer.analyze_file(file_path):
            for comp in analyzer.components:
                if comp['type'] == 'class':
                    comp_type = "class"
                else:
                    comp_type = "function"
                comp_text = f"{prefix}    {comp['name']} [component] ({comp_type})"
                self._print(comp_text, style="bright_cyan")
                
                for method in comp['methods']:
                    method_text = f"{prefix}        {method}() [method]"
                    self._print(method_text, style="cyan")
            
            for cls in analyzer.classes:
                class_text = f"{prefix}    {cls['name']} [class]"
                self._print(class_text, style="bright_yellow")
                for method in cls['methods']:
                    method_text = f"{prefix}        {method}() [method]"
                    self._print(method_text, style="yellow")

            for func in analyzer.functions:
                if ext == '.py':
                    args_str = ', '.join(func['args'])
                    func_text = f"{prefix}    {func['name']}({args_str}) [function]"
                else:
                    func_text = f"{prefix}    {func['name']}() [function]"
                self._print(func_text, style="bright_green")
    
    def print_tree(self, path, prefix="", depth=0):
        if self.max_depth and depth >= self.max_depth:
            return
            
        items = []
        try:
            for p in path.iterdir():
                if not self.should_skip(p):
                    items.append(p)
            
            dirs = []
            files = []
            for x in items:
                if x.is_dir():
                    dirs.append(x)
                else:
                    files.append(x)

            dirs.sort()
            files.sort()
            items = dirs + files
                            
        except PermissionError:
            self.permission_errors.append(str(path))
            self._print(f"{prefix}├── {path.name}/ (permission denied)")
            return
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")
            
            if item.is_file():
                self.total_files += 1
                if self.show_extensions:
                    self.track_extension(item)
                
                file_summary = self.get_file_summary(item)
                
                size = self.get_file_size(item)
                if size is None:
                    file_text = f"{prefix}{current_prefix}{item.name} (no access)"
                    self._print(file_text, style="red")
                    continue

                parts = [item.name]
                if self.show_size:
                    parts.append(f"({format_size(size)})")
                if file_summary:
                    parts.append(file_summary)

                file_text = f"{prefix}{current_prefix}{' '.join(parts)}"
                self._print(file_text, style="white")
                
                self.analyze_code_file(item, prefix + ("    " if is_last else "│   "))
                
            else:
                self.total_dirs += 1
                dir_display = f"{item.name}/"
                
                if self.show_file_count:
                    files, dirs = self.count_items(item)
                    if files > 0 or dirs > 0:
                        dir_display += f" ({files} files, {dirs} dirs)"
                
                dir_text = f"{prefix}{current_prefix}{dir_display}"
                self._print(dir_text, style="bright_blue")
                self.print_tree(item, next_prefix, depth + 1)
    
    def render(self, directory):
        target_dir = Path(directory).resolve()
        root_text = f"{target_dir.name}/"
        self._print(root_text, style="bold bright_blue")
        self.print_tree(target_dir)
        
        if self.permission_errors:
            error_text = f"\n{len(self.permission_errors)} files/folders can't be read"
            self._print(error_text, style="red")
        
        if self.output_file:
            with open(self.output_file, 'w') as f:
                for line in self.output_lines:
                    f.write(line + '\n')
            success_text = f"Output saved to {self.output_file}"
            if self.console:
                self.console.print(success_text, style="green")
            else:
                print(success_text)

def tree(directory=".", max_depth=None, show_size=True, show_all=False, 
         include=None, exclude=None, output_file=None, show_file_count=False,
         show_extensions=False, show_code_structure=False):
    renderer = TreeRenderer(
        max_depth=max_depth,
        show_size=show_size,
        show_all=show_all,
        include_patterns=set(include) if include else None,
        exclude_patterns=set(exclude) if exclude else None,
        output_file=output_file,
        show_file_count=show_file_count,
        show_extensions=show_extensions,
        show_code_structure=show_code_structure
    )
    renderer.render(directory)