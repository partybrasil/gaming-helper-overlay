"""
Configuration Manager
Handles loading, saving and managing application configuration.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal


class ConfigManager(QObject):
    """Manages application configuration using YAML files."""
    
    # Signals
    config_changed = Signal(str, object)  # key, value
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger("ConfigManager")
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_file = self.config_dir / "config.yaml"
        self.plugins_config_dir = self.config_dir / "plugins"
        
        # Ensure config directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.plugins_config_dir.mkdir(exist_ok=True)
        
        # Main configuration data
        self.config = {}
        
        # Default configuration
        self.default_config = {
            "app": {
                "version": "1.0.0",
                "first_run": True,
                "theme": "dark",
                "transparency_enabled": True,
                "always_on_top": False,
                "auto_start": False,
                "minimize_to_tray": True
            },
            "floating_icon": {
                "position": {"x": 100, "y": 100},
                "size": {"width": 50, "height": 50},
                "icon_path": "assets/icons/app_icon.png",
                "opacity": 0.8,
                "always_on_top": True,
                "draggable": True
            },
            "control_panel": {
                "position": {"x": 200, "y": 200},
                "size": {"width": 800, "height": 600},
                "opacity": 0.95,
                "always_on_top": False,
                "remember_position": True,
                "auto_hide": False
            },
            "plugins": {
                "enabled": [],
                "auto_load": True,
                "check_updates": True
            },
            "ui": {
                "glass_effect": True,
                "animations": True,
                "smooth_transitions": True,
                "blur_background": True,
                "custom_borders": True,
                "border_color": "#3498db",
                "border_width": 2
            },
            "performance": {
                "max_threads": 10,
                "fps_limit": 60,
                "low_cpu_mode": False,
                "memory_limit_mb": 500
            },
            "hotkeys": {
                "toggle_control_panel": "Ctrl+Shift+G",
                "toggle_all_panels": "Ctrl+Shift+A",
                "emergency_hide": "Ctrl+Shift+H"
            }
        }
    
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    self.config = yaml.safe_load(file) or {}
                self.logger.info("Configuration loaded successfully")
            else:
                self.config = self.default_config.copy()
                self.save_config()
                self.logger.info("Created default configuration")
            
            # Merge with defaults to ensure all keys exist
            self._merge_with_defaults()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.config = self.default_config.copy()
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        # Emit signal if value changed
        if old_value != value:
            self.config_changed.emit(key, value)
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration for a specific plugin."""
        plugin_config_file = self.plugins_config_dir / f"{plugin_name}.yaml"
        
        if plugin_config_file.exists():
            try:
                with open(plugin_config_file, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file) or {}
            except Exception as e:
                self.logger.error(f"Failed to load plugin config for {plugin_name}: {e}")
        
        return {}
    
    def save_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Save configuration for a specific plugin."""
        plugin_config_file = self.plugins_config_dir / f"{plugin_name}.yaml"
        
        try:
            with open(plugin_config_file, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, indent=2)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save plugin config for {plugin_name}: {e}")
            return False
    
    def _merge_with_defaults(self) -> None:
        """Merge current config with defaults to ensure all keys exist."""
        def merge_dict(default: dict, current: dict) -> dict:
            result = default.copy()
            for key, value in current.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        self.config = merge_dict(self.default_config, self.config)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.default_config.copy()
        self.save_config()
        self.logger.info("Configuration reset to defaults")
    
    def export_config(self, file_path: Path) -> bool:
        """Export configuration to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, file_path: Path) -> bool:
        """Import configuration from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                imported_config = yaml.safe_load(file)
            
            if imported_config:
                self.config = imported_config
                self._merge_with_defaults()
                self.save_config()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            
        return False
