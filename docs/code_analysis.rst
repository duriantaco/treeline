.. _code-analysis:

Code Analysis Guide
====================

This guide explains how to use Treeline's code analysis features to understand your Python codebase's structure and relationships.

.. _code-analysis-basics:

Basic Analysis
---------------

The core of Treeline's analysis starts with the ``generate_tree`` function:

.. code-block:: python

    from treeline.core import generate_tree

    analysis = generate_tree(
        directory="your_project",
        show_params=True,
        show_relationships=True
    )

.. _code-analysis-understanding-output:

Understanding Output
---------------------

Treeline's output uses specific symbols to represent different code elements:

* ⚡ - Functions
* 🏛️ - Classes
* ⚠️ - Errors or warnings

Example output::

    your_project/
    ├── module.py
    │   ├── [CLASS] 🏛️ MyClass
    │   │   └─ # Class documentation
    │   │   └─ ⚡ method1(self, param: str) -> int
    │   ├── [FUNC] ⚡ helper_function(x: int, y: int) -> int
    │   │   └─ # Calculates something
    │   └── ⚠️ High complexity (15)

.. _code-analysis-detailed-features:

Detailed Analysis Features
---------------------------

.. _code-analysis-function-analysis:

Function Analysis
~~~~~~~~~~~~~~~~~~

Treeline analyzes functions for:

* Parameter types and return types
* Documentation coverage
* Complexity metrics
* Function relationships

.. code-block:: python

    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

    analyzer = EnhancedCodeAnalyzer()
    results = analyzer.analyze_file("path/to/file.py")

    # Access function metrics
    for item in results:
        if item["type"] == "function":
            print(f"Function: {item['name']}")
            print(f"Metrics: {item['metrics']}")

.. _code-analysis-class-analysis:

Class Analysis
~~~~~~~~~~~~~~~

Class analysis includes:

* Method count and complexity
* Inheritance relationships
* Documentation quality
* Class metrics

Example of class analysis:

.. code-block:: python

    # Results include class-specific metrics
    for item in results:
        if item["type"] == "class":
            print(f"Class: {item['name']}")
            print(f"Methods: {item['metrics']['method_count']}")
            print(f"Complexity: {item['metrics']['complexity']}")

.. _code-analysis-relationship-analysis:

Relationship Analysis
~~~~~~~~~~~~~~~~~~~~~~

Track how code elements interact:

* Function calls
* Class inheritance
* Module dependencies
* Import relationships

.. code-block:: python

    from treeline.dependency_analyzer import ModuleDependencyAnalyzer

    dep_analyzer = ModuleDependencyAnalyzer()
    dep_analyzer.analyze_directory("your_project")

    # Access relationship data
    function_calls = dep_analyzer.function_calls
    class_relationships = dep_analyzer.class_info

.. _code-analysis-configuration:

Configuration Options
----------------------

Key analysis options:

.. code-block:: python

    generate_tree(
        directory=".",              # Project root
        create_md=False,           # Create markdown report
        hide_structure=False,      # Show code structure
        show_params=True,         # Show parameters
        show_relationships=True   # Show relationships
    )

.. _code-analysis-ignoring-files:

Ignoring Files
---------------

Use ``.treeline-ignore`` to exclude files:

.. code-block:: text

    *.pyc
    __pycache__
    .git
    .env
    venv/
    .DS_Store
    node_modules/

.. _code-analysis-results:

Analysis Results
-----------------

.. _code-analysis-working-with-results:

Working with Analysis Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Results are returned as structured data:

.. code-block:: python

    {
        "type": "function",
        "name": "example_function",
        "docstring": "Function documentation",
        "metrics": {
            "lines": 10,
            "complexity": 5,
            "params": 2,
            "returns": 1,
            "nested_depth": 2,
            "cognitive_complexity": 3
        },
        "code_smells": []
    }

.. _code-analysis-large-codebases:

Handling Large Codebases
~~~~~~~~~~~~~~~~~~~~~~~~~

For large projects:

1. Use selective analysis:

   .. code-block:: python

       # Analyze specific directories
       generate_tree("src/core")
       generate_tree("src/utils")

2. Disable detailed features:

   .. code-block:: python

       generate_tree(
           directory="large_project",
           show_params=False,
           show_relationships=False
       )

3. Use ignore patterns effectively

.. _code-analysis-best-practices:

Best Practices
---------------

1. Regular Analysis
   - Run analysis regularly during development
   - Track metrics over time
   - Set up automated analysis in CI/CD

2. Progressive Resolution
   - Address high-complexity functions first
   - Focus on heavily-used modules
   - Prioritize public APIs

3. Documentation Integration
   - Use analysis results in documentation
   - Track documentation coverage
   - Update docs based on relationships

.. _code-analysis-common-issues:

Common Issues
--------------

1. Performance
   - Limit analysis scope for large projects
   - Use appropriate ignore patterns
   - Disable unnecessary features

2. False Positives
   - Customize complexity thresholds
   - Update ignore patterns
   - Document known exceptions

3. Integration
   - Use with linters and formatters
   - Integrate with IDE tools
   - Automate in build process

.. _code-analysis-next-steps:

Next Steps
-----------

- Learn about :ref:`quality_metrics <user_guide:quality-metrics>`
- Explore :ref:`visualization <visualization:visualization>`
- Configure :ref:`custom rules <user_guide:configuration>`
