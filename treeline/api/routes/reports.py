from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List
from pathlib import Path
import re
import json

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
from treeline.utils.report import ReportGenerator
from concurrent.futures import ProcessPoolExecutor

reports_router = APIRouter(prefix="/reports", tags=["reports"])
static_path = Path(__file__).parent.parent / "static"

def is_safe_path(base_dir: Path, requested_path: Path) -> bool:
    """
    Check if the requested path is within the allowed base directory
    """
    base_dir = base_dir.resolve()
    requested_path = requested_path.resolve()
    
    try:
        requested_path.relative_to(base_dir)
        return True
    except ValueError:
        return False
        
def analyze_file_wrapper(file_path, analyzer):
    return analyzer.analyze_file(file_path)

def analyze_directory(directory: Path):
    global dependency_analyzer, enhanced_analyzer, current_directory
    if current_directory == directory and dependency_analyzer and enhanced_analyzer:
        return dependency_analyzer, enhanced_analyzer
    
    dependency_analyzer = ModuleDependencyAnalyzer()
    enhanced_analyzer = EnhancedCodeAnalyzer()
    
    dependency_analyzer.analyze_directory(directory)
    python_files = list(directory.rglob("*.py"))
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(analyze_file_wrapper, f, enhanced_analyzer) for f in python_files]
        [f.result() for f in futures]
    
    current_directory = directory
    return dependency_analyzer, enhanced_analyzer

@reports_router.get("/complexity")
async def get_complexity_report():
    try:
        with open(".treeline_dir", "r") as f:
            target_dir = Path(f.read().strip()).resolve()
    except FileNotFoundError:
        target_dir = Path(".").resolve()
    
    _, enh_analyzer = analyze_directory(target_dir)
    
    complexity_issues = [
        issue for issue in enh_analyzer.quality_issues["complexity"]
        if "cyclomatic complexity" in issue["description"]
    ]
    
    hotspots = []
    for issue in complexity_issues:
        match = re.search(r"High cyclomatic complexity \((\d+) > (\d+)\) in (function|class) '(\w+)'", issue["description"])
        if match:
            complexity = int(match.group(1))
            threshold = int(match.group(2))
            func_name = match.group(4)
            hotspots.append({
                "module": Path(issue["file_path"]).relative_to(target_dir).as_posix().replace(".py", "").replace("/", "."),
                "function": func_name,
                "complexity": complexity,
                "exceeds_threshold": complexity > threshold,
            })
    
    if not hotspots:
        return {"message": "No complex functions found"}
    
    return {"hotspots": sorted(hotspots, key=lambda x: x["complexity"], reverse=True)}

@reports_router.get("/structure")
async def get_structure_report(tree_str: List[str] = Query(...)):
    global dependency_analyzer

    if not dependency_analyzer:
        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()
        dependency_analyzer = ModuleDependencyAnalyzer()
        dependency_analyzer.analyze_directory(target_dir)

    if not all(isinstance(line, str) for line in tree_str):
        raise HTTPException(status_code=400, detail="Invalid tree_str format")
    
    processed_tree = [dependency_analyzer.clean_for_markdown(line) for line in tree_str]
    return {"structure": processed_tree, "metrics": dependency_analyzer.module_metrics}

@reports_router.get("/quality")
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

@reports_router.get("/export/{format}")
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
        }

        return HTMLResponse(template.replace("REPORT_DATA", json.dumps(report_data)))

    elif format == "markdown":
        md_content = []
        md_content.append("# Code Analysis Report\n")

        quality_data = await get_quality_report()

        md_content.extend(
            [
                "## Module Overview\n",
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


@reports_router.get("/{format}")
async def generate_report(
    format: str = "html", tree_str: List[str] = Query(None), path: str = Query(None)
):
    """Generate a comprehensive report"""
    base_dir = Path.cwd().resolve()
    if path:
        target_path = Path(path).resolve()
        if not is_safe_path(base_dir, target_path):
            raise HTTPException(status_code=403, detail=f"Access denied: {path} is outside the allowed directory")
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"Path {path} not found")
        dependency_analyzer.analyze_directory(target_path)

    report_data = ReportGenerator.generate_report_data(
        tree_str=tree_str or [],
        complex_functions=dependency_analyzer.complex_functions,
        module_metrics=dependency_analyzer.module_metrics,
        quality_metrics=dependency_analyzer.QUALITY_METRICS,
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

