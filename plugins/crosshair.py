"""
Crosshair Plugin
Provides a customizable crosshair overlay for gaming with advanced configuration.
"""
import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QSlider, QLabel, QComboBox, QColorDialog, 
                              QSpinBox, QGroupBox, QCheckBox, QDoubleSpinBox,
                              QTabWidget, QFormLayout, QFrame)
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QCursor

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
        
        # Mouse tracking timer for follow mouse mode
        self.mouse_timer = QTimer()
        self.mouse_timer.timeout.connect(self._update_mouse_position)
        self.mouse_timer.setInterval(16)  # ~60 FPS for smooth following
    
    def _center_on_screen(self):
        """Center the crosshair on the screen."""
        # Get screen geometry
        screen = self.screen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def _update_mouse_position(self):
        """Update crosshair position to follow mouse cursor."""
        if self.crosshair_plugin.plugin_config.get('follow_mouse', False):
            cursor_pos = QCursor.pos()
            # Center the crosshair widget on cursor position
            x = cursor_pos.x() - self.width() // 2
            y = cursor_pos.y() - self.height() // 2
            self.move(x, y)
    
    def show_crosshair(self):
        """Show the crosshair and start mouse tracking if needed."""
        self.show()
        if self.crosshair_plugin.plugin_config.get('follow_mouse', False):
            self.mouse_timer.start()
        else:
            self.mouse_timer.stop()
            self._center_on_screen()
    
    def hide_crosshair(self):
        """Hide the crosshair and stop mouse tracking."""
        self.hide()
        self.mouse_timer.stop()
    
    def update_tracking_mode(self):
        """Update tracking mode based on settings."""
        if self.isVisible():
            if self.crosshair_plugin.plugin_config.get('follow_mouse', False):
                self.mouse_timer.start()
            else:
                self.mouse_timer.stop()
                self._center_on_screen()
    
    def paintEvent(self, event):
        """Draw the crosshair."""
        if not self.crosshair_plugin.plugin_config.get('enabled', False):
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
        elif style == "Custom Cross":
            self._draw_custom_cross(painter, center_x, center_y, settings)
        elif style == "Mini Dot":
            self._draw_mini_dot(painter, center_x, center_y, settings)
    
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
    
    def _draw_custom_cross(self, painter, x, y, settings):
        """Draw a custom cross with advanced settings."""
        size = settings['size']
        gap = settings['gap']
        
        # Top line
        if settings.get('show_top', True):
            top_length = settings.get('top_length', size)
            painter.drawLine(x, y - gap, x, y - gap - top_length)
        
        # Bottom line
        if settings.get('show_bottom', True):
            bottom_length = settings.get('bottom_length', size)
            painter.drawLine(x, y + gap, x, y + gap + bottom_length)
        
        # Left line
        if settings.get('show_left', True):
            left_length = settings.get('left_length', size)
            painter.drawLine(x - gap, y, x - gap - left_length, y)
        
        # Right line
        if settings.get('show_right', True):
            right_length = settings.get('right_length', size)
            painter.drawLine(x + gap, y, x + gap + right_length, y)
    
    def _draw_mini_dot(self, painter, x, y, settings):
        """Draw a very small precision dot."""
        size = settings.get('mini_size', 0.5)  # Support decimal sizes
        painter.drawEllipse(int(x - size), int(y - size), int(size * 2), int(size * 2))


