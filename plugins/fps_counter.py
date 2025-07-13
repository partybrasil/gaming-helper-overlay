"""
FPS Counter Plugin
Displays current FPS (frames per second) in a floating panel.
"""

import time
import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QGroupBox, QSpinBox, QComboBox, QCheckBox,
                              QSlider)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor

from core.plugin_manager import BasePlugin
from ui.floating_panel import FloatingPanel


class FPSDisplay(QWidget):
    """Custom FPS display widget."""
    
    def __init__(self, fps_plugin):
        super().__init__()
        
        self.fps_plugin = fps_plugin
        self._setup_ui()
        
        # FPS calculation
        self.frame_times = []
        self.last_frame_time = time.time()
        self.current_fps = 0
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_fps)
        self.update_timer.start(100)  # Update every 100ms
    
    def _setup_ui(self):
        """Setup the FPS display UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # FPS label
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setAlignment(Qt.AlignCenter)
        self._update_fps_label_style()
        layout.addWidget(self.fps_label)
        
        # Statistics
        self.avg_label = QLabel("Avg: --")
        self.min_label = QLabel("Min: --")
        self.max_label = QLabel("Max: --")
        
        for label in [self.avg_label, self.min_label, self.max_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: #bdc3c7;
                    font-size: 12px;
                    padding: 2px;
                }
            """)
            layout.addWidget(label)
    
    def _update_fps_label_style(self):
        """Update FPS label style based on current FPS."""
        config = self.fps_plugin.plugin_config
        font_size = config.get('font_size', 24)
        
        # Color based on FPS thresholds
        if self.current_fps >= 60:
            color = "#27ae60"  # Green
        elif self.current_fps >= 30:
            color = "#f39c12"  # Orange
        else:
            color = "#e74c3c"  # Red
        
        self.fps_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                font-weight: bold;
                padding: 5px;
                background: rgba(0, 0, 0, 50);
                border-radius: 5px;
            }}
        """)
    
    def _update_fps(self):
        """Update FPS calculation and display."""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Add to frame times list
        self.frame_times.append(frame_time)
        
        # Keep only recent frames (for averaging)
        max_samples = self.fps_plugin.plugin_config.get('sample_count', 60)
        if len(self.frame_times) > max_samples:
            self.frame_times.pop(0)
        
        # Calculate FPS
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            if avg_frame_time > 0:
                self.current_fps = 1.0 / avg_frame_time
            else:
                self.current_fps = 0
        
        # Update display
        self._update_display()
    
    def _update_display(self):
        """Update the FPS display."""
        config = self.fps_plugin.plugin_config
        
        # Current FPS
        if config.get('show_decimal', True):
            fps_text = f"FPS: {self.current_fps:.1f}"
        else:
            fps_text = f"FPS: {int(self.current_fps)}"
        
        self.fps_label.setText(fps_text)
        self._update_fps_label_style()
        
        # Statistics
        if len(self.frame_times) > 10:  # Only show stats with enough samples
            fps_values = [1.0/ft for ft in self.frame_times if ft > 0]
            
            if fps_values:
                avg_fps = sum(fps_values) / len(fps_values)
                min_fps = min(fps_values)
                max_fps = max(fps_values)
                
                if config.get('show_stats', True):
                    self.avg_label.setText(f"Avg: {avg_fps:.1f}")
                    self.min_label.setText(f"Min: {min_fps:.1f}")
                    self.max_label.setText(f"Max: {max_fps:.1f}")
                    
                    self.avg_label.show()
                    self.min_label.show()
                    self.max_label.show()
                else:
                    self.avg_label.hide()
                    self.min_label.hide()
                    self.max_label.hide()
        
        # Update panel widget size if needed
        if hasattr(self.fps_plugin, 'panel_widget') and self.fps_plugin.panel_widget:
            self.fps_plugin.panel_widget.adjustSize()


class FPSConfigWidget(QWidget):
    """Configuration widget for FPS counter settings."""
    
    settings_changed = Signal()
    
    def __init__(self, fps_plugin):
        super().__init__()
        
        self.fps_plugin = fps_plugin
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the configuration UI."""
        layout = QVBoxLayout(self)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout(display_group)
        
        # Font size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(12, 72)
        self.font_size_spin.setValue(24)
        self.font_size_spin.valueChanged.connect(self._on_setting_changed)
        font_layout.addWidget(self.font_size_spin)
        font_layout.addStretch()
        display_layout.addLayout(font_layout)
        
        # Show decimal places
        self.show_decimal_cb = QCheckBox("Show decimal places")
        self.show_decimal_cb.setChecked(True)
        self.show_decimal_cb.toggled.connect(self._on_setting_changed)
        display_layout.addWidget(self.show_decimal_cb)
        
        # Show statistics
        self.show_stats_cb = QCheckBox("Show statistics (Avg/Min/Max)")
        self.show_stats_cb.setChecked(True)
        self.show_stats_cb.toggled.connect(self._on_setting_changed)
        display_layout.addWidget(self.show_stats_cb)
        
        layout.addWidget(display_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QVBoxLayout(perf_group)
        
        # Sample count
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Sample Count:"))
        self.sample_count_spin = QSpinBox()
        self.sample_count_spin.setRange(10, 300)
        self.sample_count_spin.setValue(60)
        self.sample_count_spin.valueChanged.connect(self._on_setting_changed)
        sample_layout.addWidget(self.sample_count_spin)
        sample_layout.addStretch()
        perf_layout.addLayout(sample_layout)
        
        # Update interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Update Interval (ms):"))
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(50, 1000)
        self.update_interval_spin.setValue(100)
        self.update_interval_spin.valueChanged.connect(self._on_setting_changed)
        interval_layout.addWidget(self.update_interval_spin)
        interval_layout.addStretch()
        perf_layout.addLayout(interval_layout)
        
        layout.addWidget(perf_group)
        
        # Position settings
        pos_group = QGroupBox("Position Settings")
        pos_layout = QVBoxLayout(pos_group)
        
        # Position preset
        pos_preset_layout = QHBoxLayout()
        pos_preset_layout.addWidget(QLabel("Position Preset:"))
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "Custom", "Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"
        ])
        self.position_combo.currentTextChanged.connect(self._on_position_preset_changed)
        pos_preset_layout.addWidget(self.position_combo)
        pos_preset_layout.addStretch()
        pos_layout.addLayout(pos_preset_layout)
        
        layout.addWidget(pos_group)
        
        layout.addStretch()
    
    def _load_settings(self):
        """Load settings from plugin configuration."""
        config = self.fps_plugin.plugin_config
        
        self.font_size_spin.setValue(config.get('font_size', 24))
        self.show_decimal_cb.setChecked(config.get('show_decimal', True))
        self.show_stats_cb.setChecked(config.get('show_stats', True))
        self.sample_count_spin.setValue(config.get('sample_count', 60))
        self.update_interval_spin.setValue(config.get('update_interval', 100))
        self.position_combo.setCurrentText(config.get('position_preset', 'Custom'))
    
    def _on_setting_changed(self):
        """Handle setting changes."""
        # Update plugin configuration
        config = self.fps_plugin.plugin_config
        config['font_size'] = self.font_size_spin.value()
        config['show_decimal'] = self.show_decimal_cb.isChecked()
        config['show_stats'] = self.show_stats_cb.isChecked()
        config['sample_count'] = self.sample_count_spin.value()
        config['update_interval'] = self.update_interval_spin.value()
        
        # Save and update
        self.fps_plugin.save_config()
        self.fps_plugin.update_display()
        self.settings_changed.emit()
    
    def _on_position_preset_changed(self, preset):
        """Handle position preset changes."""
        if preset == "Custom":
            return
        
        # Apply position preset
        self.fps_plugin.plugin_config['position_preset'] = preset
        self.fps_plugin.save_config()
        self.fps_plugin.apply_position_preset(preset)


