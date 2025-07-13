"""
Multi-Hotkey / Macros Plugin
Advanced macro system for creating hotkey combinations, loops, delays and mouse/keyboard automation.
"""
import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import win32api
import win32con
import win32gui

# Optional imports for input simulation
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    keyboard = None

try:
    import mouse
    MOUSE_AVAILABLE = True
except ImportError:
    MOUSE_AVAILABLE = False
    mouse = None

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QComboBox, QSpinBox, QGroupBox, QCheckBox,
                              QSlider, QTabWidget, QFormLayout, QLineEdit,
                              QListWidget, QListWidgetItem, QTextEdit, QTreeWidget,
                              QTreeWidgetItem, QSplitter, QFrame, QSpacerItem,
                              QSizePolicy, QDialog, QDialogButtonBox, QScrollArea,
                              QGridLayout, QDoubleSpinBox, QProgressBar, QTableWidget,
                              QTableWidgetItem, QHeaderView, QMenu, QMessageBox)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QAction

from core.plugin_manager import BasePlugin
from ui.floating_panel import FloatingPanel


class ActionType(Enum):
    """Types of macro actions."""
    KEY_PRESS = "key_press"
    KEY_HOLD = "key_hold" 
    KEY_RELEASE = "key_release"
    MOUSE_CLICK = "mouse_click"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"
    DELAY = "delay"
    LOOP_START = "loop_start"
    LOOP_END = "loop_end"
    CONDITION = "condition"
    VARIABLE_SET = "variable_set"
    HOTKEY_TRIGGER = "hotkey_trigger"


@dataclass
class MacroAction:
    """Represents a single macro action."""
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    description: str = ""
    id: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(int(time.time() * 1000000))


@dataclass
class Macro:
    """Represents a complete macro with actions and settings."""
    name: str
    actions: List[MacroAction] = field(default_factory=list)
    hotkey: str = ""
    enabled: bool = True
    repeat_count: int = 1
    repeat_delay: float = 0.0
    description: str = ""
    category: str = "General"
    created_date: str = ""
    modified_date: str = ""
    id: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(int(time.time() * 1000000))
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()


