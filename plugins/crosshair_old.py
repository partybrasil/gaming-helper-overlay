"""
Crosshair Plugin
Provides a customizable crosshair overlay for gaming.
"""

import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QSlider, QLabel, QComboBox, QColorDialog, 
                              QSpinBox, QGroupBox, QCheckBox)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

from core.plugin_manager import BasePlugin
from ui.floating_panel import FloatingPanel


class CrosshairWidget(QWidget):
    """Custom widget that draws the crosshair."""
    
    def __init__(self, crosshair_plugin):
        super().__init__()
        
        self.crosshair_plugin = crosshair_plugin
        
        # Set window properties for overlay
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Make it click-through
        
        # Set size and position to cover screen center
        self.resize(200, 200)
        self._center_on_screen()
    
    def _center_on_screen(self):
        """Center the crosshair on the screen."""
        # Get screen geometry
        screen = self.screen()
        if screen:
            screen_rect = screen.geometry()
            # Center on screen
            x = screen_rect.center().x() - self.width() // 2
            y = screen_rect.center().y() - self.height() // 2
            self.move(x, y)
    
    def paintEvent(self, event):
        """Draw the crosshair."""
        if not self.crosshair_plugin.is_active:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get crosshair settings
        settings = self.crosshair_plugin.get_crosshair_settings()
        
        # Set up pen
        color = QColor(settings['color'])
        color.setAlpha(settings['opacity'])
        pen = QPen(color, settings['thickness'])
        painter.setPen(pen)
        
        # Calculate center
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Draw crosshair based on style
        style = settings['style']
        size = settings['size']
        gap = settings['gap']
        
        if style == "Cross":
            self._draw_cross(painter, center_x, center_y, size, gap)
        elif style == "Dot":
            self._draw_dot(painter, center_x, center_y, size)
        elif style == "Circle":
            self._draw_circle(painter, center_x, center_y, size)
        elif style == "Square":
            self._draw_square(painter, center_x, center_y, size)
        elif style == "T-Shape":
            self._draw_t_shape(painter, center_x, center_y, size, gap)
    
    def _draw_cross(self, painter, x, y, size, gap):
        """Draw a cross-style crosshair."""
        # Horizontal line
        painter.drawLine(x - size, y, x - gap, y)
        painter.drawLine(x + gap, y, x + size, y)
        
        # Vertical line
        painter.drawLine(x, y - size, x, y - gap)
        painter.drawLine(x, y + gap, x, y + size)
    
    def _draw_dot(self, painter, x, y, size):
        """Draw a dot-style crosshair."""
        painter.drawEllipse(x - size//2, y - size//2, size, size)
    
    def _draw_circle(self, painter, x, y, size):
        """Draw a circle-style crosshair."""
        painter.drawEllipse(x - size, y - size, size * 2, size * 2)
    
    def _draw_square(self, painter, x, y, size):
        """Draw a square-style crosshair."""
        painter.drawRect(x - size, y - size, size * 2, size * 2)
    
    def _draw_t_shape(self, painter, x, y, size, gap):
        """Draw a T-shape crosshair."""
        # Horizontal line
        painter.drawLine(x - size, y, x + size, y)
        
        # Vertical line (only bottom)
        painter.drawLine(x, y + gap, x, y + size)


class CrosshairConfigWidget(QWidget):
    """Configuration widget for crosshair settings."""
    
    settings_changed = Signal()
    
    def __init__(self, crosshair_plugin):
        super().__init__()
        
        self.crosshair_plugin = crosshair_plugin
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the configuration UI."""
        layout = QVBoxLayout(self)
        
        # Crosshair style
        style_group = QGroupBox("Crosshair Style")
        style_layout = QVBoxLayout(style_group)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Cross", "Dot", "Circle", "Square", "T-Shape"])
        self.style_combo.currentTextChanged.connect(self._on_setting_changed)
        style_layout.addWidget(QLabel("Style:"))
        style_layout.addWidget(self.style_combo)
        
        layout.addWidget(style_group)
        
        # Size and gap
        size_group = QGroupBox("Size Settings")
        size_layout = QVBoxLayout(size_group)
        
        # Size slider
        size_layout.addWidget(QLabel("Size:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(5, 50)
        self.size_slider.setValue(20)
        self.size_slider.valueChanged.connect(self._on_setting_changed)
        self.size_label = QLabel("20")
        
        size_h_layout = QHBoxLayout()
        size_h_layout.addWidget(self.size_slider)
        size_h_layout.addWidget(self.size_label)
        size_layout.addLayout(size_h_layout)
        
        # Gap slider
        size_layout.addWidget(QLabel("Gap:"))
        self.gap_slider = QSlider(Qt.Horizontal)
        self.gap_slider.setRange(0, 20)
        self.gap_slider.setValue(3)
        self.gap_slider.valueChanged.connect(self._on_setting_changed)
        self.gap_label = QLabel("3")
        
        gap_h_layout = QHBoxLayout()
        gap_h_layout.addWidget(self.gap_slider)
        gap_h_layout.addWidget(self.gap_label)
        size_layout.addLayout(gap_h_layout)
        
        layout.addWidget(size_group)
        
        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_group)
        
        # Thickness
        appearance_layout.addWidget(QLabel("Thickness:"))
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 10)
        self.thickness_spin.setValue(2)
        self.thickness_spin.valueChanged.connect(self._on_setting_changed)
        appearance_layout.addWidget(self.thickness_spin)
        
        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_btn = QPushButton("")
        self.color_btn.setFixedSize(30, 30)
        self.color_btn.clicked.connect(self._choose_color)
        self.color_btn.setStyleSheet("background-color: #00FF00;")
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        appearance_layout.addLayout(color_layout)
        
        # Opacity
        appearance_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self._on_setting_changed)
        self.opacity_label = QLabel("100%")
        
        opacity_h_layout = QHBoxLayout()
        opacity_h_layout.addWidget(self.opacity_slider)
        opacity_h_layout.addWidget(self.opacity_label)
        appearance_layout.addLayout(opacity_h_layout)
        
        layout.addWidget(appearance_group)
        
        # Enable/Disable
        self.enable_cb = QCheckBox("Enable Crosshair")
        self.enable_cb.setChecked(True)
        self.enable_cb.toggled.connect(self._on_enable_toggled)
        layout.addWidget(self.enable_cb)
        
        layout.addStretch()
    
    def _load_settings(self):
        """Load settings from plugin configuration."""
        config = self.crosshair_plugin.plugin_config
        
        self.style_combo.setCurrentText(config.get('style', 'Cross'))
        self.size_slider.setValue(config.get('size', 20))
        self.gap_slider.setValue(config.get('gap', 3))
        self.thickness_spin.setValue(config.get('thickness', 2))
        self.opacity_slider.setValue(config.get('opacity', 255))
        self.enable_cb.setChecked(config.get('enabled', True))
        
        # Update color button
        color = config.get('color', '#00FF00')
        self.color_btn.setStyleSheet(f"background-color: {color};")
        
        self._update_labels()
    
    def _update_labels(self):
        """Update value labels."""
        self.size_label.setText(str(self.size_slider.value()))
        self.gap_label.setText(str(self.gap_slider.value()))
        opacity_percent = int((self.opacity_slider.value() / 255.0) * 100)
        self.opacity_label.setText(f"{opacity_percent}%")
    
    def _on_setting_changed(self):
        """Handle setting changes."""
        self._update_labels()
        
        # Update plugin configuration
        config = self.crosshair_plugin.plugin_config
        config['style'] = self.style_combo.currentText()
        config['size'] = self.size_slider.value()
        config['gap'] = self.gap_slider.value()
        config['thickness'] = self.thickness_spin.value()
        config['opacity'] = self.opacity_slider.value()
        
        # Save and update
        self.crosshair_plugin.save_config()
        self.crosshair_plugin.update_crosshair()
        self.settings_changed.emit()
    
    def _choose_color(self):
        """Open color chooser dialog."""
        current_color = QColor(self.crosshair_plugin.plugin_config.get('color', '#00FF00'))
        color = QColorDialog.getColor(current_color, self)
        
        if color.isValid():
            color_hex = color.name()
            self.color_btn.setStyleSheet(f"background-color: {color_hex};")
            self.crosshair_plugin.plugin_config['color'] = color_hex
            self.crosshair_plugin.save_config()
            self.crosshair_plugin.update_crosshair()
    
    def _on_enable_toggled(self, enabled):
        """Handle enable/disable toggle."""
        self.crosshair_plugin.plugin_config['enabled'] = enabled
        self.crosshair_plugin.save_config()
        
        if enabled:
            self.crosshair_plugin.show_crosshair()
        else:
            self.crosshair_plugin.hide_crosshair()


class CrosshairPlugin(BasePlugin):
    """Crosshair overlay plugin."""
    
    name = "Crosshair Overlay"
    description = "Provides a customizable crosshair overlay for gaming"
    version = "1.0.0"
    author = "Party Brasil"
    
    def __init__(self, config_manager, thread_manager):
        super().__init__(config_manager, thread_manager)
        
        # Plugin widgets
        self.crosshair_widget = None
        self.config_widget = None
        
        # Default configuration
        default_config = {
            'enabled': True,
            'style': 'Cross',
            'size': 20,
            'gap': 3,
            'thickness': 2,
            'color': '#00FF00',
            'opacity': 255
        }
        
        # Merge with existing config
        for key, value in default_config.items():
            if key not in self.plugin_config:
                self.plugin_config[key] = value
    
    def initialize(self) -> bool:
        """Initialize the crosshair plugin."""
        try:
            # Create crosshair widget
            self.crosshair_widget = CrosshairWidget(self)
            
            # Create configuration widget
            self.config_widget = CrosshairConfigWidget(self)
            
            # Create panel
            self.panel_widget = FloatingPanel(self.config_manager, "Crosshair Settings")
            self.panel_widget.add_content_widget(self.config_widget)
            
            # Connect signals
            self.panel_widget.close_requested.connect(self.deactivate)
            
            return super().initialize()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize crosshair: {e}")
            return False
    
    def activate(self) -> bool:
        """Activate the crosshair plugin."""
        try:
            if super().activate():
                # Show panel
                if self.panel_widget:
                    self.panel_widget.show()
                
                # Show crosshair if enabled
                if self.plugin_config.get('enabled', True):
                    self.show_crosshair()
                
                return True
            return False
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to activate crosshair: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the crosshair plugin."""
        try:
            # Hide crosshair and panel
            self.hide_crosshair()
            
            if self.panel_widget:
                self.panel_widget.hide()
            
            return super().deactivate()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to deactivate crosshair: {e}")
            return False
    
    def show_crosshair(self):
        """Show the crosshair overlay."""
        if self.crosshair_widget and self.plugin_config.get('enabled', True):
            self.crosshair_widget.show()
            self.crosshair_widget.update()
    
    def hide_crosshair(self):
        """Hide the crosshair overlay."""
        if self.crosshair_widget:
            self.crosshair_widget.hide()
    
    def update_crosshair(self):
        """Update the crosshair appearance."""
        if self.crosshair_widget:
            self.crosshair_widget.update()
    
    def get_crosshair_settings(self) -> dict:
        """Get current crosshair settings."""
        return self.plugin_config.copy()
    
    def get_panel_widget(self):
        """Get the plugin's panel widget."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Get the plugin's configuration widget."""
        return self.config_widget
