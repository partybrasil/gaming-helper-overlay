"""
Main Window
The main application window (usually hidden, accessible via floating icon).
"""

import logging
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from core.config_manager import ConfigManager
from core.plugin_manager import PluginManager


class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    control_panel_requested = Signal()
    shutdown_requested = Signal()
    
    def __init__(self, config_manager: ConfigManager, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.plugin_manager = plugin_manager
        self.logger = logging.getLogger("MainWindow")
        
        # Setup window
        self._setup_window()
        self._setup_ui()
        self._load_config()
    
    def _setup_window(self):
        """Setup main window properties."""
        self.setWindowTitle("Gaming Helper Overlay")
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Set minimum size
        self.setMinimumSize(400, 300)
    
    def _setup_ui(self):
        """Setup the main window UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Gaming Helper Overlay")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Your gaming companion is running in the background.")
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(desc_label)
        
        # Status info
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #27ae60;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Control panel button
        self.control_panel_btn = QPushButton("Open Control Panel")
        self.control_panel_btn.clicked.connect(self.control_panel_requested.emit)
        self.control_panel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        button_layout.addWidget(self.control_panel_btn)
        
        # Hide to tray button
        self.hide_btn = QPushButton("Hide to Tray")
        self.hide_btn.clicked.connect(self.hide)
        self.hide_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        button_layout.addWidget(self.hide_btn)
        
        # Exit button
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.shutdown_requested.emit)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        button_layout.addWidget(self.exit_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Quick stats
        stats_label = QLabel("Quick Stats")
        stats_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(stats_label)
        
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.active_plugins_label = QLabel("Active plugins: 0")
        self.loaded_plugins_label = QLabel("Loaded plugins: 0")
        self.available_plugins_label = QLabel("Available plugins: 0")
        
        for label in [self.active_plugins_label, self.loaded_plugins_label, self.available_plugins_label]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #34495e;
                    padding: 2px;
                }
            """)
            stats_layout.addWidget(label)
        
        layout.addWidget(self.stats_widget)
        
        # Style the main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def _load_config(self):
        """Load window configuration."""
        # Window position and size
        pos = self.config_manager.get("main_window.position", {"x": 300, "y": 300})
        size = self.config_manager.get("main_window.size", {"width": 500, "height": 400})
        
        self.move(pos["x"], pos["y"])
        self.resize(size["width"], size["height"])
        
        # Window state
        if self.config_manager.get("main_window.maximized", False):
            self.showMaximized()
    
    def _save_config(self):
        """Save window configuration."""
        # Position and size
        pos = self.pos()
        size = self.size()
        
        self.config_manager.set("main_window.position", {"x": pos.x(), "y": pos.y()})
        self.config_manager.set("main_window.size", {"width": size.width(), "height": size.height()})
        self.config_manager.set("main_window.maximized", self.isMaximized())
    
    def update_status(self, status: str):
        """Update the status label."""
        self.status_label.setText(f"Status: {status}")
    
    def update_stats(self):
        """Update plugin statistics."""
        if hasattr(self, 'plugin_manager'):
            active_count = len(self.plugin_manager.get_active_plugins())
            loaded_count = len(self.plugin_manager.get_loaded_plugins())
            available_count = len(self.plugin_manager.get_available_plugins())
            
            self.active_plugins_label.setText(f"Active plugins: {active_count}")
            self.loaded_plugins_label.setText(f"Loaded plugins: {loaded_count}")
            self.available_plugins_label.setText(f"Available plugins: {available_count}")
    
    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        self.update_stats()
    
    def closeEvent(self, event):
        """Handle close event."""
        # Save configuration
        self._save_config()
        
        # Hide instead of closing if minimize to tray is enabled
        if self.config_manager.get("app.minimize_to_tray", True):
            event.ignore()
            self.hide()
        else:
            # Actually close the application
            self.shutdown_requested.emit()
            event.accept()
    
    def changeEvent(self, event):
        """Handle window state changes."""
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            # Handle minimize to tray
            if (self.isMinimized() and 
                self.config_manager.get("app.minimize_to_tray", True)):
                self.hide()
        
        super().changeEvent(event)
