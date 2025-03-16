# treeline/api/app.py
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import traceback
from concurrent.futures import ProcessPoolExecutor
import logging
import re
from collections import defaultdict
import os

from fastapi import FastAPI, HTTPException, Query, Depends, APIRouter, Path as FastAPIPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.utils.report import ReportGenerator
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = Path(".treeline_cache")
CACHE_DIR.mkdir(exist_ok=True)
dependency_analyzer = None
code_analyzer = None

class GraphData(BaseModel):
    nodes: List[Dict]
    links: List[Dict]

class AnalysisRequest(BaseModel):
    path: str
    show_params: bool = True
    show_relationships: bool = True


class AnalysisResponse(BaseModel):
    nodes: List[Dict]
    relationships: List[Dict]
    metrics: Dict
    insights: Dict

class FunctionMetricsDetail(BaseModel):
    name: str
    line: int
    lines: int
    params: int
    returns: Optional[int] = None
    complexity: int
    cognitive_complexity: Optional[int] = None
    nested_depth: Optional[int] = None
    has_docstring: Optional[bool] = None
    docstring_length: Optional[int] = None
    maintainability_index: Optional[float] = None
    cognitive_load: Optional[int] = None
    code_smells: List[Dict[str, Any]] = []

class ClassMetricsDetail(BaseModel):
    name: str
    line: int
    lines: int
    method_count: int
    public_methods: Optional[int] = None
    private_methods: Optional[int] = None
    complexity: Optional[int] = None
    inheritance_depth: Optional[int] = None
    has_docstring: Optional[bool] = None
    docstring_length: Optional[int] = None
    code_smells: List[Dict[str, Any]] = []
    methods: List[FunctionMetricsDetail] = []

class FileMetricsDetail(BaseModel):
    path: str
    lines: int
    functions: List[FunctionMetricsDetail] = []
    classes: List[ClassMetricsDetail] = []
    imports: List[str] = []
    issues_by_category: Dict[str, List[Dict[str, Any]]] = {}
    metrics_summary: Dict[str, Any] = {}

class DetailedAnalysisResponse(BaseModel):
    files: Dict[str, FileMetricsDetail]
    project_metrics: Dict[str, Any]
    dependency_metrics: Dict[str, Any]
    issues_summary: Dict[str, int]

class ComplexityBreakdown(BaseModel):
    if_statements: int = 0
    for_loops: int = 0
    while_loops: int = 0
    except_blocks: int = 0
    try_blocks: int = 0
    boolean_operations: int = 0
    and_operations: int = 0
    or_operations: int = 0
    comprehensions: int = 0
    list_comprehensions: int = 0
    dict_comprehensions: int = 0
    set_comprehensions: int = 0
    generator_expressions: int = 0
    lambda_functions: int = 0
    nested_functions: int = 0
    nested_classes: int = 0

def load_cache(dir_path: Path) -> Optional[Dict[str, Any]]:
    cache_file = CACHE_DIR / f"{dir_path.name}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                GraphData(**data)  
                return data
        except (json.JSONDecodeError, ValidationError):
            return None
    return None

def save_cache(dir_path: Path, data: Dict[str, Any]) -> None:
    """
    Save data to cache using JSON instead of pickle for security
    
    Args:
        dir_path: Directory path to use as cache key
        data: Data to cache
    """
    cache_file = CACHE_DIR / f"{dir_path.name}.json"
    with open(cache_file, "w") as f:
        json.dump(data, f)

def analyze_file_wrapper(file_path, analyzer):
    return analyzer.analyze_file(file_path)


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

def get_dependency_analyzer():
    return ModuleDependencyAnalyzer()

