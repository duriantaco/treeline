# treeline

<p align="center" style="margin: 0; padding: 0;">
    <img src="https://raw.githubusercontent.com/duriantaco/treeline/main/assets/Treeline.png" alt="Treeline Logo" width="400" />
</p>

A Python toolkit for generating directory trees. Treeline helps developers understand codebases through ASCII tree representations. 

## Installation

`pip install treeline`

## Usage

### Command Line

```bash
treeline  
treeline /path/to/project

treeline --code
treeline --code --depth 2

treeline --include "*.py"
treeline --exclude "node_modules"
treeline --all

treeline --no-size
treeline --file-count
treeline --output tree.txt
```

### Python Library

```python
from treeline import tree, TreeRenderer

# eg1
tree("./my_project", show_code_structure=True)

# eg2
renderer = TreeRenderer(
    show_code_structure=True,
    max_depth=3,
    show_size=True,
    output_file="structure.txt"
)
renderer.render("./my_project")
```

## Supported Languages

* Python (.py) - Classes, functions, methods with full AST parsing
* JavaScript (.js, .mjs) - Classes, functions, modules
* TypeScript (.ts) - Classes, functions, interfaces
* React (.jsx, .tsx) - Components (both class and functional), hooks

## Options

| Flag | Description |
|------|-------------|
| `directory` | Directory to analyze |
| `--code` | Show code structure (classes, functions, components) |
| `--depth N` | Limit tree depth to N levels |
| `--no-size` | Hide size |
| `--all` | Show all files |
| `--include PATTERN` | Include files matching pattern |
| `--exclude PATTERN` | Exclude files matching pattern |
| `-o FILE, --output FILE` | Save output |
| `--file-count` | Show file and directory counts |
| `--extensions` | Show file extension |

## Author
Oha