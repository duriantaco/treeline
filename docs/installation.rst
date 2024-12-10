.. _installation:

Installation Guide
===================

.. _installation-basic:

Basic Installation
-------------------

You can install Treeline using pip:

.. code-block:: bash

    pip install treeline

.. _installation-dependencies:

Dependencies
-------------

Treeline requires Python 3.7 or later and depends on the following packages:

.. _installation-dependencies-core:

Core Dependencies
~~~~~~~~~~~~~~~~~~
- ``ast`` (built-in)
- ``pathlib`` (built-in)
- ``typing`` (built-in)

.. _installation-dependencies-viz:

Visualization Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~
These are used for the interactive visualizations and graphs:

- ``d3.js`` (automatically included)
- ``mermaid`` (for diagram generation)

.. _installation-dependencies-optional:

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~
For enhanced functionality:

.. code-block:: bash

    # For development and testing
    pip install treeline[dev]

    # For documentation generation
    pip install treeline[docs]

.. _installation-development:

Development Installation
-------------------------

For development purposes, you can install from source:

.. code-block:: bash

    git clone https://github.com/yourusername/treeline.git
    cd treeline
    pip install -e .

.. _installation-post-setup:

Post-Installation Setup
------------------------

After installation, Treeline will create a default configuration file when first run:

1. Run Treeline in your project directory:

   .. code-block:: bash

       treeline

2. This will create a ``.treeline-ignore`` file with default ignore patterns. Do also note that the ignore file is created in the current working directory.

3. You can customize the ignore patterns by editing this file:

   .. code-block:: text

       *.pyc
       __pycache__
       .git
       .env
       venv/
       .DS_Store
       node_modules/

.. _installation-troubleshooting:

Troubleshooting
----------------

.. _installation-common-issues:

Common Issues
~~~~~~~~~~~~~~

1. **Import Errors**

   If you see import errors, ensure all dependencies are installed:

   .. code-block:: bash

       pip install --upgrade treeline

2. **Git Integration Issues**

   For Git-related features, ensure Git is installed and accessible from command line:

   .. code-block:: bash

       git --version

3. **Visualization Problems**

   If visualizations don't render:

   - Ensure you're using a modern web browser
   - Check browser console for JavaScript errors
   - Verify file permissions for output directories

.. _installation-help:

Getting Help
-------------

If you encounter any issues:

1. Check the :ref:`troubleshooting guide <troubleshooting>`
2. Search existing GitHub issues
3. Create a new issue with:
   - Your Python version
   - Installation method used
   - Complete error message
   - Minimal reproducible example