@app.get("/", dependencies=[Depends(get_dependency_analyzer)])
async def get_visualization(analyzer: ModuleDependencyAnalyzer = Depends(get_dependency_analyzer)):
    global dependency_analyzer

    try:
        index_path = static_path / "index.html"
        with open(index_path, "r") as f:
            html_content = f.read()
        logger.info("Successfully read HTML template")

        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()

        if not dependency_analyzer:
            dependency_analyzer = ModuleDependencyAnalyzer()

        cached_data = load_cache(target_dir)
        if cached_data:
            graph_data = cached_data
        else:
            enhanced_analyzer = EnhancedCodeAnalyzer()
            python_files = list(target_dir.rglob("*.py"))
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(analyze_file_wrapper, f, enhanced_analyzer) for f in python_files]
                results = [f.result() for f in futures]
            all_results = [item for sublist in results for item in sublist]

            analyzer.analyze_directory(target_dir)
            nodes, links = analyzer.get_graph_data_with_quality(enhanced_analyzer, all_results)
            graph_data = {"nodes": nodes, "links": links}
            save_cache(target_dir, graph_data)

        json_data = json.dumps(graph_data)

        html_content = html_content.replace("GRAPH_DATA_PLACEHOLDER", json_data)
        logger.info("Successfully injected graph data")

        return HTMLResponse(html_content)

    except Exception as e:
        traceback_str = traceback.format_exc()
        return HTMLResponse(
            f"""
            <html>
                <body>
                    <h1>Server Error</h1>
                    <p>An unexpected error occurred. Please contact the administrator.</p>
                </body>
            </html>
            """
        )


def build_path_indices(nodes):
    path_to_node_id = {}
    name_to_node_id = {}
    
    for node in nodes:
        node_id = str(node.get('id'))
        
        if 'name' in node:
            name = node['name']
            name_to_node_id[name] = node_id
        
        path_props = ['file_path', 'path', 'filepath', 'filename', 'id']
        for prop in path_props:
            if prop in node and isinstance(node[prop], str):
                path = node[prop]
                
                path_to_node_id[path] = node_id
                
                if path.startswith('/'):
                    path_to_node_id[path[1:]] = node_id
                else:
                    path_to_node_id['/' + path] = node_id
                
                try:
                    filename = Path(path).name
                    if filename:
                        path_to_node_id[filename] = node_id
                except:
                    pass
    
    return {
        "path_to_node_id": path_to_node_id,
        "name_to_node_id": name_to_node_id
    }


@app.get("/api/graph-data")
async def get_graph_data():
    try:
        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()
            
        cached_data = load_cache(target_dir)
        
        if cached_data:
            logger.info("Using cached graph data")
            if 'indices' not in cached_data:
                cached_data['indices'] = build_path_indices(cached_data.get('nodes', []))
                save_cache(target_dir, cached_data)
            return cached_data
        else:
            try:
                from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
                enhanced_analyzer = EnhancedCodeAnalyzer()                
                python_files = list(target_dir.rglob("*.py"))
                with ProcessPoolExecutor(max_workers=4) as executor:
                    futures = [executor.submit(analyze_file_wrapper, f, enhanced_analyzer) for f in python_files]
                    results = [f.result() for f in futures]
                
                enhanced_analyzer.analyze_directory(target_dir)
                dependency_analyzer.analyze_directory(target_dir)
                nodes, links = dependency_analyzer.get_graph_data_with_quality(enhanced_analyzer)
                
                indices = build_path_indices(nodes)
                
                graph_data = {
                    "nodes": nodes, 
                    "links": links,
                    "indices": indices
                }
                
                save_cache(target_dir, graph_data)
                return graph_data
            except Exception as e:
                raise
                
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating graph data: {str(e)}"
        )
    
@app.get("/api/file-content")
async def get_file_content(path: str = Query(...)):
    """Get file content with basic structure analysis"""
    try:
        provided_path = Path(path).resolve()
        
        base_dir = Path.cwd().resolve()
        if not is_safe_path(base_dir, provided_path):
            return JSONResponse(status_code=403, content={"detail": "Access denied"})
        
        if not provided_path.exists() or not provided_path.is_file():
            return JSONResponse(status_code=404, content={"detail": f"File not found: {path}"})
        
        try:
            with open(provided_path, 'r') as f:
                content = f.read()
            
            file_info = {
                "path": str(provided_path),
                "name": provided_path.name,
                "content": content,
                "structure": []
            }
            
            
            class_matches = re.finditer(r'^\s*class\s+(\w+)', content, re.MULTILINE)
            for match in class_matches:
                line_number = content[:match.start()].count('\n') + 1
                file_info["structure"].append({
                    "type": "class",
                    "name": match.group(1),
                    "line": line_number
                })
            
            func_matches = re.finditer(r'^\s*def\s+(\w+)', content, re.MULTILINE)
            for match in func_matches:
                line_number = content[:match.start()].count('\n') + 1
                file_info["structure"].append({
                    "type": "function",
                    "name": match.group(1),
                    "line": line_number
                })
            
            file_info["structure"].sort(key=lambda x: x["line"])
            
            return file_info
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error analyzing file: {str(e)}"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error: {str(e)}"}
        )
    
