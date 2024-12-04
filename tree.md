# Project Analysis Report

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
│ │   └─ ! Excessive nesting depth (> 4, Pylint)
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
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → clean_for_markdown
│ │   └─ # Remove ANSI colors and simplify symbols for markdown.
│ │   **Function**: → format_mermaid_section
│ │   └─ # Format mermaid graph with proper styling and layout.
│ │   **Function**: → format_structure
│ │   └─ # Format the analysis results into a readable tree structure.
│ │    Args:
│ │    structure: List of analysis results
│ │    indent: String to use for indentation
│ │    Returns:
│ │    List of formatted strings representing the code structure
│ │   └─ ! High complexity (12)
│ │   └─ ! High cyclomatic complexity (> 10, McCabe)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_markdown_report
│ │   └─ # Generate a markdown report with tree structure and analysis results.
│ │   **Function**: → generate_tree
│ │   └─ # Generate tree structure with code quality and security analysis.
│ │   └─ ! High complexity (13)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cyclomatic complexity (> 10, McCabe)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
│ │   └─ ! Excessive nesting depth (> 4, Pylint)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → main
│ │   **Function**: → add_directory
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
│ │   └─ ! Excessive nesting depth (> 4, Pylint)
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ default_ignore
│ ├─ dependency_analyzer.py
│ │   **Class**: ◆ ModuleDependencyAnalyzer
│ │   └─ # Analyzes module-level dependencies and generates summary reports.
│ │   └─ ! High complexity (62)
│ │   └─ ! Too long (221 lines)
│ │   └─ ! Class too long
│ │   └─ ! High class complexity
│ │   **Function**: → __init__
│ │   **Function**: → analyze_directory
│ │   └─ # Analyze all Python files in directory.
│ │   **Function**: → _analyze_module
│ │   └─ # Analyze a single module's contents and relationships.
│ │   └─ ! High complexity (15)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cyclomatic complexity (> 10, McCabe)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
│ │   └─ ! Excessive nesting depth (> 4, Pylint)
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
│ │   └─ ! High complexity (14)
│ │   └─ ! Too long (51 lines)
│ │   └─ ! Function exceeds 50 lines (Pylint)
│ │   └─ ! High cyclomatic complexity (> 10, McCabe)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_summary_report
│ │   └─ # Generate a readable markdown report without tables.
│ │   └─ ! High complexity (14)
│ │   └─ ! Too long (55 lines)
│ │   └─ ! Deep nesting (depth 6)
│ │   └─ ! Function exceeds 50 lines (Pylint)
│ │   └─ ! High cyclomatic complexity (> 10, McCabe)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
│ │   └─ ! Excessive nesting depth (> 4, Pylint)
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ enhanced_analyzer.py
│ │   **Class**: ◆ EnhancedCodeAnalyzer
│ │   └─ # Enhanced analyzer for code quality and maintainability metrics.
│ │    This analyzer implements industry-standard code quality checks and metrics
│ │    following Clean Code principles, SOLID principles, and PEP 8 standards.
│ │   └─ ! High complexity (123)
│ │   └─ ! Too long (529 lines)
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
│ │   └─ ! Function exceeds 50 lines (Pylint)
│ │   └─ ! High cyclomatic complexity (> 10, McCabe)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
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
│ │   └─ ! High cyclomatic complexity (> 10, McCabe)
│ │   └─ ! High cognitive complexity (> 15, SonarQube)
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
│     **Class**: ◆ SecurityAnalyzer
│     └─ # Security analyzer for Python code to detect potential vulnerabilities and risks.
│      Follows OWASP guidelines and common security best practices.
│     └─ ! High complexity (27)
│     └─ ! Too long (224 lines)
│     └─ ! Class too long
│     **Function**: → __init__
│     └─ # Initialize the security analyzer.
│     **Function**: → analyze_file
│     └─ # Analyze a Python file for security vulnerabilities.
│      Args:
│      file_path: Path to the Python file to analyze
│      Returns:
│      Dictionary containing security analysis results
│     **Function**: → _scan_patterns
│     └─ # Scan code for vulnerable patterns using regex.
│     **Function**: → _analyze_ast_security
│     └─ # Analyze AST for security issues.
│     **Function**: → _check_dangerous_attributes
│     └─ # Check for access to dangerous attributes.
│     **Function**: → _check_dangerous_imports
│     └─ # Check for potentially dangerous imports.
│     **Function**: → _add_security_issue
│     └─ # Add a security issue to the collection.
│     └─ ! Too many parameters (> 5, Pylint)
│     **Function**: → generate_security_report
│     └─ # Generate a comprehensive security analysis report.
├─ treeline.egg-info
│ ├─ dependency_links.txt
│ ├─ entry_points.txt
│ ├─ PKG-INFO
│ ├─ SOURCES.txt
│ └─ top_level.txt
├─ .treeline-ignore
├─ License
├─ README.md
├─ setup.py
└─ tree.md
```

## Module Dependencies

```mermaid
%%{init: {'theme': 'neutral', 'flowchart': {'curve': 'basis'} }}%%
graph TD
    %% Styling
    classDef module fill:#b7e2d8,stroke:#333,stroke-width:2px;
    classDef function fill:#e4d1d1,stroke:#333;
    classDef class fill:#d1e0e4,stroke:#333;
    subgraph setup["setup"]
        setup_node["setup"]:::module
    end
    subgraph tests_test_special_char["tests.test_special_char"]
        tests_test_special_char_node["tests.test_special_char"]:::module
        tests_test_special_char_test_special_characters["⚡ test_special_characters()"]:::function
        tests_test_special_char_node --> tests_test_special_char_test_special_characters
    end
    subgraph tests_test_missing_dir["tests.test_missing_dir"]
        tests_test_missing_dir_node["tests.test_missing_dir"]:::module
        tests_test_missing_dir_test_non_existent_directory["⚡ test_non_existent_directory()"]:::function
        tests_test_missing_dir_node --> tests_test_missing_dir_test_non_existent_directory
    end
    subgraph tests_test_empty_dir["tests.test_empty_dir"]
        tests_test_empty_dir_node["tests.test_empty_dir"]:::module
        tests_test_empty_dir_test_empty_directory["⚡ test_empty_directory()"]:::function
        tests_test_empty_dir_node --> tests_test_empty_dir_test_empty_directory
    end
    subgraph tests_test_core["tests.test_core"]
        tests_test_core_node["tests.test_core"]:::module
        tests_test_core_TestTreeGenerator["📦 TestTreeGenerator"]:::class
        tests_test_core_node --> tests_test_core_TestTreeGenerator
        tests_test_core_TestTreeGenerator_setUp["⚡ setUp()"]:::function
        tests_test_core_TestTreeGenerator --> tests_test_core_TestTreeGenerator_setUp
        tests_test_core_TestTreeGenerator_tearDown["⚡ tearDown()"]:::function
        tests_test_core_TestTreeGenerator --> tests_test_core_TestTreeGenerator_tearDown
        tests_test_core_TestTreeGenerator_test_tree_structure["⚡ test_tree_structure()"]:::function
        tests_test_core_TestTreeGenerator --> tests_test_core_TestTreeGenerator_test_tree_structure
        tests_test_core_TestTreeGenerator_test_markdown_creation["⚡ test_markdown_creation()"]:::function
        tests_test_core_TestTreeGenerator --> tests_test_core_TestTreeGenerator_test_markdown_creation
    end
    subgraph tests_test_treeline["tests.test_treeline"]
        tests_test_treeline_node["tests.test_treeline"]:::module
        tests_test_treeline_TestTreeLine["📦 TestTreeLine"]:::class
        tests_test_treeline_node --> tests_test_treeline_TestTreeLine
        tests_test_treeline_TestTreeLine_setUp["⚡ setUp()"]:::function
        tests_test_treeline_TestTreeLine --> tests_test_treeline_TestTreeLine_setUp
        tests_test_treeline_TestTreeLine_tearDown["⚡ tearDown()"]:::function
        tests_test_treeline_TestTreeLine --> tests_test_treeline_TestTreeLine_tearDown
        tests_test_treeline_TestTreeLine_test_basic_tree["⚡ test_basic_tree()"]:::function
        tests_test_treeline_TestTreeLine --> tests_test_treeline_TestTreeLine_test_basic_tree
    end
    subgraph tests_test_nested_dir["tests.test_nested_dir"]
        tests_test_nested_dir_node["tests.test_nested_dir"]:::module
        tests_test_nested_dir_test_nested_directories["⚡ test_nested_directories()"]:::function
        tests_test_nested_dir_node --> tests_test_nested_dir_test_nested_directories
    end
    subgraph treeline_dependency_analyzer["treeline.dependency_analyzer"]
        treeline_dependency_analyzer_node["treeline.dependency_analyzer"]:::module
        treeline_dependency_analyzer_ModuleDependencyAnalyzer["📦 ModuleDependencyAnalyzer"]:::class
        treeline_dependency_analyzer_node --> treeline_dependency_analyzer_ModuleDependencyAnalyzer
        treeline_dependency_analyzer_ModuleDependencyAnalyzer___init__["⚡ __init__()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer___init__
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_analyze_directory["⚡ analyze_directory()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_analyze_directory
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_module["⚡ _analyze_module()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_module
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_imports["⚡ _analyze_imports()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_imports
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__collect_metrics["⚡ _collect_metrics()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__collect_metrics
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__calculate_complexity["⚡ _calculate_complexity()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__calculate_complexity
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_mermaid_graph["⚡ generate_mermaid_graph()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_mermaid_graph
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_summary_report["⚡ generate_summary_report()"]:::function
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_summary_report
    end
    subgraph treeline_analyzer["treeline.analyzer"]
        treeline_analyzer_node["treeline.analyzer"]:::module
        treeline_analyzer_CodeAnalyzer["📦 CodeAnalyzer"]:::class
        treeline_analyzer_node --> treeline_analyzer_CodeAnalyzer
        treeline_analyzer_CodeAnalyzer___init__["⚡ __init__()"]:::function
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer___init__
        treeline_analyzer_CodeAnalyzer_analyze_file["⚡ analyze_file()"]:::function
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer_analyze_file
        treeline_analyzer_CodeAnalyzer__get_function_params["⚡ _get_function_params()"]:::function
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer__get_function_params
        treeline_analyzer_CodeAnalyzer__find_function_calls["⚡ _find_function_calls()"]:::function
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer__find_function_calls
        treeline_analyzer_CodeAnalyzer_get_symbol["⚡ get_symbol()"]:::function
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer_get_symbol
        treeline_analyzer_CodeAnalyzer_format_structure["⚡ format_structure()"]:::function
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer_format_structure
    end
    subgraph treeline___init__["treeline.__init__"]
        treeline___init___node["treeline.__init__"]:::module
        treeline___init_____call__["⚡ __call__()"]:::function
        treeline___init___node --> treeline___init_____call__
    end
    subgraph treeline_enhanced_analyzer["treeline.enhanced_analyzer"]
        treeline_enhanced_analyzer_node["treeline.enhanced_analyzer"]:::module
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer["📦 EnhancedCodeAnalyzer"]:::class
        treeline_enhanced_analyzer_node --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer___init__["⚡ __init__()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer___init__
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer_analyze_file["⚡ analyze_file()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer_analyze_file
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_maintainability_index["⚡ _calculate_maintainability_index()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_maintainability_index
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_load["⚡ _calculate_cognitive_load()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_load
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_function_metrics["⚡ _check_function_metrics()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_function_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cyclomatic_complexity["⚡ _calculate_cyclomatic_complexity()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cyclomatic_complexity
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_complexity["⚡ _calculate_cognitive_complexity()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_complexity
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_file_metrics["⚡ _analyze_file_metrics()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_file_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__read_file["⚡ _read_file()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__read_file
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__parse_content["⚡ _parse_content()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__parse_content
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_elements["⚡ _analyze_code_elements()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_elements
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_class["⚡ _analyze_class()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_class
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_class_metrics["⚡ _check_class_metrics()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_class_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer_format_structure["⚡ format_structure()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer_format_structure
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_metrics_section["⚡ _format_metrics_section()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_metrics_section
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_function["⚡ _analyze_function()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_class_metrics["⚡ _calculate_class_metrics()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_class_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_function_metrics["⚡ _calculate_function_metrics()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_function_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_complexity["⚡ _calculate_complexity()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_complexity
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_nested_depth["⚡ _calculate_nested_depth()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_nested_depth
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_duplication["⚡ _analyze_code_duplication()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_duplication
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_imports["⚡ _analyze_imports()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_imports
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_inheritance["⚡ _analyze_inheritance()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_inheritance
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__add_issue["⚡ _add_issue()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__add_issue
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer_generate_report["⚡ generate_report()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer_generate_report
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_report_sections["⚡ _format_report_sections()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_report_sections
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_overview_section["⚡ _format_overview_section()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_overview_section
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_issues_section["⚡ _format_issues_section()"]:::function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_issues_section
    end
    subgraph treeline_core["treeline.core"]
        treeline_core_node["treeline.core"]:::module
        treeline_core_create_default_ignore["⚡ create_default_ignore()"]:::function
        treeline_core_node --> treeline_core_create_default_ignore
        treeline_core_read_ignore_patterns["⚡ read_ignore_patterns()"]:::function
        treeline_core_node --> treeline_core_read_ignore_patterns
        treeline_core_should_ignore["⚡ should_ignore()"]:::function
        treeline_core_node --> treeline_core_should_ignore
        treeline_core_clean_for_markdown["⚡ clean_for_markdown()"]:::function
        treeline_core_node --> treeline_core_clean_for_markdown
        treeline_core_format_mermaid_section["⚡ format_mermaid_section()"]:::function
        treeline_core_node --> treeline_core_format_mermaid_section
        treeline_core_format_structure["⚡ format_structure()"]:::function
        treeline_core_node --> treeline_core_format_structure
        treeline_core_generate_markdown_report["⚡ generate_markdown_report()"]:::function
        treeline_core_node --> treeline_core_generate_markdown_report
        treeline_core_generate_tree["⚡ generate_tree()"]:::function
        treeline_core_node --> treeline_core_generate_tree
        treeline_core_main["⚡ main()"]:::function
        treeline_core_node --> treeline_core_main
    end
    subgraph treeline_security_analyzer["treeline.security_analyzer"]
        treeline_security_analyzer_node["treeline.security_analyzer"]:::module
        treeline_security_analyzer_SecurityAnalyzer["📦 SecurityAnalyzer"]:::class
        treeline_security_analyzer_node --> treeline_security_analyzer_SecurityAnalyzer
        treeline_security_analyzer_SecurityAnalyzer___init__["⚡ __init__()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer___init__
        treeline_security_analyzer_SecurityAnalyzer_analyze_file["⚡ analyze_file()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer_analyze_file
        treeline_security_analyzer_SecurityAnalyzer__scan_patterns["⚡ _scan_patterns()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer__scan_patterns
        treeline_security_analyzer_SecurityAnalyzer__analyze_ast_security["⚡ _analyze_ast_security()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer__analyze_ast_security
        treeline_security_analyzer_SecurityAnalyzer__check_dangerous_attributes["⚡ _check_dangerous_attributes()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer__check_dangerous_attributes
        treeline_security_analyzer_SecurityAnalyzer__check_dangerous_imports["⚡ _check_dangerous_imports()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer__check_dangerous_imports
        treeline_security_analyzer_SecurityAnalyzer__add_security_issue["⚡ _add_security_issue()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer__add_security_issue
        treeline_security_analyzer_SecurityAnalyzer_generate_security_report["⚡ generate_security_report()"]:::function
        treeline_security_analyzer_SecurityAnalyzer --> treeline_security_analyzer_SecurityAnalyzer_generate_security_report
    end
    subgraph treeline___main__["treeline.__main__"]
        treeline___main___node["treeline.__main__"]:::module
    end
    tests_test_special_char_test_special_characters -.->|calls| treeline_core_generate_tree
    tests_test_missing_dir_test_non_existent_directory -.->|calls| treeline_core_generate_tree
    tests_test_empty_dir_test_empty_directory -.->|calls| treeline_core_generate_tree
    tests_test_nested_dir_test_nested_directories -.->|calls| treeline_core_generate_tree
    treeline___init_____call__ -.->|calls| treeline_core_generate_tree
    treeline_core_main -.->|calls| treeline_core_generate_tree
    treeline_core_generate_markdown_report -.->|calls| treeline_core_format_mermaid_section
    treeline_core_generate_markdown_report -.->|calls| treeline_core_clean_for_markdown
    treeline_core_generate_tree -.->|calls| treeline_core_read_ignore_patterns
    treeline_core_generate_tree -.->|calls| treeline_core_generate_markdown_report
    treeline_core_generate_tree -.->|calls| treeline_core_should_ignore
    treeline_core_main -.->|calls| treeline_core_create_default_ignore
    tests_test_special_char_node --> treeline_core_node
    tests_test_missing_dir_node --> treeline_core_node
    tests_test_empty_dir_node --> treeline_core_node
    tests_test_core_node --> treeline_core_node
    tests_test_nested_dir_node --> treeline_core_node
    treeline___main___node --> treeline_core_node
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
- Functions: **10**
- Classes: **0**
- Complexity: **56**

### treeline.dependency_analyzer
- Functions: **8**
- Classes: **1**
- Complexity: **62**

### treeline.enhanced_analyzer
- Functions: **31**
- Classes: **1**
- Complexity: **123**

### treeline.security_analyzer
- Functions: **8**
- Classes: **1**
- Complexity: **27**

## Complexity Hotspots

### _analyze_module
- **Module**: treeline.dependency_analyzer
- **Complexity**: 15

### format_structure
- **Module**: treeline.enhanced_analyzer
- **Complexity**: 15

### generate_mermaid_graph
- **Module**: treeline.dependency_analyzer
- **Complexity**: 14

### generate_summary_report
- **Module**: treeline.dependency_analyzer
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

