"""
Plugin Manager
Discovers, loads, and manages all plugins.
"""

import importlib
import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Type, Any, Optional
from PySide6.QtCore import QObject, Signal

from core.config_manager import ConfigManager
from core.thread_manager import ThreadManager


class BasePlugin(QObject):
    """Base class for all plugins."""
    
    # Plugin metadata
    name = "Base Plugin"
    description = "Base plugin class"
    version = "1.0.0"
    author = "Unknown"
    
    # Signals
    status_changed = Signal(str)  # status message
    data_updated = Signal(dict)  # plugin data
    error_occurred = Signal(str)  # error message
    
    def __init__(self, config_manager: ConfigManager, thread_manager: ThreadManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.thread_manager = thread_manager
        self.logger = logging.getLogger(f"Plugin.{self.name}")
        
        # Plugin state
        self.is_active = False
        self.is_initialized = False
        self.panel_widget = None
        
        # Plugin configuration - create safe filename
        safe_name = self.name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
        self.plugin_config = self.config_manager.get_plugin_config(safe_name)
    
    def initialize(self) -> bool:
        """Initialize the plugin. Override in subclasses."""
        try:
            self.is_initialized = True
            self.logger.info(f"Plugin '{self.name}' initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin '{self.name}': {e}")
            return False
    
    def activate(self) -> bool:
        """Activate the plugin. Override in subclasses."""
        try:
            if not self.is_initialized:
                if not self.initialize():
                    return False
            
            self.is_active = True
            self.status_changed.emit("activated")
            self.logger.info(f"Plugin '{self.name}' activated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to activate plugin '{self.name}': {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the plugin. Override in subclasses."""
        try:
            self.is_active = False
            
            # Hide panel if it exists
            if self.panel_widget:
                self.panel_widget.hide()
            
            self.status_changed.emit("deactivated")
            self.logger.info(f"Plugin '{self.name}' deactivated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate plugin '{self.name}': {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown the plugin. Override in subclasses."""
        try:
            if self.is_active:
                self.deactivate()
            
            # Close panel widget
            if self.panel_widget:
                self.panel_widget.close()
                self.panel_widget = None
            
            self.is_initialized = False
            self.logger.info(f"Plugin '{self.name}' shut down")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown plugin '{self.name}': {e}")
            return False
    
    def get_panel_widget(self):
        """Get the plugin's panel widget. Override in subclasses."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Get the plugin's configuration widget. Override in subclasses."""
        return None
    
    def save_config(self) -> bool:
        """Save plugin configuration."""
        # Create a safe filename by replacing problematic characters
        safe_name = self.name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
        return self.config_manager.save_plugin_config(
            safe_name,
            self.plugin_config
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "is_active": self.is_active,
            "is_initialized": self.is_initialized
        }


class PluginManager(QObject):
    """Manages all plugins in the application."""
    
    # Signals
    plugin_discovered = Signal(str)  # plugin_name
    plugin_loaded = Signal(str)  # plugin_name
    plugin_activated = Signal(str)  # plugin_name
    plugin_deactivated = Signal(str)  # plugin_name
    plugin_error = Signal(str, str)  # plugin_name, error
    
    def __init__(self, config_manager: ConfigManager, thread_manager: ThreadManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.thread_manager = thread_manager
        self.logger = logging.getLogger("PluginManager")
        
        # Plugin storage
        self.available_plugins: Dict[str, Type[BasePlugin]] = {}
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        
        # Plugin directory
        self.plugins_dir = Path(__file__).parent.parent / "plugins"
    
    def _get_plugin_config_name(self, plugin_name: str) -> str:
        """Convert plugin display name to config name (safe filename)."""
        return plugin_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    def _find_plugin_by_config_name(self, config_name: str) -> str:
        """Find plugin display name by config name."""
        for plugin_name in self.available_plugins.keys():
            if self._get_plugin_config_name(plugin_name) == config_name:
                return plugin_name
        return None
    
    def discover_plugins(self) -> List[str]:
        """Discover all available plugins."""
        discovered = []
        
        try:
            if not self.plugins_dir.exists():
                self.logger.warning("Plugins directory does not exist")
                return discovered
            
            # Scan for Python files in plugins directory
            for plugin_file in self.plugins_dir.glob("*.py"):
                if plugin_file.name.startswith("__"):
                    continue
                
                try:
                    plugin_name = plugin_file.stem
                    
                    # Import the module
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find plugin classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BasePlugin) and 
                            obj != BasePlugin and 
                            hasattr(obj, 'name')):
                            
                            self.available_plugins[obj.name] = obj
                            discovered.append(obj.name)
                            self.plugin_discovered.emit(obj.name)
                            
                            self.logger.info(f"Discovered plugin: {obj.name}")
                
                except Exception as e:
                    self.logger.error(f"Failed to load plugin from {plugin_file}: {e}")
            
            self.logger.info(f"Discovered {len(discovered)} plugins")
            return discovered
            
        except Exception as e:
            self.logger.error(f"Failed to discover plugins: {e}")
            return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin."""
        try:
            if plugin_name in self.loaded_plugins:
                self.logger.warning(f"Plugin '{plugin_name}' already loaded")
                return True
            
            if plugin_name not in self.available_plugins:
                self.logger.error(f"Plugin '{plugin_name}' not available")
                return False
            
            # Create plugin instance
            plugin_class = self.available_plugins[plugin_name]
            plugin_instance = plugin_class(self.config_manager, self.thread_manager)
            
            # Connect signals
            plugin_instance.status_changed.connect(
                lambda status, p=plugin_name: self._on_plugin_status_changed(p, status)
            )
            plugin_instance.error_occurred.connect(
                lambda error, p=plugin_name: self.plugin_error.emit(p, error)
            )
            
            # Store loaded plugin
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_loaded.emit(plugin_name)
            
            self.logger.info(f"[PLUGIN] Loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            self.plugin_error.emit(plugin_name, str(e))
            return False
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a loaded plugin."""
        try:
            if plugin_name not in self.loaded_plugins:
                if not self.load_plugin(plugin_name):
                    return False
            
            plugin = self.loaded_plugins[plugin_name]
            if plugin.activate():
                # Add to enabled plugins list using config name
                config_name = self._get_plugin_config_name(plugin_name)
                enabled_plugins = self.config_manager.get("plugins.enabled", [])
                if config_name not in enabled_plugins:
                    enabled_plugins.append(config_name)
                    self.config_manager.set("plugins.enabled", enabled_plugins)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to activate plugin '{plugin_name}': {e}")
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate a loaded plugin."""
        try:
            if plugin_name not in self.loaded_plugins:
                return False
            
            plugin = self.loaded_plugins[plugin_name]
            if plugin.deactivate():
                # Remove from enabled plugins list using config name
                config_name = self._get_plugin_config_name(plugin_name)
                enabled_plugins = self.config_manager.get("plugins.enabled", [])
                if config_name in enabled_plugins:
                    enabled_plugins.remove(config_name)
                    self.config_manager.set("plugins.enabled", enabled_plugins)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate plugin '{plugin_name}': {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        try:
            if plugin_name not in self.loaded_plugins:
                return True
            
            plugin = self.loaded_plugins[plugin_name]
            
            # Shutdown and remove
            plugin.shutdown()
            del self.loaded_plugins[plugin_name]
            
            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin '{plugin_name}': {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin instance."""
        return self.loaded_plugins.get(plugin_name)
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin names."""
        return list(self.available_plugins.keys())
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names."""
        return list(self.loaded_plugins.keys())
    
    def get_active_plugins(self) -> List[str]:
        """Get list of active plugin names."""
        return [name for name, plugin in self.loaded_plugins.items() if plugin.is_active]
    
    def load_enabled_plugins(self) -> None:
        """Load all available plugins but keep them INACTIVE by default."""
        self.logger.info("[PLUGINS] Loading available plugins (all will start INACTIVE)")
        
        # Load all available plugins but don't activate them
        for plugin_name in self.available_plugins.keys():
            if plugin_name not in self.loaded_plugins:
                self.load_plugin(plugin_name)
                self.logger.info(f"[PLUGIN] Loaded plugin '{plugin_name}' (INACTIVE by default)")
        
        # Ensure all plugins start in INACTIVE state - clear any previous enabled state
        self.config_manager.set("plugins.enabled", [])
        self.logger.info("[BLOCKED] All plugins loaded in INACTIVE state - no auto-activation")
    
    def shutdown_all_plugins(self) -> None:
        """Shutdown all loaded plugins."""
        self.logger.info("[PLUGIN] Shutting down all plugins...")
        
        for plugin_name in list(self.loaded_plugins.keys()):
            self.logger.info(f"[PLUGIN] Unloading plugin: {plugin_name}")
            self.unload_plugin(plugin_name)
        
        self.logger.info("[SUCCESS] All plugins shut down")
    
    def _on_plugin_status_changed(self, plugin_name: str, status: str):
        """Handle plugin status changes."""
        if status == "activated":
            self.plugin_activated.emit(plugin_name)
        elif status == "deactivated":
            self.plugin_deactivated.emit(plugin_name)
