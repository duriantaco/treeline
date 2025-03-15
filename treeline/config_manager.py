# treeline/config_manager.py
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    """
    Centralized configuration manager for Treeline.
    
    This class provides a single source of truth for all configuration settings.
    It loads defaults, then overrides them with values from a user config file
    if one exists.
    """
    
    DEFAULT_CONFIG = {
        "MAX_CYCLOMATIC_COMPLEXITY": 10,
        "MAX_COGNITIVE_COMPLEXITY": 15,
        
        "MAX_PARAMS": 5,
        "MAX_FUNCTION_LINES": 50,
        "MAX_RETURNS": 4,
        "MAX_NESTED_BLOCKS": 3,
        "MIN_DOCSTRING_LENGTH": 10,
        
        "MAX_CLASS_LINES": 300,
        "MIN_PUBLIC_METHODS": 1,
        "MAX_INHERITANCE_DEPTH": 3,
        "MAX_METHODS_PER_CLASS": 20,
        
        "MAX_FILE_LINES": 1000,
        "MAX_LINE_LENGTH": 100,
        "MAX_DOC_LENGTH": 80,
        "MAX_NESTED_DEPTH": 4,
        
        "MAX_DUPLICATED_LINES": 6,
        
        "MAX_PASSWORD_LENGTH": 8,
        "ENABLE_SECURITY_CHECKS": True,
        
        "MIN_MAINTAINABILITY_INDEX": 65,
        "COGNITIVE_LOAD_THRESHOLD": 25,
    }
    
    _instance = None
    
    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern to ensure only one config manager exists."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the config manager with default and user settings."""
        if self._initialized:
            return
            
        self._config = self.DEFAULT_CONFIG.copy()
        self._config_path = None
        
        if config_path:
            self._config_path = Path(config_path)
        
        elif os.environ.get("TREELINE_CONFIG"):
            self._config_path = Path(os.environ.get("TREELINE_CONFIG"))
        
        else:
            potential_paths = [
                Path(".") / "treeline.json",
                Path(".") / "treeline_config.json",
                Path.home() / ".treeline" / "config.json",
            ]
            
            for path in potential_paths:
                if path.exists():
                    self._config_path = path
                    break
        
        if self._config_path and self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    user_config = json.load(f)
                    
                for key, value in user_config.items():
                    if key in self._config:
                        self._config[key] = value
                    else:
                        print(f"Warning: Unknown configuration key '{key}' in {self._config_path}")
                        
                print(f"Loaded configuration from {self._config_path}")
            except Exception as e:
                print(f"Error loading configuration from {self._config_path}: {e}")
                print("Using default configuration")
        
        self._initialized = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value (runtime only, not persisted)."""
        self._config[key] = value
    
    def as_dict(self) -> Dict[str, Any]:
        """Get a copy of the entire configuration dictionary."""
        return self._config.copy()
    
    def save_user_config(self, path: Optional[str] = None) -> None:
        """Save the current configuration to a user config file."""
        save_path = Path(path) if path else (self._config_path or Path("./treeline.json"))
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, "w") as f:
            json.dump(self._config, f, indent=2)
            
        print(f"Configuration saved to {save_path}")
    
    @classmethod
    def create_default_config(cls, path: str = "./treeline.json") -> None:
        """Create a default configuration file."""
        save_path = Path(path)
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, "w") as f:
            json.dump(cls.DEFAULT_CONFIG, f, indent=2)
            
        print(f"Default configuration saved to {save_path}")


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """Get the singleton ConfigManager instance."""
    return ConfigManager(config_path)