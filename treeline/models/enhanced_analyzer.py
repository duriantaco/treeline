from dataclasses import dataclass
from typing import Optional

from treeline.type_checker import ValidatedModel


@dataclass
class FunctionMetrics(ValidatedModel):
    lines: int
    params: int
    returns: int
    complexity: int
    cognitive_complexity: int
    nested_depth: int
    has_docstring: bool
    maintainability_index: float
    cognitive_load: int
    docstring_length: int


@dataclass
class ClassMetrics(ValidatedModel):
    lines: int
    method_count: int
    complexity: int
    has_docstring: bool
    public_methods: int
    private_methods: int
    inheritance_depth: int
    imports: dict[str, int]
    docstring_length: int


@dataclass
class CodeDuplication(ValidatedModel):
    duplicated_blocks: int
    duplicated_lines: int


@dataclass
class QualityIssue(ValidatedModel):
    description: str
    file_path: Optional[str]
    line: Optional[int]