class MacroExecutor(QThread):
    """Executes macros in a separate thread."""
    
    # Signals
    execution_started = Signal(str)  # macro_id
    execution_finished = Signal(str, bool)  # macro_id, success
    execution_progress = Signal(str, int, int)  # macro_id, current, total
    execution_error = Signal(str, str)  # macro_id, error_message
    action_executed = Signal(str, str)  # macro_id, action_description
    
    def __init__(self):
        super().__init__()
        self.macro = None
        self.variables = {}
        self.loop_stack = []
        self.should_stop = False
        self.is_paused = False
        self.logger = logging.getLogger("MacroExecutor")
    
    def execute_macro(self, macro: Macro, variables: Dict[str, Any] = None):
        """Execute a macro."""
        self.macro = macro
        self.variables = variables or {}
        self.should_stop = False
        self.is_paused = False
        self.start()
    
    def stop_execution(self):
        """Stop macro execution."""
        self.should_stop = True
    
    def pause_execution(self):
        """Pause macro execution."""
        self.is_paused = True
    
    def resume_execution(self):
        """Resume macro execution."""
        self.is_paused = False
    
    def run(self):
        """Main execution loop."""
        if not self.macro:
            return
        
        try:
            self.execution_started.emit(self.macro.id)
            
            for repeat in range(self.macro.repeat_count):
                if self.should_stop:
                    break
                
                self._execute_actions()
                
                if repeat < self.macro.repeat_count - 1 and self.macro.repeat_delay > 0:
                    time.sleep(self.macro.repeat_delay)
            
            self.execution_finished.emit(self.macro.id, not self.should_stop)
            
        except Exception as e:
            self.logger.error(f"Error executing macro {self.macro.name}: {e}")
            self.execution_error.emit(self.macro.id, str(e))
            self.execution_finished.emit(self.macro.id, False)
    
    def _execute_actions(self):
        """Execute all actions in the macro."""
        action_count = len(self.macro.actions)
        
        for i, action in enumerate(self.macro.actions):
            if self.should_stop:
                break
            
            # Handle pause
            while self.is_paused and not self.should_stop:
                time.sleep(0.1)
            
            if not action.enabled:
                continue
            
            try:
                self._execute_action(action)
                self.action_executed.emit(self.macro.id, action.description or f"{action.action_type.value}")
                self.execution_progress.emit(self.macro.id, i + 1, action_count)
                
            except Exception as e:
                self.logger.error(f"Error executing action {action.action_type}: {e}")
    
    def _execute_action(self, action: MacroAction):
        """Execute a single action."""
        if action.action_type == ActionType.KEY_PRESS:
            self._execute_key_press(action)
        elif action.action_type == ActionType.KEY_HOLD:
            self._execute_key_hold(action)
        elif action.action_type == ActionType.KEY_RELEASE:
            self._execute_key_release(action)
        elif action.action_type == ActionType.MOUSE_CLICK:
            self._execute_mouse_click(action)
        elif action.action_type == ActionType.MOUSE_MOVE:
            self._execute_mouse_move(action)
        elif action.action_type == ActionType.MOUSE_SCROLL:
            self._execute_mouse_scroll(action)
        elif action.action_type == ActionType.DELAY:
            self._execute_delay(action)
        elif action.action_type == ActionType.LOOP_START:
            self._execute_loop_start(action)
        elif action.action_type == ActionType.LOOP_END:
            self._execute_loop_end(action)
        elif action.action_type == ActionType.VARIABLE_SET:
            self._execute_variable_set(action)
    
    def _execute_key_press(self, action: MacroAction):
        """Execute key press action."""
        if not KEYBOARD_AVAILABLE:
            self.logger.error("Keyboard library not available")
            return
            
        key = action.parameters.get('key', '')
        if key:
            keyboard.press_and_release(key)
    
    def _execute_key_hold(self, action: MacroAction):
        """Execute key hold action."""
        if not KEYBOARD_AVAILABLE:
            self.logger.error("Keyboard library not available")
            return
            
        key = action.parameters.get('key', '')
        duration = action.parameters.get('duration', 0.1)
        if key:
            keyboard.press(key)
            time.sleep(duration)
            keyboard.release(key)
    
    def _execute_key_release(self, action: MacroAction):
        """Execute key release action."""
        if not KEYBOARD_AVAILABLE:
            self.logger.error("Keyboard library not available")
            return
            
        key = action.parameters.get('key', '')
        if key:
            keyboard.release(key)
    
    def _execute_mouse_click(self, action: MacroAction):
        """Execute mouse click action."""
        if not MOUSE_AVAILABLE:
            self.logger.error("Mouse library not available")
            return
            
        button = action.parameters.get('button', 'left')
        x = action.parameters.get('x', None)
        y = action.parameters.get('y', None)
        clicks = action.parameters.get('clicks', 1)
        
        if x is not None and y is not None:
            mouse.move(x, y)
        
        for _ in range(clicks):
            mouse.click(button)
    
    def _execute_mouse_move(self, action: MacroAction):
        """Execute mouse move action."""
        if not MOUSE_AVAILABLE:
            self.logger.error("Mouse library not available")
            return
            
        x = action.parameters.get('x', 0)
        y = action.parameters.get('y', 0)
        relative = action.parameters.get('relative', False)
        duration = action.parameters.get('duration', 0.0)
        
        if relative:
            current_x, current_y = mouse.get_position()
            x += current_x
            y += current_y
        
        if duration > 0:
            # Smooth movement
            current_x, current_y = mouse.get_position()
            steps = max(10, int(duration * 100))
            dx = (x - current_x) / steps
            dy = (y - current_y) / steps
            
            for i in range(steps):
                if self.should_stop:
                    break
                mouse.move(current_x + dx * i, current_y + dy * i)
                time.sleep(duration / steps)
        else:
            mouse.move(x, y)
    
    def _execute_mouse_scroll(self, action: MacroAction):
        """Execute mouse scroll action."""
        if not MOUSE_AVAILABLE:
            self.logger.error("Mouse library not available")
            return
            
        delta = action.parameters.get('delta', 1)
        mouse.wheel(delta)
    
    def _execute_delay(self, action: MacroAction):
        """Execute delay action."""
        duration = action.parameters.get('duration', 1.0)
        time.sleep(duration)
    
    def _execute_loop_start(self, action: MacroAction):
        """Execute loop start action."""
        iterations = action.parameters.get('iterations', 1)
        self.loop_stack.append({'iterations': iterations, 'current': 0})
    
    def _execute_loop_end(self, action: MacroAction):
        """Execute loop end action."""
        if self.loop_stack:
            loop_info = self.loop_stack[-1]
            loop_info['current'] += 1
            if loop_info['current'] < loop_info['iterations']:
                # Continue loop - find matching loop start
                pass
            else:
                # End loop
                self.loop_stack.pop()
    
    def _execute_variable_set(self, action: MacroAction):
        """Execute variable set action."""
        var_name = action.parameters.get('name', '')
        var_value = action.parameters.get('value', '')
        if var_name:
            self.variables[var_name] = var_value


