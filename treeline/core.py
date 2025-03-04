# treeline/treeline/core.py

from pathlib import Path
from treeline.cli import cli

def create_default_ignore():
    """Create a default .treeline-ignore file if it does not already exist."""
    ignore_file = Path(".treeline-ignore")
    if not ignore_file.exists():
        ignore_file.write_text(
            "\n".join([
                "*.pyc",
                "__pycache__/",
                ".git/",
                ".env/",
                "venv/",
                ".venv/",
                ".DS_Store",
                "node_modules/",
                "env/",
                "build/",
                "dist/",
                ""
            ])
        )
        print("Created .treeline-ignore file")


def main():
    """Entry point for the Treeline CLI."""
    create_default_ignore() 
    cli()  


if __name__ == "__main__":
    main()
