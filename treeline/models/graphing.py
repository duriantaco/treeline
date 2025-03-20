from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class FunctionMetricsDetail(BaseModel):
    name: str
    line: int
    lines: int
    params: int
    returns: Optional[int] = None
    complexity: int
    cognitive_complexity: Optional[int] = None
    nested_depth: Optional[int] = None
    has_docstring: Optional[bool] = None
    docstring_length: Optional[int] = None
    maintainability_index: Optional[float] = None
    cognitive_load: Optional[int] = None
    code_smells: List[Dict[str, Any]] = []

class ClassMetricsDetail(BaseModel):
    name: str
    line: int
    lines: int
    method_count: int
    public_methods: Optional[int] = None
    private_methods: Optional[int] = None
    complexity: Optional[int] = None
    inheritance_depth: Optional[int] = None
    has_docstring: Optional[bool] = None
    docstring_length: Optional[int] = None
    code_smells: List[Dict[str, Any]] = []
    methods: List[FunctionMetricsDetail] = []

class FileMetricsDetail(BaseModel):
    path: str
    lines: int
    functions: List[FunctionMetricsDetail] = []
    classes: List[ClassMetricsDetail] = []
    imports: List[str] = []
    issues_by_category: Dict[str, List[Dict[str, Any]]] = {}
    metrics_summary: Dict[str, Any] = {}

class DetailedAnalysisResponse(BaseModel):
    files: Dict[str, FileMetricsDetail]
    project_metrics: Dict[str, Any]
    dependency_metrics: Dict[str, Any]
    issues_summary: Dict[str, int]

class ComplexityBreakdown(BaseModel):
    if_statements: int = 0
    for_loops: int = 0
    while_loops: int = 0
    except_blocks: int = 0
    try_blocks: int = 0
    boolean_operations: int = 0
    and_operations: int = 0
    or_operations: int = 0
    comprehensions: int = 0
    list_comprehensions: int = 0
    dict_comprehensions: int = 0
    set_comprehensions: int = 0
    generator_expressions: int = 0
    lambda_functions: int = 0
    nested_functions: int = 0
    nested_classes: int = 0

