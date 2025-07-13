#!/usr/bin/env python3
import click
from treeline.renderer import TreeRenderer

@click.command()
@click.argument("directory", type=click.Path(exists=True), default=".", required=False)
@click.option("--depth", default=None, type=int, help="max depth")
@click.option("--no-size", is_flag=True, help="hide file sizes")
@click.option("--all", is_flag=True, help="show all files including hidden ones")
@click.option("--include", multiple=True, help="include only files matching these patterns")
@click.option("--exclude", multiple=True, help="exclude files matching these patterns")
@click.option("--output", "-o", help="save output to file instead of printing")
@click.option("--file-count", is_flag=True, help="show file counts for directories")
@click.option("--extensions", is_flag=True, help="show file extension summary")
@click.option("--code", is_flag=True, help="show classes and functions in Python/JS/TS files")

def cli(directory, depth, no_size, all, include, exclude, output, file_count, extensions, code):
    renderer = TreeRenderer(
        max_depth=depth,
        show_size=not no_size,
        show_all=all,
        include_patterns=set(include) if include else None,
        exclude_patterns=set(exclude) if exclude else None,
        output_file=output,
        show_file_count=file_count,
        show_extensions=extensions,
        show_code_structure=code
    )
    renderer.render(directory)

if __name__ == "__main__":
    cli()