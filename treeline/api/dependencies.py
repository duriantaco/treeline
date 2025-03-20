from pathlib import Path
from typing import Tuple
from concurrent.futures import ProcessPoolExecutor
from treeline.dependency_analyzer import ModuleDependencyAnalyzer
from treeline.enhanced_analyzer import EnhancedCodeAnalyzer

def get_project_path():
    """Returns the project path from .treeline_dir or current directory"""
    try:
        with open(".treeline_dir", "r") as f:
            return Path(f.read().strip()).resolve()
    except FileNotFoundError:
        return Path(".").resolve()
    
def get_analyzers(path: Path = None) -> Tuple[ModuleDependencyAnalyzer, EnhancedCodeAnalyzer]:
    """Returns initialized analyzers for the given path"""
    if path is None:
        path = get_project_path()
        
    dependency_analyzer = ModuleDependencyAnalyzer()
    enhanced_analyzer = EnhancedCodeAnalyzer()
    
    dependency_analyzer.analyze_directory(path)
    python_files = list(path.rglob("*.py"))
    
    def analyze_file_wrapper(file_path, analyzer):
        return analyzer.analyze_file(file_path)
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(analyze_file_wrapper, f, enhanced_analyzer) for f in python_files]
        [f.result() for f in futures]
    
    return dependency_analyzer, enhanced_analyzer