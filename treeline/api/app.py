# treeline/api/app.py
import json
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.utils.report import ReportGenerator
from treeline.visualizers.mermaid import MermaidVisualizer


class AnalysisRequest(BaseModel):
    path: str
    show_params: bool = True
    show_relationships: bool = True


class AnalysisResponse(BaseModel):
    nodes: List[Dict]
    relationships: List[Dict]
    metrics: Dict
    insights: Dict


app = FastAPI(
    title="Treeline API",
    description="Code analysis and visualization API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


dependency_analyzer = None
code_analyzer = None


@app.get("/")
async def get_visualization():
    """Serve the main visualization page"""
    global dependency_analyzer

    try:
        index_path = static_path / "index.html"
        try:
            with open(index_path, "r") as f:
                html_content = f.read()
            print("Successfully read HTML template")
        except Exception as e:
            print(f"Error reading HTML: {str(e)}")
            raise

        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()

        if not dependency_analyzer:
            print("Initializing dependency analyzer...")
            try:
                dependency_analyzer = ModuleDependencyAnalyzer()
            except Exception as e:
                print(f"Error initializing analyzer: {str(e)}")
                raise

        try:
            dependency_analyzer.analyze_directory(target_dir)
            print(f"Analyzed directory: {target_dir.absolute()}")
        except Exception as e:
            print(f"Error analyzing directory: {str(e)}")
            raise

        try:
            nodes, links = dependency_analyzer.get_graph_data()
            graph_data = {"nodes": nodes, "links": links}
            json_data = json.dumps(graph_data)
            print(
                f"Generated graph data with {len(nodes)} nodes and {len(links)} links"
            )
        except Exception as e:
            print(f"Error generating graph data: {str(e)}")
            raise

        try:
            html_content = html_content.replace("GRAPH_DATA_PLACEHOLDER", json_data)
            print("Successfully injected graph data")
        except Exception as e:
            print(f"Error injecting data into template: {str(e)}")
            raise

        return HTMLResponse(html_content)

    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback

        tb = traceback.format_exc()
        print(f"Traceback:\n{tb}")
        return HTMLResponse(
            f"""
            <html>
                <body>
                    <h1>Server Error</h1>
                    <pre>{tb}</pre>
                </body>
            </html>
            """
        )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_codebase(request: AnalysisRequest):
    """Analyze a codebase and return comprehensive results"""
    try:
        path = Path(request.path)
        if not path.exists():
            raise HTTPException(
                status_code=404, detail=f"Path {request.path} not found"
            )

        dependency_analyzer.analyze_directory(
            path,
            show_params=request.show_params,
            show_relationships=request.show_relationships,
        )

        nodes, links = dependency_analyzer.get_graph_data()

        return {
            "nodes": nodes,
            "relationships": links,
            "metrics": dependency_analyzer.module_metrics,
            "insights": {
                "entry_points": dependency_analyzer.get_entry_points(),
                "core_components": dependency_analyzer.get_core_components(),
                "workflows": dependency_analyzer.get_common_flows(),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing codebase: {str(e)}"
        )


@app.get("/metrics/{module_path}")
async def get_module_metrics(module_path: str):
    """Get detailed metrics for a specific module"""
    if module_path not in dependency_analyzer.module_metrics:
        raise HTTPException(status_code=404, detail=f"Module {module_path} not found")

    return {
        "metrics": dependency_analyzer.module_metrics[module_path],
        "quality": code_analyzer.analyze_file(Path(module_path)),
    }


@app.get("/api/diagrams")
async def get_diagrams():
    """Get Mermaid diagrams for the codebase"""
    visualizer = MermaidVisualizer()

    overview = visualizer.generate_module_overview_diagram(
        module_imports=dependency_analyzer.module_imports
    )

    details = []
    for module in sorted(dependency_analyzer.module_imports.keys()):
        if module.startswith("treeline."):
            detail = visualizer.generate_module_detail_diagram(
                module=module,
                class_info=dependency_analyzer.class_info,
                function_locations=dependency_analyzer.function_locations,
                function_calls=dependency_analyzer.function_calls,
            )
            details.append({"module": module, "diagram": detail})

    return {"overview": overview, "details": details}


@app.get("/reports/complexity")
async def get_complexity_report():
    """Get complexity analysis report"""
    if not dependency_analyzer.complex_functions:
        return {"message": "No complex functions found"}

    return {
        "hotspots": [
            {
                "module": module,
                "function": func,
                "complexity": complexity,
                "exceeds_threshold": complexity
                > dependency_analyzer.QUALITY_METRICS["MAX_CYCLOMATIC_COMPLEXITY"],
            }
            for module, func, complexity in sorted(
                dependency_analyzer.complex_functions, key=lambda x: x[2], reverse=True
            )
        ]
    }


@app.get("/reports/structure")
async def get_structure_report(tree_str: List[str]):
    """Get codebase structure report"""
    processed_tree = [dependency_analyzer.clean_for_markdown(line) for line in tree_str]

    return {"structure": processed_tree, "metrics": dependency_analyzer.module_metrics}


@app.get("/reports/mermaid")
async def get_mermaid_report():
    """Get Mermaid diagram report"""
    visualizer = MermaidVisualizer()

    overview = visualizer.generate_module_overview_diagram(
        dependency_analyzer.module_imports
    )

    details = []
    for module in sorted(dependency_analyzer.module_imports.keys()):
        if module.startswith("treeline."):
            detail = visualizer.generate_module_detail_diagram(
                module=module,
                class_info=dependency_analyzer.class_info,
                function_locations=dependency_analyzer.function_locations,
                function_calls=dependency_analyzer.function_calls,
            )
            details.append({"module": module, "diagram": detail})

    return {"overview": overview, "details": details}


@app.get("/reports/quality")
async def get_quality_report():
    """Get code quality metrics report"""
    return {
        "metrics": {
            "module_metrics": dependency_analyzer.module_metrics,
            "complex_functions": dependency_analyzer.complex_functions,
            "quality_thresholds": dependency_analyzer.QUALITY_METRICS,
        },
        "insights": {
            "entry_points": dependency_analyzer.get_entry_points(),
            "core_components": dependency_analyzer.get_core_components(),
            "common_flows": dependency_analyzer.get_common_flows(),
        },
    }


@app.get("/reports/export/{format}")
async def export_report(format: str = "html"):
    """Export analysis report in specified format"""
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    nodes, links = dependency_analyzer.get_graph_data()

    if format == "html":
        template_path = static_path / "templates" / "report.html"
        template = template_path.read_text()

        report_data = {
            "nodes": nodes,
            "links": links,
            "metrics": dependency_analyzer.module_metrics,
            "quality": await get_quality_report(),
            "mermaid": await get_mermaid_report(),
        }

        return HTMLResponse(template.replace("REPORT_DATA", json.dumps(report_data)))

    elif format == "markdown":
        md_content = []
        md_content.append("# Code Analysis Report\n")

        quality_data = await get_quality_report()
        mermaid_data = await get_mermaid_report()

        md_content.extend(
            [
                "## Module Overview\n",
                f"```mermaid\n{mermaid_data['overview']}\n```\n",
                "## Quality Metrics\n",
                f"Complex Functions: {len(quality_data['metrics']['complex_functions'])}\n",
                "## Core Components\n",
                *[
                    f"- {comp['name']} (in: {comp['incoming']}, out: {comp['outgoing']})"
                    for comp in quality_data["insights"]["core_components"]
                ],
            ]
        )

        return "\n".join(md_content)

    raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@app.get("/reports/{format}")
async def generate_report(
    format: str = "html", tree_str: List[str] = Query(None), path: str = Query(None)
):
    """Generate a comprehensive report"""
    if path:
        target_path = Path(path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"Path {path} not found")
        dependency_analyzer.analyze_directory(target_path)

    mermaid_data = await get_diagrams()

    report_data = ReportGenerator.generate_report_data(
        tree_str=tree_str or [],
        complex_functions=dependency_analyzer.complex_functions,
        module_metrics=dependency_analyzer.module_metrics,
        quality_metrics=dependency_analyzer.QUALITY_METRICS,
        mermaid_diagrams=mermaid_data,
    )

    if format == "json":
        return report_data

    if format == "html":
        template_path = static_path / "report.html"
        if not template_path.exists():
            raise HTTPException(status_code=500, detail="Report template not found")

        template = template_path.read_text()
        html_content = ReportGenerator.convert_to_html(report_data)

        result = template.replace(
            "REPORT_DATA_PLACEHOLDER", json.dumps(report_data)
        ).replace(
            '<div id="report-content"></div>',
            f'<div id="report-content">{html_content}</div>',
        )

        return HTMLResponse(result)

    raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    print(f"ERROR: {str(exc)}")
    return {"detail": str(exc)}
