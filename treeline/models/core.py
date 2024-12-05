from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

from treeline.type_checker import ValidatedModel


@dataclass
class CodeStructure(ValidatedModel):
    type: str
    name: str
    docstring: Optional[str] = None
    metrics: Optional[Dict[str, Union[int, float]]] = None
    code_smells: Optional[List[str]] = None


@dataclass
class TreeOptions(ValidatedModel):
    directory: Union[str, Path]
    create_md: bool = False
    hide_structure: bool = False
    show_params: bool = True
    show_relationships: bool = False


@dataclass
class ModuleMetrics(ValidatedModel):
    functions: int
    classes: int
    complexity: float
