# treeline

<p align="center">
  <img src="assets/Treeline.png" alt="Treeline Logo" width="600"/>
</p>

A powerful Python toolkit for analyzing and visualizing code structure, dependencies, and generating directory trees. treeline helps developers understand codebases through ASCII tree representations, interactive dependency graphs, and structural diff visualizations.

<p align="center">
  <img src="assets/output.gif" alt="Treeline Demo" width="800"/>
</p>

## Installation

`pip install treeline`

## Usage

### As a python module

```
from treeline import treeline

# Generate and print tree structure
print(treeline("/path/to/directory"))

# Generate tree and save to markdown file
treeline("/path/to/directory", create_md=True)

# Advanced code analysis
from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.diff_visualizer import DiffVisualizer
from pathlib import Path

# Analyze code dependencies
analyzer = ModuleDependencyAnalyzer()
analyzer.analyze_directory(Path("."))

# Generate interactive visualization
with open("dependencies.html", "w", encoding="utf-8") as f:
    f.write(analyzer.generate_html_visualization())

# Compare code structure between git commits
visualizer = DiffVisualizer()
diff_html = visualizer.generate_structural_diff("HEAD^", "HEAD")
with open("code_diff.html", "w", encoding="utf-8") as f:
    f.write(diff_html)
```

### In terminal

#### Basic commands
```
# Show current directory tree
treeline
```
```
# Show specific directory tree
treeline /path/to/dir
```
```
# Create markdown file (tree.md)
treeline -m
```
```
# Ignore specific patterns
treeline -i ".pyc,.git"
```
```
# Show help message
treeline -h
```
#### Code analysis commands
```
# Generate code dependency visualization
treeline --analyze
```
```
# Create diff visualization between git commits
treeline --diff HEAD^ HEAD
```
```
# Show code metrics and complexity analysis
treeline --metrics
```
```
# Export analysis to HTML report
treeline --report
```

#### Visualization Options
```
# Create diff visualization between git commits
treeline --diff HEAD^ HEAD
```
```
# Hide all code structure details
treeline --hide-structure
```
```
# Hide function parameters
treeline --no-params
```
```
# Hide code relationships
treeline --no-relationships
```
```
# Show only specific types of relationships
treeline --show-relationships "imports,calls"
```
```
# Customize visualization layout
treeline --layout "force-directed|radial"
```
```
# Filter by module types
treeline --show-types "module,class,function"
```

#### Analysis filters
```
# Show only files with complexity above threshold
treeline --min-complexity 10
```
```
# Filter by specific module patterns
treeline --module-pattern "*/models/*"
```
```
# Show only modified files (with git)
treeline --show-modified
```
```
# Focus on specific relationships
treeline --focus "imports|calls|contains"
```

## Configuration

### .treeline-ignore
the .treeline-ignore will ignore whatever is in the folder.

Place .treeline-ignore in any directory to apply rules to that directory and its subdirectories.

```
# Ignore all .pyc files
*.pyc

# Ignore specific directories
__pycache__
.git
.venv

# Ignore specific files
config.local.py
secrets.py
```
### Analysis configuration

Create a treeline.config.json to customize analysis settings:

```
{
  "complexity_threshold": 10,
  "ignore_patterns": [".pyc", ".git"],
  "relationship_types": ["imports", "calls", "contains"],
  "visualization": {
    "layout": "force-directed",
    "theme": "light"
  }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (git checkout -b branch)
3. Commit your changes (git commit -m 'cool stuff')
4. Push to the branch (git push origin branch)
5. Open a Pull Request

## Sources for best practices

1. https://peps.python.org/
2. https://peps.python.org/pep-0008/
3. https://google.github.io/styleguide/pyguide.html

## Author
Oha
