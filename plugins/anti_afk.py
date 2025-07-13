"""
Anti-AFK Plugin
Prevents AFK kicks by simulating mouse and keyboard inputs automatically.
"""
import time
import random
import logging
import win32api
import win32con
import win32gui
import win32process
import psutil
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QComboBox, QSpinBox, QGroupBox, QCheckBox,
                              QSlider, QTabWidget, QFormLayout, QLineEdit,
                              QListWidget, QListWidgetItem, QTextEdit)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor

from core.plugin_manager import BasePlugin
from ui.floating_panel import FloatingPanel


class AntiAFKPlugin(BasePlugin):
    """Anti-AFK Plugin to prevent being kicked for inactivity."""
    
    # Plugin metadata
    name = "Anti-AFK Emulation"
    description = "Prevents AFK kicks by simulating mouse and keyboard inputs automatically"
    version = "1.0.0"
    author = "Party Brasil"
    
    def __init__(self, config_manager, thread_manager):
        super().__init__(config_manager, thread_manager)
        
        # Plugin components
        self.anti_afk_widget = None
        self.panel_widget = None
        
        # AFK prevention state
        self.is_anti_afk_active = False
        self.current_game_window = None
        self.last_input_time = time.time()
        
        # Timers
        self.afk_timer = QTimer()
        self.afk_timer.timeout.connect(self._execute_anti_afk_action)
        
        self.game_detection_timer = QTimer()
        self.game_detection_timer.timeout.connect(self._detect_active_game)
        self.game_detection_timer.start(2000)  # Check every 2 seconds
        
        # Default configuration
        default_config = {
            'enabled': True,
            'interval_min': 30,  # Minimum seconds between actions
            'interval_max': 60,  # Maximum seconds between actions
            'mouse_enabled': True,
            'keyboard_enabled': True,
            'mouse_movement_range': 10,  # Pixels to move mouse
            'keyboard_keys': ['space', 'w', 'a', 's', 'd'],
            'only_in_games': True,
            'game_whitelist': [],  # Specific games to work with
            'game_blacklist': [],  # Games to avoid
            'smart_detection': True,  # Detect if user is active
            'safe_mode': True,  # More conservative inputs
            'action_type': 'random',  # 'random', 'mouse_only', 'keyboard_only'
            'last_activity_threshold': 30,  # Seconds of inactivity before starting
        }
        
        # Merge with existing config
        for key, value in default_config.items():
            if key not in self.plugin_config:
                self.plugin_config[key] = value
    
    def initialize(self) -> bool:
        """Initialize the Anti-AFK plugin."""
        try:
            # Create main widget
            self.anti_afk_widget = AntiAFKWidget(self)
            
            # Create floating panel
            self.panel_widget = FloatingPanel(self.config_manager, "Anti-AFK Emulation")
            self.panel_widget.add_content_widget(self.anti_afk_widget)
            
            # Connect signals
            self.panel_widget.close_requested.connect(self.deactivate)
            self.anti_afk_widget.toggle_requested.connect(self._toggle_anti_afk)
            self.anti_afk_widget.config_changed.connect(self._on_config_changed)
            
            self.logger.info("Anti-AFK plugin initialized successfully")
            return super().initialize()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize Anti-AFK plugin: {e}")
            return False
    
    def activate(self) -> bool:
        """Activate the Anti-AFK plugin."""
        try:
            if super().activate():
                if self.panel_widget:
                    self.panel_widget.show()
                    self.status_changed.emit("Anti-AFK plugin activated")
                return True
            return False
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to activate Anti-AFK plugin: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the Anti-AFK plugin."""
        try:
            # Stop Anti-AFK if running
            self._stop_anti_afk()
            
            if self.panel_widget:
                self.panel_widget.hide()
            
            self.status_changed.emit("Anti-AFK plugin deactivated")
            return super().deactivate()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to deactivate Anti-AFK plugin: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown the Anti-AFK plugin."""
        try:
            self._stop_anti_afk()
            
            if self.afk_timer:
                self.afk_timer.stop()
            
            if self.game_detection_timer:
                self.game_detection_timer.stop()
            
            return super().shutdown()
            
        except Exception as e:
            self.logger.error(f"Error during Anti-AFK plugin shutdown: {e}")
            return False
    
    def get_panel_widget(self):
        """Return the plugin's main panel widget."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Return a configuration widget for the control panel."""
        return AntiAFKConfigWidget(self)
    
    def _toggle_anti_afk(self):
        """Toggle Anti-AFK functionality."""
        if self.is_anti_afk_active:
            self._stop_anti_afk()
        else:
            self._start_anti_afk()
    
    def _start_anti_afk(self):
        """Start Anti-AFK functionality."""
        try:
            if not self.plugin_config.get('enabled', True):
                self.status_changed.emit("Anti-AFK is disabled in settings")
                return
            
            # Check if we should only work in games
            if self.plugin_config.get('only_in_games', True):
                if not self._is_game_active():
                    self.status_changed.emit("No game detected - Anti-AFK not started")
                    return
            
            self.is_anti_afk_active = True
            self.last_input_time = time.time()
            
            # Calculate random interval
            min_interval = self.plugin_config.get('interval_min', 30)
            max_interval = self.plugin_config.get('interval_max', 60)
            interval = random.randint(min_interval, max_interval) * 1000  # Convert to ms
            
            self.afk_timer.start(interval)
            
            self.status_changed.emit("Anti-AFK started")
            self.data_updated.emit({"status": "active", "next_action_in": interval // 1000})
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to start Anti-AFK: {e}")
    
    def _stop_anti_afk(self):
        """Stop Anti-AFK functionality."""
        self.is_anti_afk_active = False
        self.afk_timer.stop()
        self.status_changed.emit("Anti-AFK stopped")
        self.data_updated.emit({"status": "inactive"})
    
    def _execute_anti_afk_action(self):
        """Execute an anti-AFK action."""
        try:
            # Check if user has been active recently
            if self._is_user_recently_active():
                self.status_changed.emit("User activity detected - skipping action")
                self._schedule_next_action()
                return
            
            # Check if game is still active (if required)
            if self.plugin_config.get('only_in_games', True):
                if not self._is_game_active():
                    self.status_changed.emit("Game no longer active - stopping Anti-AFK")
                    self._stop_anti_afk()
                    return
            
            # Determine action type
            action_type = self.plugin_config.get('action_type', 'random')
            
            if action_type == 'random':
                action = random.choice(['mouse', 'keyboard'])
            elif action_type == 'mouse_only':
                action = 'mouse'
            elif action_type == 'keyboard_only':
                action = 'keyboard'
            else:
                action = 'mouse'  # Default fallback
            
            # Execute the action
            if action == 'mouse' and self.plugin_config.get('mouse_enabled', True):
                self._simulate_mouse_movement()
            elif action == 'keyboard' and self.plugin_config.get('keyboard_enabled', True):
                self._simulate_key_press()
            
            self.last_input_time = time.time()
            self._schedule_next_action()
            
        except Exception as e:
            self.error_occurred.emit(f"Error executing Anti-AFK action: {e}")
            self._schedule_next_action()
    
    def _simulate_mouse_movement(self):
        """Simulate small mouse movement."""
        try:
            # Get current cursor position
            current_pos = win32gui.GetCursorPos()
            
            # Calculate small random movement
            movement_range = self.plugin_config.get('mouse_movement_range', 10)
            dx = random.randint(-movement_range, movement_range)
            dy = random.randint(-movement_range, movement_range)
            
            # Apply safe mode constraints
            if self.plugin_config.get('safe_mode', True):
                dx = max(-5, min(5, dx))  # Limit to ±5 pixels
                dy = max(-5, min(5, dy))
            
            new_x = current_pos[0] + dx
            new_y = current_pos[1] + dy
            
            # Move cursor
            win32api.SetCursorPos((new_x, new_y))
            
            # Optional: Move back to original position after a short delay
            if self.plugin_config.get('safe_mode', True):
                time.sleep(0.1)
                win32api.SetCursorPos(current_pos)
            
            self.status_changed.emit(f"Mouse moved by ({dx}, {dy})")
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to simulate mouse movement: {e}")
    
    def _simulate_key_press(self):
        """Simulate a key press."""
        try:
            keys = self.plugin_config.get('keyboard_keys', ['space'])
            if not keys:
                return
            
            # Choose random key
            key = random.choice(keys)
            
            # Map key names to virtual key codes
            key_map = {
                'space': win32con.VK_SPACE,
                'w': ord('W'),
                'a': ord('A'),
                's': ord('S'),
                'd': ord('D'),
                'shift': win32con.VK_SHIFT,
                'ctrl': win32con.VK_CONTROL,
                'alt': win32con.VK_MENU,
                'tab': win32con.VK_TAB,
                'escape': win32con.VK_ESCAPE,
            }
            
            vk_code = key_map.get(key.lower(), win32con.VK_SPACE)
            
            # Send key press
            win32api.keybd_event(vk_code, 0, 0, 0)  # Key down
            time.sleep(0.05)  # Brief hold
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            
            self.status_changed.emit(f"Key pressed: {key}")
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to simulate key press: {e}")
    
    def _schedule_next_action(self):
        """Schedule the next Anti-AFK action."""
        if self.is_anti_afk_active:
            min_interval = self.plugin_config.get('interval_min', 30)
            max_interval = self.plugin_config.get('interval_max', 60)
            interval = random.randint(min_interval, max_interval) * 1000
            
            self.afk_timer.start(interval)
            self.data_updated.emit({"next_action_in": interval // 1000})
    
    def _detect_active_game(self):
        """Detect if a game is currently active."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                try:
                    process = psutil.Process(pid)
                    process_name = process.name().lower()
                    
                    # Update current game info
                    self.current_game_window = {
                        'title': window_title,
                        'process': process_name,
                        'pid': pid,
                        'hwnd': hwnd
                    }
                    
                    self.data_updated.emit({"current_window": window_title, "process": process_name})
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self.current_game_window = None
            
        except Exception as e:
            pass  # Silent fail for game detection
    
    def _is_game_active(self):
        """Check if a game is currently active."""
        if not self.current_game_window:
            return False
        
        # Check whitelist
        whitelist = self.plugin_config.get('game_whitelist', [])
        if whitelist:
            process_name = self.current_game_window.get('process', '').lower()
            title = self.current_game_window.get('title', '').lower()
            
            for game in whitelist:
                if game.lower() in process_name or game.lower() in title:
                    return True
            return False
        
        # Check blacklist
        blacklist = self.plugin_config.get('game_blacklist', [])
        if blacklist:
            process_name = self.current_game_window.get('process', '').lower()
            title = self.current_game_window.get('title', '').lower()
            
            for game in blacklist:
                if game.lower() in process_name or game.lower() in title:
                    return False
        
        # Basic game detection heuristics
        if self.plugin_config.get('smart_detection', True):
            window_title = self.current_game_window.get('title', '').lower()
            process_name = self.current_game_window.get('process', '').lower()
            
            # Common game indicators
            game_indicators = [
                'steam', 'epic', 'origin', 'uplay', 'battle.net', 'gog',
                'minecraft', 'roblox', 'unity', 'unreal', 'gamemode',
                '.exe', 'game', 'online', 'multiplayer', 'fps', 'mmo'
            ]
            
            # Check if it's likely a game
            for indicator in game_indicators:
                if indicator in window_title or indicator in process_name:
                    return True
        
        return True  # Default to true if no specific filtering
    
    def _is_user_recently_active(self):
        """Check if user has been active recently."""
        if not self.plugin_config.get('smart_detection', True):
            return False
        
        threshold = self.plugin_config.get('last_activity_threshold', 30)
        time_since_last_action = time.time() - self.last_input_time
        
        return time_since_last_action < threshold
    
    def _on_config_changed(self):
        """Handle configuration changes."""
        self.save_config()
        
        # Restart timer if active with new intervals
        if self.is_anti_afk_active:
            self.afk_timer.stop()
            self._schedule_next_action()


class AntiAFKWidget(QWidget):
    """Main widget for Anti-AFK controls."""
    
    toggle_requested = Signal()
    config_changed = Signal()
    
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._setup_ui()
        self._connect_signals()
        self._update_display()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second
    
    def _setup_ui(self):
        """Setup the Anti-AFK widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Status display
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Inactive")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #555;
                border-radius: 5px;
                background: rgba(50, 50, 50, 100);
            }
        """)
        status_layout.addWidget(self.status_label)
        
        self.game_label = QLabel("No game detected")
        self.game_label.setAlignment(Qt.AlignCenter)
        self.game_label.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        status_layout.addWidget(self.game_label)
        
        self.next_action_label = QLabel("")
        self.next_action_label.setAlignment(Qt.AlignCenter)
        self.next_action_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
        status_layout.addWidget(self.next_action_label)
        
        layout.addWidget(status_group)
        
        # Control buttons
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Toggle button
        self.toggle_btn = QPushButton("Start Anti-AFK")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
                background: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background: #2ecc71;
            }
            QPushButton:pressed {
                background: #229954;
            }
        """)
        controls_layout.addWidget(self.toggle_btn)
        
        # Quick settings
        settings_layout = QHBoxLayout()
        
        # Interval setting
        settings_layout.addWidget(QLabel("Interval:"))
        self.interval_min_spin = QSpinBox()
        self.interval_min_spin.setRange(10, 300)
        self.interval_min_spin.setSuffix("s")
        self.interval_min_spin.setValue(self.plugin.plugin_config.get('interval_min', 30))
        settings_layout.addWidget(self.interval_min_spin)
        
        settings_layout.addWidget(QLabel("to"))
        
        self.interval_max_spin = QSpinBox()
        self.interval_max_spin.setRange(10, 600)
        self.interval_max_spin.setSuffix("s")
        self.interval_max_spin.setValue(self.plugin.plugin_config.get('interval_max', 60))
        settings_layout.addWidget(self.interval_max_spin)
        
        controls_layout.addLayout(settings_layout)
        
        # Action type
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Random", "Mouse Only", "Keyboard Only"])
        action_types = {"random": 0, "mouse_only": 1, "keyboard_only": 2}
        current_action = self.plugin.plugin_config.get('action_type', 'random')
        self.action_combo.setCurrentIndex(action_types.get(current_action, 0))
        action_layout.addWidget(self.action_combo)
        
        controls_layout.addLayout(action_layout)
        
        # Checkboxes
        self.only_games_cb = QCheckBox("Only in games")
        self.only_games_cb.setChecked(self.plugin.plugin_config.get('only_in_games', True))
        controls_layout.addWidget(self.only_games_cb)
        
        self.safe_mode_cb = QCheckBox("Safe mode (minimal movement)")
        self.safe_mode_cb.setChecked(self.plugin.plugin_config.get('safe_mode', True))
        controls_layout.addWidget(self.safe_mode_cb)
        
        layout.addWidget(controls_group)
        
        # Advanced button
        self.advanced_btn = QPushButton("Advanced Settings")
        self.advanced_btn.setStyleSheet("""
            QPushButton {
                background: #34495e;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #5d6d7e;
            }
        """)
        layout.addWidget(self.advanced_btn)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.toggle_btn.clicked.connect(self.toggle_requested.emit)
        self.interval_min_spin.valueChanged.connect(self._on_settings_changed)
        self.interval_max_spin.valueChanged.connect(self._on_settings_changed)
        self.action_combo.currentTextChanged.connect(self._on_settings_changed)
        self.only_games_cb.toggled.connect(self._on_settings_changed)
        self.safe_mode_cb.toggled.connect(self._on_settings_changed)
        self.advanced_btn.clicked.connect(self._show_advanced_settings)
        
        # Plugin signals
        self.plugin.status_changed.connect(self._on_status_changed)
        self.plugin.data_updated.connect(self._on_data_updated)
    
    def _update_display(self):
        """Update the display with current information."""
        # Update status
        if self.plugin.is_anti_afk_active:
            self.status_label.setText("🟢 ACTIVE")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    border: 2px solid #27ae60;
                    border-radius: 5px;
                    background: rgba(39, 174, 96, 50);
                    color: #27ae60;
                }
            """)
            self.toggle_btn.setText("Stop Anti-AFK")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    background: #e74c3c;
                    color: white;
                }
                QPushButton:hover {
                    background: #c0392b;
                }
            """)
        else:
            self.status_label.setText("🔴 INACTIVE")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    border: 2px solid #555;
                    border-radius: 5px;
                    background: rgba(50, 50, 50, 100);
                    color: #bdc3c7;
                }
            """)
            self.toggle_btn.setText("Start Anti-AFK")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    background: #27ae60;
                    color: white;
                }
                QPushButton:hover {
                    background: #2ecc71;
                }
            """)
        
        # Update game detection
        if self.plugin.current_game_window:
            title = self.plugin.current_game_window.get('title', 'Unknown')
            process = self.plugin.current_game_window.get('process', 'unknown')
            self.game_label.setText(f"🎮 {title[:30]}{'...' if len(title) > 30 else ''}")
        else:
            self.game_label.setText("No game detected")
    
    def _on_status_changed(self, message):
        """Handle status change signals."""
        # This could be used to show notifications or update status
        pass
    
    def _on_data_updated(self, data):
        """Handle data update signals."""
        if "next_action_in" in data:
            seconds = data["next_action_in"]
            self.next_action_label.setText(f"Next action in: {seconds}s")
        
        if "current_window" in data:
            self._update_display()
    
    def _on_settings_changed(self):
        """Handle settings changes."""
        # Update plugin configuration
        action_map = {"Random": "random", "Mouse Only": "mouse_only", "Keyboard Only": "keyboard_only"}
        
        self.plugin.plugin_config['interval_min'] = self.interval_min_spin.value()
        self.plugin.plugin_config['interval_max'] = self.interval_max_spin.value()
        self.plugin.plugin_config['action_type'] = action_map.get(self.action_combo.currentText(), 'random')
        self.plugin.plugin_config['only_in_games'] = self.only_games_cb.isChecked()
        self.plugin.plugin_config['safe_mode'] = self.safe_mode_cb.isChecked()
        
        # Validate intervals
        if self.interval_min_spin.value() > self.interval_max_spin.value():
            self.interval_max_spin.setValue(self.interval_min_spin.value())
            self.plugin.plugin_config['interval_max'] = self.interval_min_spin.value()
        
        self.config_changed.emit()
    
    def _show_advanced_settings(self):
        """Show advanced settings dialog."""
        try:
            from plugins.anti_afk_advanced import AntiAFKAdvancedDialog
            dialog = AntiAFKAdvancedDialog(self.plugin, self)
            dialog.exec()
        except ImportError:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Advanced Settings", 
                                  "Advanced settings dialog is not available yet.")


