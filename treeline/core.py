# treeline/treeline/core.py
import os
from pathlib import Path
import argparse
from .enhanced_analyzer import EnhancedCodeAnalyzer 
from .dependency_analyzer import ModuleDependencyAnalyzer
import re

def create_default_ignore():
    """Create default .treeline-ignore if it doesn't exist"""
    if not Path('.treeline-ignore').exists():
        with open('.treeline-ignore', 'w') as f:
            f.write("*.pyc\n__pycache__\n.git\n.env\nvenv/\n.DS_Store\nnode_modules/\n")
        print("Created .treeline-ignore file")

def read_ignore_patterns():
    """Read patterns from .treeline-ignore file"""
    ignore_patterns = []
    if Path('.treeline-ignore').exists():
        with open('.treeline-ignore', 'r') as f:
            ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ignore_patterns

def should_ignore(path, ignore_patterns):
    """Check if path should be ignored based on patterns"""
    path_str = str(path)
    for pattern in ignore_patterns:
        if pattern.endswith('/'):
            if pattern[:-1] in path_str:
                return True
        elif pattern.startswith('*.'):
            if path_str.endswith(pattern[1:]):
                return True
        else:
            if pattern in path_str:
                return True
    return False

def clean_for_markdown(line: str) -> str:
    """Remove ANSI colors and simplify symbols for markdown."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_line = ansi_escape.sub('', line)
    
    replacements = {
        '⚡': '→',     
        '🏛️': '◆', 
        '⚠️': '!',    
        '📏': '▸',    
        '[FUNC]': '**Function**:',   
        '[CLASS]': '**Class**:',      
        '├── ': '├─ ',  
        '└── ': '└─ ',
        '│   ': '│ ',
        '    ': '  '
    }
    
    for old, new in replacements.items():
        clean_line = clean_line.replace(old, new)
    
    return clean_line.rstrip()

def format_mermaid_section(dep_analyzer):
    """Format mermaid graph with proper styling and layout."""
    mermaid_content = dep_analyzer.generate_mermaid_graph()
    return [
        "## Module Dependencies",
        "",
        "```mermaid",
        "%%{init: {'theme': 'neutral', 'flowchart': {'curve': 'basis'} }}%%",  # Add styling
        mermaid_content,
        "```",
        ""
    ]

def generate_tree(directory, create_md=False, hide_structure=False, show_params=True, show_relationships=True):
    """Generate tree structure with configurable display options."""
    tree_str = []
    directory = Path(directory)
    ignore_patterns = read_ignore_patterns()
    
    code_analyzer = None if hide_structure else EnhancedCodeAnalyzer(
        show_params=show_params,
        show_relationships=show_relationships
    )
    
    dep_analyzer = ModuleDependencyAnalyzer() if create_md else None
    if dep_analyzer:
        dep_analyzer.analyze_directory(directory)

    def add_directory(path, prefix=""):
        files = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for i, entry in enumerate(files):
            if should_ignore(entry, ignore_patterns):
                continue
                
            is_last = i == len(files) - 1
            tree_str.append(f"{prefix}{'└── ' if is_last else '├── '}{entry.name}")
            
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                add_directory(entry, prefix + extension)
            elif not hide_structure and entry.suffix == '.py':
                extension = "    " if is_last else "│   "
                structure = code_analyzer.analyze_file(entry)
                structure_lines = code_analyzer.format_structure(structure, prefix + extension + "  ")
                tree_str.extend(structure_lines)

    tree_str.append(str(directory.name))
    add_directory(directory)
    
    if create_md:
        with open("tree.md", 'w', encoding='utf-8') as f:
            f.write("# Project Structure Analysis\n\n")
            
            f.write("## Directory Structure\n\n")
            f.write("```\n")
            clean_result = "\n".join(clean_for_markdown(line) for line in tree_str)
            f.write(clean_result)
            f.write("\n```\n\n")
            
            if dep_analyzer:
                mermaid_section = format_mermaid_section(dep_analyzer)
                f.write("\n".join(mermaid_section))
                
                f.write("## Module Metrics\n\n")
                for module, metrics in sorted(dep_analyzer.module_metrics.items()):
                    f.write(f"### {module}\n")
                    f.write(f"- Functions: **{metrics['functions']}**\n")
                    f.write(f"- Classes: **{metrics['classes']}**\n")
                    f.write(f"- Complexity: **{metrics['complexity']}**\n\n")
                
                f.write("## Complexity Hotspots\n\n")
                if dep_analyzer.complex_functions:
                    for module, func, complexity in sorted(dep_analyzer.complex_functions, key=lambda x: x[2], reverse=True):
                        f.write(f"### {func}\n")
                        f.write(f"- **Module**: {module}\n")
                        f.write(f"- **Complexity**: {complexity}\n\n")
                else:
                    f.write("*No complex functions found.*\n")
    
    return "\n".join(tree_str)

def main():
    create_default_ignore()
    parser = argparse.ArgumentParser(
        description='Generate ASCII tree structure of directories',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=
        '''
            Examples:
            treeline                      # Show full tree with all features
            treeline /path/to/dir         # Show specific directory tree
            treeline -m                   # Create markdown file
            treeline -i "*.pyc,*.git"     # Ignore patterns
            treeline --hide-structure     # Hide all code structure
            treeline --no-params          # Hide function parameters
            treeline --no-relationships   # Hide code relationships
            treeline -h                   # Show this help message
        '''
    )
    
    parser.add_argument('directory', nargs='?', default='.',
                       help='Directory path (default: current directory)')
    parser.add_argument('-m', '--markdown', action='store_true',
                       help='Create markdown file (tree.md)')
    parser.add_argument('-i', '--ignore',
                       help='Comma-separated patterns to ignore (e.g., "*.pyc,*.git")')
    parser.add_argument('--hide-structure', action='store_true',
                       help='Hide all code structure')
    parser.add_argument('--no-params', action='store_true',
                       help='Hide function parameters')
    parser.add_argument('--no-relationships', action='store_true',
                       help='Hide code relationships')

    args = parser.parse_args()
    
    ignore_patterns = args.ignore.split(',') if args.ignore else []
    
    print(generate_tree(
        args.directory,
        create_md=args.markdown,
        hide_structure=args.hide_structure,
        show_params=not args.no_params,
        show_relationships=not args.no_relationships
    ))

if __name__ == "__main__":
    main()