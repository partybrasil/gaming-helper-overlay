"""
Gaming Helper App Core
Central application controller that manages all components.
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QFont

from core.plugin_manager import PluginManager
from core.config_manager import ConfigManager
from core.thread_manager import ThreadManager
from ui.main_window import MainWindow
from ui.control_panel import ControlPanel
from ui.icon_widget import FloatingIcon


class GamingHelperApp(QObject):
    """Main application class that coordinates all components."""
    
    # Signals
    shutdown_requested = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.config_manager = None
        self.plugin_manager = None
        self.thread_manager = None
        
        # UI components
        self.main_window = None
        self.control_panel = None
        self.floating_icon = None
        
        # Application state
        self.is_initialized = False
        self.is_shutting_down = False
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure application logging."""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "gaming_helper.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("GamingHelperApp")
        self.logger.info("Gaming Helper Overlay starting...")
    
    def initialize(self):
        """Initialize all application components."""
        try:
            self.logger.info("Initializing Gaming Helper Overlay...")
            
            # Initialize core managers
            self._init_core_managers()
            
            # Initialize UI components
            self._init_ui_components()
            
            # Connect signals
            self._connect_signals()
            
            # Load and activate plugins
            self._load_plugins()
            
            # Show floating icon
            self.floating_icon.show()
            
            self.is_initialized = True
            self.logger.info("Gaming Helper Overlay initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            raise
    
    def _init_core_managers(self):
        """Initialize core management components."""
        # Config manager
        self.config_manager = ConfigManager()
        self.config_manager.load_config()
        
        # Thread manager
        self.thread_manager = ThreadManager()
        
        # Plugin manager
        self.plugin_manager = PluginManager(
            config_manager=self.config_manager,
            thread_manager=self.thread_manager
        )
    
    def _init_ui_components(self):
        """Initialize UI components."""
        # Main window (hidden by default)
        self.main_window = MainWindow(
            config_manager=self.config_manager,
            plugin_manager=self.plugin_manager
        )
        
        # Control panel
        self.control_panel = ControlPanel(
            config_manager=self.config_manager,
            plugin_manager=self.plugin_manager,
            thread_manager=self.thread_manager
        )
        
        # Floating icon
        self.floating_icon = FloatingIcon(
            config_manager=self.config_manager,
            control_panel=self.control_panel
        )
    
    def _connect_signals(self):
        """Connect signals between components."""
        # Shutdown signal
        self.shutdown_requested.connect(self.shutdown)
        
        # Plugin manager signals
        self.plugin_manager.plugin_activated.connect(self._on_plugin_activated)
        self.plugin_manager.plugin_deactivated.connect(self._on_plugin_deactivated)
        
        # Control panel signals
        self.control_panel.close_requested.connect(self.control_panel.hide)
        
        # Floating icon signals
        self.floating_icon.clicked.connect(self._toggle_control_panel)
    
    def _load_plugins(self):
        """Load and initialize plugins."""
        self.plugin_manager.discover_plugins()
        self.plugin_manager.load_enabled_plugins()
    
    def _on_plugin_activated(self, plugin_name):
        """Handle plugin activation."""
        self.logger.info(f"Plugin activated: {plugin_name}")
    
    def _on_plugin_deactivated(self, plugin_name):
        """Handle plugin deactivation."""
        self.logger.info(f"Plugin deactivated: {plugin_name}")
    
    def _toggle_control_panel(self):
        """Toggle control panel visibility."""
        if self.control_panel.isVisible():
            self.control_panel.hide()
        else:
            self.control_panel.show()
            self.control_panel.raise_()
            self.control_panel.activateWindow()
    
    def shutdown(self):
        """Gracefully shutdown the application."""
        if self.is_shutting_down:
            return
            
        self.is_shutting_down = True
        self.logger.info("Shutting down Gaming Helper Overlay...")
        
        try:
            # Save configuration
            if self.config_manager:
                self.config_manager.save_config()
            
            # Shutdown plugins
            if self.plugin_manager:
                self.plugin_manager.shutdown_all_plugins()
            
            # Shutdown threads
            if self.thread_manager:
                self.thread_manager.shutdown_all_threads()
            
            # Close UI components
            if self.control_panel:
                self.control_panel.close()
            
            if self.floating_icon:
                self.floating_icon.close()
            
            if self.main_window:
                self.main_window.close()
            
            # Quit application
            QApplication.quit()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
