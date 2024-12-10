import os
import sys

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath(".."))

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
    "sphinx_rtd_theme",
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}

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

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2
