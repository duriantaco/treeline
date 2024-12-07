from dataclasses import dataclass

from ..type_checker import TypeChecked


@dataclass
class FunctionLocation(TypeChecked):
    module: str
    file: str
    line: int


@dataclass
class FunctionCallInfo(TypeChecked):
    from_module: str
    from_function: str
    line: int


@dataclass
class ClassMethod(TypeChecked):
    line: int
    calls: list[str]


@dataclass
class ClassInfo(TypeChecked):
    module: str
    file: str
    line: int
    methods: dict[str, ClassMethod]


@dataclass
class ModuleMetrics(TypeChecked):
    functions: int
    classes: int
    complexity: int


@dataclass
class ComplexFunction(TypeChecked):
    module: str
    name: str
    complexity: int


@dataclass
class MethodInfo(TypeChecked):
    line: int
    calls: list[str]


@dataclass
class Node(TypeChecked):
    id: int
    name: str
    type: str


@dataclass
class Link(TypeChecked):
    source: int
    target: int
    type: str


@dataclass
class GraphData(TypeChecked):
    nodes: list[Node]
    links: list[Link]
