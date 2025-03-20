# treeline/api/app.py
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import traceback
from concurrent.futures import ProcessPoolExecutor
import logging
import re
import os
import hashlib

from fastapi import FastAPI, HTTPException, Query, Depends, APIRouter, Path as FastAPIPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.utils.report import ReportGenerator
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
from treeline.api.routes.reports import reports_router
from treeline.api.routes.detailed_metrics import detailed_metrics_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = Path(".treeline_cache")
CACHE_DIR.mkdir(exist_ok=True)
dependency_analyzer = None
code_analyzer = None

def calculate_directory_hash(directory: Path) -> str:
    file_hashes = []
    for file_path in sorted(directory.rglob("*.py")):
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        file_hashes.append(file_hash)
    combined_hash = hashlib.sha256("".join(file_hashes).encode()).hexdigest()
    return combined_hash

def load_cache(dir_path: Path) -> Optional[Dict[str, Any]]:

    cache_file = CACHE_DIR / f"{dir_path.name}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            stored_hash = cache_data.get("directory_hash")
            current_hash = calculate_directory_hash(dir_path)
            if stored_hash == current_hash:
                return cache_data["graph_data"]
            else:
                return None
        except (json.JSONDecodeError, ValidationError):
            return None  
    return None

def save_cache(dir_path: Path, data: Dict[str, Any]) -> None:
    """
    Save the analysis data and directory hash to a cache file.
    
    Args:
        dir_path (Path): The directory being analyzed.
        data (Dict[str, Any]): The analysis data to cache (e.g., graph data).
    """
    cache_file = CACHE_DIR / f"{dir_path.name}.json"
    directory_hash = calculate_directory_hash(dir_path)
    cache_data = {
        "directory_hash": directory_hash,
        "graph_data": data
    }
    with open(cache_file, "w") as f:
        json.dump(cache_data, f)

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

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = static_path / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text())
    else:
        return HTMLResponse("<html><body><h1>Welcome to Treeline</h1><p>Index file not found.</p></body></html>")

def get_dependency_analyzer():
    return ModuleDependencyAnalyzer()

@app.get("/", dependencies=[Depends(get_dependency_analyzer)])
async def get_visualization(analyzer: ModuleDependencyAnalyzer = Depends(get_dependency_analyzer)):
    global dependency_analyzer, code_analyzer

    try:
        try:
            with open(".treeline_dir", "r") as f:
                target_dir = Path(f.read().strip()).resolve()
        except FileNotFoundError:
            target_dir = Path(".").resolve()

        if not dependency_analyzer:
            dependency_analyzer = ModuleDependencyAnalyzer()
        if not code_analyzer:
            code_analyzer = EnhancedCodeAnalyzer()

        cached_data = load_cache(target_dir)
        if cached_data:
            logger.info("Loaded graph data from cache")
            return cached_data
        else:
            python_files = list(target_dir.rglob("*.py"))
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(analyze_file_wrapper, f, code_analyzer) for f in python_files]
                results = [f.result() for f in futures]
            all_results = [item for sublist in results for item in sublist if item is not None]

            dependency_analyzer.analyze_directory(target_dir)
            nodes, links = dependency_analyzer.get_graph_data_with_quality(code_analyzer)
            graph_data = {"nodes": nodes, "links": links}
            save_cache(target_dir, graph_data)
            logger.info("Generated and cached new graph data")

            return graph_data

    except Exception as e:
        logger.error(f"Error in get_visualization: {str(e)}")
        traceback_str = traceback.format_exc()
        logger.debug(f"Traceback:\n{traceback_str}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error generating graph data: {str(e)}"}
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
            from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
            from treeline.dependency_analyzer import ModuleDependencyAnalyzer
            enhanced_analyzer = EnhancedCodeAnalyzer()
            dependency_analyzer = ModuleDependencyAnalyzer()
            
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
        tb = traceback.format_exc()
        logger.error(f"Error in get_graph_data: {str(e)}\nTraceback:\n{tb}")
        raise HTTPException(status_code=500, detail=f"Error generating graph data: {str(e)}")
    
@app.get("/api/file-content")
def get_file_content(path: str = Query(...)):
    try:
        with open(".treeline_dir", "r") as f:
            base_dir = Path(f.read().strip()).resolve()
    except FileNotFoundError:
        base_dir = Path(".").resolve()
    
    provided_path = (base_dir / path).resolve()
    
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
                        break
        
        if not node:
            for n in nodes:
                for prop in ['file_path', 'path', 'filepath', 'id', 'name']:
                    if prop not in n or not isinstance(n[prop], str):
                        continue
                    
                    if n[prop] == search_path:
                        node = n
                        break
                    
                    if n[prop].endswith(search_path):
                        node = n
                        break
                    
                    if search_path in n[prop]:
                        node = n
                        break
                    
                    if Path(n[prop]).name == filename:
                        node = n
                        break
                
                if node:
                    break
        
        if not node:
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
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error fetching node details: {str(e)}"}
        )

def is_safe_path(base_dir: Path, requested_path: Path) -> bool:
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
app.include_router(reports_router)