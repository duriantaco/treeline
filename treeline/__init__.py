import sys

from .core import generate_tree


def __call__(*args, **kwargs):
    return generate_tree(*args, **kwargs)


sys.modules[__name__] = type(
    "TreeLine",
    (),
    {"__call__": staticmethod(__call__)},
)()

__all__ = ["generate_tree"]