class AntiAFKConfigWidget(QWidget):
    """Configuration widget for the control panel."""
    
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup configuration UI."""
        layout = QVBoxLayout(self)
        
        # Enable/Disable
        self.enabled_cb = QCheckBox("Enable Anti-AFK Plugin")
        layout.addWidget(self.enabled_cb)
        
        # Timing settings
        timing_group = QGroupBox("Timing Settings")
        timing_layout = QFormLayout(timing_group)
        
        self.interval_min_spin = QSpinBox()
        self.interval_min_spin.setRange(5, 300)
        self.interval_min_spin.setSuffix(" seconds")
        timing_layout.addRow("Minimum Interval:", self.interval_min_spin)
        
        self.interval_max_spin = QSpinBox()
        self.interval_max_spin.setRange(5, 600)
        self.interval_max_spin.setSuffix(" seconds")
        timing_layout.addRow("Maximum Interval:", self.interval_max_spin)
        
        layout.addWidget(timing_group)
        
        # Action settings
        action_group = QGroupBox("Action Settings")
        action_layout = QFormLayout(action_group)
        
        self.mouse_enabled_cb = QCheckBox("Enable mouse movements")
        action_layout.addRow(self.mouse_enabled_cb)
        
        self.keyboard_enabled_cb = QCheckBox("Enable keyboard inputs")
        action_layout.addRow(self.keyboard_enabled_cb)
        
        self.safe_mode_cb = QCheckBox("Safe mode (minimal inputs)")
        action_layout.addRow(self.safe_mode_cb)
        
        layout.addWidget(action_group)
        
        # Game detection settings
        game_group = QGroupBox("Game Detection")
        game_layout = QFormLayout(game_group)
        
        self.only_games_cb = QCheckBox("Only activate in games")
        game_layout.addRow(self.only_games_cb)
        
        self.smart_detection_cb = QCheckBox("Smart user activity detection")
        game_layout.addRow(self.smart_detection_cb)
        
        layout.addWidget(game_group)
    
    def _load_settings(self):
        """Load current settings."""
        config = self.plugin.plugin_config
        
        self.enabled_cb.setChecked(config.get('enabled', True))
        self.interval_min_spin.setValue(config.get('interval_min', 30))
        self.interval_max_spin.setValue(config.get('interval_max', 60))
        self.mouse_enabled_cb.setChecked(config.get('mouse_enabled', True))
        self.keyboard_enabled_cb.setChecked(config.get('keyboard_enabled', True))
        self.safe_mode_cb.setChecked(config.get('safe_mode', True))
        self.only_games_cb.setChecked(config.get('only_in_games', True))
        self.smart_detection_cb.setChecked(config.get('smart_detection', True))
    
    def _connect_signals(self):
        """Connect setting change signals."""
        self.enabled_cb.toggled.connect(self._save_settings)
        self.interval_min_spin.valueChanged.connect(self._save_settings)
        self.interval_max_spin.valueChanged.connect(self._save_settings)
        self.mouse_enabled_cb.toggled.connect(self._save_settings)
        self.keyboard_enabled_cb.toggled.connect(self._save_settings)
        self.safe_mode_cb.toggled.connect(self._save_settings)
        self.only_games_cb.toggled.connect(self._save_settings)
        self.smart_detection_cb.toggled.connect(self._save_settings)
    
    def _save_settings(self):
        """Save settings to plugin configuration."""
        self.plugin.plugin_config['enabled'] = self.enabled_cb.isChecked()
        self.plugin.plugin_config['interval_min'] = self.interval_min_spin.value()
        self.plugin.plugin_config['interval_max'] = self.interval_max_spin.value()
        self.plugin.plugin_config['mouse_enabled'] = self.mouse_enabled_cb.isChecked()
        self.plugin.plugin_config['keyboard_enabled'] = self.keyboard_enabled_cb.isChecked()
        self.plugin.plugin_config['safe_mode'] = self.safe_mode_cb.isChecked()
        self.plugin.plugin_config['only_in_games'] = self.only_games_cb.isChecked()
        self.plugin.plugin_config['smart_detection'] = self.smart_detection_cb.isChecked()
        
        # Validate intervals
        if self.interval_min_spin.value() > self.interval_max_spin.value():
            self.interval_max_spin.setValue(self.interval_min_spin.value())
            self.plugin.plugin_config['interval_max'] = self.interval_min_spin.value()
        
        self.plugin.save_config()