@app.get("/api/node-by-path/{file_path:path}")
async def get_node_by_path(file_path: str):
    provided_path = Path(file_path).resolve()
    try:
        with open(".treeline_dir", "r") as f:
            project_root = Path(f.read().strip()).resolve()
    except FileNotFoundError:
        project_root = Path(".").resolve()

    try:
        cached_data = load_cache(project_root)
        
        if not cached_data or 'nodes' not in cached_data or not cached_data['nodes']:
            print("Cache is empty or invalid, generating new cache data...")
            dependency_analyzer = ModuleDependencyAnalyzer()
            enhanced_analyzer = EnhancedCodeAnalyzer()
            
            dependency_analyzer.analyze_directory(project_root)
            python_files = list(project_root.rglob("*.py"))
            
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(analyze_file_wrapper, f, enhanced_analyzer) for f in python_files]
                results = [f.result() for f in futures]
            
            nodes, links = dependency_analyzer.get_graph_data()
            indices = build_path_indices(nodes)
            
            cached_data = {
                "nodes": nodes,
                "links": links,
                "indices": indices
            }
            
            save_cache(project_root, cached_data)
            print(f"Generated new cache with {len(nodes)} nodes")
        
        nodes = cached_data.get('nodes', [])
        links = cached_data.get('links', [])
        
        try:
            search_path = str(provided_path.relative_to(project_root))
        except ValueError:
            search_path = file_path.lstrip("/")
 
        for i, node in enumerate(nodes[:5]):
            if 'file_path' in node:
                print(f"Node {i} path: {node['file_path']}")
        
        filename = Path(search_path).name
        basename = filename.replace('.py', '')
        node = None
        
        if 'indices' in cached_data and cached_data['indices']:
            path_to_node_id = cached_data['indices'].get('path_to_node_id', {})
            
            path_variations = [
                search_path,
                str(provided_path),
                filename,
                basename,
                search_path.replace('\\', '/'),
                search_path.replace('/', '\\')
            ]
            
            for path_var in path_variations:
                if path_var in path_to_node_id:
                    node_id = path_to_node_id[path_var]
                    node = next((n for n in nodes if str(n.get('id')) == node_id), None)
                    if node:
                        print(f"Found node via index lookup: {path_var}")
                        break
        
        if not node:
            for n in nodes:
                for prop in ['file_path', 'path', 'filepath', 'id', 'name']:
                    if prop not in n or not isinstance(n[prop], str):
                        continue
                    
                    if n[prop] == search_path:
                        node = n
                        print(f"Found direct match on {prop}: {n[prop]}")
                        break
                    
                    if n[prop].endswith(search_path):
                        node = n
                        print(f"Found ends-with match on {prop}: {n[prop]}")
                        break
                    
                    if search_path in n[prop]:
                        node = n
                        print(f"Found contains match on {prop}: {n[prop]}")
                        break
                    
                    if Path(n[prop]).name == filename:
                        node = n
                        print(f"Found filename match on {prop}: {n[prop]}")
                        break
                
                if node:
                    break
        
        if not node:
            print(f"No node found for path: {search_path}")
            return JSONResponse(
                status_code=404,
                content={"detail": f"No node found for file path: {search_path}"}
            )
        
        node_id = str(node.get('id'))
        node_lookup = {str(n.get('id')): n for n in nodes}
        incoming_links = [link for link in links if str(link.get('target')) == node_id]
        outgoing_links = [link for link in links if str(link.get('source')) == node_id]
        
        incoming_links_with_names = [
            {
                "source_id": link['source'],
                "source_name": node_lookup.get(link['source'], {}).get('name', 'Unknown'),
                "source_type": node_lookup.get(link['source'], {}).get('type', 'unknown'),
                "target_id": link['target'],
                "target_name": node_lookup.get(link['target'], {}).get('name', 'Unknown'),
                "target_type": node_lookup.get(link['target'], {}).get('type', 'unknown'),
                "type": link['type']
            }
            for link in incoming_links
        ]
        
        outgoing_links_with_names = [
            {
                "source_id": link['source'],
                "source_name": node_lookup.get(link['source'], {}).get('name', 'Unknown'),
                "source_type": node_lookup.get(link['source'], {}).get('type', 'unknown'),
                "target_id": link['target'],
                "target_name": node_lookup.get(link['target'], {}).get('name', 'Unknown'),
                "target_type": node_lookup.get(link['target'], {}).get('type', 'unknown'),
                "type": link['type']
            }
            for link in outgoing_links
        ]
        
        file_content = None
        if 'file_path' in node and os.path.exists(node['file_path']):
            try:
                with open(node['file_path'], 'r') as f:
                    file_content = f.read()
            except Exception as e:
                print(f"Could not read file content: {str(e)}")
        
        return {
            "node": node,
            "connections": {
                "incoming": incoming_links_with_names,
                "outgoing": outgoing_links_with_names
            },
            "file_content": file_content
        }
    
    except Exception as e:
        import traceback
        print(f"Error in get_node_by_path: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error fetching node details: {str(e)}"}
        )

