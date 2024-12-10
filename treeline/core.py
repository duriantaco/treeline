# treeline/treeline/core.py
import argparse
from pathlib import Path
from typing import Dict, List

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
from treeline.models.core import CodeStructure, TreeOptions
from treeline.type_checker import ValidationError


def create_default_ignore():
    """Create default .treeline-ignore if it doesn't exist"""
    if not Path(".treeline-ignore").exists():
        with open(".treeline-ignore", "w") as f:
            f.write("*.pyc\n__pycache__\n.git\n.env\nvenv/\n.DS_Store\nnode_modules/\n")
        print("Created .treeline-ignore file")


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
    """Check if path should be ignored based on patterns"""
    path_str = str(path)
    for pattern in ignore_patterns:
        if pattern.endswith("/"):
            if pattern[:-1] in path_str:
                return True
        elif pattern.startswith("*."):
            if path_str.endswith(pattern[1:]):
                return True
        else:
            if pattern in path_str:
                return True
    return False


def format_structure(self, structure: List[Dict], indent: str = "") -> List[str]:
    """
    Format the analysis results into a readable tree structure.

    Args:
        structure: List of analysis results
        indent: String to use for indentation

    Returns:
        List of formatted strings representing the code structure
    """
    lines = []

    for item in structure:
        try:
            validated_item = CodeStructure(**item)
        except ValidationError as e:
            lines.append(f"{indent}⚠️ Invalid item: {str(e)}")
            continue

        if validated_item.type == "class":
            lines.append(f"{indent}[CLASS] 🏛️ {validated_item.name}")
        elif validated_item.type == "function":
            lines.append(f"{indent}[FUNC] ⚡ {validated_item.name}")
        elif validated_item.type == "error":
            lines.append(f"{indent}⚠️ {validated_item.name}")
            continue

        if validated_item.docstring:
            lines.append(f"{indent}  └─ # {validated_item.docstring}")

        if validated_item.metrics:
            if (
                validated_item.metrics.get("complexity", 0)
                > self.QUALITY_METRICS["MAX_CYCLOMATIC_COMPLEXITY"]
            ):
                lines.append(
                    f"{indent}  └─ ⚠️ High complexity ({validated_item.metrics['complexity']})"
                )

            if (
                validated_item.metrics.get("lines", 0)
                > self.QUALITY_METRICS["MAX_FUNCTION_LINES"]
            ):
                lines.append(
                    f"{indent}  └─ ⚠️ Too long ({validated_item.metrics['lines']} lines)"
                )

            if (
                validated_item.metrics.get("nested_depth", 0)
                > self.QUALITY_METRICS["MAX_NESTED_DEPTH"]
            ):
                lines.append(
                    f"{indent}  └─ ⚠️ Deep nesting (depth {validated_item.metrics['nested_depth']})"
                )

        if validated_item.code_smells:
            for smell in validated_item.code_smells:
                lines.append(f"{indent}  └─ ⚠️ {smell}")

    return lines


def generate_tree(
    directory,
    create_md=False,
    hide_structure=False,
    show_params=True,
    show_relationships=False,
):
    """Generate tree structure with code quality and security analysis."""

    options = TreeOptions(
        directory=directory,
        create_md=create_md,
        hide_structure=hide_structure,
        show_params=show_params,
        show_relationships=show_relationships,
    )

    tree_str = []
    directory = Path(options.directory)
    ignore_patterns = read_ignore_patterns()

    code_analyzer = (
        None if hide_structure else EnhancedCodeAnalyzer(show_params=show_params)
    )

    dep_analyzer = ModuleDependencyAnalyzer() if create_md else None
    if dep_analyzer:
        dep_analyzer.analyze_directory(directory)

    def add_directory(path, prefix=""):
        try:
            files = sorted(
                path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
            )
            for i, entry in enumerate(files):
                if should_ignore(entry, ignore_patterns):
                    continue

                is_last = i == len(files) - 1
                cur_prefix = prefix + ("└── " if is_last else "├── ")
                tree_str.append(f"{cur_prefix}{entry.name}")

                if entry.is_dir():
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    add_directory(entry, next_prefix)
                elif not hide_structure and entry.suffix == ".py":
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    if code_analyzer:
                        try:
                            structure = code_analyzer.analyze_file(entry)
                            if structure:
                                tree_str.extend(
                                    code_analyzer.format_structure(
                                        structure, next_prefix + "  "
                                    )
                                )
                        except Exception as e:
                            tree_str.append(
                                f"{next_prefix}  ⚠️ Error analyzing: {str(e)}"
                            )
        except Exception as e:
            tree_str.append(f"{prefix}⚠️ Error reading directory: {str(e)}")

    try:
        tree_str.append(str(directory.name))
        add_directory(directory)
    except Exception as e:
        tree_str.append(f"⚠️ Fatal error: {str(e)}")

    print("\n".join(tree_str))
    print("\n")

    if create_md and dep_analyzer:
        dep_analyzer.generate_reports(tree_str)

    return "\n".join(tree_str)


def main():
    create_default_ignore()
    parser = argparse.ArgumentParser(
        description="Generate code analysis with quality checks",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
            Examples:
            treeline                      # Show full analysis
            treeline /path/to/dir         # Analyze specific directory
            treeline -m                   # Create markdown report
            treeline -i "*.pyc,*.git"     # Ignore patterns
            treeline --hide-structure     # Hide code structure
            treeline --no-params          # Hide function parameters
            treeline -h                   # Show this help message
        """,
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory path (default: current directory)",
    )
    parser.add_argument(
        "-m", "--markdown", action="store_true", help="Create markdown report (tree.md)"
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help='Comma-separated patterns to ignore (e.g., "*.pyc,*.git")',
    )
    parser.add_argument(
        "--hide-structure", action="store_true", help="Hide code structure"
    )
    parser.add_argument(
        "--no-params", action="store_true", help="Hide function parameters"
    )

    parser.add_argument(
        "--diff",
        nargs="*",
        help="Compare code structure between commits. Usage: --diff [before_commit] [after_commit]",
    )
    args = parser.parse_args()

    generate_tree(
        args.directory,
        create_md=args.markdown,
        hide_structure=args.hide_structure,
        show_params=not args.no_params,
    )
