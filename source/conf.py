import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Project information
project = "Treeline"
copyright = "2024, oha"
author = "oha"
release = "1.0.0"

# General config
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True

autodoc_member_order = "bysource"
autodoc_typehints = "description"
add_module_names = False

nitpicky = True
