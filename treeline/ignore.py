import os
from pathlib import Path
from typing import List


def read_ignore_patterns() -> List[str]:
    """Read patterns from .treeline-ignore file"""
    ignore_patterns = []
    if Path(".treeline-ignore").exists():
        with open(".treeline-ignore", "r") as f:
            ignore_patterns = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return ignore_patterns


def should_ignore(path: Path, ignore_patterns: List[str]) -> bool:
    """Check if path should be ignored based on patterns."""
    path_str = str(path.resolve())
    dot_path = str(path).replace(os.sep, ".")

    if dot_path.startswith("venv.") and (
        "site-packages" in dot_path or "lib" in dot_path
    ):
        return True

    if "venv_" in path_str and ("site-packages" in path_str or "lib" in path_str):
        return True

    for pattern in ignore_patterns:
        pattern = pattern.rstrip("/")

        if pattern in path_str or pattern in dot_path:
            return True

        if pattern.startswith("*.") and (
            path_str.endswith(pattern[1:]) or dot_path.endswith(pattern[1:])
        ):
            return True

    return False
