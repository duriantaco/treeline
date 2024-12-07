# models/security.py
from dataclasses import dataclass
from typing import Set

from ..type_checker import TypeChecked


@dataclass
class SecurityPattern(TypeChecked):
    patterns: Set[str]
    safe_patterns: Set[str] = None
    modules: Set[str] = None
    risky_modules: Set[str] = None
    safe_modules: Set[str] = None


@dataclass
class SecurityIssue(TypeChecked):
    description: str
    file: str
    line: int


@dataclass
class SecurityPatterns(TypeChecked):
    sql_injection: SecurityPattern
    command_injection: SecurityPattern
    deserialization: SecurityPattern
    file_operations: SecurityPattern
