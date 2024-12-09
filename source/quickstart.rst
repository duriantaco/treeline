Quick Start Guide
==============

This guide will help you get started with Treeline's core features for analyzing and visualizing your Python codebase.

Basic Usage
---------

1. Simple Code Analysis
~~~~~~~~~~~~~~~~~~~~

Analyze a Python project's structure:

.. code-block:: python

    from treeline.core import generate_tree

    # Generate basic structure analysis
    tree = generate_tree(
        directory="your_project",
        create_md=True,
        show_params=True
    )
    print(tree)

2. Generate Quality Report
~~~~~~~~~~~~~~~~~~~~~~~

Analyze code quality and metrics:

.. code-block:: python

    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

    analyzer = EnhancedCodeAnalyzer()

    # Analyze a specific file
    results = analyzer.analyze_file("path/to/your/file.py")

    # Generate comprehensive report
    report = analyzer.generate_report()
    print(report)

3. Visualize Dependencies
~~~~~~~~~~~~~~~~~~~~~~

Create interactive dependency graphs:

.. code-block:: python

    from treeline.dependency_analyzer import ModuleDependencyAnalyzer

    # Initialize analyzer
    dep_analyzer = ModuleDependencyAnalyzer()

    # Analyze directory
    dep_analyzer.analyze_directory("your_project")

    # Generate HTML visualization
    with open("dependencies.html", "w") as f:
        f.write(dep_analyzer.generate_html_visualization())

4. Compare Code Changes
~~~~~~~~~~~~~~~~~~~

Visualize structural changes between Git commits:

.. code-block:: python

    from treeline.diff_visualizer import DiffVisualizer

    visualizer = DiffVisualizer()

    # Compare current code with previous commit
    diff_html = visualizer.generate_structural_diff("HEAD^", "HEAD")

    # Save visualization
    with open("code_diff.html", "w") as f:
        f.write(diff_html)

Command Line Interface
-------------------

Treeline can also be used from the command line:

.. code-block:: bash

    # Basic analysis
    treeline /path/to/project

    # Create markdown report
    treeline -m /path/to/project

    # Compare with previous commit
    treeline --diff

    # Hide function parameters
    treeline --no-params

    # Hide code structure
    treeline --hide-structure

Common Options
------------

.. code-block:: python

    generate_tree(
        directory=".",              # Project directory
        create_md=False,           # Create markdown report
        hide_structure=False,      # Show/hide code structure
        show_params=True,         # Show function parameters
        show_relationships=False  # Show code relationships
    )

Quality Metrics
-------------

Treeline checks for various quality metrics including:

- Cyclomatic complexity (limit: 10)
- Maximum function lines (limit: 50)
- Nested depth (limit: 4)
- Class complexity (limit: 50)
- Import statements (limit: 15)
- Inheritance depth (limit: 3)

Next Steps
---------

- Check out the :ref:`User Guide <user_guide/index>` for detailed feature explanations

Example Project Analysis
---------------------

Here's a complete example analyzing a Python project:

.. code-block:: python

    from treeline.core import generate_tree
    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
    from treeline.dependency_analyzer import ModuleDependencyAnalyzer

    # Directory to analyze
    project_dir = "your_project"

    # Basic structure analysis
    tree = generate_tree(project_dir, create_md=True)

    # Quality analysis
    analyzer = EnhancedCodeAnalyzer()
    quality_report = analyzer.generate_report()

    # Dependency analysis
    dep_analyzer = ModuleDependencyAnalyzer()
    dep_analyzer.analyze_directory(project_dir)

    # Generate visualizations
    with open("dependencies.html", "w") as f:
        f.write(dep_analyzer.generate_html_visualization())

    print("Analysis complete! Check the generated reports and visualizations.")
