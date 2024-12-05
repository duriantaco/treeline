from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from treeline.type_checker import ValidatedModel


@dataclass
class FunctionCall(ValidatedModel):
    caller: str
    called: str


@dataclass
class CodeStructure(ValidatedModel):
    type: str
    name: str
    docstring: Optional[str] = None
    metrics: Optional[Dict[str, Union[int, float]]] = None
    code_smells: Optional[List[str]] = None


@dataclass
class FunctionNode(ValidatedModel):
    name: str
    docstring: Optional[str]
    params: Optional[str] = ""
    relationship: Optional[str] = ""
    type: str = "function"


@dataclass
class ClassNode(ValidatedModel):
    name: str
    docstring: Optional[str]
    bases: Optional[List[str]] = None
    relationship: Optional[str] = ""
    type: str = "class"


@dataclass
class AnalyzerConfig(ValidatedModel):
    show_params: bool = True
    show_relationships: bool = True
