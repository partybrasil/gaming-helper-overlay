"""
Enhanced Log Handler for Control Panel
Provides colored and organized logging display in the UI        self.add_colored_text(' [SYSTEM] ', '#50E3C2')
        self.add_colored_text('🚀 Gaming Helper Overlay started - Ready for gaming!\n', '#50E3C2')
        self.add_colored_text(
            datetime.datetime.now().strftime('%H:%M:%S'),
            '#666666'
        )
        self.add_colored_text(' [SYSTEM] ', '#50E3C2') 
        self.add_colored_text('📊 Enhanced log system initialized - All events will be recorded with colors and organization\n', '#50E3C2')
        self.add_colored_text('💡 Use filters to control what you see in the logs\n\n', '#F39C12')mport logging
import datetime
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont


class LogLevel:
    """Log level definitions with colors."""
    DEBUG = {'name': 'DEBUG', 'color': '#888888', 'prefix': '🔍'}
    INFO = {'name': 'INFO', 'color': '#00AA00', 'prefix': 'ℹ️'}
    WARNING = {'name': 'WARNING', 'color': '#FFA500', 'prefix': '⚠️'}
    ERROR = {'name': 'ERROR', 'color': '#FF0000', 'prefix': '❌'}
    CRITICAL = {'name': 'CRITICAL', 'color': '#AA0000', 'prefix': '🚨'}


class ComponentColors:
    """Color scheme for different components."""
    CORE = '#4A90E2'          # Blue
    PLUGIN = '#7ED321'        # Green  
    UI = '#F5A623'            # Orange
    THREAD = '#BD10E0'        # Purple
    CONFIG = '#50E3C2'        # Cyan
    CROSSHAIR = '#FF6B6B'     # Red
    FPS = '#4ECDC4'           # Teal
    CPU_GPU = '#FFE66D'       # Yellow
    SYSTEM = '#95A5A6'        # Gray
    DEFAULT = '#FFFFFF'       # White


class EnhancedLogHandler(logging.Handler):
    """Custom log handler that emits signals for UI updates."""
    
    log_message = Signal(str, str, str, str)  # timestamp, level, component, message
    
    def __init__(self):
        super().__init__()
        self.setLevel(logging.DEBUG)
        
        # Set format
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        self.setFormatter(formatter)
    
    def emit(self, record):
        """Emit log record as signal."""
        try:
            timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
            level = record.levelname
            component = record.name
            message = self.format(record)
            
            self.log_message.emit(timestamp, level, component, message)
            
        except Exception:
            self.handleError(record)


class LogDisplay(QTextEdit):
    """Enhanced log display widget with colors and filtering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setReadOnly(True)
        self.document().setMaximumBlockCount(1000)  # Limit log entries using document
        
        # Setup font
        font = QFont("Consolas", 9)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Setup log handler
        self.log_handler = EnhancedLogHandler()
        self.log_handler.log_message.connect(self.add_log_entry)
        
        # Add to root logger
        logging.getLogger().addHandler(self.log_handler)
        
        # Filter settings
        self.show_debug = False
        self.show_info = True
        self.show_warning = True
        self.show_error = True
        self.show_critical = True
        
        # Component filters
        self.component_filters = set()
        
        # Add welcome message
        self._add_welcome_message()
    
    def _add_welcome_message(self):
        """Add welcome message to log."""
        self.add_colored_text(
            datetime.datetime.now().strftime('%H:%M:%S'),
            '#666666'
        )
        self.add_colored_text(' [SYSTEM] ', '#50E3C2')
        self.add_colored_text('� Gaming Helper Overlay started - Ready for gaming!\n', '#50E3C2')
        self.add_colored_text(
            datetime.datetime.now().strftime('%H:%M:%S'),
            '#666666'
        )
        self.add_colored_text(' [SYSTEM] ', '#50E3C2') 
        self.add_colored_text('📊 Enhanced log system initialized - All events will be recorded with colors and organization\n', '#50E3C2')
        self.add_colored_text('💡 Use filters to control what you see in the logs\n\n', '#F39C12')
    
    def add_log_entry(self, timestamp: str, level: str, component: str, message: str):
        """Add a log entry with proper formatting."""
        # Check filters
        if not self._should_show_log(level, component):
            return
        
        # Get colors and formatting
        level_info = self._get_level_info(level)
        component_color = self._get_component_color(component)
        
        # Build formatted message
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Timestamp
        self.add_colored_text(f"[{timestamp}] ", '#666666')
        
        # Level with icon
        level_text = f"{level_info['prefix']} {level_info['name']} "
        self.add_colored_text(level_text, level_info['color'])
        
        # Component
        component_short = self._format_component(component)
        self.add_colored_text(f"[{component_short}] ", component_color)
        
        # Message
        clean_message = self._clean_message(message)
        self.add_colored_text(f"{clean_message}\n", '#000000')
        
        # Auto-scroll to bottom
        self.ensureCursorVisible()
    
    def add_colored_text(self, text: str, color: str):
        """Add colored text to the log display."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        
        cursor.insertText(text, format)
        self.setTextCursor(cursor)
    
    def _get_level_info(self, level: str) -> dict:
        """Get level information with color and icon."""
        level_map = {
            'DEBUG': LogLevel.DEBUG,
            'INFO': LogLevel.INFO,
            'WARNING': LogLevel.WARNING,
            'ERROR': LogLevel.ERROR,
            'CRITICAL': LogLevel.CRITICAL
        }
        return level_map.get(level, LogLevel.INFO)
    
    def _get_component_color(self, component: str) -> str:
        """Get color for component based on type."""
        component_lower = component.lower()
        
        # Specific plugin colors
        if 'crosshair' in component_lower:
            return ComponentColors.CROSSHAIR
        elif 'fps' in component_lower:
            return ComponentColors.FPS
        elif any(x in component_lower for x in ['cpu', 'gpu', 'monitor']):
            return ComponentColors.CPU_GPU
        elif 'system' in component_lower:
            return ComponentColors.SYSTEM
        # General component types
        elif any(x in component_lower for x in ['core', 'app', 'manager']):
            return ComponentColors.CORE
        elif 'plugin' in component_lower:
            return ComponentColors.PLUGIN
        elif any(x in component_lower for x in ['ui', 'panel', 'widget', 'window']):
            return ComponentColors.UI
        elif 'thread' in component_lower:
            return ComponentColors.THREAD
        elif 'config' in component_lower:
            return ComponentColors.CONFIG
        else:
            return ComponentColors.DEFAULT
    
    def _format_component(self, component: str) -> str:
        """Format component name for display."""
        # Remove common prefixes and shorten
        component = component.replace('GamingHelperApp', 'APP')
        component = component.replace('PluginManager', 'PLUGIN-MGR')
        component = component.replace('ConfigManager', 'CONFIG')
        component = component.replace('ThreadManager', 'THREAD-MGR')
        component = component.replace('ControlPanel', 'CONTROL')
        component = component.replace('Plugin.', '')
        
        # Limit length
        if len(component) > 15:
            component = component[:12] + "..."
        
        return component
    
    def _clean_message(self, message: str) -> str:
        """Clean up message text."""
        # Remove component prefix if it's repeated
        parts = message.split(' - ', 2)
        if len(parts) >= 3:
            return parts[2]
        elif len(parts) >= 2:
            return parts[1]
        return message
    
    def _should_show_log(self, level: str, component: str) -> bool:
        """Check if log should be shown based on filters."""
        # Level filter
        level_filters = {
            'DEBUG': self.show_debug,
            'INFO': self.show_info,
            'WARNING': self.show_warning,
            'ERROR': self.show_error,
            'CRITICAL': self.show_critical
        }
        
        if not level_filters.get(level, True):
            return False
        
        # Component filter
        if self.component_filters and component not in self.component_filters:
            return False
        
        return True
    
    def set_level_filter(self, level: str, enabled: bool):
        """Set level filter."""
        if level == 'DEBUG':
            self.show_debug = enabled
        elif level == 'INFO':
            self.show_info = enabled
        elif level == 'WARNING':
            self.show_warning = enabled
        elif level == 'ERROR':
            self.show_error = enabled
        elif level == 'CRITICAL':
            self.show_critical = enabled
    
    def set_component_filters(self, components: set):
        """Set component filters."""
        self.component_filters = components
    
    def clear_log(self):
        """Clear the log display."""
        self.clear()
        self._add_welcome_message()
    
    def save_log(self, filename: str):
        """Save log to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            return True
        except Exception as e:
            logging.error(f"Failed to save log: {e}")
            return False
