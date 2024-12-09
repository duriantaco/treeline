.. _treeline-documentation:

Welcome to Treeline Documentation
==================================

Treeline is a powerful Python code analysis and visualization tool that helps developers understand and improve their codebase through:

* Code structure analysis and visualization
* Dependency tracking and graphing
* Code quality metrics and validation
* Git-based structural diff visualization

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide

.. _getting-started:

Installation
-------------

.. code-block:: bash

   pip install treeline

.. _quick-example:

Quick Example
--------------

.. code-block:: python

   from treeline.core import generate_tree

   # Generate a tree structure analysis
   tree = generate_tree(
       directory="your_project",
       create_md=True,
       show_params=True
   )

.. _feature-highlights:

Feature Highlights
-------------------

.. _feature-code-analysis:

Code Analysis
~~~~~~~~~~~~~~
- Function and class structure analysis
- Cyclomatic complexity calculation
- Code quality metrics
- Documentation coverage checking

.. _feature-visualization:

Visualization
~~~~~~~~~~~~~~
- Interactive dependency graphs
- Module relationship diagrams
- Code structure trees
- Git diff visualizations

.. _feature-quality-metrics:

Quality Metrics
~~~~~~~~~~~~~~~~
- Maintainability index
- Cognitive complexity
- Inheritance depth
- Code duplication detection

.. _indices-and-tables:

Indices and Tables
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
