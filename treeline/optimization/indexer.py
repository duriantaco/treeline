# flake8: noqa: E203
import ast
import json
import mmap
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

import xxhash


@dataclass
class IndexEntry:
    """Represents a single indexed code element"""

    path: str
    line_start: int
    line_end: int
    type: str  # 'class', 'function', 'import'
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

        self.last_index_state: Dict[str, str] = {}

        self.index_state_file = "treeline_index_state.json"

        self._load_index_state()

    def _load_index_state(self):
        index_state_path = Path(self.index_state_file)
        if index_state_path.exists():
            try:
                with open(index_state_path, "r", encoding="utf-8") as f:
                    self.last_index_state = json.load(f)
            except Exception as e:
                print(f"Could not load index state file: {e}")

    def _save_index_state(self):
        try:
            with open(self.index_state_file, "w", encoding="utf-8") as f:
                json.dump(self.file_hashes, f, indent=2)
        except Exception as e:
            print(f"Could not save index state: {e}")

    def _fast_hash_file(self, file_path: Path) -> str:
        """Use xxhash for extremely fast file hashing"""
        hasher = xxhash.xxh64()

        chunk_size = 2_000_000  # 2 MB at a time
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        return hasher.hexdigest()

    def _parse_file_fast(self, file_path: Path) -> List[IndexEntry]:
        """Full AST parsing for code elements (function/class/import)"""
        entries = []
        try:
            with open(file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    content = mm.read().decode("utf-8")
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            entry = IndexEntry(
                                path=str(file_path),
                                line_start=node.lineno,
                                line_end=node.end_lineno,
                                type=(
                                    "function"
                                    if isinstance(node, ast.FunctionDef)
                                    else "class"
                                ),
                                name=node.name,
                                hash=xxhash.xxh64(
                                    content[node.lineno : node.end_lineno]
                                ).hexdigest(),
                                dependencies=set(),
                            )
                            entries.append(entry)

                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            if entries:
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        entries[-1].dependencies.add(alias.name)
                                else:
                                    module = node.module
                                    for alias in node.names:
                                        full_name = f"{module}.{alias.name}"
                                        entries[-1].dependencies.add(full_name)

        except Exception as e:
            print(f"Error parsing {file_path} in _parse_file_fast: {e}")
            return []

        return entries

    def index_codebase(self, root_path: Path):
        """
        Index entire codebase using parallel processing:
          1) Hash all files in parallel
          2) Parse only those that changed since last run
          3) Build up our dependency graph
        """

        python_files = list(root_path.rglob("*.py"))
        total_files = len(python_files)

        if total_files == 0:
            print("No Python files found to index.")
            return

        print(f"Found {total_files} Python files. Hashing...")

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self._fast_hash_file, path): path
                for path in python_files
            }

            for i, future in enumerate(future_to_path, start=1):
                path = future_to_path[future]
                try:
                    file_hash = future.result()
                    self.file_hashes[str(path)] = file_hash
                except Exception as e:
                    print(f"Error hashing {path}: {e}")

                if i % 100 == 0:
                    print(f" Hashed {i}/{total_files} files...")

        self._save_index_state()

        print("Hashing completed. Checking which files changed...")

        # if hash is the same as the last index run, skip re-parsing
        files_to_parse = []
        for path in python_files:
            path_str = str(path)
            new_hash = self.file_hashes.get(path_str, "")
            old_hash = self.last_index_state.get(path_str, "")

            if old_hash != new_hash:
                # file has changed or wasn't indexed before
                files_to_parse.append(path)

        changed_count = len(files_to_parse)
        print(f"{changed_count} files changed or new since last index; parsing now...")

        if changed_count == 0:
            print("No files changed. Skipping AST parsing.")
            return

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self._parse_file_fast, path): path
                for path in files_to_parse
            }

            for i, future in enumerate(future_to_path, start=1):
                path = future_to_path[future]
                try:
                    entries = future.result()
                    for entry in entries:
                        self.index[entry.hash] = entry

                        # update the dependency graph with new dependencies
                        for dep in entry.dependencies:
                            self.dependency_graph[entry.name].add(dep)
                            self.reverse_index[dep].add(entry.name)

                except Exception as e:
                    print(f"Error parsing {path}: {e}")

                if i % 50 == 0:
                    print(f" Parsed {i}/{changed_count} changed files...")

        self._save_index_state()
        print("Indexing completed.")

    def get_dependencies(self, name: str, depth: int = -1) -> Set[str]:
        """Get all dependencies for a given element, with optional depth limit"""
        if depth == 0:
            return set()
        deps = self.dependency_graph[name]
        if depth == -1:
            for dep in list(deps):
                deps.update(self.get_dependencies(dep))
        else:
            for dep in list(deps):
                deps.update(self.get_dependencies(dep, depth - 1))
        return deps

    def get_dependents(self, name: str, depth: int = -1) -> Set[str]:
        """Get all elements that depend on the given element"""
        if depth == 0:
            return set()
        deps = self.reverse_index[name]
        if depth == -1:
            for dep in list(deps):
                deps.update(self.get_dependents(dep))
        else:
            for dep in list(deps):
                deps.update(self.get_dependents(dep, depth - 1))
        return deps

    def get_definitions_for_file(self, file_path: str) -> List[IndexEntry]:
        """
        Returns a list of IndexEntry objects that belong to the given file path.

        This simulates an LSP call that fetches definitions for an editor.
        """
        results = []
        for entry_hash, entry in self.index.items():
            # compare the entry's path to the requested file_path
            if entry.path == file_path:
                results.append(entry)
        return results
