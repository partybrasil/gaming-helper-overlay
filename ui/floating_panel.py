"""
Floating Panel
Base class for all floating panels with common functionality.
"""

import logging
from typing import Optional, Tuple
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QSlider, QLabel, QFrame, QGraphicsDropShadowEffect,
                              QSizeGrip, QMenu)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPalette, QCursor

from core.config_manager import ConfigManager


class FloatingPanel(QWidget):
    """Base floating panel with transparency, always-on-top, and resize capabilities."""
    
    # Signals
    close_requested = Signal()
    minimize_requested = Signal()
    panel_moved = Signal(QPoint)  # new position
    panel_resized = Signal(tuple)  # new size (width, height)
    transparency_changed = Signal(float)  # opacity value
    
    def __init__(self, config_manager: ConfigManager, panel_name: str, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.panel_name = panel_name
        self.logger = logging.getLogger(f"FloatingPanel.{panel_name}")
        
        # Panel state
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.always_on_top = False
        self.transparency_enabled = True
        self.glassmorphism_enabled = True
        
        # Animation
        self.fade_animation = None
        
        # Setup UI
        self._setup_ui()
        self._setup_animations()
        self._load_panel_config()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the basic UI structure."""
        # Set window flags for floating behavior
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(0)
        
        # Title bar
        self._create_title_bar()
        
        # Content area
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        self.main_layout.addWidget(self.content_frame)
        
        # Size grip for resizing
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)
        
        # Position size grip in bottom-right corner
        self.size_grip.move(self.width() - 16, self.height() - 16)
    
    def _create_title_bar(self):
        """Create the title bar with controls."""
        self.title_bar = QFrame()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(35)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 5, 5, 5)
        
        # Title label
        self.title_label = QLabel(self.panel_name)
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Controls
        self._create_controls(title_layout)
        
        self.main_layout.addWidget(self.title_bar)
    
    def _create_controls(self, layout):
        """Create panel controls."""
        # Transparency slider
        self.transparency_label = QLabel("T:")
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(10, 100)
        self.transparency_slider.setValue(95)
        self.transparency_slider.setFixedWidth(80)
        self.transparency_slider.valueChanged.connect(self._on_transparency_changed)
        
        # Always on top button
        self.always_on_top_btn = QPushButton("📌")
        self.always_on_top_btn.setFixedSize(25, 25)
        self.always_on_top_btn.setCheckable(True)
        self.always_on_top_btn.clicked.connect(self._toggle_always_on_top)
        self.always_on_top_btn.setToolTip("Always on top")
        
        # Minimize button
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(25, 25)
        self.minimize_btn.clicked.connect(self.minimize_requested.emit)
        self.minimize_btn.setToolTip("Minimize")
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.close_requested.emit)
        self.close_btn.setToolTip("Close")
        
        # Add to layout
        layout.addWidget(self.transparency_label)
        layout.addWidget(self.transparency_slider)
        layout.addWidget(self.always_on_top_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)
    
    def _setup_animations(self):
        """Setup animations for the panel."""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
    
    def _load_panel_config(self):
        """Load panel configuration."""
        config_key = f"panels.{self.panel_name.lower().replace(' ', '_')}"
        
        # Position
        pos = self.config_manager.get(f"{config_key}.position", {"x": 100, "y": 100})
        self.move(pos["x"], pos["y"])
        
        # Size
        size = self.config_manager.get(f"{config_key}.size", {"width": 300, "height": 200})
        self.resize(size["width"], size["height"])
        
        # Transparency
        opacity = self.config_manager.get(f"{config_key}.opacity", 0.95)
        self.setWindowOpacity(opacity)
        self.transparency_slider.setValue(int(opacity * 100))
        
        # Always on top
        self.always_on_top = self.config_manager.get(f"{config_key}.always_on_top", False)
        self.always_on_top_btn.setChecked(self.always_on_top)
        self._update_always_on_top()
    
    def _save_panel_config(self):
        """Save panel configuration."""
        config_key = f"panels.{self.panel_name.lower().replace(' ', '_')}"
        
        # Position
        pos = self.pos()
        self.config_manager.set(f"{config_key}.position", {"x": pos.x(), "y": pos.y()})
        
        # Size
        size = self.size()
        self.config_manager.set(f"{config_key}.size", {"width": size.width(), "height": size.height()})
        
        # Transparency
        self.config_manager.set(f"{config_key}.opacity", self.windowOpacity())
        
        # Always on top
        self.config_manager.set(f"{config_key}.always_on_top", self.always_on_top)
    
    def _apply_styling(self):
        """Apply glassmorphism and custom styling."""
        style = """
        QWidget {
            background: rgba(30, 30, 30, 180);
            border: 2px solid rgba(255, 255, 255, 30);
            border-radius: 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        #titleBar {
            background: rgba(50, 50, 50, 200);
            border: 1px solid rgba(255, 255, 255, 50);
            border-radius: 8px;
            margin: 2px;
        }
        
        #titleLabel {
            color: white;
            font-weight: bold;
            font-size: 12px;
            background: transparent;
            border: none;
        }
        
        #contentFrame {
            background: rgba(40, 40, 40, 150);
            border: 1px solid rgba(255, 255, 255, 20);
            border-radius: 8px;
            margin: 2px;
        }
        
        QPushButton {
            background: rgba(70, 70, 70, 180);
            border: 1px solid rgba(255, 255, 255, 50);
            border-radius: 4px;
            color: white;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background: rgba(90, 90, 90, 200);
            border: 1px solid rgba(255, 255, 255, 80);
        }
        
        QPushButton:pressed {
            background: rgba(50, 50, 50, 200);
        }
        
        QPushButton:checked {
            background: rgba(100, 150, 255, 180);
        }
        
        QSlider::groove:horizontal {
            border: 1px solid rgba(255, 255, 255, 50);
            height: 6px;
            background: rgba(60, 60, 60, 180);
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background: rgba(100, 150, 255, 200);
            border: 1px solid rgba(255, 255, 255, 80);
            width: 14px;
            border-radius: 7px;
            margin: -4px 0;
        }
        
        QSlider::handle:horizontal:hover {
            background: rgba(120, 170, 255, 230);
        }
        
        QLabel {
            color: white;
            background: transparent;
            border: none;
        }
        """
        
        self.setStyleSheet(style)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
    
    def _on_transparency_changed(self, value):
        """Handle transparency slider changes."""
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
        self.transparency_changed.emit(opacity)
    
    def _toggle_always_on_top(self):
        """Toggle always on top state."""
        self.always_on_top = self.always_on_top_btn.isChecked()
        self._update_always_on_top()
    
    def _update_always_on_top(self):
        """Update always on top window flag."""
        current_flags = self.windowFlags()
        
        if self.always_on_top:
            new_flags = current_flags | Qt.WindowStaysOnTopHint
        else:
            new_flags = current_flags & ~Qt.WindowStaysOnTopHint
        
        if new_flags != current_flags:
            # Store current geometry
            geometry = self.geometry()
            
            # Update flags
            self.setWindowFlags(new_flags)
            
            # Restore geometry and show
            self.setGeometry(geometry)
            self.show()
    
    def add_content_widget(self, widget):
        """Add a widget to the content area."""
        self.content_layout.addWidget(widget)
    
    def fade_in(self):
        """Fade in animation."""
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(self.transparency_slider.value() / 100.0)
        self.fade_animation.start()
    
    def fade_out(self):
        """Fade out animation."""
        self.fade_animation.setStartValue(self.windowOpacity())
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()
    
    # Event handlers
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.is_dragging = True
            self.drag_start_pos = event.globalPos() - self.pos()
            event.accept()
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_start_pos
            self.move(new_pos)
            self.panel_moved.emit(new_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        
        # Update size grip position
        self.size_grip.move(self.width() - 16, self.height() - 16)
        
        # Emit signal
        new_size = event.size()
        self.panel_resized.emit((new_size.width(), new_size.height()))
    
    def closeEvent(self, event):
        """Handle close event."""
        self._save_panel_config()
        super().closeEvent(event)
    
    def _show_context_menu(self, pos):
        """Show context menu."""
        menu = QMenu(self)
        
        # Always on top action
        always_on_top_action = menu.addAction("Always on Top")
        always_on_top_action.setCheckable(True)
        always_on_top_action.setChecked(self.always_on_top)
        always_on_top_action.triggered.connect(self._toggle_always_on_top)
        
        menu.addSeparator()
        
        # Reset position action
        reset_pos_action = menu.addAction("Reset Position")
        reset_pos_action.triggered.connect(lambda: self.move(100, 100))
        
        # Reset size action
        reset_size_action = menu.addAction("Reset Size")
        reset_size_action.triggered.connect(lambda: self.resize(300, 200))
        
        menu.addSeparator()
        
        # Close action
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close_requested.emit)
        
        menu.exec_(pos)
