from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from treeline.type_checker import TypeChecked


@dataclass
class FunctionCall(TypeChecked):
    caller: str
    called: str


@dataclass
class CodeStructure(TypeChecked):
    type: str
    name: str
    docstring: Optional[str] = None
    metrics: Optional[Dict[str, Union[int, float]]] = None
    code_smells: Optional[List[str]] = None


@dataclass
class FunctionNode(TypeChecked):
    name: str
    docstring: Optional[str]
    params: Optional[str] = ""
    relationship: Optional[str] = ""
    type: str = "function"


@dataclass
class ClassNode(TypeChecked):
    name: str
    docstring: Optional[str]
    bases: Optional[List[str]] = None
    relationship: Optional[str] = ""
    type: str = "class"


@dataclass
class AnalyzerConfig(TypeChecked):
    show_params: bool = True
    show_relationships: bool = True
