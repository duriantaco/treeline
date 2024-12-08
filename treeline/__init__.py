import sys

from .core import generate_tree
from .diff_visualizer import DiffVisualizer


def __call__(*args, **kwargs):
    return generate_tree(*args, **kwargs)


sys.modules[__name__] = type(
    "TreeLine",
    (),
    {"__call__": staticmethod(__call__), "DiffVisualizer": DiffVisualizer},
)()

__all__ = ["generate_tree", "DiffVisualizer"]
