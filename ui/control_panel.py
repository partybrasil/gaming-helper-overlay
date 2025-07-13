"""
Control Panel
Central control panel for managing plugins, settings, and application state.
"""

import logging
from typing import Dict, Any
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                              QListWidget, QPushButton, QLabel, QFrame,
                              QScrollArea, QGridLayout, QGroupBox, QTextEdit,
                              QProgressBar, QCheckBox, QSpinBox, QComboBox,
                              QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QFont

from ui.floating_panel import FloatingPanel
from ui.log_display import LogDisplay
from core.config_manager import ConfigManager
from core.plugin_manager import PluginManager
from core.thread_manager import ThreadManager
from core.tool_manager import ToolManager
from core.tool_manager import ToolManager


class PluginListItem(QListWidgetItem):
    """Custom list item for plugins."""
    
    def __init__(self, plugin_name: str, plugin_info: Dict[str, Any]):
        super().__init__()
        
        self.plugin_name = plugin_name
        self.plugin_info = plugin_info
        
        # Set display text
        status = "🟢" if plugin_info.get("is_active", False) else "🔴"
        self.setText(f"{status} {plugin_name}")
        
        # Set tooltip
        self.setToolTip(f"Version: {plugin_info.get('version', 'Unknown')}\n"
                       f"Author: {plugin_info.get('author', 'Unknown')}\n"
                       f"Description: {plugin_info.get('description', 'No description')}")


class ToolListItem(QListWidgetItem):
    """Custom list item for tools."""
    
    def __init__(self, tool_name: str, tool_info: Dict[str, Any]):
        super().__init__()
        
        self.tool_name = tool_name
        self.tool_info = tool_info
        
        # Set display text with category emoji
        category_icons = {
            "GPU/Graphics": "🎮",
            "System": "💻", 
            "Network": "🌐",
            "Gaming": "🎯",
            "General": "🔧"
        }
        
        category = tool_info.get("category", "General")
        icon = category_icons.get(category, "🔧")
        admin_marker = " 🛡️" if tool_info.get("requires_admin", False) else ""
        
        self.setText(f"{icon} {tool_name}{admin_marker}")
        
        # Set tooltip
        self.setToolTip(f"File: {tool_info.get('filename', 'Unknown')}\n"
                       f"Version: {tool_info.get('version', 'Unknown')}\n"
                       f"Author: {tool_info.get('author', 'Unknown')}\n"
                       f"Category: {category}\n"
                       f"Requires Admin: {'Yes' if tool_info.get('requires_admin', False) else 'No'}\n"
                       f"Description: {tool_info.get('description', 'No description')}")