def is_safe_path(base_dir: Path, requested_path: Path) -> bool:
    """
    Validate that the requested path is within the allowed base directory.
    
    Args:
        base_dir: The allowed base directory
        requested_path: The path requested by the user
        
    Returns:
        True if the path is safe, False otherwise
    """
    base_dir = base_dir.resolve()
    requested_path = requested_path.resolve()
    
    try:
        requested_path.relative_to(base_dir)
        return True
    except ValueError:
        return False

@app.get("/metrics/{module_path}")
async def get_module_metrics(module_path: str):
    """Get detailed metrics for a specific module"""
    if module_path not in dependency_analyzer.module_metrics:
        raise HTTPException(status_code=404, detail=f"Module {module_path} not found")

    return {
        "metrics": dependency_analyzer.module_metrics[module_path],
        "quality": code_analyzer.analyze_file(Path(module_path)),
    }

dependency_analyzer = None
enhanced_analyzer = None
current_directory = None

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

@app.get("/reports/complexity")
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


@app.get("/reports/structure")
async def get_structure_report(tree_str: List[str]):
    """Get codebase structure report"""
    if not all(isinstance(line, str) for line in tree_str):
        raise HTTPException(status_code=400, detail="Invalid tree_str format")
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
    if not node_id.isalnum():
        raise HTTPException(status_code=400, detail="Invalid node_id")
    try:
        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()

        cached_data = load_cache(target_dir)
        if not cached_data:
            return JSONResponse(status_code=404, content={"detail": "No graph data available"})

        nodes = cached_data.get('nodes', [])
        links = cached_data.get('links', [])
        node_lookup = {str(n.get('id')): n for n in nodes}

        if node_id in node_lookup:
            node = node_lookup[node_id]
        else:
            node = next((n for n in nodes if n.get('file_path') == node_id), None)

            if not node:
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"Node with ID or path {node_id} not found"}
                )

        node = node_lookup[node_id]
        incoming_links = []
        outgoing_links = []

        def extract_id(item):
            """Extract a string ID from various input types"""
            try:
                if isinstance(item, str):
                    return item
                elif isinstance(item, dict) and 'id' in item:
                    return item['id']
                elif isinstance(item, int) and 0 <= item < len(nodes):
                    return str(nodes[item].get('id'))
                raise ValueError("Invalid link data")
            except Exception:
                return None

        for link in links:
            try:
                source_id = extract_id(link['source'])
                target_id = extract_id(link['target'])
                if source_id == node_id:
                    outgoing_links.append(link)
                if target_id == node_id:
                    incoming_links.append(link)
            except Exception:
                continue

        incoming_links_with_names = [
            {
                "source": {
                    "id": extract_id(link['source']),
                    "name": node_lookup.get(extract_id(link['source']), {}).get('name', 'Unknown'),
                    "type": node_lookup.get(extract_id(link['source']), {}).get('type', 'unknown')
                },
                "target": {
                    "id": extract_id(link['target']),
                    "name": node_lookup.get(extract_id(link['target']), {}).get('name', 'Unknown'),
                    "type": node_lookup.get(extract_id(link['target']), {}).get('type', 'unknown')
                },
                "type": link['type']
            }
            for link in incoming_links if extract_id(link['source']) and extract_id(link['target'])
        ]

        outgoing_links_with_names = [
            {
                "source": {
                    "id": extract_id(link['source']),
                    "name": node_lookup.get(extract_id(link['source']), {}).get('name', 'Unknown'),
                    "type": node_lookup.get(extract_id(link['source']), {}).get('type', 'unknown')
                },
                "target": {
                    "id": extract_id(link['target']),
                    "name": node_lookup.get(extract_id(link['target']), {}).get('name', 'Unknown'),
                    "type": node_lookup.get(extract_id(link['target']), {}).get('type', 'unknown')
                },
                "type": link['type']
            }
            for link in outgoing_links if extract_id(link['source']) and extract_id(link['target'])
        ]

        file_content = None
        if 'file_path' in node:
            try:
                with open(node['file_path'], 'r') as f:
                    file_content = f.read()
            except:
                file_content = None

        return {
            "node": node,
            "connections": {
                "incoming": incoming_links_with_names,
                "outgoing": outgoing_links_with_names
            },
            "file_content": file_content
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error fetching node details: {str(e)}"}
        )
    
