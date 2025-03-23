from collections import defaultdict
from typing import Dict, List, Set
from collections import deque

class OptimizedDependencyGraph:
    """High-performance graph structure for code dependencies"""

    def __init__(self):
        self.nodes: Dict[str, int] = {} 
        self.reverse_nodes: Dict[int, str] = {} 
        self.node_types: Dict[int, str] = {}  
        self._next_index: int = 0
        self.outgoing_edges: Dict[int, Set[int]] = defaultdict(set)
        self._cache = {}

    def _get_node_index(self, name: str, node_type: str = None) -> int:
        if name not in self.nodes:
            self.nodes[name] = self._next_index
            self.reverse_nodes[self._next_index] = name
            if node_type:
                self.node_types[self._next_index] = node_type
            self._next_index += 1
        return self.nodes[name]

    def add_edge(
        self, from_node: str, to_node: str, from_type: str = None, to_type: str = None
    ):
        """Add a directed edge between nodes"""
        from_idx = self._get_node_index(from_node, from_type)
        to_idx = self._get_node_index(to_node, to_type)

        self.outgoing_edges[from_idx].add(to_idx)

        self._cache.clear()

    def get_connected_components(self) -> List[Set[str]]:
        """Get strongly connected components using efficient algorithms"""
        cache_key = "connected_components"
        if cache_key not in self._cache:
            components = self._strongly_connected_components()

            self._cache[cache_key] = components

        return self._cache[cache_key]

    def get_dependency_chain(self, start_node: str, max_depth: int = -1) -> Dict[str, int]:
        """Get all dependencies and their distances from start node"""
        if start_node not in self.nodes:
            return {}
        start_idx = self.nodes[start_node]
        queue = deque([(start_idx, 0)])
        visited = set([start_idx])
        chain = {}
        while queue:
            node_idx, depth = queue.popleft()
            if max_depth != -1 and depth > max_depth:
                continue
            node_name = self.reverse_nodes[node_idx]
            chain[node_name] = depth
            for neighbor in self.outgoing_edges[node_idx]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        return chain

    def _strongly_connected_components(self) -> List[Set[str]]:
        index_counter = 0
        stack = []
        on_stack = set()
        index_map = {}
        lowlink = {}
        sccs = []

        def strongconnect(v):
            nonlocal index_counter
            index_map[v] = index_counter
            lowlink[v] = index_counter
            index_counter += 1
            stack.append(v)
            on_stack.add(v)

            for w in self.outgoing_edges[v]:
                if w not in index_map:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], index_map[w])

            if lowlink[v] == index_map[v]:
                comp = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    comp.add(self.reverse_nodes[w])
                    if w == v:
                        break
                sccs.append(comp)

        for node_idx in range(self._next_index):
            if node_idx not in index_map:
                strongconnect(node_idx)

        return sccs

    def get_cycles(self) -> List[List[str]]:
        """Detect dependency cycles efficiently"""
        cache_key = "cycles"
        if cache_key in self._cache:
            return self._cache[cache_key]

        cycles = []
        visited = set()
        path = []
        path_set = set()

        def dfs(node_idx):
            if node_idx in path_set:
                cycle_start = path.index(node_idx)
                cycle = path[cycle_start:]
                cycles.append([self.reverse_nodes[i] for i in cycle])
                return

            if node_idx in visited:
                return

            visited.add(node_idx)
            path.append(node_idx)
            path_set.add(node_idx)

            for neighbor in self.outgoing_edges[node_idx]:
                dfs(neighbor)

            path.pop()
            path_set.remove(node_idx)

        for node_idx in range(self._next_index):
            if node_idx not in visited:
                dfs(node_idx)

        self._cache[cache_key] = cycles
        return cycles
