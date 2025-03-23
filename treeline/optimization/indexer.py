import ast
import json
import mmap
import os
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

import xxhash

@dataclass
class IndexEntry:
    path: str
    line_start: int
    line_end: int
    type: str
    name: str
    hash: str
    dependencies: Set[str]

class FastIndexer:
    def __init__(self, max_workers: int = 8):
        self.index: Dict[str, IndexEntry] = {}
        self.dependency_graph = defaultdict(set)
        self.reverse_index = defaultdict(set)
        self.file_hashes = {}
        self.max_workers = max_workers
        self.index_state_file = "treeline_index_state.json"
        self.last_index_state: Dict[str, str] = {}
        self.mmap_threshold = 10 * 1024 * 1024
        self.batch_size = 1000
        self._load_index_state()

    def _load_index_state(self):
        index_state_path = Path(self.index_state_file)
        if index_state_path.exists():
            try:
                with open(index_state_path, "r", encoding="utf-8") as f:
                    self.last_index_state = json.load(f)
            except json.JSONDecodeError:
                self.last_index_state = {}
            except FileNotFoundError:
                self.last_index_state = {}
            except PermissionError:
                self.last_index_state = {}

    def _save_index_state(self):
        try:
            with open(self.index_state_file, "w", encoding="utf-8") as f:
                json.dump(self.file_hashes, f, indent=2)
        except PermissionError:
            pass
        except IOError:
            pass

    def _process_file(self, file_path: Path) -> Tuple[str, List[IndexEntry]]:
        try:
            file_size = os.path.getsize(file_path)
            file_hash = ""
            
            if file_size > self.mmap_threshold:
                try:
                    with open(file_path, "rb") as f:
                        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                            file_hash = xxhash.xxh64(mm).hexdigest()
                except (OSError, ValueError):
                    with open(file_path, "rb") as f:
                        file_hash = xxhash.xxh64(f.read()).hexdigest()
            else:
                with open(file_path, "rb") as f:
                    file_hash = xxhash.xxh64(f.read()).hexdigest()
            
            path_str = str(file_path)
            old_hash = self.last_index_state.get(path_str, "")
            
            if old_hash == file_hash and old_hash:
                return file_hash, []
                
            entries = []
            try:
                if file_size > self.mmap_threshold:
                    entries = self._parse_large_file(file_path, file_hash)
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)
                    entries = self._parse_ast(tree, file_path, file_hash)
            except SyntaxError:
                pass
            except UnicodeDecodeError:
                try:
                    with open(file_path, "r", encoding="latin-1") as f:
                        content = f.read()
                    tree = ast.parse(content)
                    entries = self._parse_ast(tree, file_path, file_hash)
                except:
                    pass
                    
            return file_hash, entries
        except FileNotFoundError:
            return "", []
        except PermissionError:
            return "", []
        except Exception:
            return "", []

    def _parse_ast(self, tree: ast.AST, file_path: Path, file_hash: str) -> List[IndexEntry]:
        entries = []
        module_deps = set()
        module_entry = None
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    module_deps.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for name in node.names:
                        module_deps.add(f"{node.module}.{name.name}")
        
        if module_deps:
            module_name = Path(file_path).stem
            module_entry = IndexEntry(
                path=str(file_path),
                line_start=1,
                line_end=1,
                type="module",
                name=module_name,
                hash=f"{file_hash}:module",
                dependencies=module_deps
            )
            entries.append(module_entry)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                func_deps = set()
                
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Import):
                        for name in subnode.names:
                            func_deps.add(name.name)
                    elif isinstance(subnode, ast.ImportFrom):
                        if subnode.module:
                            for name in subnode.names:
                                func_deps.add(f"{subnode.module}.{name.name}")
                
                end_lineno = getattr(node, "end_lineno", node.lineno + 1)
                entry = IndexEntry(
                    path=str(file_path),
                    line_start=node.lineno,
                    line_end=end_lineno,
                    type="function" if isinstance(node, ast.FunctionDef) else "class",
                    name=node.name,
                    hash=f"{file_hash}:{node.lineno}-{end_lineno}",
                    dependencies=func_deps
                )
                entries.append(entry)
                
        return entries

    def _parse_large_file(self, file_path: Path, file_hash: str) -> List[IndexEntry]:
        entries = []
        module_deps = set()
        functions = []
        classes = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            line_num = 0
            current_def = None
            current_type = None
            current_start = 0
            
            for line in f:
                line_num += 1
                stripped = line.strip()
                
                if stripped.startswith("import ") or stripped.startswith("from "):
                    if "import " in stripped:
                        parts = stripped.split("import ")
                        if len(parts) > 1:
                            imports = parts[1].split(",")
                            for imp in imports:
                                module_deps.add(imp.strip().split(" as ")[0])
                
                elif stripped.startswith("def "):
                    if current_def:
                        if current_type == "function":
                            functions.append((current_def, current_start, line_num - 1))
                        else:
                            classes.append((current_def, current_start, line_num - 1))
                    
                    current_def = stripped[4:].split("(")[0].strip()
                    current_type = "function"
                    current_start = line_num
                
                elif stripped.startswith("class "):
                    if current_def:
                        if current_type == "function":
                            functions.append((current_def, current_start, line_num - 1))
                        else:
                            classes.append((current_def, current_start, line_num - 1))
                    
                    current_def = stripped[6:].split("(")[0].split(":")[0].strip()
                    current_type = "class"
                    current_start = line_num
        
        if current_def:
            if current_type == "function":
                functions.append((current_def, current_start, line_num))
            else:
                classes.append((current_def, current_start, line_num))
        
        if module_deps:
            module_name = file_path.stem
            entries.append(IndexEntry(
                path=str(file_path),
                line_start=1,
                line_end=1,
                type="module",
                name=module_name,
                hash=f"{file_hash}:module",
                dependencies=module_deps
            ))
        
        for name, start, end in functions:
            entries.append(IndexEntry(
                path=str(file_path),
                line_start=start,
                line_end=end,
                type="function",
                name=name,
                hash=f"{file_hash}:{start}-{end}",
                dependencies=set()
            ))
        
        for name, start, end in classes:
            entries.append(IndexEntry(
                path=str(file_path),
                line_start=start,
                line_end=end,
                type="class",
                name=name,
                hash=f"{file_hash}:{start}-{end}",
                dependencies=set()
            ))
        
        return entries

    def index_codebase(self, root_path: Path):
        python_files = list(root_path.rglob("*.py"))
        if not python_files:
            return

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {executor.submit(self._process_file, path): path for path in python_files}
            
            new_entries = []
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                file_hash, entries = future.result()
                
                if file_hash:
                    self.file_hashes[str(path)] = file_hash
                
                if entries:
                    new_entries.extend(entries)
        
        self._save_index_state()
        
        for i in range(0, len(new_entries), self.batch_size):
            batch = new_entries[i:i+self.batch_size]
            
            for entry in batch:
                self.index[entry.hash] = entry
                
                for dep in entry.dependencies:
                    self.dependency_graph[entry.name].add(dep)
                    self.reverse_index[dep].add(entry.name)

    def get_dependencies(self, name: str, depth: int = -1) -> Set[str]:
        if depth == 0:
            return set()
        
        result = set()
        visited = set()
        queue = deque([(name, 0)])
        
        while queue:
            current, level = queue.popleft()
            
            if current in visited:
                continue
                
            visited.add(current)
            deps = self.dependency_graph[current]
            result.update(deps)
            
            if depth == -1 or level + 1 < depth:
                for dep in deps:
                    queue.append((dep, level + 1))
        
        return result

    def get_dependents(self, name: str, depth: int = -1) -> Set[str]:
        if depth == 0:
            return set()
        
        result = set()
        visited = set()
        queue = deque([(name, 0)])
        
        while queue:
            current, level = queue.popleft()
            
            if current in visited:
                continue
                
            visited.add(current)
            dependents = self.reverse_index[current]
            result.update(dependents)
            
            if depth == -1 or level + 1 < depth:
                for dep in dependents:
                    queue.append((dep, level + 1))
        
        return result

    def get_definitions_for_file(self, file_path: str) -> List[IndexEntry]:
        file_path_str = str(file_path)
        return [entry for entry in self.index.values() if entry.path == file_path_str]