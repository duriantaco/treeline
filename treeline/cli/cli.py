# treeline/cli.py
# flake8: noqa: E265
#!/usr/bin/env python3
import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
from treeline.optimization.indexer import FastIndexer
from treeline.time_travel.time_travel import TimeTravelAnalyzer
from treeline.visualizers.mermaid import MermaidVisualizer

console = Console()


@click.group()
def cli():
    """🌲 Treeline - Code Analysis & Visualization Tool"""
    pass


@cli.group()
def snapshot():
    """Create and manage codebase snapshots"""
    pass


@snapshot.command(name="create")
@click.argument("directory", type=click.Path(exists=True))
@click.argument("label", type=str)
@click.option("--force", is_flag=True, help="Overwrite if snapshot exists")
def create_snapshot(directory, label, force):
    """Take a snapshot of your codebase"""
    with console.status("[bold green]Creating snapshot..."):
        try:
            indexer = FastIndexer()
            time_travel = TimeTravelAnalyzer()

            indexer.index_codebase(Path(directory))

            time_travel.store_snapshot(indexer, label)
            console.print(f"✨ [green]Snapshot created:[/] {label}")

        except Exception as e:
            console.print(f"[red]Error:[/] {str(e)}")


@snapshot.command(name="list")
def list_snapshots():
    """List all available snapshots"""
    try:
        time_travel = TimeTravelAnalyzer()
        snapshots = list(Path(time_travel.snapshot_dir).glob("*.json"))

        if not snapshots:
            console.print("[yellow]No snapshots found[/]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Label", style="dim")
        table.add_column("Date", justify="right")

        for snap in sorted(snapshots):
            created = snap.stat().st_mtime
            table.add_row(snap.stem, click.format_datetime(created))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@snapshot.command(name="compare")
@click.argument("old_label")
@click.argument("new_label")
@click.option("--output", type=click.Choice(["text", "json"]), default="text")
def compare_snapshots(old_label, new_label, output):
    """Compare two snapshots"""
    try:
        time_travel = TimeTravelAnalyzer()

        if output == "json":
            results = time_travel.compare_snapshots(old_label, new_label)
            console.print_json(json.dumps(results))
        else:
            time_travel.print_comparison_report(old_label, new_label)

    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--depth", default=1, help="Analysis depth for dependencies")
def analyze(directory, depth):
    """Analyze your codebase structure and quality"""
    with console.status("[bold green]Analyzing codebase...") as status:
        try:
            status.update("[bold green]Initializing analyzers...")
            dep_analyzer = ModuleDependencyAnalyzer()
            # code_analyzer = EnhancedCodeAnalyzer()

            status.update("[bold green]Analyzing dependencies...")
            dep_analyzer.analyze_directory(Path(directory))

            status.update("[bold green]Gathering insights...")
            entry_points = dep_analyzer.get_entry_points()
            core_components = dep_analyzer.get_core_components()

            console.print("\n[bold]📊 Analysis Results[/]")

            console.print("\n[bold]Entry Points:[/]")
            for ep in entry_points:
                console.print(f"  • {ep}")

            console.print("\n[bold]Core Components:[/]")
            table = Table(show_header=True)
            table.add_column("Component")
            table.add_column("Incoming", justify="right")
            table.add_column("Outgoing", justify="right")

            for comp in core_components:
                table.add_row(
                    comp["name"], str(comp["incoming"]), str(comp["outgoing"])
                )
            console.print(table)

            status.update("[bold green]Generating visualization...")
            visualizer = MermaidVisualizer()
            diagram = visualizer.generate_module_overview_diagram(
                dep_analyzer.module_imports
            )

            output_dir = Path("treeline_output")
            output_dir.mkdir(exist_ok=True)

            with open(output_dir / "diagram.mmd", "w") as f:
                f.write(diagram)

            console.print("\n✨ [green]Analysis complete![/]")
            console.print(f"Mermaid diagram saved to: {output_dir}/diagram.mmd")

        except Exception as e:
            console.print(f"\n[red]Error during analysis:[/] {str(e)}")


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--min-complexity", default=10, help="Minimum complexity to report")
def quality(directory, min_complexity):
    """Analyze code quality metrics"""
    with console.status("[bold green]Analyzing code quality..."):
        try:
            analyzer = EnhancedCodeAnalyzer()

            results = []
            for file in Path(directory).rglob("*.py"):
                results.extend(analyzer.analyze_file(file))

            console.print("\n[bold]🔍 Code Quality Report[/]\n")

            complex_funcs = [
                r
                for r in results
                if r["type"] == "function"
                and r["metrics"]["complexity"] >= min_complexity
            ]

            if complex_funcs:
                table = Table(show_header=True)
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

                console.print(Panel(table, title="Complex Functions"))

            smells = [r for r in results if r["code_smells"]]
            if smells:
                console.print("\n[bold]Code Smells:[/]")
                for item in smells:
                    console.print(f"\n[bold]{item['type']}:[/] {item['name']}")
                    for smell in item["code_smells"]:
                        console.print(f"  • {smell}")

        except Exception as e:
            console.print(f"[red]Error:[/] {str(e)}")


@cli.command()
def serve():
    """Start the Treeline web interface"""
    try:
        import uvicorn

        from treeline.api.app import app

        console.print("[green]Starting Treeline web interface...[/]")
        console.print("Visit http://localhost:8000 in your browser")

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        console.print("[red]Error:[/] Missing required packages. Install with:")
        console.print("pip install fastapi uvicorn")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


if __name__ == "__main__":
    cli()