class MultiHotkeyMacrosPlugin(BasePlugin):
    """Multi-Hotkey / Macros Plugin for advanced automation."""
    
    # Plugin metadata
    name = "Multi-Hotkey Macros"
    description = "Advanced macro system with hotkey combinations, loops, delays and mouse/keyboard automation"
    version = "1.0.0"
    author = "Party Brasil"
    
    def __init__(self, config_manager, thread_manager):
        super().__init__(config_manager, thread_manager)
        
        # Plugin components
        self.macros_widget = None
        self.panel_widget = None
        
        # Macro management
        self.macros: Dict[str, Macro] = {}
        self.hotkey_bindings: Dict[str, str] = {}  # hotkey -> macro_id
        self.macro_executor = MacroExecutor()
        self.currently_executing = None
        
        # Recording state
        self.is_recording = False
        self.recorded_actions = []
        self.recording_start_time = None
        
        # Global variables for macros
        self.global_variables = {}
        
        # Hotkey listener
        self.hotkey_thread = None
        self.hotkey_active = True
        
        # Status tracking
        self.execution_stats = {
            'total_executed': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'last_execution': None
        }
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        try:
            self.logger.info("Initializing Multi-Hotkey Macros plugin...")
            
            # Check dependencies
            missing_deps = []
            if not KEYBOARD_AVAILABLE:
                missing_deps.append("keyboard")
            if not MOUSE_AVAILABLE:
                missing_deps.append("mouse")
            
            if missing_deps:
                self.logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
                self.logger.warning("Install with: pip install " + " ".join(missing_deps))
                # Continue initialization but with limited functionality
            
            # Load saved macros
            self._load_macros()
            
            # Setup default configuration
            default_config = {
                'enabled': True,
                'global_hotkey_enabled': True and KEYBOARD_AVAILABLE,
                'recording_mouse': True and MOUSE_AVAILABLE,
                'recording_keyboard': True and KEYBOARD_AVAILABLE,
                'execution_delay': 0.01,
                'max_concurrent_macros': 5,
                'auto_save': True,
                'notification_enabled': True,
                'debug_mode': False
            }
            
            # Apply defaults for missing config
            for key, value in default_config.items():
                if key not in self.plugin_config:
                    self.plugin_config[key] = value
            
            # Setup macro executor
            self._setup_executor()
            
            # Start hotkey listener
            self._start_hotkey_listener()
            
            self.is_initialized = True
            self.logger.info("Multi-Hotkey Macros plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Multi-Hotkey Macros plugin: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def activate(self) -> bool:
        """Activate the plugin."""        
        # Initialize plugin if not already initialized
        if not self.is_initialized:
            if not self.initialize():
                self.logger.error("Plugin initialization failed, cannot activate")
                return False
        
        try:
            # Create the panel widget
            self.panel_widget = FloatingPanel(
                self.config_manager, 
                "Multi-Hotkey Macros"
            )
            
            # Create the main widget
            self.macros_widget = MacrosWidget(self)
            self.panel_widget.add_content_widget(self.macros_widget)
            
            # Connect panel signals
            self.panel_widget.close_requested.connect(self.deactivate)
            
            # Show the panel
            self.panel_widget.show()
            
            self.is_active = True
            self.status_changed.emit("Multi-Hotkey Macros activated")
            self.logger.info("Multi-Hotkey Macros plugin activated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to activate Multi-Hotkey Macros plugin: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the plugin."""
        try:
            # Hide the panel
            if self.panel_widget:
                self.panel_widget.hide()
                self.panel_widget = None
            
            # Stop any running macros
            self._stop_all_macros()
            
            self.is_active = False
            self.status_changed.emit("Multi-Hotkey Macros deactivated")
            self.logger.info("Multi-Hotkey Macros plugin deactivated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate Multi-Hotkey Macros plugin: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown the plugin."""
        try:
            # Stop hotkey listener
            self._stop_hotkey_listener()
            
            # Stop macro executor
            if self.macro_executor.isRunning():
                self.macro_executor.stop_execution()
                self.macro_executor.wait(5000)
            
            # Save macros
            self._save_macros()
            
            self.logger.info("Multi-Hotkey Macros plugin shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during Multi-Hotkey Macros plugin shutdown: {e}")
            return False
    
    def get_panel_widget(self):
        """Get the panel widget."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Get the configuration widget."""
        return MacrosConfigWidget(self)
    
    def _setup_executor(self):
        """Setup the macro executor."""
        self.macro_executor.execution_started.connect(self._on_execution_started)
        self.macro_executor.execution_finished.connect(self._on_execution_finished)
        self.macro_executor.execution_progress.connect(self._on_execution_progress)
        self.macro_executor.execution_error.connect(self._on_execution_error)
        self.macro_executor.action_executed.connect(self._on_action_executed)
    
    def _start_hotkey_listener(self):
        """Start the global hotkey listener."""
        if not self.plugin_config.get('global_hotkey_enabled', True):
            return
        
        if not KEYBOARD_AVAILABLE:
            self.logger.warning("Keyboard library not available - global hotkeys disabled")
            return
        
        def hotkey_listener():
            for hotkey, macro_id in self.hotkey_bindings.items():
                try:
                    keyboard.add_hotkey(hotkey, lambda mid=macro_id: self.execute_macro(mid))
                except Exception as e:
                    self.logger.error(f"Failed to bind hotkey {hotkey}: {e}")
        
        if self.hotkey_thread is None or not self.hotkey_thread.is_alive():
            self.hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
            self.hotkey_thread.start()
    
    def _stop_hotkey_listener(self):
        """Stop the global hotkey listener."""
        if not KEYBOARD_AVAILABLE:
            return
            
        try:
            keyboard.unhook_all_hotkeys()
        except Exception as e:
            self.logger.error(f"Error stopping hotkey listener: {e}")
    
    def _load_macros(self):
        """Load saved macros from configuration."""
        try:
            macros_data = self.plugin_config.get('saved_macros', {})
            
            for macro_id, macro_data in macros_data.items():
                # Convert actions from dict to MacroAction objects
                actions = []
                for action_data in macro_data.get('actions', []):
                    action = MacroAction(
                        action_type=ActionType(action_data['action_type']),
                        parameters=action_data.get('parameters', {}),
                        enabled=action_data.get('enabled', True),
                        description=action_data.get('description', ''),
                        id=action_data.get('id', '')
                    )
                    actions.append(action)
                
                # Create macro object
                macro = Macro(
                    name=macro_data['name'],
                    actions=actions,
                    hotkey=macro_data.get('hotkey', ''),
                    enabled=macro_data.get('enabled', True),
                    repeat_count=macro_data.get('repeat_count', 1),
                    repeat_delay=macro_data.get('repeat_delay', 0.0),
                    description=macro_data.get('description', ''),
                    category=macro_data.get('category', 'General'),
                    created_date=macro_data.get('created_date', ''),
                    modified_date=macro_data.get('modified_date', ''),
                    id=macro_id
                )
                
                self.macros[macro_id] = macro
                
                # Register hotkey if present
                if macro.hotkey and macro.enabled:
                    self.hotkey_bindings[macro.hotkey] = macro_id
            
            self.logger.info(f"Loaded {len(self.macros)} macros")
            
        except Exception as e:
            self.logger.error(f"Error loading macros: {e}")
    
    def _save_macros(self):
        """Save macros to configuration."""
        try:
            macros_data = {}
            
            for macro_id, macro in self.macros.items():
                # Convert actions to serializable format
                actions_data = []
                for action in macro.actions:
                    action_data = {
                        'action_type': action.action_type.value,
                        'parameters': action.parameters,
                        'enabled': action.enabled,
                        'description': action.description,
                        'id': action.id
                    }
                    actions_data.append(action_data)
                
                # Convert macro to serializable format
                macro_data = {
                    'name': macro.name,
                    'actions': actions_data,
                    'hotkey': macro.hotkey,
                    'enabled': macro.enabled,
                    'repeat_count': macro.repeat_count,
                    'repeat_delay': macro.repeat_delay,
                    'description': macro.description,
                    'category': macro.category,
                    'created_date': macro.created_date,
                    'modified_date': macro.modified_date
                }
                
                macros_data[macro_id] = macro_data
            
            self.plugin_config['saved_macros'] = macros_data
            self.save_config()
            
            self.logger.info(f"Saved {len(self.macros)} macros")
            
        except Exception as e:
            self.logger.error(f"Error saving macros: {e}")
    
    def create_macro(self, name: str, category: str = "General") -> str:
        """Create a new macro."""
        macro = Macro(name=name, category=category)
        self.macros[macro.id] = macro
        
        if self.plugin_config.get('auto_save', True):
            self._save_macros()
        
        self.data_updated.emit({'action': 'macro_created', 'macro_id': macro.id})
        return macro.id
    
    def delete_macro(self, macro_id: str) -> bool:
        """Delete a macro."""
        if macro_id not in self.macros:
            return False
        
        macro = self.macros[macro_id]
        
        # Remove hotkey binding
        if macro.hotkey in self.hotkey_bindings:
            del self.hotkey_bindings[macro.hotkey]
        
        # Delete macro
        del self.macros[macro_id]
        
        if self.plugin_config.get('auto_save', True):
            self._save_macros()
        
        self.data_updated.emit({'action': 'macro_deleted', 'macro_id': macro_id})
        return True
    
    def execute_macro(self, macro_id: str, variables: Dict[str, Any] = None):
        """Execute a macro by ID."""
        if macro_id not in self.macros:
            self.error_occurred.emit(f"Macro {macro_id} not found")
            return
        
        macro = self.macros[macro_id]
        
        if not macro.enabled:
            self.status_changed.emit(f"Macro '{macro.name}' is disabled")
            return
        
        # Check if already executing
        if self.macro_executor.isRunning():
            self.status_changed.emit("Another macro is already running")
            return
        
        # Execute macro
        self.currently_executing = macro_id
        merged_variables = {**self.global_variables, **(variables or {})}
        self.macro_executor.execute_macro(macro, merged_variables)
    
    def stop_macro(self):
        """Stop the currently executing macro."""
        if self.macro_executor.isRunning():
            self.macro_executor.stop_execution()
    
    def _stop_all_macros(self):
        """Stop all running macros."""
        self.stop_macro()
    
    def start_recording(self):
        """Start recording a new macro."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recorded_actions = []
        self.recording_start_time = time.time()
        
        # Start recording listeners
        self._start_recording_listeners()
        
        self.status_changed.emit("Recording started")
    
    def stop_recording(self) -> List[MacroAction]:
        """Stop recording and return recorded actions."""
        if not self.is_recording:
            return []
        
        self.is_recording = False
        self._stop_recording_listeners()
        
        actions = self.recorded_actions.copy()
        self.recorded_actions = []
        
        self.status_changed.emit("Recording stopped")
        return actions
    
    def _start_recording_listeners(self):
        """Start input recording listeners."""
        # This would implement keyboard and mouse recording
        # For now, this is a placeholder
        pass
    
    def _stop_recording_listeners(self):
        """Stop input recording listeners."""
        # This would stop the recording listeners
        # For now, this is a placeholder
        pass
    
    # Event handlers
    def _on_execution_started(self, macro_id: str):
        """Handle macro execution start."""
        if macro_id in self.macros:
            macro_name = self.macros[macro_id].name
            self.status_changed.emit(f"Executing macro: {macro_name}")
    
    def _on_execution_finished(self, macro_id: str, success: bool):
        """Handle macro execution finish."""
        self.currently_executing = None
        
        if success:
            self.execution_stats['successful_executions'] += 1
            self.status_changed.emit("Macro execution completed")
        else:
            self.execution_stats['failed_executions'] += 1
            self.status_changed.emit("Macro execution failed")
        
        self.execution_stats['total_executed'] += 1
        self.execution_stats['last_execution'] = datetime.now().isoformat()
    
    def _on_execution_progress(self, macro_id: str, current: int, total: int):
        """Handle macro execution progress."""
        self.data_updated.emit({
            'action': 'execution_progress',
            'macro_id': macro_id,
            'current': current,
            'total': total,
            'progress': int((current / total) * 100) if total > 0 else 0
        })
    
    def _on_execution_error(self, macro_id: str, error_message: str):
        """Handle macro execution error."""
        self.error_occurred.emit(f"Macro execution error: {error_message}")
    
    def _on_action_executed(self, macro_id: str, action_description: str):
        """Handle individual action execution."""
        self.data_updated.emit({
            'action': 'action_executed',
            'macro_id': macro_id,
            'description': action_description
        })


class MacrosWidget(QWidget):
    """Main widget for macro management and execution."""
    
    def __init__(self, plugin: MultiHotkeyMacrosPlugin):
        super().__init__()
        self.plugin = plugin
        self.current_macro = None
        
        self._setup_ui()
        self._connect_signals()
        self._refresh_macro_list()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Multi-Hotkey Macros")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Quick execute button
        self.quick_execute_btn = QPushButton("▶ Execute")
        self.quick_execute_btn.setEnabled(False)
        self.quick_execute_btn.clicked.connect(self._execute_selected_macro)
        header_layout.addWidget(self.quick_execute_btn)
        
        # Stop button
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.plugin.stop_macro)
        header_layout.addWidget(self.stop_btn)
        
        layout.addLayout(header_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Macro list
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        
        # Macro list
        macros_label = QLabel("Saved Macros")
        macros_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(macros_label)
        
        self.macro_list = QListWidget()
        self.macro_list.itemSelectionChanged.connect(self._on_macro_selected)
        left_layout.addWidget(self.macro_list)
        
        # Macro management buttons
        macro_buttons_layout = QGridLayout()
        
        self.new_macro_btn = QPushButton("+ New")
        self.new_macro_btn.clicked.connect(self._create_new_macro)
        macro_buttons_layout.addWidget(self.new_macro_btn, 0, 0)
        
        self.edit_macro_btn = QPushButton("✏ Edit")
        self.edit_macro_btn.setEnabled(False)
        self.edit_macro_btn.clicked.connect(self._edit_selected_macro)
        macro_buttons_layout.addWidget(self.edit_macro_btn, 0, 1)
        
        self.delete_macro_btn = QPushButton("🗑 Delete")
        self.delete_macro_btn.setEnabled(False)
        self.delete_macro_btn.clicked.connect(self._delete_selected_macro)
        macro_buttons_layout.addWidget(self.delete_macro_btn, 1, 0)
        
        self.clone_macro_btn = QPushButton("📋 Clone")
        self.clone_macro_btn.setEnabled(False)
        self.clone_macro_btn.clicked.connect(self._clone_selected_macro)
        macro_buttons_layout.addWidget(self.clone_macro_btn, 1, 1)
        
        left_layout.addLayout(macro_buttons_layout)
        
        # Recording section
        recording_group = QGroupBox("Recording")
        recording_layout = QVBoxLayout(recording_group)
        
        self.record_btn = QPushButton("🔴 Start Recording")
        self.record_btn.clicked.connect(self._toggle_recording)
        recording_layout.addWidget(self.record_btn)
        
        self.recording_status = QLabel("Ready to record")
        self.recording_status.setStyleSheet("color: #666;")
        recording_layout.addWidget(self.recording_status)
        
        left_layout.addWidget(recording_group)
        
        # Right side - Macro details
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        # Macro info
        info_label = QLabel("Macro Details")
        info_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(info_label)
        
        self.macro_info = QTextEdit()
        self.macro_info.setMaximumHeight(100)
        self.macro_info.setReadOnly(True)
        right_layout.addWidget(self.macro_info)
        
        # Execution status
        status_group = QGroupBox("Execution Status")
        status_layout = QVBoxLayout(status_group)
        
        self.execution_status = QLabel("No macro running")
        status_layout.addWidget(self.execution_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        right_layout.addWidget(status_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.total_executed_label = QLabel("0")
        self.successful_executions_label = QLabel("0")
        self.failed_executions_label = QLabel("0")
        
        stats_layout.addRow("Total Executed:", self.total_executed_label)
        stats_layout.addRow("Successful:", self.successful_executions_label)
        stats_layout.addRow("Failed:", self.failed_executions_label)
        
        right_layout.addWidget(stats_group)
        
        right_layout.addStretch()
        
        # Add to splitter
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
    
    def _connect_signals(self):
        """Connect plugin signals."""
        self.plugin.status_changed.connect(self._on_status_changed)
        self.plugin.data_updated.connect(self._on_data_updated)
        self.plugin.error_occurred.connect(self._on_error_occurred)
    
    def _refresh_macro_list(self):
        """Refresh the macro list."""
        self.macro_list.clear()
        
        for macro_id, macro in self.plugin.macros.items():
            item = QListWidgetItem()
            
            # Create display text
            display_text = f"{macro.name}"
            if macro.hotkey:
                display_text += f" ({macro.hotkey})"
            if not macro.enabled:
                display_text += " [DISABLED]"
            
            item.setText(display_text)
            item.setData(Qt.UserRole, macro_id)
            
            # Set color based on status
            if not macro.enabled:
                item.setForeground(QColor("#999"))
            elif macro.hotkey:
                item.setForeground(QColor("#2196F3"))
            
            self.macro_list.addItem(item)
    
    def _on_macro_selected(self):
        """Handle macro selection."""
        current_item = self.macro_list.currentItem()
        has_selection = current_item is not None
        
        self.edit_macro_btn.setEnabled(has_selection)
        self.delete_macro_btn.setEnabled(has_selection)
        self.clone_macro_btn.setEnabled(has_selection)
        self.quick_execute_btn.setEnabled(has_selection)
        
        if has_selection:
            macro_id = current_item.data(Qt.UserRole)
            self.current_macro = self.plugin.macros.get(macro_id)
            self._update_macro_info()
        else:
            self.current_macro = None
            self.macro_info.clear()
    
    def _update_macro_info(self):
        """Update macro information display."""
        if not self.current_macro:
            return
        
        info_text = f"""
        <b>Name:</b> {self.current_macro.name}<br>
        <b>Category:</b> {self.current_macro.category}<br>
        <b>Hotkey:</b> {self.current_macro.hotkey or 'None'}<br>
        <b>Actions:</b> {len(self.current_macro.actions)}<br>
        <b>Repeat:</b> {self.current_macro.repeat_count} times<br>
        <b>Enabled:</b> {'Yes' if self.current_macro.enabled else 'No'}<br>
        <b>Description:</b> {self.current_macro.description or 'No description'}
        """
        
        self.macro_info.setHtml(info_text)
    
    def _create_new_macro(self):
        """Create a new macro."""
        # This would open a macro editor dialog
        macro_id = self.plugin.create_macro("New Macro")
        self._refresh_macro_list()
        
        # Select the new macro
        for i in range(self.macro_list.count()):
            item = self.macro_list.item(i)
            if item.data(Qt.UserRole) == macro_id:
                self.macro_list.setCurrentItem(item)
                break
    
    def _edit_selected_macro(self):
        """Edit the selected macro."""
        if not self.current_macro:
            return
        
        # This would open a macro editor dialog
        QMessageBox.information(self, "Edit Macro", "Macro editor would open here")
    
    def _delete_selected_macro(self):
        """Delete the selected macro."""
        if not self.current_macro:
            return
        
        reply = QMessageBox.question(
            self, 
            "Delete Macro",
            f"Are you sure you want to delete '{self.current_macro.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.plugin.delete_macro(self.current_macro.id)
            self._refresh_macro_list()
    
    def _clone_selected_macro(self):
        """Clone the selected macro."""
        if not self.current_macro:
            return
        
        # Create a copy of the macro
        cloned_macro = Macro(
            name=f"{self.current_macro.name} (Copy)",
            actions=self.current_macro.actions.copy(),
            hotkey="",  # Clear hotkey for clone
            enabled=self.current_macro.enabled,
            repeat_count=self.current_macro.repeat_count,
            repeat_delay=self.current_macro.repeat_delay,
            description=self.current_macro.description,
            category=self.current_macro.category
        )
        
        self.plugin.macros[cloned_macro.id] = cloned_macro
        
        if self.plugin.plugin_config.get('auto_save', True):
            self.plugin._save_macros()
        
        self._refresh_macro_list()
    
    def _execute_selected_macro(self):
        """Execute the selected macro."""
        if not self.current_macro:
            return
        
        self.plugin.execute_macro(self.current_macro.id)
    
    def _toggle_recording(self):
        """Toggle macro recording."""
        if self.plugin.is_recording:
            # Stop recording
            actions = self.plugin.stop_recording()
            self.record_btn.setText("🔴 Start Recording")
            self.recording_status.setText(f"Recorded {len(actions)} actions")
            
            # If we have actions, ask to save as macro
            if actions:
                reply = QMessageBox.question(
                    self,
                    "Save Recording",
                    "Save recorded actions as a new macro?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    macro_id = self.plugin.create_macro("Recorded Macro")
                    self.plugin.macros[macro_id].actions = actions
                    self.plugin._save_macros()
                    self._refresh_macro_list()
        else:
            # Start recording
            self.plugin.start_recording()
            self.record_btn.setText("⏹ Stop Recording")
            self.recording_status.setText("Recording in progress...")
    
    def _on_status_changed(self, message: str):
        """Handle plugin status changes."""
        self.execution_status.setText(message)
    
    def _on_data_updated(self, data: dict):
        """Handle plugin data updates."""
        action = data.get('action')
        
        if action == 'execution_progress':
            progress = data.get('progress', 0)
            self.progress_bar.setValue(progress)
            self.progress_bar.setVisible(progress > 0 and progress < 100)
        elif action in ['macro_created', 'macro_deleted']:
            self._refresh_macro_list()
        
        # Update statistics
        stats = self.plugin.execution_stats
        self.total_executed_label.setText(str(stats['total_executed']))
        self.successful_executions_label.setText(str(stats['successful_executions']))
        self.failed_executions_label.setText(str(stats['failed_executions']))
    
    def _on_error_occurred(self, error_message: str):
        """Handle plugin errors."""
        QMessageBox.warning(self, "Error", error_message)


class MacrosConfigWidget(QWidget):
    """Configuration widget for the control panel."""
    
    def __init__(self, plugin: MultiHotkeyMacrosPlugin):
        super().__init__()
        self.plugin = plugin
        
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the configuration UI."""
        layout = QVBoxLayout(self)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout(general_group)
        
        self.enabled_checkbox = QCheckBox()
        general_layout.addRow("Plugin Enabled:", self.enabled_checkbox)
        
        self.global_hotkey_checkbox = QCheckBox()
        general_layout.addRow("Global Hotkeys:", self.global_hotkey_checkbox)
        
        self.auto_save_checkbox = QCheckBox()
        general_layout.addRow("Auto Save:", self.auto_save_checkbox)
        
        self.notification_checkbox = QCheckBox()
        general_layout.addRow("Notifications:", self.notification_checkbox)
        
        layout.addWidget(general_group)
        
        # Recording settings
        recording_group = QGroupBox("Recording Settings")
        recording_layout = QFormLayout(recording_group)
        
        self.record_mouse_checkbox = QCheckBox()
        recording_layout.addRow("Record Mouse:", self.record_mouse_checkbox)
        
        self.record_keyboard_checkbox = QCheckBox()
        recording_layout.addRow("Record Keyboard:", self.record_keyboard_checkbox)
        
        layout.addWidget(recording_group)
        
        # Execution settings
        execution_group = QGroupBox("Execution Settings")
        execution_layout = QFormLayout(execution_group)
        
        self.execution_delay_spinbox = QDoubleSpinBox()
        self.execution_delay_spinbox.setRange(0.0, 10.0)
        self.execution_delay_spinbox.setSingleStep(0.01)
        self.execution_delay_spinbox.setSuffix(" seconds")
        execution_layout.addRow("Execution Delay:", self.execution_delay_spinbox)
        
        self.max_concurrent_spinbox = QSpinBox()
        self.max_concurrent_spinbox.setRange(1, 20)
        execution_layout.addRow("Max Concurrent Macros:", self.max_concurrent_spinbox)
        
        layout.addWidget(execution_group)
        
        # Debug settings
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QFormLayout(debug_group)
        
        self.debug_mode_checkbox = QCheckBox()
        debug_layout.addRow("Debug Mode:", self.debug_mode_checkbox)
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
    
    def _load_settings(self):
        """Load settings from plugin configuration."""
        config = self.plugin.plugin_config
        
        self.enabled_checkbox.setChecked(config.get('enabled', True))
        self.global_hotkey_checkbox.setChecked(config.get('global_hotkey_enabled', True))
        self.auto_save_checkbox.setChecked(config.get('auto_save', True))
        self.notification_checkbox.setChecked(config.get('notification_enabled', True))
        self.record_mouse_checkbox.setChecked(config.get('recording_mouse', True))
        self.record_keyboard_checkbox.setChecked(config.get('recording_keyboard', True))
        self.execution_delay_spinbox.setValue(config.get('execution_delay', 0.01))
        self.max_concurrent_spinbox.setValue(config.get('max_concurrent_macros', 5))
        self.debug_mode_checkbox.setChecked(config.get('debug_mode', False))
    
    def _connect_signals(self):
        """Connect signal handlers."""
        self.enabled_checkbox.toggled.connect(self._save_settings)
        self.global_hotkey_checkbox.toggled.connect(self._save_settings)
        self.auto_save_checkbox.toggled.connect(self._save_settings)
        self.notification_checkbox.toggled.connect(self._save_settings)
        self.record_mouse_checkbox.toggled.connect(self._save_settings)
        self.record_keyboard_checkbox.toggled.connect(self._save_settings)
        self.execution_delay_spinbox.valueChanged.connect(self._save_settings)
        self.max_concurrent_spinbox.valueChanged.connect(self._save_settings)
        self.debug_mode_checkbox.toggled.connect(self._save_settings)
    
    def _save_settings(self):
        """Save settings to plugin configuration."""
        config = self.plugin.plugin_config
        
        config['enabled'] = self.enabled_checkbox.isChecked()
        config['global_hotkey_enabled'] = self.global_hotkey_checkbox.isChecked()
        config['auto_save'] = self.auto_save_checkbox.isChecked()
        config['notification_enabled'] = self.notification_checkbox.isChecked()
        config['recording_mouse'] = self.record_mouse_checkbox.isChecked()
        config['recording_keyboard'] = self.record_keyboard_checkbox.isChecked()
        config['execution_delay'] = self.execution_delay_spinbox.value()
        config['max_concurrent_macros'] = self.max_concurrent_spinbox.value()
        config['debug_mode'] = self.debug_mode_checkbox.isChecked()
        
        self.plugin.save_config()
