"""
Floating Icon Widget
A draggable floating icon that provides quick access to the control panel.
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor, QFont, QPen, QBrush

from core.config_manager import ConfigManager


class FloatingIcon(QWidget):
    """Floating icon widget for quick access to control panel."""
    
    # Signals
    clicked = Signal()
    double_clicked = Signal()
    right_clicked = Signal()
    
    def __init__(self, config_manager: ConfigManager, control_panel, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.control_panel = control_panel
        self.logger = logging.getLogger("FloatingIcon")
        
        # State variables
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.is_expanded = False
        self.notification_count = 0
        
        # Animations
        self.pulse_animation = None
        self.bounce_animation = None
        
        # Load configuration first
        self._load_config()
        
        # Setup UI
        self._setup_ui()
        self._setup_animations()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the floating icon UI."""
        # Window flags for floating behavior
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setScaledContents(True)
        
        layout.addWidget(self.icon_label)
        
        # Load default icon
        self._load_icon()
    
    def _setup_animations(self):
        """Setup animations for the icon."""
        # Pulse animation for notifications
        self.pulse_animation = QPropertyAnimation(self, b"windowOpacity")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(0.8)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.pulse_animation.setLoopCount(-1)  # Infinite loop
        
        # Bounce animation for interactions
        self.bounce_animation = QPropertyAnimation(self, b"geometry")
        self.bounce_animation.setDuration(200)
        self.bounce_animation.setEasingCurve(QEasingCurve.OutBounce)
    
    def _load_config(self):
        """Load icon configuration."""
        # Position
        pos = self.config_manager.get("floating_icon.position", {"x": 100, "y": 100})
        self.move(pos["x"], pos["y"])
        
        # Size
        size = self.config_manager.get("floating_icon.size", {"width": 50, "height": 50})
        self.resize(size["width"], size["height"])
        
        # Opacity
        opacity = self.config_manager.get("floating_icon.opacity", 0.8)
        self.setWindowOpacity(opacity)
        
        # Icon path
        self.icon_path = self.config_manager.get("floating_icon.icon_path", "assets/icons/app_icon.png")
    
    def _save_config(self):
        """Save icon configuration."""
        # Position
        pos = self.pos()
        self.config_manager.set("floating_icon.position", {"x": pos.x(), "y": pos.y()})
        
        # Size
        size = self.size()
        self.config_manager.set("floating_icon.size", {"width": size.width(), "height": size.height()})
        
        # Opacity
        self.config_manager.set("floating_icon.opacity", self.windowOpacity())
    
    def _load_icon(self):
        """Load the icon image."""
        try:
            icon_path = Path(__file__).parent.parent / self.icon_path
            
            if icon_path.exists():
                pixmap = QPixmap(str(icon_path))
            else:
                # Create default icon if file doesn't exist
                pixmap = self._create_default_icon()
            
            # Scale pixmap to fit label
            scaled_pixmap = pixmap.scaled(
                self.icon_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.icon_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Failed to load icon: {e}")
            # Use default icon
            self.icon_label.setPixmap(self._create_default_icon())
    
    def _create_default_icon(self) -> QPixmap:
        """Create a default icon when no icon file is available."""
        size = 48
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle background
        painter.setBrush(QBrush(QColor(100, 150, 255, 200)))
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        painter.drawEllipse(2, 2, size - 4, size - 4)
        
        # Draw text
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "GH")
        
        painter.end()
        return pixmap
    
    def _apply_styling(self):
        """Apply styling to the icon."""
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)
        
        # Style sheet
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)
    
    def set_icon(self, icon_path: str):
        """Set a custom icon."""
        self.icon_path = icon_path
        self.config_manager.set("floating_icon.icon_path", icon_path)
        self._load_icon()
    
    def set_notification_count(self, count: int):
        """Set notification count and start/stop pulsing."""
        self.notification_count = count
        
        if count > 0:
            self.start_pulse_animation()
        else:
            self.stop_pulse_animation()
        
        self.update()  # Trigger repaint to show notification badge
    
    def start_pulse_animation(self):
        """Start the pulse animation."""
        if not self.pulse_animation.state() == QPropertyAnimation.Running:
            self.pulse_animation.start()
    
    def stop_pulse_animation(self):
        """Stop the pulse animation."""
        if self.pulse_animation.state() == QPropertyAnimation.Running:
            self.pulse_animation.stop()
            self.setWindowOpacity(self.config_manager.get("floating_icon.opacity", 0.8))
    
    def bounce(self):
        """Animate a bounce effect."""
        current_rect = self.geometry()
        bounce_rect = current_rect.adjusted(0, -5, 0, -5)
        
        self.bounce_animation.setStartValue(current_rect)
        self.bounce_animation.setKeyValueAt(0.5, bounce_rect)
        self.bounce_animation.setEndValue(current_rect)
        self.bounce_animation.start()
    
    def expand_preview(self):
        """Show a preview/expanded view of the icon."""
        # This could show a tooltip or mini preview
        pass
    
    def paintEvent(self, event):
        """Custom paint event to draw notification badge."""
        super().paintEvent(event)
        
        if self.notification_count > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw notification badge
            badge_size = 16
            badge_x = self.width() - badge_size - 2
            badge_y = 2
            
            # Badge background
            painter.setBrush(QBrush(QColor(255, 50, 50, 220)))
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)
            
            # Badge text
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            
            count_text = str(self.notification_count) if self.notification_count < 100 else "99+"
            painter.drawText(badge_x, badge_y, badge_size, badge_size, Qt.AlignCenter, count_text)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPos() - self.pos()
            
            # Start bounce animation
            self.bounce()
            
            event.accept()
        elif event.button() == Qt.RightButton:
            self.right_clicked.emit()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging."""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_start_pos
            self.move(new_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            
            # Save new position
            self._save_config()
            
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click events."""
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()
            event.accept()
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for opacity adjustment."""
        # Adjust opacity with mouse wheel
        current_opacity = self.windowOpacity()
        delta = event.angleDelta().y() / 1200.0  # Scale wheel delta
        
        new_opacity = max(0.1, min(1.0, current_opacity + delta))
        self.setWindowOpacity(new_opacity)
        
        # Update config
        self.config_manager.set("floating_icon.opacity", new_opacity)
        
        event.accept()
    
    def enterEvent(self, event):
        """Handle mouse enter events."""
        # Slightly increase opacity on hover
        current_opacity = self.windowOpacity()
        self.setWindowOpacity(min(1.0, current_opacity + 0.1))
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave events."""
        # Restore original opacity
        original_opacity = self.config_manager.get("floating_icon.opacity", 0.8)
        self.setWindowOpacity(original_opacity)
        
        super().leaveEvent(event)
    
    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        
        # Reload icon to fit new size
        self._load_icon()
    
    def closeEvent(self, event):
        """Handle close events."""
        self._save_config()
        super().closeEvent(event)
    
    def show(self):
        """Override show to emit clicked signal when shown."""
        super().show()
        
        # Connect click signal to control panel toggle
        if not self.clicked.connect:
            self.clicked.connect(self._handle_click)
    
    def _handle_click(self):
        """Handle icon click."""
        # Toggle control panel visibility
        if hasattr(self.control_panel, 'isVisible'):
            if self.control_panel.isVisible():
                self.control_panel.hide()
            else:
                self.control_panel.show()
                self.control_panel.raise_()
                self.control_panel.activateWindow()
