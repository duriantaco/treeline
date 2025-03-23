from collections import defaultdict
from pathlib import Path
from typing import Dict
import ast
from treeline.models.enhanced_analyzer import QualityIssue

class DuplicationDetector:
    def __init__(self, config: Dict = None):
        self.config = config or {"MIN_DUPLICATED_BLOCK_SIZE": 5}

    def analyze_directory(self, directory: Path, quality_issues: defaultdict):

        function_defs = defaultdict(list)
        class_defs = defaultdict(list)

        for file_path in directory.rglob("*.py"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue  

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_code = ast.unparse(node).strip()
                    normalized_code = "\n".join(line.strip() for line in func_code.splitlines())
                    function_defs[normalized_code].append((str(file_path), node.lineno))
                
                elif isinstance(node, ast.ClassDef):
                    class_code = ast.unparse(node).strip()
                    normalized_code = "\n".join(line.strip() for line in class_code.splitlines())
                    class_defs[normalized_code].append((str(file_path), node.lineno))

        for func_code, locations in function_defs.items():
            if len(locations) > 1:  
                description = "Duplicated function found at " + ", ".join(
                    [f"{file}:{line}" for file, line in locations]
                )
                quality_issues["duplication"].append(
                    QualityIssue(
                        description=description,
                        file_path=locations[0][0],
                        line=locations[0][1]
                    ).__dict__
                )

        for class_code, locations in class_defs.items():
            if len(locations) > 1:  
                description = "Duplicated class found at " + ", ".join(
                    [f"{file}:{line}" for file, line in locations]
                )
                quality_issues["duplication"].append(
                    QualityIssue(
                        description=description,
                        file_path=locations[0][0],
                        line=locations[0][1]
                    ).__dict__
                )