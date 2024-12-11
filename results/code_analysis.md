# Project Analysis Report

[Open Interactive Code Visualization](./code_visualization.html)

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
    treeline_dependency_analyzer["treeline.dependency_analyzer"]:::modNode
    treeline_analyzer["treeline.analyzer"]:::modNode
    treeline___init__["treeline.__init__"]:::modNode
    treeline_enhanced_analyzer["treeline.enhanced_analyzer"]:::modNode
    treeline_core["treeline.core"]:::modNode
    treeline_ignore["treeline.ignore"]:::modNode
    treeline___main__["treeline.__main__"]:::modNode
    treeline_models_dependency_analyzer["treeline.models.dependency_analyzer"]:::modNode
    treeline_models_analyzer["treeline.models.analyzer"]:::modNode
    treeline_models___init__["treeline.models.__init__"]:::modNode
    treeline_models_enhanced_analyzer["treeline.models.enhanced_analyzer"]:::modNode
    treeline_models_core["treeline.models.core"]:::modNode
    docs_conf["docs.conf"]:::modNode
    build_lib_treeline_type_checker["build.lib.treeline.type_checker"]:::modNode
    build_lib_treeline_dependency_analyzer["build.lib.treeline.dependency_analyzer"]:::modNode
    build_lib_treeline_analyzer["build.lib.treeline.analyzer"]:::modNode
    build_lib_treeline___init__["build.lib.treeline.__init__"]:::modNode
    build_lib_treeline_enhanced_analyzer["build.lib.treeline.enhanced_analyzer"]:::modNode
    build_lib_treeline_core["build.lib.treeline.core"]:::modNode
    build_lib_treeline___main__["build.lib.treeline.__main__"]:::modNode
    build_lib_treeline_models_dependency_analyzer["build.lib.treeline.models.dependency_analyzer"]:::modNode
    build_lib_treeline_models_analyzer["build.lib.treeline.models.analyzer"]:::modNode
    build_lib_treeline_models___init__["build.lib.treeline.models.__init__"]:::modNode
    build_lib_treeline_models_enhanced_analyzer["build.lib.treeline.models.enhanced_analyzer"]:::modNode
    build_lib_treeline_models_core["build.lib.treeline.models.core"]:::modNode

    tests_test_special_char --> treeline_core
    tests_test_empty_dir --> treeline_core
    tests_test_core --> treeline_core
    tests_test_nested_dir --> treeline_core
    treeline_dependency_analyzer --> treeline_models_dependency_analyzer
    treeline_dependency_analyzer --> treeline_ignore
    treeline_analyzer --> treeline_models_analyzer
    treeline_analyzer --> treeline_type_checker
    treeline_enhanced_analyzer --> treeline_models_enhanced_analyzer
    treeline_core --> treeline_models_core
    treeline_core --> treeline_dependency_analyzer
    treeline_core --> treeline_enhanced_analyzer
    treeline_core --> treeline_type_checker
    treeline_core --> treeline_ignore
    treeline___main__ --> treeline_core
    treeline_models_analyzer --> treeline_type_checker
    treeline_models_enhanced_analyzer --> treeline_type_checker
    treeline_models_core --> treeline_type_checker
    build_lib_treeline_dependency_analyzer --> treeline_models_dependency_analyzer
    build_lib_treeline_analyzer --> treeline_models_analyzer
    build_lib_treeline_analyzer --> treeline_type_checker
    build_lib_treeline_enhanced_analyzer --> treeline_models_enhanced_analyzer
    build_lib_treeline_core --> treeline_models_core
    build_lib_treeline_core --> treeline_enhanced_analyzer
    build_lib_treeline_core --> treeline_type_checker
    build_lib_treeline_core --> treeline_dependency_analyzer
    build_lib_treeline___main__ --> treeline_core
    build_lib_treeline_models_analyzer --> treeline_type_checker
    build_lib_treeline_models_enhanced_analyzer --> treeline_type_checker
    build_lib_treeline_models_core --> treeline_type_checker
