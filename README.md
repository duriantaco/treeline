# treeline

<p align="center" style="margin: 0; padding: 0;">
    <img src="https://raw.githubusercontent.com/duriantaco/treeline/main/assets/Treeline.png" alt="Treeline Logo" width="400" />
</p>

A Python toolkit for analyzing and visualizing code structure, dependencies, and generating directory trees. treeline helps developers understand codebases through ASCII tree representations, interactive dependency graphs, and structural diff visualizations.

<p align="center" style="margin: 0; padding: 0;">
    <img src="https://raw.githubusercontent.com/duriantaco/treeline/main/assets/screenshot2.png" alt="Screenshot" width="800" />
</p>

## Installation

`pip install treeline`

## Usage

### In the CLI

1. Command-Line Interface (CLI)
After installing, Treeline provides the following commands:

```bash
treeline analyze DIRECTORY [--depth=N]
```

2. Analyzes code structure and prints entry points plus core components.
   
```bash
treeline quality DIRECTORY [--min-complexity=N]
```

3. Performs code-quality checks, highlighting complex or smelly functions.
```bash
treeline serve
```

4. Launches the Treeline web interface (FastAPI + Uvicorn) at localhost:8000.
Ideal for interactive dependency graphs, metrics, and code exploration.
```bash
treeline report [DIRECTORY] [--output=FILENAME]
```

Examples:

```bash
# Analyze your codebase structure
treeline analyze /path/to/codebase

# Increase analysis depth
treeline analyze . --depth 2

# Check code quality with a higher complexity threshold
treeline quality . --min-complexity 12

# Start the web interface
treeline serve

# Generate a markdown report (saved as 'treeline_report.md' by default)
treeline report /path/to/codebase

Generates a Markdown report summarizing issues and hotspots in the specified directory (defaults to .).

```

### Configuration Management

Treeline now includes CLI commands to manage your configuration:

```bash
# Create a default configuration file
treeline config init [--path=CONFIG_PATH]

# Show current configuration settings
treeline config show [--path=CONFIG_PATH]

# Set a specific configuration value
treeline config set KEY VALUE [--path=CONFIG_PATH]
```

Examples:

```bash
# Create a default config file in the current directory
treeline config init

# Create a config file in a specific location
treeline config init --path ~/.treeline/config.json

# View all current settings
treeline config show

# Increase the maximum allowed line length
treeline config set MAX_LINE_LENGTH 120

# Disable security checks
treeline config set ENABLE_SECURITY_CHECKS false
```


### As a python module

```python
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

#### Visualization Options

```bash
# Hide all code structure details
treeline --hide-structure
```
```bash
# Hide function parameters
treeline --no-params
```

## Configuration

Treeline looks for configuration in the following order:

1. Command-line `--config` parameter
2. `TREELINE_CONFIG` environment variable
3. `./treeline.json` or `./treeline_config.json` in the current directory
4. `~/.treeline/config.json` in the user's home directory
5. Default built-in values

### Creating a configuration file

1. Using the CLI:

```bash
treeline config init [--path=CONFIG_PATH]
```

### .treeline-ignore

the `.treeline-ignore` will ignore whatever is in the folder.

Place `.treeline-ignore` in any directory to apply rules to that directory and its subdirectories.

```
# Ignore all .pyc files
*.pyc

# Ignore specific directories
__pycache__/
.git
.venv

# Ignore specific files
config.local.py
secrets.py
```

### Analysis Configuration (Optional)
You can place a JSON config file (e.g. treeline.config.json) to override default thresholds or configure how the analysis runs:

```json
{
  "MAX_CYCLOMATIC_COMPLEXITY": 12,
  "MAX_LINE_LENGTH": 100,
  "MAX_FILE_LINES": 1000
}
```

## Key metrics tracked

| **Config Key**               | **Typical Meaning**                                                       | **Default/Threshold** |
|------------------------------|---------------------------------------------------------------------------|-----------------------|
| **MAX_PARAMS**               | Maximum allowed parameters in a function or method.                       | 5                     |
| **MAX_CYCLOMATIC_COMPLEXITY**| Cyclomatic complexity threshold (linearly independent paths).             | 10                    |
| **MAX_COGNITIVE_COMPLEXITY** | Cognitive complexity threshold (accounts for nesting, branching).         | 15                    |
| **MAX_DUPLICATED_LINES**     | Number of duplicated lines in code blocks.                                 | 5                     |
| **MAX_LINE_LENGTH**          | Preferred maximum line length for style checks.                            | 80                    |
| **MAX_DOC_LENGTH**           | Preferred docstring/comment line length.                                   | 80                    |
| **MAX_NESTED_DEPTH**         | Maximum nesting depth allowed (if/else/switch/try).                        | 4                     |
| **MAX_FUNCTION_LINES**       | Max lines per function.                                                    | 50                    |
| **MAX_RETURNS**              | How many return statements are acceptable in one function.                 | 4                     |
| **MAX_ARGUMENTS_PER_LINE**   | Maximum arguments in a single call line.                                   | 5                     |
| **MIN_MAINTAINABILITY_INDEX**| Minimum maintainability index (not all projects enforce this in code).     | 20                    |
| **MAX_FUNC_COGNITIVE_LOAD**  | Another cognitive load threshold for functions.                            | 15                    |
| **MIN_PUBLIC_METHODS**       | Lower bound for how many public methods a class should have.               | 1                     |
| **MAX_IMPORT_STATEMENTS**    | How many import statements per module (beyond is ‘too big’).               | 15                    |
| **MAX_MODULE_DEPENDENCIES**  | Maximum module-level dependencies.                                         | 10                    |
| **MAX_INHERITANCE_DEPTH**    | Depth of inheritance in class hierarchies.                                 | 3                     |
| **MAX_DUPLICATED_BLOCKS**    | Number of duplicated code blocks allowed.                                  | 2                     |
| **MAX_CLASS_LINES**          | Approx. limit on lines per class.                                          | 300                   |
| **MAX_METHODS_PER_CLASS**    | Method count threshold in a single class.                                  | 20                    |
| **MAX_CLASS_COMPLEXITY**     | Overall complexity threshold for a class.                                 | 50                    |


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
