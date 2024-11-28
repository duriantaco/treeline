# treeline/treeline/core.py
import os
from pathlib import Path
import shutil
import argparse
import pkg_resources

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
            # Directory pattern
            if pattern[:-1] in path_str:
                return True
        elif pattern.startswith('*.'):
            # Extension pattern
            if path_str.endswith(pattern[1:]):
                return True
        else:
            # Exact match or simple pattern
            if pattern in path_str:
                return True
    return False

def generate_tree(directory, create_md=False):
    """Generate tree structure and optionally create MD file."""
    tree_str = []
    directory = Path(directory)
    ignore_patterns = read_ignore_patterns()

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

    tree_str.append(str(directory.name))
    add_directory(directory)
    
    result = "\n".join(tree_str)
    
    if create_md:
        with open("tree.md", 'w', encoding='utf-8') as f:
            f.write("```\n")
            f.write(result)
            f.write("\n```")
    
    return result

def main():
    create_default_ignore() 
    parser = argparse.ArgumentParser(
        description='Generate ASCII tree structure of directories',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=
        '''
            Examples:
            treeline                      # Show current directory tree
            treeline /path/to/dir         # Show specific directory tree
            treeline -m                   # Create markdown file
            treeline -i "*.pyc,*.git"     # Ignore patterns
            treeline -h                   # Show this help message
        '''
                    )
    
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory path (default: current directory)')
    parser.add_argument('-m', '--markdown', action='store_true',
                       help='Create markdown file (tree.md)')
    parser.add_argument('-i', '--ignore', 
                       help='Comma-separated patterns to ignore (e.g., "*.pyc,*.git")')

    args = parser.parse_args()
    
    # Handle ignore patterns
    ignore_patterns = args.ignore.split(',') if args.ignore else []
    
    print(generate_tree(args.directory, create_md=args.markdown))

if __name__ == "__main__":
    main()