```

### treeline.__init__

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline___init__["treeline.__init__"]
        direction TB
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
    end

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
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_clean_for_markdown["⚡ clean_for_markdown"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_clean_for_markdown
        treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_reports["⚡ generate_reports"]:::fnNode
        treeline_dependency_analyzer_ModuleDependencyAnalyzer --> treeline_dependency_analyzer_ModuleDependencyAnalyzer_generate_reports
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

### treeline.ignore

```mermaid
graph TD

    %% Styling
    classDef fnNode fill:#e4d1d1,stroke:#333
    classDef clsNode fill:#d1e0e4,stroke:#333

    subgraph treeline_ignore["treeline.ignore"]
        direction TB
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
        treeline_models_dependency_analyzer_Node___post_init__["⚡ __post_init__"]:::fnNode
        treeline_models_dependency_analyzer_Node --> treeline_models_dependency_analyzer_Node___post_init__
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

├─ assets
│ ├─ screenshot1.png
│ ├─ screenshot2.png
│ └─ Treeline.png
├─ build
│ ├─ bdist.macosx-13.0-arm64
│ └─ lib
│   └─ treeline
│     ├─ models
│     │ ├─ __init__.py
│     │ ├─ analyzer.py
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionCall
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeStructure
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionNode
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassNode
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> AnalyzerConfig
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ ├─ core.py
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeStructure
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TreeOptions
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ModuleMetrics
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ ├─ dependency_analyzer.py
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionLocation
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionCallInfo
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassMethod
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassInfo
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ModuleMetrics
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ComplexFunction
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> MethodInfo
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> Node
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> Link
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> GraphData
│     │ │   └─ ! Missing class docstring
│     │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│     │ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __post_init__
│     │ └─ enhanced_analyzer.py
│     │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionMetrics
│     │     └─ ! Missing class docstring
│     │     └─ ! Too few public method (< 1, SOLID-ISP)
│     │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassMetrics
│     │     └─ ! Missing class docstring
│     │     └─ ! Too few public method (< 1, SOLID-ISP)
│     │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeDuplication
│     │     └─ ! Missing class docstring
│     │     └─ ! Too few public method (< 1, SOLID-ISP)
│     │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> QualityIssue
│     │     └─ ! Missing class docstring
│     │     └─ ! Too few public method (< 1, SOLID-ISP)
│     ├─ __init__.py
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __call__
│     ├─ __main__.py
│     ├─ analyzer.py
│     │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeAnalyzer
│     │   └─ <span class="docstring">Simple analyzer for extracting functions and classes from Python files.</span>
│     │   └─ ! High complexity (34)
│     │   └─ ! Too long (207 lines)
│     │   └─ ! Class too long
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __init__
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> analyze_file
│     │   └─ <span class="docstring">Extracts functions and classes with optional params and relationships.</span>
│     │   └─ ! High complexity (12)
│     │   └─ ! Too long (99 lines)
│     │   └─ ! Deep nesting (depth 7)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! Excessive nesting depth (> 4)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _get_function_params
│     │   └─ <span class="docstring">Extract function parameters with type hints.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _find_function_calls
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> get_symbol
│     │   └─ <span class="docstring">Maps item types to their display symbols.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> format_structure
│     │   └─ <span class="docstring">Formats the code structure into displayable lines with colors and prefixes.</span>
│     │   └─ ! High cognitive load (> 7 items)
│     ├─ core.py
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> create_default_ignore
│     │   └─ <span class="docstring">Create default .treeline-ignore if it doesn't exist.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> read_ignore_patterns
│     │   └─ <span class="docstring">Read patterns from .treeline-ignore file</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> should_ignore
│     │   └─ <span class="docstring">Check if path should be ignored based on patterns.</span>
│     │   └─ ! High complexity (11)
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> format_structure
│     │   └─ <span class="docstring">Format the analysis results into a readable tree structure.</span>
│     │    Args:
│     │    structure: List of analysis results
│     │    indent: String to use for indentation
│     │    Returns:
│     │    List of formatted strings representing the code structure
│     │   └─ ! High complexity (13)
│     │   └─ ! Too long (61 lines)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_tree
│     │   └─ <span class="docstring">Generate tree structure with code quality and security analysis.</span>
│     │   └─ ! High complexity (14)
│     │   └─ ! Too long (76 lines)
│     │   └─ ! Deep nesting (depth 7)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! Excessive nesting depth (> 4)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> main
│     │   └─ ! Too long (51 lines)
│     │   └─ ! Function exceeds 50 lines
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> add_directory
│     │   └─ ! Deep nesting (depth 7)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! Excessive nesting depth (> 4)
│     │   └─ ! High cognitive load (> 7 items)
│     ├─ default_ignore
│     ├─ dependency_analyzer.py
│     │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ModuleDependencyAnalyzer
│     │   └─ <span class="docstring">Analyzes module-level dependencies and generates summary reports.</span>
│     │   └─ ! High complexity (92)
│     │   └─ ! Too long (1211 lines)
│     │   └─ ! Class too long
│     │   └─ ! Too many methods
│     │   └─ ! High class complexity
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __init__
│     │   └─ ! Too long (487 lines)
│     │   └─ ! Function exceeds 50 lines
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> analyze_directory
│     │   └─ <span class="docstring">Analyze all Python files in directory.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_module
│     │   └─ <span class="docstring">Analyze a single module's contents and relationships.</span>
│     │   └─ ! High complexity (15)
│     │   └─ ! Too long (52 lines)
│     │   └─ ! Deep nesting (depth 7)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! Excessive nesting depth (> 4)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_imports
│     │   └─ <span class="docstring">Collect import information from AST.</span>
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _collect_metrics
│     │   └─ <span class="docstring">Collect code metrics for the module.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_complexity
│     │   └─ <span class="docstring">Calculate cyclomatic complexity.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_module_overview_diagram
│     │   └─ <span class="docstring">Generate a Mermaid diagram showing modules and their relationships.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_module_detail_diagram
│     │   └─ <span class="docstring">Generate a Mermaid diagram showing functions and classes in a module.</span>
│     │   └─ ! High complexity (17)
│     │   └─ ! Too long (59 lines)
│     │   └─ ! Deep nesting (depth 5)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! Excessive nesting depth (> 4)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_mermaid_graphs
│     │   └─ <span class="docstring">Generate a markdown report with multiple focused Mermaid graphs.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_html_visualization
│     │   └─ <span class="docstring">Generate an interactive HTML visualization using D3.js</span>
│     │   └─ ! High complexity (18)
│     │   └─ ! Too long (177 lines)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> clean_for_markdown
│     │   └─ <span class="docstring">Remove ANSI colors and simplify symbols for markdown.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_reports
│     │   └─ <span class="docstring">Generate comprehensive HTML and markdown reports of the code analysis.</span>
│     │   └─ ! High complexity (12)
│     │   └─ ! Too long (226 lines)
│     │   └─ ! Deep nesting (depth 6)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! Excessive nesting depth (> 4)
│     │   └─ ! High cognitive load (> 7 items)
│     ├─ enhanced_analyzer.py
│     │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> EnhancedCodeAnalyzer
│     │   └─ <span class="docstring">Enhanced analyzer for code quality and maintainability metrics.</span>
│     │    This analyzer implements industry-standard code quality checks and metrics
│     │    following Clean Code principles, SOLID principles, and PEP 8 standards.
│     │   └─ ! High complexity (123)
│     │   └─ ! Too long (606 lines)
│     │   └─ ! Class too long
│     │   └─ ! Too many methods
│     │   └─ ! High class complexity
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __init__
│     │   └─ <span class="docstring">Initialize the code analyzer.</span>
│     │    Args:
│     │    show_params: Whether to show function parameters in analysis
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> analyze_file
│     │   └─ <span class="docstring">Analyze a Python file for code quality metrics.</span>
│     │    Args:
│     │    file_path: Path to the Python file to analyze
│     │    Returns:
│     │    List of analysis results for each code element
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_maintainability_index
│     │   └─ <span class="docstring">Calculate Maintainability Index (MI) following Microsoft's formula.</span>
│     │    MI = max(0, (171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
│     │    where:
│     │    - HV = Halstead Volume
│     │    - CC = Cyclomatic Complexity
│     │    - LOC = Lines of Code
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_cognitive_load
│     │   └─ <span class="docstring">Counts control structures and parameters as cognitive items.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _check_function_metrics
│     │   └─ <span class="docstring">Check function metrics against quality thresholds.</span>
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_cyclomatic_complexity
│     │   └─ <span class="docstring">Calculate McCabe's cyclomatic complexity.</span>
│     │    Based on McCabe, 1976 and implementation in Radon/SonarQube.
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_cognitive_complexity
│     │   └─ <span class="docstring">Calculate cognitive complexity based on SonarQube's metric.</span>
│     │    Implements SonarSource's cognitive complexity calculation.
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_file_metrics
│     │   └─ <span class="docstring">Analyze file-level metrics including style, duplication, imports, and documentation.</span>
│     │    Args:
│     │    content: File content as string
│     │    file_path: Path to the file being analyzed
│     │   └─ ! High complexity (13)
│     │   └─ ! Too long (66 lines)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _read_file
│     │   └─ <span class="docstring">Read and return file content safely.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _parse_content
│     │   └─ <span class="docstring">Parse Python content into AST safely.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_code_elements
│     │   └─ <span class="docstring">Analyze individual code elements in the AST.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_class
│     │   └─ <span class="docstring">Analyze a class's quality metrics.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _check_class_metrics
│     │   └─ <span class="docstring">Check class metrics against quality thresholds.</span>
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> format_structure
│     │   └─ <span class="docstring">Format the analysis results into a tree structure.</span>
│     │   └─ ! High complexity (15)
│     │   └─ ! Too long (56 lines)
│     │   └─ ! Function exceeds 50 lines
│     │   └─ ! High cyclomatic complexity(> 10)
│     │   └─ ! High cognitive complexity (> 15)
│     │   └─ ! High cognitive load (> 7 items)
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_metrics_section
│     │   └─ <span class="docstring">Format the metrics section of the report.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_function
│     │   └─ <span class="docstring">Analyze a function's quality metrics.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_class_metrics
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_function_metrics
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_complexity
│     │   └─ <span class="docstring">Calculate cyclomatic complexity of code.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_nested_depth
│     │   └─ <span class="docstring">Calculate maximum nesting depth in code.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_code_duplication
│     │   └─ <span class="docstring">Analyze code for duplication using line-based comparison.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_imports
│     │   └─ <span class="docstring">Analyze import statements and module dependencies.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_inheritance
│     │   └─ <span class="docstring">Analyze class inheritance depth and hierarchy.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _add_issue
│     │   └─ <span class="docstring">Add a quality issue to the collection.</span>
│     │    Args:
│     │    category: The category of the issue
│     │    description: Description of the issue
│     │    file_path: Optional path to the file where the issue was found
│     │    line: Optional line number where the issue was found
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_report
│     │   └─ <span class="docstring">Generate a formatted quality report.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_report_sections
│     │   └─ <span class="docstring">Format and combine report sections.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_overview_section
│     │   └─ <span class="docstring">Format the report overview section.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_issues_section
│     │   └─ <span class="docstring">Format the quality issues section.</span>
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> walk_cognitive
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> get_depth
│     │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> get_inheritance_depth
│     └─ type_checker.py
│         <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TypeValidator
│         └─ ! High complexity (22)
│         └─ ! Too long (62 lines)
│         └─ ! Missing class docstring
│         <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TypeChecked
│         └─ <span class="docstring">Base class for type-checked dataclasses</span>
│         └─ ! Too few public method (< 1, SOLID-ISP)
│         <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ValidationError
│         └─ <span class="docstring">Raised when type validation fails</span>
│         └─ ! Too few public method (< 1, SOLID-ISP)
│         <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> validate
│         └─ <span class="docstring">Validates that a value matches the expected type, with support for generics.</span>
│          Args:
│          value: The value to validate
│          expected_type: The expected type (can be a generic type)
│          Raises:
│          TypeError: If the value doesn't match the expected type
│         └─ ! High complexity (22)
│         └─ ! Too long (60 lines)
│         └─ ! Deep nesting (depth 6)
│         └─ ! Function exceeds 50 lines
│         └─ ! High cyclomatic complexity(> 10)
│         └─ ! High cognitive complexity (> 15)
│         └─ ! Excessive nesting depth (> 4)
│         └─ ! High cognitive load (> 7 items)
│         <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __post_init__
│         └─ <span class="docstring">Validate types after initialization</span>
├─ dist
│ ├─ treeline-0.1.2-py3-none-any.whl
│ └─ treeline-0.1.2.tar.gz
├─ docs
│ ├─ _static
│ ├─ code_analysis.rst
│ ├─ conf.py
│ ├─ index.rst
│ ├─ installation.rst
│ ├─ make.bat
│ ├─ Makefile
│ ├─ quickstart.rst
│ ├─ requirements.txt
│ ├─ user_guide.rst
│ └─ visualization.rst
├─ example
│ ├─ sample.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> Calculator
│ │   └─ <span class="docstring">A simple calculator class.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> main
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __init__
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> add
│ │   └─ <span class="docstring">Add two numbers.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> multiply
│ │   └─ <span class="docstring">Multiply two numbers.</span>
│ ├─ tree.md
│ └─ tut1.ipynb
├─ results
│ ├─ code_analysis.html
│ ├─ code_analysis.md
│ └─ code_visualization.html
├─ tests
│ ├─ test_core.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TestTreeGenerator
│ │   └─ ! Missing class docstring
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> setUp
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> tearDown
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> test_tree_structure
│ │   └─ <span class="docstring">Test if the tree structure is generated correctly</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> test_markdown_creation
│ │   └─ <span class="docstring">Test if markdown file is created when flag is True</span>
│ ├─ test_empty_dir.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TestEmptyDirectory
│ │   └─ ! Missing class docstring
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> setUp
│ │   └─ <span class="docstring">Set up test directory</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> tearDown
│ │   └─ <span class="docstring">Clean up test directory</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> test_empty_directory
│ │   └─ <span class="docstring">Test handling of empty directory</span>
│ ├─ test_nested_dir.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TestNestedDirectories
│ │   └─ ! Missing class docstring
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> setUp
│ │   └─ <span class="docstring">Set up test directory</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> tearDown
│ │   └─ <span class="docstring">Clean up test directory</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> test_nested_directories
│ │   └─ <span class="docstring">Test handling of nested directories</span>
│ ├─ test_special_char.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TestSpecialCharacters
│ │   └─ ! Missing class docstring
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> setUp
│ │   └─ <span class="docstring">Set up test directory</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> tearDown
│ │   └─ <span class="docstring">Clean up test directory</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> test_special_characters
│ │   └─ <span class="docstring">Test handling of special characters in names</span>
│ └─ test_treeline.py
│     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TestTreeLine
│     └─ ! Missing class docstring
│     <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> setUp
│     <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> tearDown
│     <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> test_basic_tree
│     └─ <span class="docstring">Test if tree structure is generated correctly</span>
├─ treeline
│ ├─ models
│ │ ├─ __init__.py
│ │ ├─ analyzer.py
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionCall
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeStructure
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionNode
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassNode
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> AnalyzerConfig
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ ├─ core.py
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeStructure
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TreeOptions
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ModuleMetrics
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ ├─ dependency_analyzer.py
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionLocation
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionCallInfo
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassMethod
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassInfo
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ModuleMetrics
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ComplexFunction
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> MethodInfo
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> Node
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> Link
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> GraphData
│ │ │   └─ ! Missing class docstring
│ │ │   └─ ! Too few public method (< 1, SOLID-ISP)
│ │ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __post_init__
│ │ └─ enhanced_analyzer.py
│ │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> FunctionMetrics
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ClassMetrics
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeDuplication
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ │     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> QualityIssue
│ │     └─ ! Missing class docstring
│ │     └─ ! Too few public method (< 1, SOLID-ISP)
│ ├─ __init__.py
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __call__
│ ├─ __main__.py
│ ├─ analyzer.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> CodeAnalyzer
│ │   └─ <span class="docstring">Simple analyzer for extracting functions and classes from Python files.</span>
│ │   └─ ! High complexity (34)
│ │   └─ ! Too long (207 lines)
│ │   └─ ! Class too long
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __init__
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> analyze_file
│ │   └─ <span class="docstring">Extracts functions and classes with optional params and relationships.</span>
│ │   └─ ! High complexity (12)
│ │   └─ ! Too long (99 lines)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _get_function_params
│ │   └─ <span class="docstring">Extract function parameters with type hints.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _find_function_calls
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> get_symbol
│ │   └─ <span class="docstring">Maps item types to their display symbols.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> format_structure
│ │   └─ <span class="docstring">Formats the code structure into displayable lines with colors and prefixes.</span>
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ core.py
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> create_default_ignore
│ │   └─ <span class="docstring">Create default .treeline-ignore if it doesn't exist.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> format_structure
│ │   └─ <span class="docstring">Format the analysis results into a readable tree structure.</span>
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
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_tree
│ │   └─ <span class="docstring">Generate tree structure with code quality and security analysis.</span>
│ │   └─ ! High complexity (14)
│ │   └─ ! Too long (76 lines)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> main
│ │   └─ ! Too long (51 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> add_directory
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ ├─ default_ignore
│ ├─ dependency_analyzer.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ModuleDependencyAnalyzer
│ │   └─ <span class="docstring">Analyzes module-level dependencies and generates summary reports.</span>
│ │   └─ ! High complexity (96)
│ │   └─ ! Too long (1264 lines)
│ │   └─ ! Class too long
│ │   └─ ! Too many methods
│ │   └─ ! High class complexity
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __init__
│ │   └─ ! Too long (487 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> analyze_directory
│ │   └─ <span class="docstring">Analyze all Python files in directory.</span>
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_module
│ │   └─ <span class="docstring">Analyze a single module's contents and relationships.</span>
│ │   └─ ! High complexity (15)
│ │   └─ ! Too long (52 lines)
│ │   └─ ! Deep nesting (depth 7)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_imports
│ │   └─ <span class="docstring">Collect import information from AST.</span>
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _collect_metrics
│ │   └─ <span class="docstring">Collect code metrics for the module.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_complexity
│ │   └─ <span class="docstring">Calculate cyclomatic complexity.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_module_overview_diagram
│ │   └─ <span class="docstring">Generate a Mermaid diagram showing modules and their relationships.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_module_detail_diagram
│ │   └─ <span class="docstring">Generate a Mermaid diagram showing functions and classes in a module.</span>
│ │   └─ ! High complexity (17)
│ │   └─ ! Too long (59 lines)
│ │   └─ ! Deep nesting (depth 5)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! Excessive nesting depth (> 4)
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_mermaid_graphs
│ │   └─ <span class="docstring">Generate a markdown report with multiple focused Mermaid graphs.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_html_visualization
│ │   └─ <span class="docstring">Generate an interactive HTML visualization using D3.js</span>
│ │   └─ ! High complexity (18)
│ │   └─ ! Too long (177 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> clean_for_markdown
│ │   └─ <span class="docstring">Remove ANSI colors and simplify symbols for markdown.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_reports
│ │   └─ <span class="docstring">Generate comprehensive HTML and markdown reports of the code analysis.</span>
│ │   └─ ! Too long (243 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> should_skip_module
│ │   └─ <span class="docstring">Check if a module path should be skipped.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> save_mermaid
│ ├─ enhanced_analyzer.py
│ │   <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> EnhancedCodeAnalyzer
│ │   └─ <span class="docstring">Enhanced analyzer for code quality and maintainability metrics.</span>
│ │    This analyzer implements industry-standard code quality checks and metrics
│ │    following Clean Code principles, SOLID principles, and PEP 8 standards.
│ │   └─ ! High complexity (123)
│ │   └─ ! Too long (606 lines)
│ │   └─ ! Class too long
│ │   └─ ! Too many methods
│ │   └─ ! High class complexity
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __init__
│ │   └─ <span class="docstring">Initialize the code analyzer.</span>
│ │    Args:
│ │    show_params: Whether to show function parameters in analysis
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> analyze_file
│ │   └─ <span class="docstring">Analyze a Python file for code quality metrics.</span>
│ │    Args:
│ │    file_path: Path to the Python file to analyze
│ │    Returns:
│ │    List of analysis results for each code element
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_maintainability_index
│ │   └─ <span class="docstring">Calculate Maintainability Index (MI) following Microsoft's formula.</span>
│ │    MI = max(0, (171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
│ │    where:
│ │    - HV = Halstead Volume
│ │    - CC = Cyclomatic Complexity
│ │    - LOC = Lines of Code
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_cognitive_load
│ │   └─ <span class="docstring">Counts control structures and parameters as cognitive items.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _check_function_metrics
│ │   └─ <span class="docstring">Check function metrics against quality thresholds.</span>
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_cyclomatic_complexity
│ │   └─ <span class="docstring">Calculate McCabe's cyclomatic complexity.</span>
│ │    Based on McCabe, 1976 and implementation in Radon/SonarQube.
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_cognitive_complexity
│ │   └─ <span class="docstring">Calculate cognitive complexity based on SonarQube's metric.</span>
│ │    Implements SonarSource's cognitive complexity calculation.
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_file_metrics
│ │   └─ <span class="docstring">Analyze file-level metrics including style, duplication, imports, and documentation.</span>
│ │    Args:
│ │    content: File content as string
│ │    file_path: Path to the file being analyzed
│ │   └─ ! High complexity (13)
│ │   └─ ! Too long (66 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _read_file
│ │   └─ <span class="docstring">Read and return file content safely.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _parse_content
│ │   └─ <span class="docstring">Parse Python content into AST safely.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_code_elements
│ │   └─ <span class="docstring">Analyze individual code elements in the AST.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_class
│ │   └─ <span class="docstring">Analyze a class's quality metrics.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _check_class_metrics
│ │   └─ <span class="docstring">Check class metrics against quality thresholds.</span>
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> format_structure
│ │   └─ <span class="docstring">Format the analysis results into a tree structure.</span>
│ │   └─ ! High complexity (15)
│ │   └─ ! Too long (56 lines)
│ │   └─ ! Function exceeds 50 lines
│ │   └─ ! High cyclomatic complexity(> 10)
│ │   └─ ! High cognitive complexity (> 15)
│ │   └─ ! High cognitive load (> 7 items)
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_metrics_section
│ │   └─ <span class="docstring">Format the metrics section of the report.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_function
│ │   └─ <span class="docstring">Analyze a function's quality metrics.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_class_metrics
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_function_metrics
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_complexity
│ │   └─ <span class="docstring">Calculate cyclomatic complexity of code.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _calculate_nested_depth
│ │   └─ <span class="docstring">Calculate maximum nesting depth in code.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_code_duplication
│ │   └─ <span class="docstring">Analyze code for duplication using line-based comparison.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_imports
│ │   └─ <span class="docstring">Analyze import statements and module dependencies.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _analyze_inheritance
│ │   └─ <span class="docstring">Analyze class inheritance depth and hierarchy.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _add_issue
│ │   └─ <span class="docstring">Add a quality issue to the collection.</span>
│ │    Args:
│ │    category: The category of the issue
│ │    description: Description of the issue
│ │    file_path: Optional path to the file where the issue was found
│ │    line: Optional line number where the issue was found
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> generate_report
│ │   └─ <span class="docstring">Generate a formatted quality report.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_report_sections
│ │   └─ <span class="docstring">Format and combine report sections.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_overview_section
│ │   └─ <span class="docstring">Format the report overview section.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> _format_issues_section
│ │   └─ <span class="docstring">Format the quality issues section.</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> walk_cognitive
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> get_depth
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> get_inheritance_depth
│ ├─ ignore.py
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> read_ignore_patterns
│ │   └─ <span class="docstring">Read patterns from .treeline-ignore file</span>
│ │   <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> should_ignore
│ │   └─ <span class="docstring">Check if path should be ignored based on patterns.</span>
│ │   └─ ! High complexity (13)
│ │   └─ ! High cyclomatic complexity(> 10)
│ └─ type_checker.py
│     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TypeValidator
│     └─ ! High complexity (22)
│     └─ ! Too long (62 lines)
│     └─ ! Missing class docstring
│     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> TypeChecked
│     └─ <span class="docstring">Base class for type-checked dataclasses</span>
│     └─ ! Too few public method (< 1, SOLID-ISP)
│     <span class='class-label'>Class:</span> <i class="fas fa-cube icon-class"></i> ValidationError
│     └─ <span class="docstring">Raised when type validation fails</span>
│     └─ ! Too few public method (< 1, SOLID-ISP)
│     <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> validate
│     └─ <span class="docstring">Validates that a value matches the expected type, with support for generics.</span>
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
│     <span class='function-label'>Function:</span> <i class="fas fa-bolt icon-function"></i> __post_init__
│     └─ <span class="docstring">Validate types after initialization</span>
├─ treeline.egg-info
│ ├─ dependency_links.txt
│ ├─ entry_points.txt
│ ├─ PKG-INFO
│ ├─ requires.txt
│ ├─ SOURCES.txt
│ └─ top_level.txt
├─ .dockerignore
├─ .editorconfig
├─ .pre-commit-config.yaml
├─ .readthedocs.yaml
├─ .treeline-ignore
├─ deploy_to_pypi.sh
├─ docker-compose.yaml
├─ dockerfile
├─ License
├─ pyproject.toml
├─ README.md
├─ setup.py
└─ tox.ini
```


## Complexity Hotspots

### validate
- **Module**: treeline.type_checker
- **Complexity**: <span style='color: red'>22</span>

### validate
- **Module**: build.lib.treeline.type_checker
- **Complexity**: <span style='color: red'>22</span>

### generate_html_visualization
- **Module**: treeline.dependency_analyzer
- **Complexity**: <span style='color: red'>18</span>

### generate_html_visualization
- **Module**: build.lib.treeline.dependency_analyzer
- **Complexity**: <span style='color: red'>18</span>

### generate_module_detail_diagram
- **Module**: treeline.dependency_analyzer
- **Complexity**: <span style='color: red'>17</span>

### generate_module_detail_diagram
- **Module**: build.lib.treeline.dependency_analyzer
- **Complexity**: <span style='color: red'>17</span>

### _analyze_module
- **Module**: treeline.dependency_analyzer
- **Complexity**: <span style='color: red'>15</span>

### format_structure
- **Module**: treeline.enhanced_analyzer
- **Complexity**: <span style='color: red'>15</span>

### _analyze_module
- **Module**: build.lib.treeline.dependency_analyzer
- **Complexity**: <span style='color: red'>15</span>

### format_structure
- **Module**: build.lib.treeline.enhanced_analyzer
- **Complexity**: <span style='color: red'>15</span>

### generate_tree
- **Module**: treeline.core
- **Complexity**: <span style='color: red'>14</span>

### generate_tree
- **Module**: build.lib.treeline.core
- **Complexity**: <span style='color: red'>14</span>

### _analyze_file_metrics
- **Module**: treeline.enhanced_analyzer
- **Complexity**: <span style='color: red'>13</span>

### format_structure
- **Module**: treeline.core
- **Complexity**: <span style='color: red'>13</span>

### should_ignore
- **Module**: treeline.ignore
- **Complexity**: <span style='color: red'>13</span>

### _analyze_file_metrics
- **Module**: build.lib.treeline.enhanced_analyzer
- **Complexity**: <span style='color: red'>13</span>

### format_structure
- **Module**: build.lib.treeline.core
- **Complexity**: <span style='color: red'>13</span>

### analyze_file
- **Module**: treeline.analyzer
- **Complexity**: <span style='color: red'>12</span>

### generate_reports
- **Module**: build.lib.treeline.dependency_analyzer
- **Complexity**: <span style='color: red'>12</span>

### analyze_file
- **Module**: build.lib.treeline.analyzer
- **Complexity**: <span style='color: red'>12</span>

### should_ignore
- **Module**: build.lib.treeline.core
- **Complexity**: <span style='color: red'>11</span>