class FPSCounterPlugin(BasePlugin):
    """FPS counter plugin."""
    
    name = "FPS Counter"
    description = "Displays current frames per second with statistics"
    version = "1.0.0"
    author = "Party Brasil"
    
    def __init__(self, config_manager, thread_manager):
        super().__init__(config_manager, thread_manager)
        
        # Plugin widgets
        self.fps_display = None
        self.config_widget = None
        
        # Default configuration
        default_config = {
            'font_size': 24,
            'show_decimal': True,
            'show_stats': True,
            'sample_count': 60,
            'update_interval': 100,
            'position_preset': 'Top Right'
        }
        
        # Merge with existing config
        for key, value in default_config.items():
            if key not in self.plugin_config:
                self.plugin_config[key] = value
    
    def initialize(self) -> bool:
        """Initialize the FPS counter plugin."""
        try:
            # Create FPS display
            self.fps_display = FPSDisplay(self)
            
            # Create configuration widget
            self.config_widget = FPSConfigWidget(self)
            
            # Create panel
            self.panel_widget = FloatingPanel(self.config_manager, "FPS Counter")
            self.panel_widget.add_content_widget(self.fps_display)
            
            # Connect signals
            self.panel_widget.close_requested.connect(self.deactivate)
            
            # Apply initial position
            preset = self.plugin_config.get('position_preset', 'Top Right')
            if preset != 'Custom':
                self.apply_position_preset(preset)
            
            return super().initialize()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize FPS counter: {e}")
            return False
    
    def activate(self) -> bool:
        """Activate the FPS counter plugin."""
        try:
            if super().activate():
                # Show panel
                if self.panel_widget:
                    self.panel_widget.show()
                    self.panel_widget.resize(200, 120)
                
                # Start FPS monitoring
                if self.fps_display:
                    interval = self.plugin_config.get('update_interval', 100)
                    self.fps_display.update_timer.start(interval)
                
                return True
            return False
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to activate FPS counter: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the FPS counter plugin."""
        try:
            # Stop FPS monitoring
            if self.fps_display and self.fps_display.update_timer:
                self.fps_display.update_timer.stop()
            
            # Hide panel
            if self.panel_widget:
                self.panel_widget.hide()
            
            return super().deactivate()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to deactivate FPS counter: {e}")
            return False
    
    def update_display(self):
        """Update the FPS display with current settings."""
        if self.fps_display:
            self.fps_display._update_fps_label_style()
            
            # Update timer interval
            interval = self.plugin_config.get('update_interval', 100)
            if self.fps_display.update_timer.isActive():
                self.fps_display.update_timer.stop()
                self.fps_display.update_timer.start(interval)
    
    def apply_position_preset(self, preset):
        """Apply a position preset to the panel."""
        if not self.panel_widget:
            return
        
        # Get screen geometry
        screen = self.panel_widget.screen()
        if not screen:
            return
        
        screen_rect = screen.geometry()
        panel_size = self.panel_widget.size()
        
        # Calculate position based on preset
        margin = 20
        
        if preset == "Top Left":
            x, y = margin, margin
        elif preset == "Top Right":
            x = screen_rect.width() - panel_size.width() - margin
            y = margin
        elif preset == "Bottom Left":
            x = margin
            y = screen_rect.height() - panel_size.height() - margin
        elif preset == "Bottom Right":
            x = screen_rect.width() - panel_size.width() - margin
            y = screen_rect.height() - panel_size.height() - margin
        elif preset == "Center":
            x = (screen_rect.width() - panel_size.width()) // 2
            y = (screen_rect.height() - panel_size.height()) // 2
        else:
            return  # Custom or unknown preset
        
        self.panel_widget.move(x, y)
    
    def get_panel_widget(self):
        """Get the plugin's panel widget."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Get the plugin's configuration widget."""
        return self.config_widget
