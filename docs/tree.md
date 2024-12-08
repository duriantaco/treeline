# Project Analysis Report

## Code Structure Visualization

The following diagrams show the project structure from different perspectives:

### Module Dependencies
Overview of how modules are connected:

```mermaid
graph TD

    %% Styling
    classDef modNode fill:#b7e2d8,stroke:#333,stroke-width:2px

    setup["setup"]:::modNode
    tests_test_special_char["tests.test_special_char"]:::modNode
    tests_test_empty_dir["tests.test_empty_dir"]:::modNode
    tests_test_core["tests.test_core"]:::modNode
    tests_test_treeline["tests.test_treeline"]:::modNode
    tests_test_nested_dir["tests.test_nested_dir"]:::modNode
    treeline_type_checker["treeline.type_checker"]:::modNode
    treeline_diff_visualizer["treeline.diff_visualizer"]:::modNode
    treeline_dependency_analyzer["treeline.dependency_analyzer"]:::modNode
    treeline_analyzer["treeline.analyzer"]:::modNode
    treeline___init__["treeline.__init__"]:::modNode
    treeline_enhanced_analyzer["treeline.enhanced_analyzer"]:::modNode
    treeline_core["treeline.core"]:::modNode
    treeline___main__["treeline.__main__"]:::modNode
    treeline_models_dependency_analyzer["treeline.models.dependency_analyzer"]:::modNode
    treeline_models_analyzer["treeline.models.analyzer"]:::modNode
    treeline_models___init__["treeline.models.__init__"]:::modNode
    treeline_models_enhanced_analyzer["treeline.models.enhanced_analyzer"]:::modNode
    treeline_models_core["treeline.models.core"]:::modNode

    tests_test_special_char --> treeline_core
    tests_test_empty_dir --> treeline_core
    tests_test_core --> treeline_core
    tests_test_nested_dir --> treeline_core
    treeline_diff_visualizer --> treeline_dependency_analyzer
    treeline_diff_visualizer --> treeline_models_dependency_analyzer
    treeline_dependency_analyzer --> treeline_models_dependency_analyzer
    treeline_analyzer --> treeline_type_checker
    treeline_analyzer --> treeline_models_analyzer
    treeline_enhanced_analyzer --> treeline_models_enhanced_analyzer
    treeline_core --> treeline_type_checker
    treeline_core --> treeline_dependency_analyzer
    treeline_core --> treeline_enhanced_analyzer
    treeline_core --> treeline_diff_visualizer
    treeline_core --> treeline_models_core
    treeline___main__ --> treeline_core
    treeline_models_analyzer --> treeline_type_checker
    treeline_models_enhanced_analyzer --> treeline_type_checker
    treeline_models_core --> treeline_type_checker
```

### treeline.__init__

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline___init__["treeline.__init__"]
        direction TB
        treeline___init_____call__["⚡ __call__"]:::fnNode
    end

```

### treeline.__main__

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline___main__["treeline.__main__"]
        direction TB
    end

```

### treeline.analyzer

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_analyzer["treeline.analyzer"]
        direction TB
        treeline_analyzer_CodeAnalyzer["📦 CodeAnalyzer"]:::clsNode
        treeline_analyzer_CodeAnalyzer___init__["⚡ __init__"]:::fnNode
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer___init__
        treeline_analyzer_CodeAnalyzer_analyze_file["⚡ analyze_file"]:::fnNode
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer_analyze_file
        treeline_analyzer_CodeAnalyzer__get_function_params["⚡ _get_function_params"]:::fnNode
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer__get_function_params
        treeline_analyzer_CodeAnalyzer__find_function_calls["⚡ _find_function_calls"]:::fnNode
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer__find_function_calls
        treeline_analyzer_CodeAnalyzer_get_symbol["⚡ get_symbol"]:::fnNode
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer_get_symbol
        treeline_analyzer_CodeAnalyzer_format_structure["⚡ format_structure"]:::fnNode
        treeline_analyzer_CodeAnalyzer --> treeline_analyzer_CodeAnalyzer_format_structure
    end

