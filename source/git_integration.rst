Git Integration Guide
==================

Treeline provides Git integration features that help you visualize structural changes between different versions of your code.

Basic Usage
---------

Compare code structure between commits:

.. code-block:: python

    from treeline.diff_visualizer import DiffVisualizer

    # Initialize visualizer
    visualizer = DiffVisualizer()

    # Compare with previous commit
    html = visualizer.generate_structural_diff("HEAD^", "HEAD")

    # Save visualization
    with open("code_diff.html", "w") as f:
        f.write(html)

Visualization Features
-------------------

The structural diff visualization shows how your code structure has changed between commits.

Node Status
~~~~~~~~~
Nodes are color-coded to show their status:

- Green: Added nodes
- Red: Removed nodes
- White: Unchanged nodes

Link Status
~~~~~~~~~
Relationships between nodes are also color-coded:

- Green: New relationships
- Red: Removed relationships
- Default color: Unchanged relationships

Interactive Features
-----------------

1. Node Selection
   - Click on nodes to see details
   - Highlighted selection state
   - Connected nodes emphasis

2. Diff Popup
   - Shows detailed node information
   - Displays Git diff for related files
   - Color-coded diff display:
     - Green: Added lines
     - Red: Removed lines
     - Gray: Context lines

3. Controls
   - Zoom and pan functionality
   - Reset view button
   - Layout toggle
   - Search functionality

Common Usage Patterns
------------------

Compare Recent Changes
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Compare with previous commit
    diff = visualizer.generate_structural_diff("HEAD^", "HEAD")

Compare Specific Commits
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Compare any two commits
    diff = visualizer.generate_structural_diff(
        "abc123",  # older commit
        "def456"   # newer commit
    )

Technical Details
--------------

Repository Detection
~~~~~~~~~~~~~~~~~
The visualizer automatically detects if you're in a Git repository:

.. code-block:: python

    # Custom repository path
    visualizer = DiffVisualizer(repo_path="path/to/repo")

    # Automatic detection for current directory
    visualizer = DiffVisualizer()

Analysis Process
~~~~~~~~~~~~~
For each commit, the visualizer:

1. Creates a temporary worktree
2. Analyzes the code structure
3. Computes structural differences
4. Generates an interactive visualization

Error Handling
-----------

The visualizer includes robust error handling for common Git scenarios:

1. Invalid Repository
   - Checks if directory is a Git repository
   - Provides clear error message if not

2. Missing Commits
   - Validates commit existence
   - Handles invalid commit references

3. Git Command Failures
   - Timeout handling
   - Command execution errors
   - Debug output for troubleshooting

Best Practices
-----------

1. Commit Selection
   - Use meaningful commits for comparison
   - Avoid comparing very distant commits
   - Consider commit size for performance

2. Repository Management
   - Ensure clean repository state
   - Use appropriate ignore patterns
   - Keep repository size manageable

3. Performance
   - Limit comparison scope when needed
   - Use specific commits rather than branches
   - Consider file system performance

Troubleshooting
------------

Common Issues
~~~~~~~~~~

1. "Not a git repository" error
   - Ensure you're in a Git repository
   - Check repository initialization
   - Verify repository path

2. Commit not found
   - Verify commit exists
   - Ensure repository is up to date
   - Check commit hash accuracy

3. Performance issues
   - Reduce comparison scope
   - Check repository size
   - Verify system resources

Debug Output
~~~~~~~~~~

The visualizer includes debug logging:

.. code-block:: python

    # Debug output will show:
    # - Git commands being run
    # - Command outputs
    # - Error messages
    # - Diff computation progress

Customization
-----------

The Git diff visualization can be customized through CSS:

.. code-block:: css

    /* Example customizations */
    .node-added circle { fill: #22c55e; }      /* Added nodes */
    .node-removed circle { fill: #ef4444; }     /* Removed nodes */
    .link-added { stroke: #22c55e; }           /* Added links */
    .link-removed { stroke: #ef4444; }         /* Removed links */

Limitations
---------

Current limitations include:

1. Only supports Python files
2. Requires Git repository
3. Temporary directory usage for analysis
4. Memory usage with large repositories

Future Enhancements
----------------

Planned features:

1. Branch comparison
2. Multi-language support
3. Performance optimizations
4. Additional visualization options

Reference
--------

Related Documentation:
- :ref:`visualization`
- :ref:`configuration`
- :ref:`best_practices`
