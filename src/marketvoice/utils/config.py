"""
Configuration loader utility for reading environment variables and YAML settings.
"""

from pathlib import Path
from typing import Any, Dict
import os
import yaml


def get_project_root() -> Path:
    """Return absolute path to the project root directory."""
    # Assuming config.py is located at src/marketvoice/utils/config.py
    return Path(__file__).resolve().parents[3]


def load_yaml_config(relative_path: str) -> Dict[str, Any]:
    """Load a YAML configuration file relative to the project root.

    Args:
        relative_path: Relative path string (e.g., 'config/project_settings.yaml').

    Returns:
        Dictionary containing configuration parameters.
    """
    root = get_project_root()
    config_path = root / relative_path

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_project_settings() -> Dict[str, Any]:
    """Load main project settings from config/project_settings.yaml."""
    return load_yaml_config("config/project_settings.yaml")