class CrosshairConfigWidget(QWidget):
    """Configuration widget for crosshair settings."""
    
    settings_changed = Signal()
    
    def __init__(self, crosshair_plugin):
        super().__init__()
        
        self.crosshair_plugin = crosshair_plugin
        self.logger = logging.getLogger("CrosshairConfig")
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the configuration UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget for organized settings
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Basic settings tab
        basic_tab = self._create_basic_tab()
        tabs.addTab(basic_tab, "🎯 Básico")
        
        # Advanced settings tab
        advanced_tab = self._create_advanced_tab()
        tabs.addTab(advanced_tab, "⚙️ Avanzado")
        
        # Appearance tab
        appearance_tab = self._create_appearance_tab()
        tabs.addTab(appearance_tab, "🎨 Apariencia")
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.enable_btn = QPushButton("Activar Crosshair")
        self.enable_btn.setCheckable(True)
        self.enable_btn.clicked.connect(self._toggle_crosshair)
        control_layout.addWidget(self.enable_btn)
        
        self.reset_btn = QPushButton("Restablecer Valores")
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        control_layout.addWidget(self.reset_btn)
        
        layout.addLayout(control_layout)
    
    def _create_basic_tab(self):
        """Create basic settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Crosshair style
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "Cross", "Dot", "Circle", "Square", "T-Shape", 
            "Custom Cross", "Mini Dot"
        ])
        self.style_combo.currentTextChanged.connect(self._on_setting_changed)
        layout.addRow("Estilo del Crosshair:", self.style_combo)
        
        # Position mode
        position_group = QGroupBox("Modo de Posición")
        position_layout = QVBoxLayout(position_group)
        
        self.follow_mouse_cb = QCheckBox("Seguir cursor del mouse")
        self.follow_mouse_cb.setToolTip("✅ ACTIVADO: El crosshair sigue tu cursor del mouse\n❌ DESACTIVADO: El crosshair se mantiene fijo en el centro de la pantalla")
        self.follow_mouse_cb.toggled.connect(self._on_position_mode_changed)
        position_layout.addWidget(self.follow_mouse_cb)
        
        # Add explanation label
        self.position_explanation = QLabel()
        self.position_explanation.setWordWrap(True)
        self.position_explanation.setStyleSheet("QLabel { color: #888888; font-size: 11px; margin: 5px; }")
        position_layout.addWidget(self.position_explanation)
        
        layout.addRow(position_group)
        
        # Size with decimal precision for ultra-fine control
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0.1, 100.0)
        self.size_spin.setDecimals(2)  # Allow .01 precision
        self.size_spin.setSingleStep(0.05)  # Smaller steps for fine control
        self.size_spin.setValue(10.0)
        self.size_spin.valueChanged.connect(self._on_setting_changed)
        layout.addRow("Tamaño:", self.size_spin)
        
        # Gap with ultra-fine decimal precision
        self.gap_spin = QDoubleSpinBox()
        self.gap_spin.setRange(0.0, 50.0)
        self.gap_spin.setDecimals(2)  # Allow .01 precision
        self.gap_spin.setSingleStep(0.05)  # Smaller steps
        self.gap_spin.setValue(3.0)
        self.gap_spin.valueChanged.connect(self._on_setting_changed)
        layout.addRow("Separación central:", self.gap_spin)
        
        # Thickness with ultra-fine decimal precision
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0.05, 10.0)  # Allow thinner lines
        self.thickness_spin.setDecimals(2)  # Allow .01 precision
        self.thickness_spin.setSingleStep(0.05)  # Smaller steps
        self.thickness_spin.setValue(1.0)
        self.thickness_spin.valueChanged.connect(self._on_setting_changed)
        layout.addRow("Grosor:", self.thickness_spin)
        
        return tab
    
    def _create_advanced_tab(self):
        """Create advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Custom cross settings
        custom_group = QGroupBox("Custom Cross Settings")
        custom_layout = QFormLayout(custom_group)
        
        # Individual line controls with ultra-fine precision
        self.show_top_cb = QCheckBox()
        self.show_top_cb.setChecked(True)
        self.show_top_cb.toggled.connect(self._on_setting_changed)
        custom_layout.addRow("Show Top:", self.show_top_cb)
        
        self.top_length_spin = QDoubleSpinBox()
        self.top_length_spin.setRange(0.05, 100.0)
        self.top_length_spin.setDecimals(2)  # Ultra-fine precision
        self.top_length_spin.setSingleStep(0.05)
        self.top_length_spin.setValue(10.0)
        self.top_length_spin.valueChanged.connect(self._on_setting_changed)
        custom_layout.addRow("Top Length:", self.top_length_spin)
        
        self.show_bottom_cb = QCheckBox()
        self.show_bottom_cb.setChecked(True)
        self.show_bottom_cb.toggled.connect(self._on_setting_changed)
        custom_layout.addRow("Show Bottom:", self.show_bottom_cb)
        
        self.bottom_length_spin = QDoubleSpinBox()
        self.bottom_length_spin.setRange(0.05, 100.0)
        self.bottom_length_spin.setDecimals(2)
        self.bottom_length_spin.setSingleStep(0.05)
        self.bottom_length_spin.setValue(10.0)
        self.bottom_length_spin.valueChanged.connect(self._on_setting_changed)
        custom_layout.addRow("Bottom Length:", self.bottom_length_spin)
        
        self.show_left_cb = QCheckBox()
        self.show_left_cb.setChecked(True)
        self.show_left_cb.toggled.connect(self._on_setting_changed)
        custom_layout.addRow("Show Left:", self.show_left_cb)
        
        self.left_length_spin = QDoubleSpinBox()
        self.left_length_spin.setRange(0.05, 100.0)
        self.left_length_spin.setDecimals(2)
        self.left_length_spin.setSingleStep(0.05)
        self.left_length_spin.setValue(10.0)
        self.left_length_spin.valueChanged.connect(self._on_setting_changed)
        custom_layout.addRow("Left Length:", self.left_length_spin)
        
        self.show_right_cb = QCheckBox()
        self.show_right_cb.setChecked(True)
        self.show_right_cb.toggled.connect(self._on_setting_changed)
        custom_layout.addRow("Show Right:", self.show_right_cb)
        
        self.right_length_spin = QDoubleSpinBox()
        self.right_length_spin.setRange(0.05, 100.0)
        self.right_length_spin.setDecimals(2)
        self.right_length_spin.setSingleStep(0.05)
        self.right_length_spin.setValue(10.0)
        self.right_length_spin.valueChanged.connect(self._on_setting_changed)
        custom_layout.addRow("Right Length:", self.right_length_spin)
        
        layout.addWidget(custom_group)
        
        # Mini dot settings
        mini_group = QGroupBox("Mini Dot Settings")
        mini_layout = QFormLayout(mini_group)
        
        self.mini_size_spin = QDoubleSpinBox()
        self.mini_size_spin.setRange(0.05, 5.0)  # Even smaller minimum for ultra-mini dots
        self.mini_size_spin.setDecimals(2)  # Ultra-fine precision
        self.mini_size_spin.setSingleStep(0.05)
        self.mini_size_spin.setValue(0.5)
        self.mini_size_spin.valueChanged.connect(self._on_setting_changed)
        mini_layout.addRow("Mini Dot Size:", self.mini_size_spin)
        self.mini_size_spin.setRange(0.1, 5.0)
        self.mini_size_spin.setDecimals(1)
        self.mini_size_spin.setSingleStep(0.1)
        self.mini_size_spin.setValue(0.5)
        self.mini_size_spin.valueChanged.connect(self._on_setting_changed)
        mini_layout.addRow("Mini Size:", self.mini_size_spin)
        
        layout.addWidget(mini_group)
        layout.addStretch()
        
        return tab
    
    def _create_appearance_tab(self):
        """Create appearance settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Color selection
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 30)
        self.color_btn.clicked.connect(self._choose_color)
        self.color_btn.setStyleSheet("background-color: #00FF00; border: 1px solid black;")
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(QLabel("Haz clic para cambiar el color"))
        color_layout.addStretch()
        layout.addRow("Color:", color_layout)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self.opacity_label = QLabel("100%")
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        layout.addRow("Opacidad:", opacity_layout)
        
        return tab
    
    def _load_settings(self):
        """Load settings from plugin configuration."""
        config = self.crosshair_plugin.plugin_config
        
        # Basic settings
        self.style_combo.setCurrentText(config.get('style', 'Cross'))
        self.follow_mouse_cb.setChecked(config.get('follow_mouse', False))
        self._update_position_explanation()  # Update explanation text
        self.size_spin.setValue(config.get('size', 10.0))
        self.gap_spin.setValue(config.get('gap', 3.0))
        self.thickness_spin.setValue(config.get('thickness', 1.0))
        
        # Advanced settings
        self.show_top_cb.setChecked(config.get('show_top', True))
        self.top_length_spin.setValue(config.get('top_length', 10.0))
        self.show_bottom_cb.setChecked(config.get('show_bottom', True))
        self.bottom_length_spin.setValue(config.get('bottom_length', 10.0))
        self.show_left_cb.setChecked(config.get('show_left', True))
        self.left_length_spin.setValue(config.get('left_length', 10.0))
        self.show_right_cb.setChecked(config.get('show_right', True))
        self.right_length_spin.setValue(config.get('right_length', 10.0))
        self.mini_size_spin.setValue(config.get('mini_size', 0.5))
        
        # Appearance
        self.opacity_slider.setValue(config.get('opacity', 255))
        self._update_opacity_label()
        
        # Enable button
        self.enable_btn.setChecked(config.get('enabled', False))
        self._update_enable_button()
        
        # Update color button
        color = config.get('color', '#00FF00')
        self.color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
    
    def _update_opacity_label(self):
        """Update opacity percentage label."""
        opacity_percent = int((self.opacity_slider.value() / 255.0) * 100)
        self.opacity_label.setText(f"{opacity_percent}%")
    
    def _update_position_explanation(self):
        """Update position mode explanation text."""
        if self.follow_mouse_cb.isChecked():
            self.position_explanation.setText("🎯 El crosshair seguirá tu cursor del mouse mientras te mueves. Útil para apuntar con precisión donde miras.")
        else:
            self.position_explanation.setText("🎯 El crosshair permanecerá fijo en el centro de la pantalla. Útil para juegos FPS donde siempre apuntas al centro.")
    
    def _update_enable_button(self):
        """Update enable button text and style."""
        enabled = self.enable_btn.isChecked()
        if enabled:
            self.enable_btn.setText("🔴 Desactivar Crosshair")
            self.enable_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-weight: bold; }")
        else:
            self.enable_btn.setText("🟢 Activar Crosshair")
            self.enable_btn.setStyleSheet("QPushButton { background-color: #44ff44; color: black; font-weight: bold; }")
    
    def _on_setting_changed(self):
        """Handle setting changes."""
        # Update plugin configuration
        config = self.crosshair_plugin.plugin_config
        
        # Basic settings
        config['style'] = self.style_combo.currentText()
        config['follow_mouse'] = self.follow_mouse_cb.isChecked()
        config['size'] = self.size_spin.value()
        config['gap'] = self.gap_spin.value()
        config['thickness'] = self.thickness_spin.value()
        
        # Advanced settings
        config['show_top'] = self.show_top_cb.isChecked()
        config['top_length'] = self.top_length_spin.value()
        config['show_bottom'] = self.show_bottom_cb.isChecked()
        config['bottom_length'] = self.bottom_length_spin.value()
        config['show_left'] = self.show_left_cb.isChecked()
        config['left_length'] = self.left_length_spin.value()
        config['show_right'] = self.show_right_cb.isChecked()
        config['right_length'] = self.right_length_spin.value()
        config['mini_size'] = self.mini_size_spin.value()
        
        # Save and update
        self.crosshair_plugin.save_config()
        self.crosshair_plugin.update_crosshair()
        self.settings_changed.emit()
        
        self.logger.info(f"🎯 Configuración de crosshair actualizada: estilo={config['style']}, tamaño={config['size']}, seguir_mouse={config['follow_mouse']}")
    
    def _on_position_mode_changed(self):
        """Handle position mode change (follow mouse toggle)."""
        follow_mouse = self.follow_mouse_cb.isChecked()
        self.crosshair_plugin.plugin_config['follow_mouse'] = follow_mouse
        self.crosshair_plugin.save_config()
        
        # Update explanation text
        self._update_position_explanation()
        
        # Update crosshair tracking mode
        if self.crosshair_plugin.crosshair_widget:
            self.crosshair_plugin.crosshair_widget.update_tracking_mode()
        
        mode_text = "siguiendo cursor" if follow_mouse else "centro fijo"
        self.logger.info(f"🎯 [CROSSHAIR] Modo de posición cambiado a: {mode_text}")
    
    def _on_opacity_changed(self):
        """Handle opacity slider changes."""
        self._update_opacity_label()
        
        self.crosshair_plugin.plugin_config['opacity'] = self.opacity_slider.value()
        self.crosshair_plugin.save_config()
        self.crosshair_plugin.update_crosshair()
        self.settings_changed.emit()
    
    def _choose_color(self):
        """Open color chooser dialog."""
        current_color = QColor(self.crosshair_plugin.plugin_config.get('color', '#00FF00'))
        color = QColorDialog.getColor(current_color, self)
        
        if color.isValid():
            color_hex = color.name()
            self.crosshair_plugin.plugin_config['color'] = color_hex
            self.color_btn.setStyleSheet(f"background-color: {color_hex}; border: 1px solid black;")
            self.crosshair_plugin.save_config()
            self.crosshair_plugin.update_crosshair()
            self.settings_changed.emit()
            
            self.logger.info(f"🎯 Color del crosshair cambiado a: {color_hex}")
    
    def _toggle_crosshair(self):
        """Toggle crosshair on/off."""
        enabled = self.enable_btn.isChecked()
        self.crosshair_plugin.plugin_config['enabled'] = enabled
        self.crosshair_plugin.save_config()
        self._update_enable_button()
        
        if enabled:
            self.crosshair_plugin.show_crosshair()
            self.logger.info("🎯 [CROSSHAIR] Crosshair activado y mostrado")
        else:
            self.crosshair_plugin.hide_crosshair()
            self.logger.info("🎯 [CROSSHAIR] Crosshair desactivado y oculto")
        
        self.settings_changed.emit()
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        defaults = {
            'style': 'Cross',
            'size': 10.0,
            'gap': 3.0,
            'thickness': 1.0,
            'color': '#00FF00',
            'opacity': 255,
            'enabled': False,
            'follow_mouse': False,
            'show_top': True,
            'top_length': 10.0,
            'show_bottom': True,
            'bottom_length': 10.0,
            'show_left': True,
            'left_length': 10.0,
            'show_right': True,
            'right_length': 10.0,
            'mini_size': 0.5
        }
        
        self.crosshair_plugin.plugin_config.update(defaults)
        self.crosshair_plugin.save_config()
        self._load_settings()
        self.crosshair_plugin.update_crosshair()
        self.settings_changed.emit()
        
        self.logger.info("🎯 [CROSSHAIR] Configuración restablecida a valores por defecto")


class CrosshairPlugin(BasePlugin):
    """Crosshair overlay plugin with advanced configuration."""
    
    name = "Crosshair Overlay"
    description = "Provides a highly customizable crosshair overlay for gaming"
    version = "2.0.0"
    author = "Party Brasil"
    
    def __init__(self, config_manager, thread_manager):
        super().__init__(config_manager, thread_manager)
        
        # Plugin widgets
        self.crosshair_widget = None
        self.config_widget = None
        self.panel_widget = None
        
        # Initialize default config
        self._init_default_config()
    
    def _init_default_config(self):
        """Initialize default configuration."""
        defaults = {
            'style': 'Cross',
            'size': 10.0,
            'gap': 3.0,
            'thickness': 1.0,
            'color': '#00FF00',
            'opacity': 255,
            'enabled': False,
            'follow_mouse': False,
            'show_top': True,
            'top_length': 10.0,
            'show_bottom': True,
            'bottom_length': 10.0,
            'show_left': True,
            'left_length': 10.0,
            'show_right': True,
            'right_length': 10.0,
            'mini_size': 0.5
        }
        
        # Only set defaults if not already configured
        for key, value in defaults.items():
            if key not in self.plugin_config:
                self.plugin_config[key] = value
    
    def initialize(self) -> bool:
        """Initialize the crosshair plugin."""
        try:
            self.logger.info("Initializing Crosshair Plugin...")
            
            # Create crosshair widget
            self.crosshair_widget = CrosshairWidget(self)
            
            # Create configuration widget
            self.config_widget = CrosshairConfigWidget(self)
            
            # Create panel with configuration
            self.panel_widget = FloatingPanel(self.config_manager, "Crosshair Settings")
            self.panel_widget.add_content_widget(self.config_widget)
            
            # Connect signals - Panel should NOT close when user closes it
            # The crosshair should remain active even if panel is closed
            # Only deactivating the plugin should stop the crosshair
            self.panel_widget.close_requested.connect(self._on_panel_close_requested)
            
            self.logger.info("🎯 [CROSSHAIR] Plugin de Crosshair inicializado correctamente")
            return super().initialize()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize crosshair: {e}")
            self.logger.error(f"Failed to initialize crosshair: {e}")
            return False
    
    def activate(self) -> bool:
        """Activate the crosshair plugin."""
        try:
            if super().activate():
                # Show panel for configuration
                if self.panel_widget:
                    self.panel_widget.show()
                    self.panel_widget.raise_()
                    self.panel_widget.activateWindow()
                
                # IMPORTANT: Don't auto-show crosshair - user must enable it in panel
                # The crosshair should only be shown when user explicitly enables it
                
                self.logger.info("🎯 [CROSSHAIR] Plugin activado - panel abierto para configuración")
                return True
            return False
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to activate crosshair: {e}")
            self.logger.error(f"❌ Failed to activate crosshair: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the crosshair plugin."""
        try:
            # Hide crosshair and panel
            self.hide_crosshair()
            
            if self.panel_widget:
                self.panel_widget.hide()
            
            self.logger.info("🎯 [CROSSHAIR] Plugin desactivado")
            return super().deactivate()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to deactivate crosshair: {e}")
            self.logger.error(f"Failed to deactivate crosshair: {e}")
            return False
    
    def show_crosshair(self):
        """Show the crosshair overlay."""
        if self.crosshair_widget and self.plugin_config.get('enabled', False):
            self.crosshair_widget.show_crosshair()
            self.logger.debug("🎯 [CROSSHAIR] Crosshair mostrado")
    
    def hide_crosshair(self):
        """Hide the crosshair overlay."""
        if self.crosshair_widget:
            self.crosshair_widget.hide_crosshair()
            self.logger.debug("🎯 [CROSSHAIR] Crosshair oculto")
    
    def update_crosshair(self):
        """Update the crosshair appearance."""
        if self.crosshair_widget:
            self.crosshair_widget.update()
            self.logger.debug("🎯 [CROSSHAIR] Crosshair actualizado")
    
    def get_crosshair_settings(self) -> dict:
        """Get current crosshair settings."""
        return self.plugin_config.copy()
    
    def get_panel_widget(self):
        """Get the plugin's panel widget."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Get the plugin's configuration widget."""
        # Return None so this plugin doesn't show in control panel
        # This plugin uses its own floating panel for configuration
        return None
    
    def _on_panel_close_requested(self):
        """Handle when user closes the crosshair panel."""
        # Hide the panel but keep crosshair active if it's enabled
        if self.panel_widget:
            self.panel_widget.hide()
            
        # Log the action but don't disable crosshair
        # The crosshair should remain visible if it was enabled
        if self.plugin_config.get('enabled', False):
            self.logger.info("🎯 [CROSSHAIR] Panel cerrado - crosshair permanece activo")
        else:
            self.logger.info("🎯 [CROSSHAIR] Panel cerrado - crosshair no estaba activo")
