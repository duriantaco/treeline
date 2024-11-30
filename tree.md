# Project Analysis Report

[Click here to open Interactive Code Visualization](./code_visualization.html)

## Directory Structure

```

├─ example
│ ├─ tree.md
│ └─ tut1.ipynb
├─ tests
│ ├─ test_core.py
│ │   **Class**: ◆ TestTreeGenerator
│ │   └─ ! Missing class docstring
│ │   **Function**: → setUp
│ │   **Function**: → tearDown
│ │   **Function**: → test_tree_structure
│ │   └─ # Test if the tree structure is generated correctly
│ │   **Function**: → test_markdown_creation
│ │   └─ # Test if markdown file is created when flag is True
│ ├─ test_empty_dir.py
│ │   **Function**: → test_empty_directory
│ │   └─ # Test handling of empty directory
│ ├─ test_missing_dir.py
│ │   **Function**: → test_non_existent_directory
│ │   └─ # Test handling of non-existent directory
│ ├─ test_nested_dir.py
│ │   **Function**: → test_nested_directories
│ │   └─ # Test handling of nested directories
│ ├─ test_security_detection.py
│ │   **Class**: ◆ TestTreelineSecurity
│ │   └─ ! High complexity (11)
│ │   └─ ! Too long (72 lines)
│ │   └─ ! Missing class docstring
│ │   **Function**: → setUp
│ │   **Function**: → create_test_file
│ │   └─ # Helper method to create a temporary test file.
│ │   **Function**: → debug_ast
│ │   └─ # Helper to print AST for debugging
│ │   **Function**: → test_sql_injection_detection
│ │   **Function**: → test_command_injection_detection
│ │   **Function**: → test_unsafe_deserialization_detection
│ │   **Function**: → test_hardcoded_secret_detection
│ │   **Function**: → test_file_operation_detection
│ │   **Function**: → tearDown
│ ├─ test_special_char.py
│ │   **Function**: → test_special_characters
│ │   └─ # Test handling of special characters in names
│ └─ test_treeline.py
│     **Class**: ◆ TestTreeLine
│     └─ ! Missing class docstring
│     **Function**: → setUp
│     **Function**: → tearDown
│     **Function**: → test_basic_tree
│     └─ # Test if tree structure is generated correctly
├─ treeline
│ ├─ __init__.py
│ │   **Function**: → __call__
│ ├─ __main__.py
│ ├─ analyzer.py
│ │   **Class**: ◆ CodeAnalyzer
│ │   └─ # Simple analyzer for extracting functions and classes from Python files.
│ │   └─ ! High complexity (30)
│ │   └─ ! Too long (129 lines)
│ │   **Function**: → __init__
│ │   **Function**: → analyze_file
│ │   └─ # Extracts functions and classes with optional params and relationships.
│ │   └─ ! Deep nesting (depth 5)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _get_function_params
│ │   └─ # Extract function parameters with type hints.
│ │   **Function**: → _find_function_calls
│ │   └─ # Find all function calls within a node.
│ │   **Function**: → get_symbol
│ │   └─ # Maps item types to their display symbols.
│ │   **Function**: → format_structure
│ │   └─ # Formats the code structure into displayable lines with colors and prefixes.
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ core.py
│ │   **Function**: → create_default_ignore
│ │   └─ # Create default .treeline-ignore if it doesn't exist
│ │   **Function**: → read_ignore_patterns
│ │   └─ # Read patterns from .treeline-ignore file
│ │   **Function**: → should_ignore
│ │   └─ # Check if path should be ignored based on patterns
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → clean_for_markdown
│ │   └─ # Remove ANSI colors and simplify symbols for markdown.
│ │   **Function**: → format_structure
│ │   └─ # Format the analysis results into a readable tree structure.
│ │    Args:
│ │    structure: List of analysis results
│ │    indent: String to use for indentation
│ │    Returns:
│ │    List of formatted strings representing the code structure
│ │   └─ ! High complexity (12)
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_markdown_report
│ │   └─ # Generate a markdown report with tree structure and analysis results.
│ │   **Function**: → generate_tree
│ │   └─ # Generate tree structure with code quality and security analysis.
│ │   └─ ! High complexity (13)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → main
│ │   **Function**: → add_directory
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ default_ignore
│ ├─ dependency_analyzer.py
│ │   **Class**: ◆ ModuleDependencyAnalyzer
│ │   └─ # Analyzes module-level dependencies and generates summary reports.
│ │   └─ ! High complexity (89)
│ │   └─ ! Too long (549 lines)
│ │   └─ ! Class too long
│ │   └─ ! High class complexity
│ │   **Function**: → __init__
│ │   └─ ! Too long (206 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   **Function**: → analyze_directory
│ │   └─ # Analyze all Python files in directory.
│ │   **Function**: → _analyze_module
│ │   └─ # Analyze a single module's contents and relationships.
│ │   └─ ! High complexity (15)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _analyze_imports
│ │   └─ # Collect import information from AST.
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _collect_metrics
│ │   └─ # Collect code metrics for the module.
│ │   **Function**: → _calculate_complexity
│ │   └─ # Calculate cyclomatic complexity.
│ │   **Function**: → generate_mermaid_graph
│ │   └─ # Generate detailed Mermaid graph showing module, function, and class relationships.
│ │   └─ ! High complexity (21)
│ │   └─ ! Too long (67 lines)
│ │   └─ ! Deep nesting (depth 5)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_html_visualization
│ │   └─ # Generate an interactive HTML visualization using D3.js
│ │   └─ ! High complexity (18)
│ │   └─ ! Too long (111 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_summary_report
│ │   └─ # Generate a readable markdown report with a link to the interactive visualization.
│ │   └─ ! High complexity (14)
│ │   └─ ! Too long (56 lines)
│ │   └─ ! Deep nesting (depth 6)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → get_node_id
│ ├─ enhanced_analyzer.py
│ │   **Class**: ◆ EnhancedCodeAnalyzer
│ │   └─ # Enhanced analyzer for code quality and maintainability metrics.
│ │    This analyzer implements industry-standard code quality checks and metrics
│ │    following Clean Code principles, SOLID principles, and PEP 8 standards.
│ │   └─ ! High complexity (123)
│ │   └─ ! Too long (530 lines)
│ │   └─ ! Class too long
│ │   └─ ! Too many methods
│ │   └─ ! High class complexity
│ │   **Function**: → __init__
│ │   └─ # Initialize the code analyzer.
│ │    Args:
│ │    show_params: Whether to show function parameters in analysis
│ │   **Function**: → analyze_file
│ │   └─ # Analyze a Python file for code quality metrics.
│ │    Args:
│ │    file_path: Path to the Python file to analyze
│ │    Returns:
│ │    List of analysis results for each code element
│ │   **Function**: → _calculate_maintainability_index
│ │   └─ # Calculate Maintainability Index (MI) following Microsoft's formula.
│ │    MI = max(0, (171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
│ │    where:
│ │    - HV = Halstead Volume
│ │    - CC = Cyclomatic Complexity
│ │    - LOC = Lines of Code
│ │   **Function**: → _calculate_cognitive_load
│ │   └─ # Counts control structures and parameters as cognitive items.
│ │   **Function**: → _check_function_metrics
│ │   └─ # Check function metrics against quality thresholds.
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _calculate_cyclomatic_complexity
│ │   └─ # Calculate McCabe's cyclomatic complexity.
│ │    Based on McCabe, 1976 and implementation in Radon/SonarQube.
│ │   **Function**: → _calculate_cognitive_complexity
│ │   └─ # Calculate cognitive complexity based on SonarQube's metric.
│ │    Implements SonarSource's cognitive complexity calculation.
│ │   **Function**: → _analyze_file_metrics
│ │   └─ # Analyze file-level metrics including style, duplication, imports, and documentation.
│ │    Args:
│ │    content: File content as string
│ │    file_path: Path to the file being analyzed
│ │   └─ ! High complexity (13)
│ │   └─ ! Too long (63 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _read_file
│ │   └─ # Read and return file content safely.
│ │   **Function**: → _parse_content
│ │   └─ # Parse Python content into AST safely.
│ │   **Function**: → _analyze_code_elements
│ │   └─ # Analyze individual code elements in the AST.
│ │   **Function**: → _analyze_class
│ │   └─ # Analyze a class's quality metrics.
│ │   **Function**: → _check_class_metrics
│ │   └─ # Check class metrics against quality thresholds.
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → format_structure
│ │   └─ # Format the analysis results into a tree structure.
│ │   └─ ! High complexity (15)
│ │   └─ ! High cyclomatic complexity (> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _format_metrics_section
│ │   └─ # Format the metrics section of the report.
│ │   **Function**: → _analyze_function
│ │   └─ # Analyze a function's quality metrics.
│ │   **Function**: → _calculate_class_metrics
│ │   └─ # Calculate comprehensive metrics for a class.
│ │   **Function**: → _calculate_function_metrics
│ │   └─ # Calculate comprehensive function metrics.
│ │   **Function**: → _calculate_complexity
│ │   └─ # Calculate cyclomatic complexity of code.
│ │   **Function**: → _calculate_nested_depth
│ │   └─ # Calculate maximum nesting depth in code.
│ │   **Function**: → _analyze_code_duplication
│ │   └─ # Analyze code for duplication using line-based comparison.
│ │   **Function**: → _analyze_imports
│ │   └─ # Analyze import statements and module dependencies.
│ │   **Function**: → _analyze_inheritance
│ │   └─ # Analyze class inheritance depth and hierarchy.
│ │   **Function**: → _add_issue
│ │   └─ # Add a quality issue to the collection.
│ │    Args:
│ │    category: The category of the issue
│ │    description: Description of the issue
│ │    file_path: Optional path to the file where the issue was found
│ │    line: Optional line number where the issue was found
│ │   **Function**: → generate_report
│ │   └─ # Generate a formatted quality report.
│ │   **Function**: → _format_report_sections
│ │   └─ # Format and combine report sections.
│ │   **Function**: → _format_overview_section
│ │   └─ # Format the report overview section.
│ │   **Function**: → _format_issues_section
│ │   └─ # Format the quality issues section.
│ │   **Function**: → walk_cognitive
│ │   **Function**: → get_depth
│ │   **Function**: → get_inheritance_depth
│ └─ security_analyzer.py
│     **Class**: ◆ TreelineSecurity
│     └─ ! High complexity (46)
│     └─ ! Too long (168 lines)
│     └─ ! Missing class docstring
│     **Function**: → __init__
│     **Function**: → analyze_file
│     **Function**: → _collect_imports
│     └─ ! High cognitive complexity (> 15)
│     **Function**: → _scan_security_issues
│     └─ ! High cognitive load (> 7 items)
│     **Function**: → _check_all_dangerous_calls
│     └─ # Check for dangerous function calls that may lead to security vulnerabilities.
│     └─ ! High complexity (14)
│     └─ ! Too long (56 lines)
│     └─ ! Deep nesting (depth 6)
│     └─ ! Function exceeds 50 lines
│     └─ ! High cyclomatic complexity (> 10)
│     └─ ! High cognitive complexity (> 15)
│     └─ ! Excessive nesting depth (> 4)
│     └─ ! High cognitive load (> 7 items)
│     **Function**: → _check_string_concat
│     └─ # Check for string concatenation with SQL-like commands.
│     **Function**: → _check_hardcoded_secrets
│     **Function**: → _add_issue
├─ treeline.egg-info
│ ├─ dependency_links.txt
│ ├─ entry_points.txt
│ ├─ PKG-INFO
│ ├─ SOURCES.txt
│ └─ top_level.txt
├─ .treeline-ignore
├─ code_visualization.html
├─ License
├─ README.md
├─ setup.py
└─ tree.md
```

