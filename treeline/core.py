import os
from pathlib import Path

def generate_tree(directory, create_md=False):
    """Generate tree structure and optionally create MD file."""
    tree_str = []
    directory = Path(directory)

    def add_directory(path, prefix=""):
        files = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for i, entry in enumerate(files):
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