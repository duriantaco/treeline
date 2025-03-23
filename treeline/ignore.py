import os
from pathlib import Path
from typing import List

DEFAULT_IGNORE_PATTERNS = [
    'venv/',
    '.venv/',
    'node_modules/',
    'env/',
    '__pycache__/',
    '.git/',
    '.svn/',
    'build/',
    'dist/',
    '*.pyc',
    '*.pyo',
    '*.log',
    '*.zip',
    '*.tar.gz',
]

def read_ignore_patterns(directory: Path) -> List[str]:
    ignore_patterns = DEFAULT_IGNORE_PATTERNS.copy()
    
    ignore_file = directory / ".treeline-ignore"
    if ignore_file.exists():
        with open(ignore_file, "r") as f:
            user_patterns = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
            ignore_patterns.extend(user_patterns)
    
    return ignore_patterns

def should_ignore(path: Path, ignore_patterns: List[str]) -> bool:
    rel_path = str(path)
    
    for excluded in {'venv/', '.venv/', 'env/', '__pycache__/', '.git/', '.svn/', 'build/', 'dist/', 'node_modules/'}:
        if f'/{excluded}' in rel_path or rel_path.startswith(excluded):
            return True

    for pattern in ignore_patterns:
        if pattern.endswith('/'):
            dir_name = pattern.rstrip('/')
            if f'/{dir_name}/' in rel_path or rel_path.startswith(f"{dir_name}/"):
                return True
        else:
            match_pattern = '**/' + pattern if not pattern.startswith('/') else pattern
            if path.match(match_pattern):
                return True
    
    return False