## Code Quality Metrics

### setup
- Functions: **0**
- Classes: **0**
- Complexity: **0**

### tests.test_core
- Functions: **4**
- Classes: **1**
- Complexity: **5**

### tests.test_empty_dir
- Functions: **1**
- Classes: **0**
- Complexity: **1**

### tests.test_missing_dir
- Functions: **1**
- Classes: **0**
- Complexity: **1**

### tests.test_nested_dir
- Functions: **1**
- Classes: **0**
- Complexity: **1**

### tests.test_security_detection
- Functions: **9**
- Classes: **1**
- Complexity: **11**

### tests.test_special_char
- Functions: **1**
- Classes: **0**
- Complexity: **1**

### tests.test_treeline
- Functions: **3**
- Classes: **1**
- Complexity: **3**

### treeline.__init__
- Functions: **1**
- Classes: **0**
- Complexity: **1**

### treeline.__main__
- Functions: **0**
- Classes: **0**
- Complexity: **0**

### treeline.analyzer
- Functions: **6**
- Classes: **1**
- Complexity: **30**

### treeline.core
- Functions: **9**
- Classes: **0**
- Complexity: **55**

### treeline.dependency_analyzer
- Functions: **10**
- Classes: **1**
- Complexity: **89**

### treeline.enhanced_analyzer
- Functions: **31**
- Classes: **1**
- Complexity: **123**

### treeline.security_analyzer
- Functions: **8**
- Classes: **1**
- Complexity: **46**

## Complexity Hotspots

### generate_mermaid_graph
- **Module**: treeline.dependency_analyzer
- **Complexity**: 21

### generate_html_visualization
- **Module**: treeline.dependency_analyzer
- **Complexity**: 18

### _analyze_module
- **Module**: treeline.dependency_analyzer
- **Complexity**: 15

### format_structure
- **Module**: treeline.enhanced_analyzer
- **Complexity**: 15

### generate_summary_report
- **Module**: treeline.dependency_analyzer
- **Complexity**: 14

### _check_all_dangerous_calls
- **Module**: treeline.security_analyzer
- **Complexity**: 14

### _analyze_file_metrics
- **Module**: treeline.enhanced_analyzer
- **Complexity**: 13

### generate_tree
- **Module**: treeline.core
- **Complexity**: 13

### format_structure
- **Module**: treeline.core
- **Complexity**: 12

