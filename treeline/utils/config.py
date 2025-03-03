import json
from pathlib import Path
from typing import Dict

DEFAULT_CONFIG = {
    "MAX_PARAMS": 5,
    "MAX_CYCLOMATIC_COMPLEXITY": 10,
    "MAX_COGNITIVE_COMPLEXITY": 15,
    "MAX_DUPLICATED_LINES": 5,
    "MAX_LINE_LENGTH": 80,
    "MAX_DOC_LENGTH": 80,
    "MAX_NESTED_DEPTH": 4,
    "MAX_FUNCTION_LINES": 50,
    "MAX_RETURNS": 4,
    "MAX_ARGUMENTS_PER_LINE": 5,
    "MIN_MAINTAINABILITY_INDEX": 20,
    "MAX_FUNC_COGNITIVE_LOAD": 15,
    "MIN_PUBLIC_METHODS": 1,
    "MAX_IMPORT_STATEMENTS": 15,
    "MAX_MODULE_DEPENDENCIES": 10,
    "MAX_INHERITANCE_DEPTH": 3,
    "MAX_DUPLICATED_BLOCKS": 2,
    "MAX_CLASS_LINES": 300,
    "MAX_METHODS_PER_CLASS": 20,
    "MAX_CLASS_COMPLEXITY": 50,
}

def load_config(config_path: Path = Path("config.json")) -> Dict:
    config = DEFAULT_CONFIG.copy()
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            config.update(user_config)
            print(f"Loaded configuration from {config_path}")
        except json.JSONDecodeError:
            print(f"Error: {config_path} contains invalid JSON. Using defaults.")
    else:
        print(f"No config file found at {config_path}, using defaults")
    return config