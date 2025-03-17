import pytest
from treeline.optimization.graph import OptimizedDependencyGraph  

@pytest.fixture
def empty_graph():
    return OptimizedDependencyGraph()

def test_add_edge(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    assert graph.nodes["A"] == 0, "Node 'A' should have index 0"
    assert graph.nodes["B"] == 1, "Node 'B' should have index 1"
    assert graph.reverse_nodes[0] == "A", "Reverse mapping for index 0 should be 'A'"
    assert graph.reverse_nodes[1] == "B", "Reverse mapping for index 1 should be 'B'"
    assert 1 in graph.outgoing_edges[0], "Edge from 'A' to 'B' should exist"

def test_add_same_edge(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("A", "B")  
    assert len(graph.outgoing_edges[0]) == 1, "Duplicate edge should not increase edge count"

def test_add_existing_nodes(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    assert graph.nodes["A"] == 0, "Node 'A' should retain index 0"
    assert graph.nodes["B"] == 1, "Node 'B' should have index 1"
    assert graph.nodes["C"] == 2, "Node 'C' should have index 2"
    assert graph.outgoing_edges[0] == {1, 2}, "Node 'A' should connect to 'B' and 'C'"

def test_connected_components_acyclic(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("C", "D")
    components = graph.get_connected_components()
    assert len(components) == 4, "Each node in an acyclic graph should be its own SCC"
    assert {"A"} in components, "SCC for 'A' should exist"
    assert {"B"} in components, "SCC for 'B' should exist"
    assert {"C"} in components, "SCC for 'C' should exist"
    assert {"D"} in components, "SCC for 'D' should exist"

def test_connected_components_with_cycle(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")
    components = graph.get_connected_components()
    assert len(components) == 1, "Cycle should form one SCC"
    assert components[0] == {"A", "B", "C"}, "SCC should include 'A', 'B', 'C'"

def test_get_dependency_chain(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    chain = graph.get_dependency_chain("A")
    assert chain == {"A": 0, "B": 1, "C": 2}, "Dependency chain should include 'A', 'B', 'C' with correct distances"

def test_get_dependency_chain_unknown_node(empty_graph):
    graph = empty_graph
    chain = graph.get_dependency_chain("X")
    assert chain == {}, "Unknown start node should return empty dict"

def test_get_cycles_with_cycle(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")
    cycles = graph.get_cycles()  
    assert len(cycles) == 1, "One cycle should be detected"
    assert set(cycles[0]) == {"A", "B", "C"}, "Cycle should include 'A', 'B', 'C'"

def test_get_cycles_no_cycle(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    cycles = graph.get_cycles() 
    assert len(cycles) == 0, "No cycles should be detected in acyclic graph"

def test_cache_behavior(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    components1 = graph.get_connected_components()
    components2 = graph.get_connected_components()
    assert components1 is components2, "Second call should return cached result"
    graph.add_edge("B", "C")
    components3 = graph.get_connected_components()
    assert components3 is not components1, "Cache should clear after adding an edge"

def test_node_types(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B", from_type="module", to_type="function")
    assert graph.node_types[0] == "module", "Node 'A' should have type 'module'"
    assert graph.node_types[1] == "function", "Node 'B' should have type 'function'"

def test_node_types_not_overwritten(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B", from_type="module")
    graph.add_edge("A", "C") 
    assert graph.node_types[0] == "module", "Node 'A' type should persist"
    assert 1 not in graph.node_types, "Node 'B' should have no type"
    assert 2 not in graph.node_types, "Node 'C' should have no type"

def test_empty_graph(empty_graph):
    graph = empty_graph
    assert graph.get_connected_components() == [], "Empty graph should have no components"

def test_single_node(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "A")  
    components = graph.get_connected_components()
    assert components == [{"A"}], "Single node with self-loop should be one SCC"

def test_multiple_components(empty_graph):
    graph = empty_graph
    graph.add_edge("A", "B")
    graph.add_edge("C", "D")
    components = graph.get_connected_components()
    assert len(components) == 4, "Four nodes without cycles should form four SCCs"
