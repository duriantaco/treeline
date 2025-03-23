import pytest
from fastapi.testclient import TestClient
from treeline.api.app import app, CACHE_DIR

dependency_analyzer = None
enhanced_analyzer = None
current_directory = None

@pytest.fixture
def client(tmp_path):
    """Fixture to set up a test client with a temporary directory."""
    target_dir = tmp_path / "test_project"
    target_dir.mkdir()
    (target_dir / "file1.py").write_text("def func1(): pass")
    (target_dir / "file2.py").write_text("class Class1: pass")
    
    with open(".treeline_dir", "w") as f:
        f.write(str(target_dir))
    
    for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()
    
    return TestClient(app)

def test_main_page(client):
    """Test the root endpoint serves JSON with graph data."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)

def test_graph_data(client):
    """Test the graph data endpoint returns valid JSON."""
    response = client.get("/api/graph-data")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)

def test_file_content_valid(client):
    """Test file content endpoint with a valid path."""
    response = client.get("/api/file-content?path=file1.py")
    assert response.status_code == 200
    data = response.json()
    assert data["path"].endswith("file1.py")
    assert data["content"] == "def func1(): pass"
    assert "structure" in data
    assert any(s["name"] == "func1" for s in data["structure"])

def test_file_content_invalid(client):
    """Test file content endpoint with an invalid path."""
    response = client.get("/api/file-content?path=nonexistent.py")
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]

def test_file_content_outside_directory(client):
    """Test file content endpoint with a path outside the base directory."""
    response = client.get("/api/file-content?path=../outside.py")
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_node_by_path_valid(client):
    """Test node-by-path endpoint with a valid file path."""
    response = client.get("/api/node-by-path/file1.py")
    assert response.status_code == 200
    data = response.json()
    assert "node" in data
    assert "connections" in data
    assert "file_content" in data
    assert data["file_content"] == "def func1(): pass"

def test_node_by_path_invalid(client):
    """Test node-by-path endpoint with an invalid file path."""
    response = client.get("/api/node-by-path/nonexistent.py")
    assert response.status_code == 404
    assert "No node found" in response.json()["detail"]

def test_node_by_id(client):
    """Test node-by-id endpoint with a valid node ID from graph data."""
    graph_response = client.get("/api/graph-data")
    assert graph_response.status_code == 200
    graph_data = graph_response.json()
    nodes = graph_data["nodes"]
    if not nodes:
        pytest.skip("No nodes available in graph data")
    
    node_id = nodes[0]["id"]
    response = client.get(f"/api/node/{node_id}")
    assert response.status_code == 200
    data = response.json()
    assert "node" in data
    assert "connections" in data
    assert "incoming" in data["connections"]
    assert "outgoing" in data["connections"]

def test_module_metrics_valid(client):
    """Test module metrics endpoint with a valid module path."""
    response = client.get("/metrics/file1")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "quality" in data

def test_module_metrics_invalid(client):
    """Test module metrics endpoint with an invalid module path."""
    response = client.get("/metrics/nonexistent")
    assert response.status_code == 404
    assert "Module nonexistent not found" in response.json()["detail"]

def test_complexity_report(client):
    """Test complexity report endpoint."""
    response = client.get("/reports/complexity")
    assert response.status_code == 200
    data = response.json()
    assert "hotspots" in data or "message" in data

def test_structure_report(client):
    """Test structure report endpoint with a sample tree_str."""
    client.get("/")
    response = client.get("/reports/structure", params={"tree_str": ["test"]})
    assert response.status_code == 200
    data = response.json()
    assert "structure" in data
    assert "metrics" in data

def test_quality_report(client):
    """Test quality report endpoint."""
    response = client.get("/reports/quality")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "insights" in data

def test_detailed_metrics(client):
    """Test detailed metrics endpoint for the entire codebase."""
    response = client.get("/api/detailed-metrics/")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert "project_metrics" in data
    assert "dependency_metrics" in data
    assert "issues_summary" in data

def test_detailed_metrics_file(client):
    """Test detailed metrics endpoint for a specific file."""
    response = client.get("/api/detailed-metrics/file/file1.py")
    assert response.status_code == 200
    data = response.json()
    assert "path" in data
    assert data["path"].endswith("file1.py")
    assert "lines" in data
    assert "functions" in data
    assert "classes" in data

def test_complexity_breakdown(client):
    """Test complexity breakdown endpoint."""
    response = client.get("/api/detailed-metrics/complexity-breakdown")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "if_statements" in data["total"]

def test_dependency_graph(client):
    """Test dependency graph endpoint."""
    response = client.get("/api/detailed-metrics/dependency-graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert "entry_points" in data
    assert "core_components" in data

def test_issues_by_category(client):
    """Test issues-by-category endpoint."""
    response = client.get("/api/detailed-metrics/issues-by-category")
    assert response.status_code == 200
    data = response.json()
    assert "issues_by_category" in data
    assert "total_issues" in data
    assert "files_with_most_issues" in data