@app.get("/reports/{format}")
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

detailed_metrics_router = APIRouter(prefix="/api/detailed-metrics", tags=["detailed_metrics"])

@detailed_metrics_router.get("/", response_model=DetailedAnalysisResponse)
async def get_detailed_metrics(
    directory: str = Query(".", description="Directory to analyze"),
    max_depth: int = Query(1, description="Maximum depth for dependency analysis")
):
    """
    Get comprehensive detailed metrics for the entire codebase.
    Returns raw metrics for all files, functions, classes, and dependencies.
    """
    target_dir = Path(directory).resolve()  
    
    from treeline.dependency_analyzer import ModuleDependencyAnalyzer
    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
    
    dep_analyzer = ModuleDependencyAnalyzer()
    code_analyzer = EnhancedCodeAnalyzer()
    
    dep_analyzer.analyze_directory(target_dir)
    file_results = code_analyzer.analyze_directory(target_dir)
    
    files_data = {}
    issues_summary = defaultdict(int)
    
    for category, issues in code_analyzer.quality_issues.items():
        for issue in issues:
            if isinstance(issue, dict) and 'file_path' in issue:
                file_path = issue['file_path']
                if file_path not in files_data:
                    files_data[file_path] = {
                        "path": file_path,
                        "lines": 0,
                        "functions": [],
                        "classes": [],
                        "imports": [],
                        "issues_by_category": defaultdict(list),
                        "metrics_summary": {}
                    }
                
                files_data[file_path]["issues_by_category"][category].append(issue)
                issues_summary[category] += 1
    
    for result in file_results:
        if result["type"] == "function":
            file_path = result.get("file_path", "unknown")
            if file_path not in files_data:
                files_data[file_path] = {
                    "path": file_path,
                    "lines": 0,
                    "functions": [],
                    "classes": [],
                    "imports": [],
                    "issues_by_category": defaultdict(list),
                    "metrics_summary": {}
                }
            
            function_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "params": result["metrics"].get("params", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "cognitive_complexity": result["metrics"].get("cognitive_complexity", 0),
                "nested_depth": result["metrics"].get("nested_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "maintainability_index": result["metrics"].get("maintainability_index", 0),
                "cognitive_load": result["metrics"].get("cognitive_load", 0),
                "code_smells": result.get("code_smells", [])
            }
            
            files_data[file_path]["functions"].append(function_detail)
            
        elif result["type"] == "class":
            file_path = result.get("file_path", "unknown")
            if file_path not in files_data:
                files_data[file_path] = {
                    "path": file_path,
                    "lines": 0,
                    "functions": [],
                    "classes": [],
                    "imports": [],
                    "issues_by_category": defaultdict(list),
                    "metrics_summary": {}
                }
            
            class_methods = []
            if "methods" in result:
                for method_name, method_info in result["methods"].items():
                    method_detail = {
                        "name": method_name,
                        "line": method_info.get("line", 0),
                        "lines": method_info.get("lines", 0),
                        "params": method_info.get("params", 0),
                        "complexity": method_info.get("complexity", 0),
                        "code_smells": []  
                    }
                    class_methods.append(method_detail)
            
            class_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "method_count": result["metrics"].get("methods", 0),
                "public_methods": result["metrics"].get("public_methods", 0),
                "private_methods": result["metrics"].get("private_methods", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "inheritance_depth": result["metrics"].get("inheritance_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "code_smells": result.get("code_smells", []),
                "methods": class_methods
            }
            
            files_data[file_path]["classes"].append(class_detail)
    
    for file_path in files_data:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                files_data[file_path]["lines"] = len(f.readlines())
        except (UnicodeDecodeError, IOError, FileNotFoundError) as e:
            files_data[file_path]["lines"] = 0
            if "issues_by_category" not in files_data[file_path]:
                files_data[file_path]["issues_by_category"] = {}
            if "file" not in files_data[file_path]["issues_by_category"]:
                files_data[file_path]["issues_by_category"]["file"] = []
            
            files_data[file_path]["issues_by_category"]["file"].append({
                "description": f"Could not read file: {str(e)}",
                "file_path": file_path,
                "line": None
            })
    
    nodes, links = dep_analyzer.get_graph_data()
    
    entry_points = dep_analyzer.get_entry_points()
    core_components = dep_analyzer.get_core_components()
    
    for module, imports in dep_analyzer.module_imports.items():
        for file_path, file_data in files_data.items():
            if module in file_path or os.path.basename(file_path).replace('.py', '') == module:
                file_data["imports"] = list(imports)
    
    total_functions = sum(len(file_data["functions"]) for file_data in files_data.values())
    total_classes = sum(len(file_data["classes"]) for file_data in files_data.values())
    total_lines = sum(file_data["lines"] for file_data in files_data.values())
    
    complexity_values = [func["complexity"] for file_data in files_data.values() 
                         for func in file_data["functions"] if "complexity" in func]
    
    avg_complexity = sum(complexity_values) / len(complexity_values) if complexity_values else 0
    max_complexity = max(complexity_values) if complexity_values else 0
    
    project_metrics = {
        "total_files": len(files_data),
        "total_functions": total_functions,
        "total_classes": total_classes,
        "total_lines": total_lines,
        "avg_complexity": round(avg_complexity, 2),
        "complex_functions_count": len(dep_analyzer.complex_functions),
        "max_complexity": max_complexity
    }
    
    dependency_counts = [len(deps) for deps in dep_analyzer.module_imports.values()]
    avg_dependencies = sum(dependency_counts) / len(dependency_counts) if dependency_counts else 0
    max_dependencies = max(dependency_counts) if dependency_counts else 0
    
    dependency_metrics = {
        "entry_points": entry_points,
        "core_components": core_components,
        "nodes": len(nodes),
        "links": len(links),
        "avg_dependencies": round(avg_dependencies, 2),
        "max_dependencies": max_dependencies
    }
    
    for file_path, file_data in files_data.items():
        if isinstance(file_data["issues_by_category"], defaultdict):
            file_data["issues_by_category"] = dict(file_data["issues_by_category"])
    
    return {
        "files": files_data,
        "project_metrics": project_metrics,
        "dependency_metrics": dependency_metrics,
        "issues_summary": dict(issues_summary)
    }

@detailed_metrics_router.get("/file/{file_path:path}", response_model=FileMetricsDetail)
async def get_file_detailed_metrics(
    file_path: str = FastAPIPath(..., description="File path to analyze")
):
    """
    Get detailed metrics for a specific file.
    """
    target_file = FastAPIPath(file_path).resolve()
    
    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
    
    code_analyzer = EnhancedCodeAnalyzer()
    
    file_results = code_analyzer.analyze_file(target_file)
    
    functions = []
    classes = []
    issues_by_category = defaultdict(list)
    
    file_path_str = str(target_file)
    for category, issues in code_analyzer.quality_issues.items():
        for issue in issues:
            if isinstance(issue, dict) and issue.get('file_path') == file_path_str:
                issues_by_category[category].append(issue)
    
    for result in file_results:
        if result["type"] == "function":
            function_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "params": result["metrics"].get("params", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "cognitive_complexity": result["metrics"].get("cognitive_complexity", 0),
                "nested_depth": result["metrics"].get("nested_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "maintainability_index": result["metrics"].get("maintainability_index", 0),
                "cognitive_load": result["metrics"].get("cognitive_load", 0),
                "code_smells": result.get("code_smells", [])
            }
            functions.append(function_detail)
            
        elif result["type"] == "class":
            class_methods = []
            if "methods" in result:
                for method_name, method_info in result["methods"].items():
                    method_detail = {
                        "name": method_name,
                        "line": method_info.get("line", 0),
                        "lines": method_info.get("lines", 0),
                        "params": method_info.get("params", 0),
                        "complexity": method_info.get("complexity", 0),
                        "code_smells": []
                    }
                    class_methods.append(method_detail)
            
            class_detail = {
                "name": result["name"],
                "line": result["line"],
                "lines": result["metrics"].get("lines", 0),
                "method_count": result["metrics"].get("methods", 0),
                "public_methods": result["metrics"].get("public_methods", 0),
                "private_methods": result["metrics"].get("private_methods", 0),
                "complexity": result["metrics"].get("complexity", 0),
                "inheritance_depth": result["metrics"].get("inheritance_depth", 0),
                "has_docstring": result["docstring"] is not None,
                "docstring_length": len(result["docstring"] or ""),
                "code_smells": result.get("code_smells", []),
                "methods": class_methods
            }
            classes.append(class_detail)
    
    line_count = 0
    imports = []
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
            line_count = len(content)
            
            for line in content:
                if line.strip().startswith(('import ', 'from ')):
                    imports.append(line.strip())
    except Exception as e:
        issues_by_category["file"].append({
            "description": f"Could not read file: {str(e)}",
            "file_path": file_path_str,
            "line": None
        })
    
    metrics_summary = {
        "lines": line_count,
        "functions": len(functions),
        "classes": len(classes),
        "imports": len(imports),
        "issues": sum(len(issues) for issues in issues_by_category.values()),
        "complexity": sum(func["complexity"] for func in functions),
        "avg_function_complexity": sum(func["complexity"] for func in functions) / len(functions) if functions else 0,
    }
    
    return {
        "path": file_path_str,
        "lines": line_count,
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "issues_by_category": dict(issues_by_category),
        "metrics_summary": metrics_summary
    }

@detailed_metrics_router.get("/complexity-breakdown", response_model=Dict[str, Union[ComplexityBreakdown, Dict[str, ComplexityBreakdown]]])
async def get_complexity_breakdown(
    directory: str = Query(".", description="Directory to analyze"),
    by_file: bool = Query(False, description="Break down complexity by file")
):
    """
    Get a detailed breakdown of what contributes to complexity in the codebase.
    """
    target_dir = Path(directory).resolve()
    
    
    import ast
    from collections import Counter
    
    class ComplexityBreakdownAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.breakdown = Counter()
            
        def visit_If(self, node):
            self.breakdown['if_statements'] += 1
            self.generic_visit(node)
            
        def visit_For(self, node):
            self.breakdown['for_loops'] += 1
            self.generic_visit(node)
            
        def visit_While(self, node):
            self.breakdown['while_loops'] += 1
            self.generic_visit(node)
            
        def visit_Try(self, node):
            self.breakdown['try_blocks'] += 1
            self.generic_visit(node)
            
        def visit_ExceptHandler(self, node):
            self.breakdown['except_blocks'] += 1
            self.generic_visit(node)
            
        def visit_BoolOp(self, node):
            if isinstance(node.op, ast.And):
                self.breakdown['and_operations'] += len(node.values) - 1
                self.breakdown['boolean_operations'] += len(node.values) - 1
            elif isinstance(node.op, ast.Or):
                self.breakdown['or_operations'] += len(node.values) - 1
                self.breakdown['boolean_operations'] += len(node.values) - 1
            self.generic_visit(node)
            
        def visit_ListComp(self, node):
            self.breakdown['list_comprehensions'] += 1
            self.breakdown['comprehensions'] += 1
            self.generic_visit(node)
            
        def visit_DictComp(self, node):
            self.breakdown['dict_comprehensions'] += 1
            self.breakdown['comprehensions'] += 1
            self.generic_visit(node)
            
        def visit_SetComp(self, node):
            self.breakdown['set_comprehensions'] += 1
            self.breakdown['comprehensions'] += 1
            self.generic_visit(node)
            
        def visit_GeneratorExp(self, node):
            self.breakdown['generator_expressions'] += 1
            self.generic_visit(node)
            
        def visit_Lambda(self, node):
            self.breakdown['lambda_functions'] += 1
            self.generic_visit(node)
            
        def visit_FunctionDef(self, node):
            parent = getattr(node, 'parent', None)
            if parent and isinstance(parent, ast.FunctionDef):
                self.breakdown['nested_functions'] += 1
            self.generic_visit(node)
            
        def visit_ClassDef(self, node):
            parent = getattr(node, 'parent', None)
            if parent and isinstance(parent, ast.ClassDef):
                self.breakdown['nested_classes'] += 1
            self.generic_visit(node)
    
    total_breakdown = Counter()
    file_breakdowns = {}
    
    for file_path in target_dir.rglob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    child.parent = parent
            
            analyzer = ComplexityBreakdownAnalyzer()
            analyzer.visit(tree)
            
            total_breakdown.update(analyzer.breakdown)
            
            if by_file:
                rel_path = file_path.relative_to(target_dir)
                file_breakdowns[str(rel_path)] = dict(analyzer.breakdown)
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    if by_file:
        return {
            "total": dict(total_breakdown),
            "by_file": file_breakdowns
        }
    
    return {"total": dict(total_breakdown)}

@detailed_metrics_router.get("/dependency-graph")
async def get_detailed_dependency_graph(
    directory: str = Query(".", description="Directory to analyze"),
    include_details: bool = Query(False, description="Include detailed node information")
):
    """
    Get detailed dependency graph including all connections between modules, classes, and functions.
    """
    target_dir = Path(directory).resolve()
    
    from treeline.dependency_analyzer import ModuleDependencyAnalyzer
    
    dep_analyzer = ModuleDependencyAnalyzer()
    
    dep_analyzer.analyze_directory(target_dir)
    
    nodes, links = dep_analyzer.get_graph_data()
    
    if include_details:
        for node in nodes:
            if node["type"] == "module":
                node["metrics"] = dep_analyzer.module_metrics.get(node["name"], {})
                
                node["functions"] = []
                node["classes"] = []
                
                for func_name, location in dep_analyzer.function_locations.items():
                    if isinstance(location, dict) and location.get("module") == node["name"]:
                        node["functions"].append({
                            "name": func_name,
                            "line": location.get("line", 0),
                            "file": location.get("file", "")
                        })
                
                for module_name, classes in dep_analyzer.class_info.items():
                    if module_name == node["name"]:
                        for class_name, info in classes.items():
                            node["classes"].append({
                                "name": class_name,
                                "line": info.get("line", 0),
                                "file": info.get("file", ""),
                                "methods": list(info.get("methods", {}).keys())
                            })
    
    return {
        "nodes": nodes,
        "links": links,
        "entry_points": dep_analyzer.get_entry_points(),
        "core_components": dep_analyzer.get_core_components(),
        # Cycles detection would require additional code
        "cycles": [],
        "module_metrics": dep_analyzer.module_metrics
    }

@detailed_metrics_router.get("/issues-by-category")
async def get_issues_by_category(
    directory: str = Query(".", description="Directory to analyze")
):
    """
    Get all quality issues grouped by category with detailed information.
    """
    target_dir = Path(directory).resolve()
    
    from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
    
    code_analyzer = EnhancedCodeAnalyzer()
    
    code_analyzer.analyze_directory(target_dir)
    
    issues_by_category = {}
    
    for category, issues in code_analyzer.quality_issues.items():
        if issues:
            issues_by_category[category] = issues
    
    file_issues_count = {}
    
    for category, issues in code_analyzer.quality_issues.items():
        for issue in issues:
            if isinstance(issue, dict) and 'file_path' in issue:
                file_path = issue['file_path']
                if file_path not in file_issues_count:
                    file_issues_count[file_path] = defaultdict(int)
                file_issues_count[file_path][category] += 1
    
    files_with_most_issues = sorted(
        [(file_path, sum(counts.values())) for file_path, counts in file_issues_count.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return {
        "issues_by_category": issues_by_category,
        "total_issues": sum(len(issues) for issues in code_analyzer.quality_issues.values()),
        "files_with_most_issues": [
            {"file_path": file_path, "issue_count": count} 
            for file_path, count in files_with_most_issues
        ],
        "category_counts": {
            category: len(issues) for category, issues in code_analyzer.quality_issues.items()
        }
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    error_detail = str(exc)
    # logger.error(f"ERROR: {error_detail}")
    traceback_str = traceback.format_exc()
    # logger.debug(f"Traceback:\n{traceback_str}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

app.include_router(detailed_metrics_router)
