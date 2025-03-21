import os
from pathlib import Path
import ast
import logging
import json
from collections import defaultdict, Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("treeline-debug")

def diagnose_line_count_issue(directory_path=".", output_file="treeline_diagnostics.json"):
    """
    Diagnose issues with line count and file association in Treeline analysis.
    """
    target_dir = Path(directory_path).resolve()
    logger.info(f"Analyzing directory: {target_dir}")
    
    all_files = []
    python_files = []
    files_with_errors = []
    files_ignored = []
    total_lines_raw = 0
    
    file_metrics = {}
    entity_metrics = {
        "functions": [],
        "classes": [],
        "files_without_entities": []
    }
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') 
                  and d not in ['venv', '.venv', 'env', '__pycache__', 'node_modules', 'build', 'dist']]
        
        for file in files:
            file_path = Path(os.path.join(root, file))
            rel_path = file_path.relative_to(target_dir)
            all_files.append(str(rel_path))
            
            # Check if Python file
            if file.endswith('.py'):
                python_files.append(str(rel_path))
                
                # Count raw lines
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.readlines()
                        line_count = len(content)
                        total_lines_raw += line_count
                        
                        file_metrics[str(rel_path)] = {
                            "path": str(rel_path),
                            "absolute_path": str(file_path),
                            "lines": line_count,
                            "functions": [],
                            "classes": []
                        }
                        
                        try:
                            tree = ast.parse("".join(content))
                            
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    func_info = {
                                        "name": node.name,
                                        "line": node.lineno,
                                        "file_path": str(rel_path)
                                    }
                                    entity_metrics["functions"].append(func_info)
                                    file_metrics[str(rel_path)]["functions"].append(func_info)
                                    
                                elif isinstance(node, ast.ClassDef):
                                    class_info = {
                                        "name": node.name,
                                        "line": node.lineno,
                                        "file_path": str(rel_path),
                                        "methods": []
                                    }
                                    
                                    for class_node in ast.iter_child_nodes(node):
                                        if isinstance(class_node, ast.FunctionDef):
                                            class_info["methods"].append({
                                                "name": class_node.name,
                                                "line": class_node.lineno
                                            })
                                    
                                    entity_metrics["classes"].append(class_info)
                                    file_metrics[str(rel_path)]["classes"].append(class_info)
                        
                        except SyntaxError as e:
                            logger.warning(f"Syntax error parsing {rel_path}: {e}")
                            files_with_errors.append({
                                "path": str(rel_path),
                                "error": f"Syntax error: {str(e)}"
                            })
                
                except Exception as e:
                    logger.error(f"Error reading file {rel_path}: {str(e)}")
                    files_with_errors.append({
                        "path": str(rel_path),
                        "error": str(e)
                    })
    
    for file_path, metrics in file_metrics.items():
        if not metrics["functions"] and not metrics["classes"]:
            entity_metrics["files_without_entities"].append(file_path)
    
    total_python_files = len(python_files)
    total_entities = len(entity_metrics["functions"]) + len(entity_metrics["classes"])
    
    entities_with_unknown_files = []
    for func in entity_metrics["functions"]:
        if func.get("file_path") == "unknown" or not func.get("file_path"):
            entities_with_unknown_files.append(func)
    
    for cls in entity_metrics["classes"]:
        if cls.get("file_path") == "unknown" or not cls.get("file_path"):
            entities_with_unknown_files.append(cls)
    
    diagnostic_report = {
        "summary": {
            "total_files": len(all_files),
            "total_python_files": total_python_files,
            "total_lines_raw": total_lines_raw,
            "total_functions": len(entity_metrics["functions"]),
            "total_classes": len(entity_metrics["classes"]),
            "files_with_errors": len(files_with_errors),
            "entities_with_unknown_files": len(entities_with_unknown_files)
        },
        "python_files": python_files,
        "file_metrics": file_metrics,
        "entities_with_unknown_files": entities_with_unknown_files,
        "files_with_errors": files_with_errors,
        "files_without_entities": entity_metrics["files_without_entities"]
    }
    
    with open(output_file, 'w') as f:
        json.dump(diagnostic_report, f, indent=2)
    
    logger.info(f"Diagnostic report written to {output_file}")
    
    print("\n=== DIAGNOSTIC SUMMARY ===")
    print(f"Total files: {len(all_files)}")
    print(f"Python files: {total_python_files}")
    print(f"Total raw lines: {total_lines_raw}")
    print(f"Total functions: {len(entity_metrics['functions'])}")
    print(f"Total classes: {len(entity_metrics['classes'])}")
    print(f"Files with errors: {len(files_with_errors)}")
    print(f"Entities with unknown file paths: {len(entities_with_unknown_files)}")
    print(f"Files without any functions/classes: {len(entity_metrics['files_without_entities'])}")
    print("===========================\n")
    
    return diagnostic_report

if __name__ == "__main__":
    diagnose_line_count_issue()