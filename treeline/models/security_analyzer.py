# models/security.py
from dataclasses import dataclass
from typing import Set

from ..type_checker import ValidatedModel


@dataclass
class SecurityPattern(ValidatedModel):
    patterns: Set[str]
    safe_patterns: Set[str] = None
    modules: Set[str] = None
    risky_modules: Set[str] = None
    safe_modules: Set[str] = None


@dataclass
class SecurityIssue(ValidatedModel):
    description: str
    file: str
    line: int


@dataclass
class SecurityPatterns(ValidatedModel):
    sql_injection: SecurityPattern
    command_injection: SecurityPattern
    deserialization: SecurityPattern
    file_operations: SecurityPattern
