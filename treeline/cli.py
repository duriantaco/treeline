#!/usr/bin/env python3
import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
from treeline.utils.report import ReportGenerator

console = Console()


@click.group()
def cli():
    """
    🌲 Treeline - Code Analysis & Visualization Tool

    A CLI to analyze and visualize Python codebases. Provides commands to:
    - Analyze structural dependencies
    - Check code quality
    - Generate reports
    - Launch a web interface
    """
    pass


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--depth", default=1, help="Analysis depth for dependencies")
def analyze(directory, depth):
    """
    Analyze your codebase structure and quality metrics.

    \b
    Examples:
      treeline analyze /path/to/codebase
      treeline analyze . --depth 2
    """
    with console.status("[bold green]Analyzing codebase..."):
        try:
            dep_analyzer = ModuleDependencyAnalyzer()
            code_analyzer = EnhancedCodeAnalyzer()

            dep_analyzer.analyze_directory(Path(directory))

            entry_points = dep_analyzer.get_entry_points()
            core_components = dep_analyzer.get_core_components()

            console.print("\n[bold]📊 Analysis Results[/]")

            console.print("\n[bold]Entry Points:[/]")
            if entry_points:
                for ep in entry_points:
                    console.print(f"  • {ep}")
            else:
                console.print("  (None found)")

            console.print("\n[bold]Core Components:[/]")
            if core_components:
                table = Table(show_header=True)
                table.add_column("Component")
                table.add_column("Incoming", justify="right")
                table.add_column("Outgoing", justify="right")
                for comp in core_components:
                    table.add_row(
                        comp["name"], 
                        str(comp["incoming"]), 
                        str(comp["outgoing"])
                    )
                console.print(table)
            else:
                console.print("  (No core components identified)")

            console.print(
                "\n[green]Analysis complete![/] You can now explore more details."
            )

        except Exception as e:
            console.print(
                f"\n[red]Error during analysis:[/] {str(e)}",
                style="bold red"
            )


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--min-complexity", default=10, help="Minimum complexity to report")
def quality(directory, min_complexity):
    """
    Analyze code quality metrics and highlight complex or smelly code.

    \b
    Examples:
      treeline quality /path/to/codebase
      treeline quality . --min-complexity 12
    """
    with console.status("[bold green]Analyzing code quality..."):
        try:
            analyzer = EnhancedCodeAnalyzer()
            results = []

            for file in Path(directory).rglob("*.py"):
                results.extend(analyzer.analyze_file(file))

            console.print("\n[bold]🔍 Code Quality Report[/]\n")

            complex_funcs = [
                r for r in results
                if r["type"] == "function"
                and r["metrics"]["complexity"] >= min_complexity
            ]
            if complex_funcs:
                table = Table(show_header=True, title="Complex Functions")
                table.add_column("Function")
                table.add_column("Complexity", justify="right")
                table.add_column("Lines", justify="right")

                for func in sorted(
                    complex_funcs,
                    key=lambda x: x["metrics"]["complexity"],
                    reverse=True,
                ):
                    table.add_row(
                        func["name"],
                        str(func["metrics"]["complexity"]),
                        str(func["metrics"]["lines"]),
                    )
                console.print(Panel(table))
            else:
                console.print("No functions exceed the specified complexity threshold.")

            smells = [r for r in results if r["code_smells"]]
            if smells:
                console.print("\n[bold]Code Smells:[/]")
                for item in smells:
                    console.print(f"\n• [bold]{item['type']}:[/] {item['name']}")
                    for smell in item["code_smells"]:
                        console.print(f"   - {smell}")
            else:
                console.print("\nNo code smells detected. Great job!")

        except Exception as e:
            console.print(f"[red]Error:[/] {str(e)}", style="bold red")


@cli.command()
def serve():
    """
    Start the Treeline web interface using FastAPI + Uvicorn.

    \b
    Examples:
      treeline serve
    """
    try:
        import uvicorn
        from treeline.api.app import app

        console.print("[green]Starting Treeline web interface...[/]")
        console.print("Visit http://localhost:8000 in your browser")

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        console.print("[red]Error:[/] Missing required packages. Install with:")
        console.print("  pip install fastapi uvicorn")
    except Exception as e:
        console.print(f"[red]Error starting web interface:[/] {str(e)}", style="bold red")


@cli.command()
@click.argument("directory", type=click.Path(exists=True), default=".")
@click.option("--output", default=None, help="Output markdown filename (default: treeline_report.md)")
def report(directory, output):
    """
    Generate a markdown report summarizing analysis results.

    \b
    Examples:
      treeline report /path/to/codebase
      treeline report . --output custom_report.md
    """
    with console.status("[bold green]Generating markdown report..."):
        try:
            report_gen = ReportGenerator(Path(directory))
            report_gen.analyze()

            filename = output or "treeline_report.md"
            report_path = report_gen.save_report(filename=filename)

            console.print(f"\n[green]Markdown report saved to {report_path}[/]")
        except Exception as e:
            console.print(f"\n[red]Error during report generation:[/] {str(e)}", style="bold red")

if __name__ == "__main__":
    cli()
