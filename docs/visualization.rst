.. _visualization-guide:

Visualization Guide
====================

Treeline provides powerful visualization tools to help you understand your codebase structure and track changes over time.

.. _visualization-dependency-graphs:

Interactive Dependency Graphs
------------------------------

.. _visualization-basic:

Basic Visualization
~~~~~~~~~~~~~~~~~~~~

Generate an interactive visualization of your code structure:

.. code-block:: python

    from treeline.dependency_analyzer import ModuleDependencyAnalyzer

    analyzer = ModuleDependencyAnalyzer()
    analyzer.analyze_directory("your_project")

    with open("visualization.html", "w") as f:
        f.write(analyzer.generate_html_visualization())

.. _visualization-features:

Visualization Features
~~~~~~~~~~~~~~~~~~~~~~~

The interactive visualization includes:

1. Node Types
   - Modules (blue circles)
   - Classes (cyan circles)
   - Functions (green circles)

2. Relationship Types
   - Imports (purple lines)
   - Contains (green lines)
   - Calls (orange lines)

3. Interactive Controls
   - Zoom and pan
   - Node dragging
   - Search functionality
   - Layout toggling

.. _visualization-git-integration:

Git Integration and Diff Visualization
---------------------------------------

The Git diff visualization shows structural changes between commits:

.. code-block:: python

    from treeline.diff_visualizer import DiffVisualizer

    visualizer = DiffVisualizer()

    # Compare with previous commit
    diff_html = visualizer.generate_structural_diff("HEAD^", "HEAD")

    # Compare specific commits
    diff_html = visualizer.generate_structural_diff(
        "abc123",  # older commit
        "def456"   # newer commit
    )

.. _visualization-diff-features:

Diff Visualization Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Color Coding
   - Added elements (green)
   - Removed elements (red)
   - Modified elements (yellow)
   - Unchanged elements (white)

2. Interactive Elements
   - Click nodes to show details
   - View file-level diffs
   - Highlight connected nodes
   - Search and filter changes

3. Change Indicators
   - Modified relationships
   - Structural changes
   - File content diffs

.. _visualization-working:

Working with Visualizations
----------------------------

.. _visualization-customizing:

Customizing the Display
~~~~~~~~~~~~~~~~~~~~~~~~

Control visualization parameters:

.. code-block:: python

    # Node size based on metrics
    node_size = len(node.methods) if hasattr(node, 'methods') else 1

    # Custom node colors
    node_color = {
        'module': '#0284c7',
        'class': '#0891b2',
        'function': '#0d9488'
    }

.. _visualization-filtering:

Filtering and Search
~~~~~~~~~~~~~~~~~~~~~

Use the built-in search functionality:

1. Module-level filtering:
   - Search by module name
   - Filter by node type
   - Show/hide relationships

2. Dependency filtering:
   - Show only imports
   - Show only function calls
   - Show only inheritance

.. _visualization-layout:

Layout Options
~~~~~~~~~~~~~~~

Toggle between different layout algorithms:

1. Force-directed layout:
   - Natural clustering
   - Interactive node positioning
   - Automatic spacing

2. Radial layout:
   - Hierarchical view
   - Circular arrangement
   - Central focus

.. _visualization-git-features:

Git Integration Features
-------------------------

.. _visualization-commit-comparison:

Commit Comparison
~~~~~~~~~~~~~~~~~~

Compare code structure between commits:

.. code-block:: python

    visualizer = DiffVisualizer()

    # Compare with previous commit
    diff_html = visualizer.generate_structural_diff(
        "HEAD^",  # Previous commit
        "HEAD"    # Current commit
    )

    # Compare specific commits
    diff_html = visualizer.generate_structural_diff(
        "main",      # Main branch
        "feature"    # Feature branch
    )

.. _visualization-interactive-diff:

Interactive Diff Features
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Node Details
   - Click nodes to show details
   - View file-level changes
   - See relationship changes

2. File Diffs
   - Syntax-highlighted diffs
   - Line-by-line changes
   - Context information

3. Change Navigation
   - Jump to changes
   - Filter by change type
   - Search within diffs

.. _visualization-export:

Exporting and Sharing
----------------------

.. _visualization-export-options:

Export Options
~~~~~~~~~~~~~~~

1. HTML Export:
   - Self-contained HTML file
   - Includes all necessary styles
   - Interactive features preserved

2. Image Export:
   - Screenshot functionality
   - SVG export
   - High-resolution output

.. _visualization-embedding:

Embedding in Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Include visualizations in documentation:

.. code-block:: html

    <!-- Include in HTML documentation -->
    <iframe src="visualization.html"
            width="100%"
            height="600px"
            frameborder="0">
    </iframe>

.. _visualization-best-practices:

Best Practices
---------------

1. Performance
   - Limit scope for large codebases
   - Use appropriate filtering
   - Consider splitting visualizations

2. Readability
   - Group related nodes
   - Use consistent layouts
   - Add meaningful labels

3. Git Integration
   - Regular structural diffs
   - Track important changes
   - Document significant changes

.. _visualization-troubleshooting:

Troubleshooting
----------------

.. _visualization-common-issues:

Common Issues
~~~~~~~~~~~~~~

1. Layout Issues
   - Reset zoom if visualization is hidden
   - Adjust window size
   - Try different layouts

2. Performance Problems
   - Reduce number of visible nodes
   - Use search and filtering
   - Split into smaller visualizations

3. Git Integration Issues
   - Ensure Git repository is valid
   - Check commit references
   - Verify file paths

.. _visualization-next-steps:

Next Steps
-----------

- Explore :doc:`/git_integration` for more VCS features
