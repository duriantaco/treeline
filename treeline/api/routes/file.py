from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import re

files_router = APIRouter(prefix="/api", tags=["files"])

def is_safe_path(base_dir: Path, requested_path: Path) -> bool:
    base_dir = base_dir.resolve()
    requested_path = requested_path.resolve()
    
    try:
        requested_path.relative_to(base_dir)
        return True
    except ValueError:
        return False

@files_router.get("/file-content")
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
        
        func_matches = re.finditer(r'^\s*(?:async\s+)?def\s+(\w+)', content, re.MULTILINE)
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