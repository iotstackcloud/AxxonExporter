"""
Configuration Manager
Handles saving and loading application configuration
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_file: str = "axxon_config.json"):
        """
        Initialize configuration manager

        Args:
            config_file: Name of configuration file
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file

        Returns:
            Configuration dictionary
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der Konfiguration: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration

        Returns:
            Default configuration dictionary
        """
        return {
            'connection': {
                'host': '',
                'port': 8000,
                'username': 'root',
                'password': '',
                'use_https': False
            },
            'export': {
                'include_archive': True,
                'resolution': '1920x1080',
                'default_archive_hours_ago': 24
            },
            'project': {
                'name': '',
                'location': '',
                'technician': '',
                'company': '',
                'logo_path': ''
            }
        }

    def save_config(self) -> bool:
        """
        Save current configuration to file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key_path: Path to value (e.g., 'connection.host')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation

        Args:
            key_path: Path to value (e.g., 'connection.host')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def get_connection_config(self) -> Dict[str, Any]:
        """Get connection configuration"""
        return self.config.get('connection', {})

    def get_export_config(self) -> Dict[str, Any]:
        """Get export configuration"""
        return self.config.get('export', {})

    def get_project_config(self) -> Dict[str, Any]:
        """Get project configuration"""
        return self.config.get('project', {})
