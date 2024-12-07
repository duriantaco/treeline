# models/security.py
from dataclasses import dataclass
from typing import Optional, Set

from ..type_checker import TypeChecked


@dataclass
class SecurityPattern(TypeChecked):
    patterns: Set[str]
    safe_patterns: Optional[Set[str]] = None
    modules: Optional[Set[str]] = None
    risky_modules: Optional[Set[str]] = None
    safe_modules: Optional[Set[str]] = None


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