class ControlPanel(FloatingPanel):
    """Main control panel for the gaming helper overlay."""
    
    # Signals
    plugin_toggle_requested = Signal(str, bool)  # plugin_name, activate
    settings_changed = Signal(str, object)  # setting_name, value
    
    def __init__(self, config_manager: ConfigManager, plugin_manager: PluginManager, 
                 thread_manager: ThreadManager, parent=None):
        
        self.plugin_manager = plugin_manager
        self.thread_manager = thread_manager
        self.tool_manager = ToolManager()  # Initialize tool manager
        
        # Initialize base floating panel
        super().__init__(config_manager, "Control Panel", parent)
        
        self.logger = logging.getLogger("ControlPanel")
        
        # UI components
        self.tabs = None
        self.plugin_list = None
        self.tool_list = None  # Tool list widget
        self.tool_details = None  # Tool details widget
        self.status_text = None
        self.thread_status_widget = None
        
        # State
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_status)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
        # Setup control panel content
        self._setup_control_panel()
        self._connect_signals()
        
        # Set initial size
        self.resize(900, 700)
    
    def _setup_control_panel(self):
        """Setup the control panel interface."""
        # Create tab widget
        self.tabs = QTabWidget()
        self.add_content_widget(self.tabs)
        
        # Create tabs
        self._create_plugins_tab()
        self._create_tools_tab()  # Add tools tab after plugins
        self._create_settings_tab()
        self._create_threads_tab()
        self._create_logs_tab()
        self._create_about_tab()
    
    def _create_plugins_tab(self):
        """Create the plugins management tab."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left side - Plugin list
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        
        # Plugin list
        plugins_label = QLabel("Available Plugins")
        plugins_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(plugins_label)
        
        self.plugin_list = QListWidget()
        self.plugin_list.itemSelectionChanged.connect(self._on_plugin_selected)
        left_layout.addWidget(self.plugin_list)
        
        # Plugin control buttons
        button_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("Activate")
        self.activate_btn.clicked.connect(self._activate_selected_plugin)
        button_layout.addWidget(self.activate_btn)
        
        self.deactivate_btn = QPushButton("Deactivate")
        self.deactivate_btn.clicked.connect(self._deactivate_selected_plugin)
        button_layout.addWidget(self.deactivate_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_plugins)
        button_layout.addWidget(self.refresh_btn)
        
        left_layout.addLayout(button_layout)
        
        # Right side - Plugin details
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        details_label = QLabel("Plugin Details")
        details_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(details_label)
        
        self.plugin_details = QTextEdit()
        self.plugin_details.setReadOnly(True)
        right_layout.addWidget(self.plugin_details)
        
        # Plugin configuration area
        config_label = QLabel("Plugin Configuration")
        config_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(config_label)
        
        # Scroll area for plugin config widgets
        self.plugin_config_scroll = QScrollArea()
        self.plugin_config_scroll.setWidgetResizable(True)
        self.plugin_config_widget = QWidget()
        self.plugin_config_layout = QVBoxLayout(self.plugin_config_widget)
        self.plugin_config_scroll.setWidget(self.plugin_config_widget)
        right_layout.addWidget(self.plugin_config_scroll)
        
        # Add to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([300, 600])
        
        layout.addWidget(splitter)
        self.tabs.addTab(tab, "Plugins")
        
        # Load plugins
        self._refresh_plugins()
    
    def _create_tools_tab(self):
        """Create the tools management tab."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left side - Tool list
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        
        # Tool list header
        tools_label = QLabel("Available Tools")
        tools_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(tools_label)
        
        # Tool list
        self.tool_list = QListWidget()
        self.tool_list.itemSelectionChanged.connect(self._on_tool_selected)
        left_layout.addWidget(self.tool_list)
        
        # Tool control buttons
        button_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("🚀 Run")
        self.run_btn.setToolTip("Run the selected tool normally")
        self.run_btn.clicked.connect(self._run_selected_tool)
        self.run_btn.setEnabled(False)
        button_layout.addWidget(self.run_btn)
        
        self.run_admin_btn = QPushButton("🛡️ Run as Admin")
        self.run_admin_btn.setToolTip("Run the selected tool with administrator privileges")
        self.run_admin_btn.clicked.connect(self._run_selected_tool_admin)
        self.run_admin_btn.setEnabled(False)
        button_layout.addWidget(self.run_admin_btn)
        
        button_layout2 = QHBoxLayout()
        
        self.run_terminal_btn = QPushButton("🖥️ New Terminal")
        self.run_terminal_btn.setToolTip("Run the selected tool in a new terminal window")
        self.run_terminal_btn.clicked.connect(self._run_selected_tool_terminal)
        self.run_terminal_btn.setEnabled(False)
        button_layout2.addWidget(self.run_terminal_btn)
        
        self.refresh_tools_btn = QPushButton("🔄 Refresh")
        self.refresh_tools_btn.setToolTip("Refresh the tools list")
        self.refresh_tools_btn.clicked.connect(self._refresh_tools)
        button_layout2.addWidget(self.refresh_tools_btn)
        
        left_layout.addLayout(button_layout)
        left_layout.addLayout(button_layout2)
        
        # Right side - Tool details
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        details_label = QLabel("Tool/Script Details")
        details_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(details_label)
        
        # Tool details display
        self.tool_details = QTextEdit()
        self.tool_details.setReadOnly(True)
        self.tool_details.setMaximumHeight(300)
        right_layout.addWidget(self.tool_details)
        
        # Additional info section
        info_label = QLabel("Execution Information")
        info_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(info_label)
        
        # Info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        info_text.setHtml("""
        <p><b>Execution Options:</b></p>
        <ul>
        <li><b>🚀 Run:</b> Execute normally in current process</li>
        <li><b>🛡️ Run as Admin:</b> Execute with administrator privileges (required for some system tools)</li>
        <li><b>🖥️ New Terminal:</b> Execute in a new terminal window for better visibility</li>
        <li><b>🔄 Refresh:</b> Scan tools directory for new scripts</li>
        </ul>
        <p><b>Icons:</b> 🎮 GPU/Graphics, 💻 System, 🌐 Network, 🎯 Gaming, 🔧 General, 🛡️ Requires Admin</p>
        """)
        right_layout.addWidget(info_text)
        
        # Add to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([300, 600])
        
        layout.addWidget(splitter)
        self.tabs.addTab(tab, "🔧 Tools")
        
        # Load tools
        self._refresh_tools()
    
    def _create_settings_tab(self):
        """Create the application settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QGridLayout(general_group)
        
        row = 0
        
        # Theme selection
        general_layout.addWidget(QLabel("Theme:"), row, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        self.theme_combo.setCurrentText(self.config_manager.get("ui.theme", "dark").title())
        self.theme_combo.currentTextChanged.connect(
            lambda text: self._on_theme_changed(text.lower())
        )
        general_layout.addWidget(self.theme_combo, row, 1)
        row += 1
        
        # Auto start
        self.auto_start_cb = QCheckBox("Start with Windows")
        self.auto_start_cb.setChecked(self.config_manager.get("app.auto_start", False))
        self.auto_start_cb.toggled.connect(
            lambda checked: self.config_manager.set("app.auto_start", checked)
        )
        general_layout.addWidget(self.auto_start_cb, row, 0, 1, 2)
        row += 1
        
        # Minimize to tray
        self.minimize_tray_cb = QCheckBox("Minimize to system tray")
        self.minimize_tray_cb.setChecked(self.config_manager.get("app.minimize_to_tray", True))
        self.minimize_tray_cb.toggled.connect(
            lambda checked: self.config_manager.set("app.minimize_to_tray", checked)
        )
        general_layout.addWidget(self.minimize_tray_cb, row, 0, 1, 2)
        row += 1
        
        settings_layout.addWidget(general_group)
        
        # UI settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QGridLayout(ui_group)
        
        row = 0
        
        # Glass effect
        self.glass_effect_cb = QCheckBox("Enable glass effect")
        self.glass_effect_cb.setChecked(self.config_manager.get("ui.glass_effect", True))
        self.glass_effect_cb.toggled.connect(
            lambda checked: self.config_manager.set("ui.glass_effect", checked)
        )
        ui_layout.addWidget(self.glass_effect_cb, row, 0, 1, 2)
        row += 1
        
        # Animations
        self.animations_cb = QCheckBox("Enable animations")
        self.animations_cb.setChecked(self.config_manager.get("ui.animations", True))
        self.animations_cb.toggled.connect(
            lambda checked: self.config_manager.set("ui.animations", checked)
        )
        ui_layout.addWidget(self.animations_cb, row, 0, 1, 2)
        row += 1
        
        # Border width
        ui_layout.addWidget(QLabel("Border width:"), row, 0)
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(0, 10)
        self.border_width_spin.setValue(self.config_manager.get("ui.border_width", 2))
        self.border_width_spin.valueChanged.connect(
            lambda value: self.config_manager.set("ui.border_width", value)
        )
        ui_layout.addWidget(self.border_width_spin, row, 1)
        row += 1
        
        settings_layout.addWidget(ui_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QGridLayout(perf_group)
        
        row = 0
        
        # Max threads
        perf_layout.addWidget(QLabel("Max threads:"), row, 0)
        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 50)
        self.max_threads_spin.setValue(self.config_manager.get("performance.max_threads", 10))
        self.max_threads_spin.valueChanged.connect(
            lambda value: self.config_manager.set("performance.max_threads", value)
        )
        perf_layout.addWidget(self.max_threads_spin, row, 1)
        row += 1
        
        # FPS limit
        perf_layout.addWidget(QLabel("FPS limit:"), row, 0)
        self.fps_limit_spin = QSpinBox()
        self.fps_limit_spin.setRange(30, 144)
        self.fps_limit_spin.setValue(self.config_manager.get("performance.fps_limit", 60))
        self.fps_limit_spin.valueChanged.connect(
            lambda value: self.config_manager.set("performance.fps_limit", value)
        )
        perf_layout.addWidget(self.fps_limit_spin, row, 1)
        row += 1
        
        # Low CPU mode
        self.low_cpu_cb = QCheckBox("Low CPU mode")
        self.low_cpu_cb.setChecked(self.config_manager.get("performance.low_cpu_mode", False))
        self.low_cpu_cb.toggled.connect(
            lambda checked: self.config_manager.set("performance.low_cpu_mode", checked)
        )
        perf_layout.addWidget(self.low_cpu_cb, row, 0, 1, 2)
        row += 1
        
        settings_layout.addWidget(perf_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        settings_layout.addLayout(button_layout)
        
        scroll.setWidget(settings_widget)
        layout.addWidget(scroll)
        self.tabs.addTab(tab, "Settings")
    
    def _create_threads_tab(self):
        """Create the threads monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Thread statistics
        stats_group = QGroupBox("Thread Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.active_threads_label = QLabel("Active threads: 0")
        stats_layout.addWidget(self.active_threads_label, 0, 0)
        
        self.total_started_label = QLabel("Total started: 0")
        stats_layout.addWidget(self.total_started_label, 0, 1)
        
        self.total_completed_label = QLabel("Total completed: 0")
        stats_layout.addWidget(self.total_completed_label, 1, 0)
        
        self.total_failed_label = QLabel("Total failed: 0")
        stats_layout.addWidget(self.total_failed_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # Active threads list
        threads_label = QLabel("Active Threads")
        threads_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(threads_label)
        
        self.thread_list = QListWidget()
        layout.addWidget(self.thread_list)
        
        # Thread control buttons
        thread_button_layout = QHBoxLayout()
        
        kill_thread_btn = QPushButton("Kill Selected Thread")
        kill_thread_btn.clicked.connect(self._kill_selected_thread)
        thread_button_layout.addWidget(kill_thread_btn)
        
        kill_all_btn = QPushButton("Kill All Threads")
        kill_all_btn.clicked.connect(self._kill_all_threads)
        thread_button_layout.addWidget(kill_all_btn)
        
        thread_button_layout.addStretch()
        layout.addLayout(thread_button_layout)
        
        self.tabs.addTab(tab, "Threads")
    
    def _create_logs_tab(self):
        """Create the enhanced logs viewing tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        # Filter controls
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.addWidget(QLabel("Show:"))
        
        self.debug_cb = QCheckBox("Debug")
        self.debug_cb.toggled.connect(lambda checked: self.log_display.set_level_filter('DEBUG', checked))
        filter_layout.addWidget(self.debug_cb)
        
        self.info_cb = QCheckBox("Info")
        self.info_cb.setChecked(True)
        self.info_cb.toggled.connect(lambda checked: self.log_display.set_level_filter('INFO', checked))
        filter_layout.addWidget(self.info_cb)
        
        self.warning_cb = QCheckBox("Warning")
        self.warning_cb.setChecked(True)
        self.warning_cb.toggled.connect(lambda checked: self.log_display.set_level_filter('WARNING', checked))
        filter_layout.addWidget(self.warning_cb)
        
        self.error_cb = QCheckBox("Error")
        self.error_cb.setChecked(True)
        self.error_cb.toggled.connect(lambda checked: self.log_display.set_level_filter('ERROR', checked))
        filter_layout.addWidget(self.error_cb)
        
        filter_layout.addStretch()
        log_controls.addWidget(filter_frame)
        
        # Action buttons
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self._clear_logs)
        log_controls.addWidget(clear_logs_btn)
        
        save_logs_btn = QPushButton("Save Logs")
        save_logs_btn.clicked.connect(self._save_logs)
        log_controls.addWidget(save_logs_btn)
        
        layout.addLayout(log_controls)
        
        # Enhanced log display
        self.log_display = LogDisplay()
        layout.addWidget(self.log_display)
        
        self.tabs.addTab(tab, "📋 Logs")
    
    def _create_about_tab(self):
        """Create the about/help tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # App info
        info_text = """
        <h2>Gaming Helper Overlay</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Author:</b> Party Brasil</p>
        <p><b>Framework:</b> PySide6</p>
        <p><b>Python:</b> 3.10+</p>
        <p><b>Target OS:</b> Windows 11</p>
        
        <h3>Description</h3>
        <p>A modular gaming helper overlay application with floating panels and plugins.
        Each plugin provides specific gaming assistance features in independent, 
        customizable floating panels.</p>
        
        <h3>Features</h3>
        <ul>
        <li>Modular plugin system</li>
        <li>Floating, resizable panels</li>
        <li>Transparency and always-on-top controls</li>
        <li>Multi-threaded background processing</li>
        <li>Customizable assets and themes</li>
        <li>Persistent configuration</li>
        </ul>
        
        <h3>Controls</h3>
        <ul>
        <li><b>Left click + drag:</b> Move panels</li>
        <li><b>Right click:</b> Context menu</li>
        <li><b>Mouse wheel on icon:</b> Adjust opacity</li>
        <li><b>Double-click icon:</b> Quick actions</li>
        </ul>
        """
        
        info_display = QTextEdit()
        info_display.setHtml(info_text)
        info_display.setReadOnly(True)
        layout.addWidget(info_display)
        
        self.tabs.addTab(tab, "About")
    
    def _connect_signals(self):
        """Connect plugin manager signals."""
        self.plugin_manager.plugin_activated.connect(self._on_plugin_activated)
        self.plugin_manager.plugin_deactivated.connect(self._on_plugin_deactivated)
        self.plugin_manager.plugin_error.connect(self._on_plugin_error)
        
        self.thread_manager.threads_changed.connect(self._refresh_thread_status)
    
    def _refresh_plugins(self):
        """Refresh the plugin list."""
        self.plugin_list.clear()
        
        # Discover plugins
        self.plugin_manager.discover_plugins()
        
        # Add available plugins to list
        for plugin_name in self.plugin_manager.get_available_plugins():
            plugin = self.plugin_manager.get_plugin(plugin_name)
            
            if plugin:
                plugin_info = plugin.get_info()
            else:
                # Create dummy info for unloaded plugins
                plugin_class = self.plugin_manager.available_plugins[plugin_name]
                plugin_info = {
                    "name": plugin_class.name,
                    "description": plugin_class.description,
                    "version": plugin_class.version,
                    "author": plugin_class.author,
                    "is_active": False,
                    "is_initialized": False
                }
            
            item = PluginListItem(plugin_name, plugin_info)
            self.plugin_list.addItem(item)
    
    def _on_plugin_selected(self):
        """Handle plugin selection."""
        current_item = self.plugin_list.currentItem()
        
        if not current_item:
            return
        
        plugin_name = current_item.plugin_name
        plugin_info = current_item.plugin_info
        
        # Update plugin details
        details = f"""
        <h3>{plugin_info['name']}</h3>
        <p><b>Version:</b> {plugin_info['version']}</p>
        <p><b>Author:</b> {plugin_info['author']}</p>
        <p><b>Status:</b> {'Active' if plugin_info['is_active'] else 'Inactive'}</p>
        <p><b>Initialized:</b> {'Yes' if plugin_info['is_initialized'] else 'No'}</p>
        
        <h4>Description</h4>
        <p>{plugin_info['description']}</p>
        """
        
        self.plugin_details.setHtml(details)
        
        # Update button states
        is_active = plugin_info['is_active']
        self.activate_btn.setEnabled(not is_active)
        self.deactivate_btn.setEnabled(is_active)
        
        # Load plugin configuration widget
        self._load_plugin_config_widget(plugin_name)
    
    def _load_plugin_config_widget(self, plugin_name: str):
        """Load configuration widget for the selected plugin."""
        # Clear existing config widgets
        for i in reversed(range(self.plugin_config_layout.count())):
            child = self.plugin_config_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get plugin instance
        plugin = self.plugin_manager.get_plugin(plugin_name)
        
        if plugin and hasattr(plugin, 'get_config_widget'):
            config_widget = plugin.get_config_widget()
            if config_widget:
                self.plugin_config_layout.addWidget(config_widget)
        
        # Add stretch to push widgets to top
        self.plugin_config_layout.addStretch()
    
    def _activate_selected_plugin(self):
        """Activate the selected plugin."""
        current_item = self.plugin_list.currentItem()
        if current_item:
            self.plugin_manager.activate_plugin(current_item.plugin_name)
    
    def _deactivate_selected_plugin(self):
        """Deactivate the selected plugin."""
        current_item = self.plugin_list.currentItem()
        if current_item:
            self.plugin_manager.deactivate_plugin(current_item.plugin_name)
    
    def _on_plugin_activated(self, plugin_name: str):
        """Handle plugin activation."""
        self._refresh_plugins()
        self.log_message(f"Plugin activated: {plugin_name}")
    
    def _on_plugin_deactivated(self, plugin_name: str):
        """Handle plugin deactivation."""
        self._refresh_plugins()
        self.log_message(f"Plugin deactivated: {plugin_name}")
    
    def _on_plugin_error(self, plugin_name: str, error: str):
        """Handle plugin errors."""
        self.log_message(f"Plugin error '{plugin_name}': {error}")
    
    def _refresh_thread_status(self):
        """Refresh thread status display."""
        stats = self.thread_manager.get_statistics()
        
        self.active_threads_label.setText(f"Active threads: {stats['active_threads'] + stats['active_tasks']}")
        self.total_started_label.setText(f"Total started: {stats['total_started']}")
        self.total_completed_label.setText(f"Total completed: {stats['total_completed']}")
        self.total_failed_label.setText(f"Total failed: {stats['total_failed']}")
        
        # Update thread list
        self.thread_list.clear()
        thread_status = self.thread_manager.get_all_threads_status()
        
        for name, status in thread_status.items():
            if status:
                status_text = "Running" if status.get('running', False) else "Idle"
                item_text = f"{name} - {status['type']} - {status_text}"
                self.thread_list.addItem(item_text)
    
    def _kill_selected_thread(self):
        """Kill the selected thread."""
        current_item = self.thread_list.currentItem()
        if current_item:
            thread_name = current_item.text().split(" - ")[0]
            self.thread_manager.stop_thread(thread_name)
    
    def _kill_all_threads(self):
        """Kill all threads."""
        # Note: This is dangerous and should be used carefully
        self.thread_manager.shutdown_all_threads()
    
    def _save_settings(self):
        """Save current settings."""
        self.config_manager.save_config()
        self.log_message("Settings saved successfully")
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        self.config_manager.reset_to_defaults()
        self.log_message("Settings reset to defaults")
        
        # Update UI controls
        self._update_settings_ui()
    
    def _update_settings_ui(self):
        """Update settings UI with current values."""
        self.theme_combo.setCurrentText(self.config_manager.get("ui.theme", "dark").title())
        self.auto_start_cb.setChecked(self.config_manager.get("app.auto_start", False))
        self.minimize_tray_cb.setChecked(self.config_manager.get("app.minimize_to_tray", True))
        self.glass_effect_cb.setChecked(self.config_manager.get("ui.glass_effect", True))
        self.animations_cb.setChecked(self.config_manager.get("ui.animations", True))
        self.border_width_spin.setValue(self.config_manager.get("ui.border_width", 2))
        self.max_threads_spin.setValue(self.config_manager.get("performance.max_threads", 10))
        self.fps_limit_spin.setValue(self.config_manager.get("performance.fps_limit", 60))
        self.low_cpu_cb.setChecked(self.config_manager.get("performance.low_cpu_mode", False))
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self.config_manager.set("ui.theme", theme)
        self.log_message(f"Theme changed to: {theme}")
        
        # Apply theme immediately
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: str):
        """Apply the selected theme to the application."""
        # This would apply the theme to all UI components
        # For now, just update the styling
        self._apply_styling()
        
        # Log the theme change
        self.logger.info(f"Applied theme: {theme}")
    
    def _clear_logs(self):
        """Clear the log display."""
        self.log_display.clear()
    
    def _save_logs(self):
        """Save logs to file."""
        # This could open a file dialog to save logs
        self.log_message("Log saving not implemented yet")
    
    def _refresh_status(self):
        """Refresh status information periodically."""
        self._refresh_thread_status()
    
    def _refresh_tools(self):
        """Refresh the tools list."""
        self.tool_list.clear()
        
        # Refresh tool manager
        self.tool_manager.refresh_tools()
        
        # Add tools to list
        tools = self.tool_manager.get_tools()
        for tool_name, tool_info in tools.items():
            tool_data = tool_info.to_dict()
            item = ToolListItem(tool_name, tool_data)
            self.tool_list.addItem(item)
        
        self.logger.info(f"Refreshed tools list: {len(tools)} tools found")
    
    def _on_tool_selected(self):
        """Handle tool selection."""
        current_item = self.tool_list.currentItem()
        
        if not current_item:
            # Disable buttons when no tool selected
            self.run_btn.setEnabled(False)
            self.run_admin_btn.setEnabled(False)
            self.run_terminal_btn.setEnabled(False)
            self.tool_details.clear()
            return
        
        tool_name = current_item.tool_name
        tool_info = current_item.tool_info
        
        # Update tool details
        details = f"""
        <h3>🔧 {tool_info['name']}</h3>
        <p><b>📁 File:</b> {tool_info['filename']}</p>
        <p><b>📂 Path:</b> {tool_info['file_path']}</p>
        <p><b>🏷️ Version:</b> {tool_info['version']}</p>
        <p><b>👤 Author:</b> {tool_info['author']}</p>
        <p><b>📋 Category:</b> {tool_info['category']}</p>
        <p><b>🛡️ Requires Admin:</b> {'Yes' if tool_info['requires_admin'] else 'No'}</p>
        <p><b>🖥️ GUI Application:</b> {'Yes' if tool_info['requires_gui'] else 'No'}</p>
        
        <h4>📝 Description</h4>
        <p>{tool_info['description']}</p>
        """
        
        self.tool_details.setHtml(details)
        
        # Enable buttons
        self.run_btn.setEnabled(True)
        self.run_admin_btn.setEnabled(True)
        self.run_terminal_btn.setEnabled(True)
        
        # Update button text if admin is recommended
        if tool_info['requires_admin']:
            self.run_admin_btn.setText("🛡️ Run as Admin (Recommended)")
        else:
            self.run_admin_btn.setText("🛡️ Run as Admin")
    
    def _run_selected_tool(self):
        """Run the selected tool normally."""
        current_item = self.tool_list.currentItem()
        if current_item:
            tool_name = current_item.tool_name
            self.logger.info(f"Running tool: {tool_name}")
            
            success = self.tool_manager.run_tool(tool_name, as_admin=False, new_terminal=False)
            if success:
                self.log_message(f"✅ Tool '{tool_name}' started successfully")
            else:
                self.log_message(f"❌ Failed to start tool '{tool_name}'")
    
    def _run_selected_tool_admin(self):
        """Run the selected tool as administrator."""
        current_item = self.tool_list.currentItem()
        if current_item:
            tool_name = current_item.tool_name
            self.logger.info(f"Running tool as admin: {tool_name}")
            
            success = self.tool_manager.run_tool(tool_name, as_admin=True, new_terminal=False)
            if success:
                self.log_message(f"🛡️ Tool '{tool_name}' started as administrator")
            else:
                self.log_message(f"❌ Failed to start tool '{tool_name}' as administrator")
    
    def _run_selected_tool_terminal(self):
        """Run the selected tool in a new terminal."""
        current_item = self.tool_list.currentItem()
        if current_item:
            tool_name = current_item.tool_name
            tool_info = current_item.tool_info
            self.logger.info(f"Running tool in new terminal: {tool_name}")
            
            # Use admin if recommended
            as_admin = tool_info.get('requires_admin', False)
            success = self.tool_manager.run_tool(tool_name, as_admin=as_admin, new_terminal=True)
            
            if success:
                admin_text = " (as admin)" if as_admin else ""
                self.log_message(f"🖥️ Tool '{tool_name}' started in new terminal{admin_text}")
            else:
                self.log_message(f"❌ Failed to start tool '{tool_name}' in new terminal")
    
    def log_message(self, message: str):
        """Add a message to the log display."""
        if hasattr(self, 'log_display'):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_display.append(f"[{timestamp}] {message}")
