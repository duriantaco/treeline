from dataclasses import dataclass

from ..type_checker import ValidatedModel


@dataclass
class FunctionLocation(ValidatedModel):
    module: str
    file: str
    line: int


@dataclass
class FunctionCallInfo(ValidatedModel):
    from_module: str
    from_function: str
    line: int


@dataclass
class ClassMethod(ValidatedModel):
    line: int
    calls: list[str]


@dataclass
class ClassInfo(ValidatedModel):
    module: str
    file: str
    line: int
    methods: dict[str, ClassMethod]


@dataclass
class ModuleMetrics(ValidatedModel):
    functions: int
    classes: int
    complexity: int


@dataclass
class ComplexFunction(ValidatedModel):
    module: str
    name: str
    complexity: int


@dataclass
class MethodInfo(ValidatedModel):
    line: int
    calls: list[str]


@dataclass
class Node(ValidatedModel):
    id: int
    name: str
    type: str


@dataclass
class Link(ValidatedModel):
    source: int
    target: int
    type: str


@dataclass
class GraphData(ValidatedModel):
    nodes: list[Node]
    links: list[Link]