```

### treeline.core

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_core["treeline.core"]
        direction TB
        treeline_core_create_default_ignore["⚡ create_default_ignore"]:::fnNode
        treeline_core_read_ignore_patterns["⚡ read_ignore_patterns"]:::fnNode
        treeline_core_should_ignore["⚡ should_ignore"]:::fnNode
        treeline_core_clean_for_markdown["⚡ clean_for_markdown"]:::fnNode
        treeline_core_format_structure["⚡ format_structure"]:::fnNode
        treeline_core_generate_markdown_report["⚡ generate_markdown_report"]:::fnNode
        treeline_core_generate_tree["⚡ generate_tree"]:::fnNode
        treeline_core_main["⚡ main"]:::fnNode
    end

    treeline_core_main -.->|calls| treeline_core_generate_tree
    treeline_core_generate_markdown_report -.->|calls| treeline_core_clean_for_markdown
    treeline_core_generate_tree -.->|calls| treeline_core_read_ignore_patterns
    treeline_core_generate_tree -.->|calls| treeline_core_generate_markdown_report
    treeline_core_generate_tree -.->|calls| treeline_core_should_ignore
    treeline_core_main -.->|calls| treeline_core_create_default_ignore
```

### treeline.dependency_analyzer

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_dependency_analyzer["treeline.dependency_analyzer"]
        direction TB
        treeline_dependency_analyzer_ModuleDependencyAnalyzer["📦 ModuleDependencyAnalyzer"]:::clsNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer___init__["⚡ __init__"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer___init__
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_analyze_directory["⚡ analyze_directory"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_analyze_directory
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_module["⚡ _analyze_module"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_module
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_imports["⚡ _analyze_imports"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__analyze_imports
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__collect_metrics["⚡ _collect_metrics"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__collect_metrics
        treeline_dependency_analyzer_ModuleDependencyAnalyzer__calculate_complexity["⚡ _calculate_complexity"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer__calculate_complexity
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_module_overview_diagram["⚡ generate_module_overview_diagram"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_module_overview_diagram
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_module_detail_diagram["⚡ generate_module_detail_diagram"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_module_detail_diagram
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_mermaid_graphs["⚡ generate_mermaid_graphs"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_mermaid_graphs
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_html_visualization["⚡ generate_html_visualization"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_html_visualization
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_summary_report["⚡ generate_summary_report"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_summary_report
    end

```

### treeline.diff_visualizer

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_diff_visualizer["treeline.diff_visualizer"]
        direction TB
        treeline_diff_visualizer_DiffVisualizer["📦 DiffVisualizer"]:::clsNode
        treeline_diff_visualizer_DiffVisualizer___init__["⚡ __init__"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer___init__
        treeline_diff_visualizer_DiffVisualizer__serialize_graph_data["⚡ _serialize_graph_data"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__serialize_graph_data
        treeline_diff_visualizer_DiffVisualizer__serialize_node["⚡ _serialize_node"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__serialize_node
        treeline_diff_visualizer_DiffVisualizer__serialize_link["⚡ _serialize_link"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__serialize_link
        treeline_diff_visualizer_DiffVisualizer__node_was_modified_serial["⚡ _node_was_modified_serial"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__node_was_modified_serial
        treeline_diff_visualizer_DiffVisualizer__get_node_changes_serial["⚡ _get_node_changes_serial"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__get_node_changes_serial
        treeline_diff_visualizer_DiffVisualizer__run_git_command["⚡ _run_git_command"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__run_git_command
        treeline_diff_visualizer_DiffVisualizer__is_git_repo["⚡ _is_git_repo"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__is_git_repo
        treeline_diff_visualizer_DiffVisualizer__commit_exists["⚡ _commit_exists"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__commit_exists
        treeline_diff_visualizer_DiffVisualizer__analyze_commit["⚡ _analyze_commit"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__analyze_commit
        treeline_diff_visualizer_DiffVisualizer__compute_changes["⚡ _compute_changes"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer__compute_changes
        treeline_diff_visualizer_DiffVisualizer_generate_structural_diff["⚡ generate_structural_diff"]:::fnNode
        treeline_diff_visualizer_DiffVisualizer --> treeline_diff_visualizer_DiffVisualizer_generate_structural_diff
    end

```

### treeline.enhanced_analyzer

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_enhanced_analyzer["treeline.enhanced_analyzer"]
        direction TB
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer["📦 EnhancedCodeAnalyzer"]:::clsNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer___init__["⚡ __init__"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer___init__
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer_analyze_file["⚡ analyze_file"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer_analyze_file
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_maintainability_index["⚡ _calculate_maintainability_index"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_maintainability_index
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_load["⚡ _calculate_cognitive_load"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_load
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_function_metrics["⚡ _check_function_metrics"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_function_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cyclomatic_complexity["⚡ _calculate_cyclomatic_complexity"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cyclomatic_complexity
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_complexity["⚡ _calculate_cognitive_complexity"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_cognitive_complexity
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_file_metrics["⚡ _analyze_file_metrics"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_file_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__read_file["⚡ _read_file"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__read_file
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__parse_content["⚡ _parse_content"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__parse_content
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_elements["⚡ _analyze_code_elements"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_elements
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_class["⚡ _analyze_class"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_class
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_class_metrics["⚡ _check_class_metrics"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__check_class_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer_format_structure["⚡ format_structure"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer_format_structure
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_metrics_section["⚡ _format_metrics_section"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_metrics_section
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_function["⚡ _analyze_function"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_function
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_class_metrics["⚡ _calculate_class_metrics"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_class_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_function_metrics["⚡ _calculate_function_metrics"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_function_metrics
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_complexity["⚡ _calculate_complexity"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_complexity
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_nested_depth["⚡ _calculate_nested_depth"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__calculate_nested_depth
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_duplication["⚡ _analyze_code_duplication"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_code_duplication
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_imports["⚡ _analyze_imports"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_imports
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_inheritance["⚡ _analyze_inheritance"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__analyze_inheritance
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__add_issue["⚡ _add_issue"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__add_issue
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer_generate_report["⚡ generate_report"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer_generate_report
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_report_sections["⚡ _format_report_sections"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_report_sections
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_overview_section["⚡ _format_overview_section"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_overview_section
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_issues_section["⚡ _format_issues_section"]:::fnNode
        treeline_enhanced_analyzer_EnhancedCodeAnalyzer --> treeline_enhanced_analyzer_EnhancedCodeAnalyzer__format_issues_section
    end

```

### treeline.models.__init__

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_models___init__["treeline.models.__init__"]
        direction TB
    end

```

### treeline.models.analyzer

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_models_analyzer["treeline.models.analyzer"]
        direction TB
        treeline_models_analyzer_FunctionCall["📦 FunctionCall"]:::clsNode
        treeline_models_analyzer_CodeStructure["📦 CodeStructure"]:::clsNode
        treeline_models_analyzer_FunctionNode["📦 FunctionNode"]:::clsNode
        treeline_models_analyzer_ClassNode["📦 ClassNode"]:::clsNode
        treeline_models_analyzer_AnalyzerConfig["📦 AnalyzerConfig"]:::clsNode
    end

```

### treeline.models.core

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_models_core["treeline.models.core"]
        direction TB
        treeline_models_core_CodeStructure["📦 CodeStructure"]:::clsNode
        treeline_models_core_TreeOptions["📦 TreeOptions"]:::clsNode
        treeline_models_core_ModuleMetrics["📦 ModuleMetrics"]:::clsNode
    end

```

### treeline.models.dependency_analyzer

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_models_dependency_analyzer["treeline.models.dependency_analyzer"]
        direction TB
        treeline_models_dependency_analyzer_FunctionLocation["📦 FunctionLocation"]:::clsNode
        treeline_models_dependency_analyzer_FunctionCallInfo["📦 FunctionCallInfo"]:::clsNode
        treeline_models_dependency_analyzer_ClassMethod["📦 ClassMethod"]:::clsNode
        treeline_models_dependency_analyzer_ClassInfo["📦 ClassInfo"]:::clsNode
        treeline_models_dependency_analyzer_ModuleMetrics["📦 ModuleMetrics"]:::clsNode
        treeline_models_dependency_analyzer_ComplexFunction["📦 ComplexFunction"]:::clsNode
        treeline_models_dependency_analyzer_MethodInfo["📦 MethodInfo"]:::clsNode
        treeline_models_dependency_analyzer_Node["📦 Node"]:::clsNode
        treeline_models_dependency_analyzer_Link["📦 Link"]:::clsNode
        treeline_models_dependency_analyzer_GraphData["📦 GraphData"]:::clsNode
    end

```

### treeline.models.enhanced_analyzer

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_models_enhanced_analyzer["treeline.models.enhanced_analyzer"]
        direction TB
        treeline_models_enhanced_analyzer_FunctionMetrics["📦 FunctionMetrics"]:::clsNode
        treeline_models_enhanced_analyzer_ClassMetrics["📦 ClassMetrics"]:::clsNode
        treeline_models_enhanced_analyzer_CodeDuplication["📦 CodeDuplication"]:::clsNode
        treeline_models_enhanced_analyzer_QualityIssue["📦 QualityIssue"]:::clsNode
    end

```

### treeline.type_checker

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_type_checker["treeline.type_checker"]
        direction TB
        treeline_type_checker_TypeValidator["📦 TypeValidator"]:::clsNode
        treeline_type_checker_TypeValidator_validate["⚡ validate"]:::fnNode
        treeline_type_checker_TypeValidator --> treeline_type_checker_TypeValidator_validate
        treeline_type_checker_TypeChecked["📦 TypeChecked"]:::clsNode
        treeline_type_checker_TypeChecked___post_init__["⚡ __post_init__"]:::fnNode
        treeline_type_checker_TypeChecked --> treeline_type_checker_TypeChecked___post_init__
        treeline_type_checker_ValidationError["📦 ValidationError"]:::clsNode
    end

```
## Directory Structure

```

├─ docs
│ ├─ code_visualization.html
│ ├─ index.html
│ └─ tree.md
├─ example
│ ├─ tree.md
│ └─ tut1.ipynb
├─ source
│ ├─ conf.py
│ └─ index.rst
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
│ │   **Class**: ◆ TestEmptyDirectory
│ │   └─ ! Missing class docstring
│ │   **Function**: → setUp
│ │   └─ # Set up test directory
│ │   **Function**: → tearDown
│ │   └─ # Clean up test directory
│ │   **Function**: → test_empty_directory
│ │   └─ # Test handling of empty directory
│ ├─ test_nested_dir.py
│ │   **Class**: ◆ TestNestedDirectories
│ │   └─ ! Missing class docstring
│ │   **Function**: → setUp
│ │   └─ # Set up test directory
│ │   **Function**: → tearDown
│ │   └─ # Clean up test directory
│ │   **Function**: → test_nested_directories
│ │   └─ # Test handling of nested directories
│ ├─ test_special_char.py
│ │   **Class**: ◆ TestSpecialCharacters
│ │   └─ ! Missing class docstring
│ │   **Function**: → setUp
│ │   └─ # Set up test directory
│ │   **Function**: → tearDown
│ │   └─ # Clean up test directory
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
│ ├─ models
│ │ ├─ __init__.py
│ │ ├─ analyzer.py
│ │ │   **Class**: ◆ FunctionCall
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ CodeStructure
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ FunctionNode
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ ClassNode
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ AnalyzerConfig
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ ├─ core.py
│ │ │   **Class**: ◆ CodeStructure
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ TreeOptions
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ ModuleMetrics
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ ├─ dependency_analyzer.py
│ │ │   **Class**: ◆ FunctionLocation
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ FunctionCallInfo
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ ClassMethod
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ ClassInfo
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ ModuleMetrics
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ ComplexFunction
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ MethodInfo
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ Node
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ Link
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   **Class**: ◆ GraphData
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ └─ enhanced_analyzer.py
│ │     **Class**: ◆ FunctionMetrics
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ │     **Class**: ◆ ClassMetrics
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ │     **Class**: ◆ CodeDuplication
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ │     **Class**: ◆ QualityIssue
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ ├─ __init__.py
│ │   **Function**: → __call__
│ ├─ __main__.py
│ ├─ analyzer.py
│ │   **Class**: ◆ CodeAnalyzer
│ │   └─ # Simple analyzer for extracting functions and classes from Python files.
│ │   └─ ! High complexity (34)
│ │   └─ ! Too long (207 lines)
│ │   └─ ! Class too long
│ │   **Function**: → __init__
│ │   **Function**: → analyze_file
│ │   └─ # Extracts functions and classes with optional params and relationships.
│ │   └─ ! High complexity (12)
│ │   └─ ! Too long (99 lines)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _get_function_params
│ │   └─ # Extract function parameters with type hints.
│ │   **Function**: → _find_function_calls
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
│ │   └─ ! High complexity (13)
│ │   └─ ! Too long (61 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_markdown_report
│ │   └─ # Generate a markdown report with tree structure and analysis results.
│ │   **Function**: → generate_tree
│ │   └─ # Generate tree structure with code quality and security analysis.
│ │   └─ ! High complexity (13)
│ │   └─ ! Too long (73 lines)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → main
│ │   └─ ! Too long (83 lines)
│ │   └─ ! Deep nesting (depth 5)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! Excessive nesting depth (> 4)
│ │   **Function**: → add_directory
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ default_ignore
│ ├─ dependency_analyzer.py
│ │   **Class**: ◆ ModuleDependencyAnalyzer
│ │   └─ # Analyzes module-level dependencies and generates summary reports.
│ │   └─ ! High complexity (95)
│ │   └─ ! Too long (916 lines)
│ │   └─ ! Class too long
│ │   └─ ! Too many methods
│ │   └─ ! High class complexity
│ │   **Function**: → __init__
│ │   └─ ! Too long (391 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   **Function**: → analyze_directory
│ │   └─ # Analyze all Python files in directory.
│ │   **Function**: → _analyze_module
│ │   └─ # Analyze a single module's contents and relationships.
│ │   └─ ! High complexity (15)
│ │   └─ ! Too long (52 lines)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
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
│ │   **Function**: → generate_module_overview_diagram
│ │   └─ # Generate a Mermaid diagram showing modules and their relationships.
│ │   **Function**: → generate_module_detail_diagram
│ │   └─ # Generate a Mermaid diagram showing functions and classes in a module.
│ │   └─ ! High complexity (17)
│ │   └─ ! Too long (59 lines)
│ │   └─ ! Deep nesting (depth 5)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_mermaid_graphs
│ │   └─ # Generate a markdown report with multiple focused Mermaid graphs.
│ │   **Function**: → generate_html_visualization
│ │   └─ # Generate an interactive HTML visualization using D3.js
│ │   └─ ! High complexity (18)
│ │   └─ ! Too long (112 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → generate_summary_report
│ │   └─ # Generate a readable markdown report with a link to the interactive visualization.
│ │   └─ ! High complexity (17)
│ │   └─ ! Too long (115 lines)
│ │   └─ ! Deep nesting (depth 6)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ diff_visualizer.py
│ │   **Class**: ◆ DiffVisualizer
│ │   └─ # Visualizes structural differences between different versions of Python code.
│ │   └─ ! High complexity (32)
│ │   └─ ! Too long (266 lines)
│ │   └─ ! Class too long
│ │   └─ ! Too many methods
│ │   **Function**: → __init__
│ │   **Function**: → _serialize_graph_data
│ │   └─ # Convert a GraphData object to a serializable dictionary
│ │   **Function**: → _serialize_node
│ │   └─ # Convert a Node object to a serializable dictionary
│ │   **Function**: → _serialize_link
│ │   └─ # Convert a link dictionary to a serializable format
│ │   **Function**: → _node_was_modified_serial
│ │   └─ # Check if a serialized node's important properties changed
│ │   **Function**: → _get_node_changes_serial
│ │   └─ # Get detailed changes for modified serialized nodes
│ │   **Function**: → _run_git_command
│ │   └─ # Run a git command with error handling
│ │   **Function**: → _is_git_repo
│ │   **Function**: → _commit_exists
│ │   **Function**: → _analyze_commit
│ │   └─ # Analyze a specific commit and return serializable data
│ │   **Function**: → _compute_changes
│ │   └─ # Compute the differences between two dependency graphs
│ │   **Function**: → generate_structural_diff
│ │   └─ # Generate a visual diff between two commits
│ │   └─ ! Too long (101 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → node_key
│ │   **Function**: → link_key
│ ├─ enhanced_analyzer.py
│ │   **Class**: ◆ EnhancedCodeAnalyzer
│ │   └─ # Enhanced analyzer for code quality and maintainability metrics.
│ │    This analyzer implements industry-standard code quality checks and metrics
│ │    following Clean Code principles, SOLID principles, and PEP 8 standards.
│ │   └─ ! High complexity (123)
│ │   └─ ! Too long (606 lines)
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
│ │   └─ ! Too long (66 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
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
│ │   └─ ! Too long (56 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   **Function**: → _format_metrics_section
│ │   └─ # Format the metrics section of the report.
│ │   **Function**: → _analyze_function
│ │   └─ # Analyze a function's quality metrics.
│ │   **Function**: → _calculate_class_metrics
│ │   **Function**: → _calculate_function_metrics
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
│ └─ type_checker.py
│     **Class**: ◆ TypeValidator
│     └─ ! High complexity (22)
│     └─ ! Too long (62 lines)
│     └─ ! Missing class docstring
│     **Class**: ◆ TypeChecked
│     └─ # Base class for type-checked dataclasses
│     └─ ! Too few public method (< 1, SOLID-ISP)
│     **Class**: ◆ ValidationError
│     └─ # Raised when type validation fails
│     └─ ! Too few public method (< 1, SOLID-ISP)
│     **Function**: → validate
│     └─ # Validates that a value matches the expected type, with support for generics.
│      Args:
│      value: The value to validate
│      expected_type: The expected type (can be a generic type)
│      Raises:
│      TypeError: If the value doesn't match the expected type
│     └─ ! High complexity (22)
│     └─ ! Too long (60 lines)
│     └─ ! Deep nesting (depth 6)
│     └─ ! Function exceeds 50 lines
│     └─ ! High cyclomatic complexity(> 10)
│     └─ ! High cognitive complexity (> 15)
│     └─ ! Excessive nesting depth (> 4)
│     └─ ! High cognitive load (> 7 items)
│     **Function**: → __post_init__
│     └─ # Validate types after initialization
├─ treeline.egg-info
│ ├─ dependency_links.txt
│ ├─ entry_points.txt
│ ├─ PKG-INFO
│ ├─ requires.txt
│ ├─ SOURCES.txt
│ └─ top_level.txt
├─ .flake8
├─ .pre-commit-config.yaml
├─ .treeline-ignore
├─ code_diff.html
├─ License
├─ make.bat
├─ Makefile
├─ pyproject.toml
├─ README.md
└─ setup.py
```

## Code Quality Metrics

### setup
- Functions: **0**
- Classes: **0**
- Complexity: **0**

### source.conf
- Functions: **0**
- Classes: **0**
- Complexity: **0**

### tests.test_core
- Functions: **4**
- Classes: **1**
- Complexity: **5**

### tests.test_empty_dir
- Functions: **3**
- Classes: **1**
- Complexity: **4**

### tests.test_nested_dir
- Functions: **3**
- Classes: **1**
- Complexity: **4**

### tests.test_special_char
- Functions: **3**
- Classes: **1**
- Complexity: **4**

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
- Complexity: **34**

### treeline.core
- Functions: **9**
- Classes: **0**
- Complexity: **61**

### treeline.dependency_analyzer
- Functions: **11**
- Classes: **1**
- Complexity: **95**

### treeline.diff_visualizer
- Functions: **14**
- Classes: **1**
- Complexity: **32**

### treeline.enhanced_analyzer
- Functions: **31**
- Classes: **1**
- Complexity: **123**

### treeline.models.__init__
- Functions: **0**
- Classes: **0**
- Complexity: **0**

### treeline.models.analyzer
- Functions: **0**
- Classes: **5**
- Complexity: **0**

### treeline.models.core
- Functions: **0**
- Classes: **3**
- Complexity: **0**

### treeline.models.dependency_analyzer
- Functions: **0**
- Classes: **10**
- Complexity: **0**

### treeline.models.enhanced_analyzer
- Functions: **0**
- Classes: **4**
- Complexity: **0**

### treeline.type_checker
- Functions: **2**
- Classes: **3**
- Complexity: **25**

## Complexity Hotspots

### validate
- **Module**: treeline.type_checker
- **Complexity**: 22

### generate_html_visualization
- **Module**: treeline.dependency_analyzer
- **Complexity**: 18

### generate_module_detail_diagram
- **Module**: treeline.dependency_analyzer
- **Complexity**: 17

### generate_summary_report
- **Module**: treeline.dependency_analyzer
- **Complexity**: 17

### _analyze_module
- **Module**: treeline.dependency_analyzer
- **Complexity**: 15

### format_structure
- **Module**: treeline.enhanced_analyzer
- **Complexity**: 15

### _analyze_file_metrics
- **Module**: treeline.enhanced_analyzer
- **Complexity**: 13

### format_structure
- **Module**: treeline.core
- **Complexity**: 13

### generate_tree
- **Module**: treeline.core
- **Complexity**: 13

### analyze_file
- **Module**: treeline.analyzer
- **Complexity**: 12
