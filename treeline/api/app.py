# treeline/api/app.py
import json
from pathlib import Path
from typing import Dict, List
import pickle
import traceback
from concurrent.futures import ProcessPoolExecutor

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.utils.report import ReportGenerator


CACHE_DIR = Path(".treeline_cache")
CACHE_DIR.mkdir(exist_ok=True)
dependency_analyzer = None
code_analyzer = None

def analyze_file_wrapper(file_path, analyzer):
    return analyzer.analyze_file(file_path)

def load_cache(dir_path: Path):
    cache_file = CACHE_DIR / f"{dir_path.name}.pkl"
    if cache_file.exists():
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    return None

def save_cache(dir_path: Path, data):
    cache_file = CACHE_DIR / f"{dir_path.name}.pkl"
    with open(cache_file, "wb") as f:
        pickle.dump(data, f)

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

@app.get("/")
async def get_visualization():
    global dependency_analyzer

    try:
        index_path = static_path / "index.html"
        with open(index_path, "r") as f:
            html_content = f.read()
        print("Successfully read HTML template")

        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()

        if not dependency_analyzer:
            print("Initializing dependency analyzer...")
            dependency_analyzer = ModuleDependencyAnalyzer()

        cached_data = load_cache(target_dir)
        
        if cached_data:
            print("Using cached graph data")
            graph_data = cached_data
        else:
            try:
                from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
                enhanced_analyzer = EnhancedCodeAnalyzer()

                print(f"Analyzing directory for quality issues: {target_dir.absolute()}")
                
                python_files = list(target_dir.rglob("*.py"))
                with ProcessPoolExecutor(max_workers=4) as executor:
                    futures = [executor.submit(analyze_file_wrapper, f, enhanced_analyzer) for f in python_files]
                    results = [f.result() for f in futures]
                
                enhanced_analyzer.analyze_directory(target_dir)

                dependency_analyzer.analyze_directory(target_dir)
                print(f"Analyzed directory structure: {target_dir.absolute()}")

                nodes, links = dependency_analyzer.get_graph_data_with_quality(enhanced_analyzer)
                graph_data = {"nodes": nodes, "links": links}
                
                save_cache(target_dir, graph_data)
            except Exception as e:
                print(f"Error analyzing directory: {str(e)}")
                raise

        json_data = json.dumps(graph_data)
        print(f"Generated graph data with {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} links")

        nodes_with_issues = [n for n in graph_data['nodes'] if n.get('code_smells') and len(n.get('code_smells')) > 0]
        print(f"Found {len(nodes_with_issues)} nodes with quality issues")

        html_content = html_content.replace("GRAPH_DATA_PLACEHOLDER", json_data)
        print("Successfully injected graph data")

        return HTMLResponse(html_content)

    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
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
    
@app.get("/api/graph-data")
async def get_graph_data():
    """Return the graph data for visualization"""
    try:
        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()
            
        cached_data = load_cache(target_dir)
        
        if cached_data:
            print("Using cached graph data")
            return cached_data
        else:
            try:
                from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
                enhanced_analyzer = EnhancedCodeAnalyzer()

                print(f"Analyzing directory for quality issues: {target_dir.absolute()}")
                
                python_files = list(target_dir.rglob("*.py"))
                with ProcessPoolExecutor(max_workers=4) as executor:
                    futures = [executor.submit(analyze_file_wrapper, f, enhanced_analyzer) for f in python_files]
                    results = [f.result() for f in futures]
                
                enhanced_analyzer.analyze_directory(target_dir)

                dependency_analyzer.analyze_directory(target_dir)
                print(f"Analyzed directory structure: {target_dir.absolute()}")

                nodes, links = dependency_analyzer.get_graph_data_with_quality(enhanced_analyzer)
                graph_data = {"nodes": nodes, "links": links}
                
                save_cache(target_dir, graph_data)
                return graph_data
            except Exception as e:
                print(f"Error analyzing directory: {str(e)}")
                raise
                
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        tb = traceback.format_exc()
        print(f"Traceback:\n{tb}")
        raise HTTPException(
            status_code=500, detail=f"Error generating graph data: {str(e)}"
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


@app.get("/reports/complexity")
async def get_complexity_report():
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

@app.get("/api/node/{node_id}")
async def get_node_details(node_id: str):
    """Return the details for a specific node"""
    try:
        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()
            
        cached_data = load_cache(target_dir)
        
        if not cached_data:
            return JSONResponse(
                status_code=404, 
                content={"detail": "No graph data available"}
            )
            
        nodes = cached_data.get('nodes', [])
        links = cached_data.get('links', [])
        
        print(f"Looking for node_id: {node_id}")
        print(f"Available node IDs: {[n.get('id') for n in nodes[:10]]}")  # Print first 10 for brevity
        print(f"Loaded {len(nodes)} nodes and {len(links)} links from cache")
        
        # Find nodes by ID
        node_lookup = {str(n.get('id')): n for n in nodes}
        
        if str(node_id) not in node_lookup:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Node with ID {node_id} not found", "available_ids_range": f"0-{len(nodes)-1}"}
            )
            
        node = node_lookup[str(node_id)]
        
        incoming_links = []
        outgoing_links = []
        
        # Helper to safely extract IDs from source/target
        def extract_id(item):
            if isinstance(item, str):
                return item
            elif isinstance(item, dict) and 'id' in item:
                return item['id']
            elif isinstance(item, int):
                # If it's an integer index, try to map it to the actual node ID
                if 0 <= item < len(nodes):
                    return nodes[item].get('id')
                return str(item)  # Fall back to string representation
            return str(item)  # Default fallback
        
        # Process links
        for link in links:
            try:
                source_id = extract_id(link['source'])
                target_id = extract_id(link['target'])
                
                # Make sure we're comparing strings
                if str(source_id) == str(node_id):
                    outgoing_links.append(link)
                if str(target_id) == str(node_id):
                    incoming_links.append(link)
            except Exception as e:
                print(f"Error processing link: {e}")
                continue
        
        file_path = None
        if 'file_path' in node:
            file_path = node['file_path']
            try:
                with open(file_path, 'r') as f:
                    file_content = f.read()
            except:
                file_content = None
        else:
            file_content = None
        
        return {
            "node": node,
            "connections": {
                "incoming": incoming_links,
                "outgoing": outgoing_links
            },
            "file_content": file_content
        }
                
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        tb = traceback.format_exc()
        print(f"Traceback:\n{tb}")
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Error fetching node details: {str(e)}"}
        )
    
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


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    print(f"ERROR: {str(exc)}")
    return {"detail": str(exc)}
