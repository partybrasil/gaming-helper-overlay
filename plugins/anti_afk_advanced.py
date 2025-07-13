"""
Advanced Anti-AFK Configuration Dialog
Provides advanced settings for the Anti-AFK plugin.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QWidget, QGroupBox, QFormLayout, QLineEdit,
                              QListWidget, QPushButton, QLabel, QSpinBox,
                              QCheckBox, QComboBox, QTextEdit, QSlider,
                              QDialogButtonBox, QMessageBox, QListWidgetItem)
from PySide6.QtCore import Qt


class AntiAFKAdvancedDialog(QDialog):
    """Advanced configuration dialog for Anti-AFK plugin."""
    
    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        
        self.setWindowTitle("Anti-AFK Advanced Settings")
        self.setModal(True)
        self.resize(500, 600)
        
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the advanced settings UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Tabs
        self._create_keyboard_tab()
        self._create_mouse_tab()
        self._create_games_tab()
        self._create_advanced_tab()
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self._apply_settings)
        layout.addWidget(button_box)
    
    def _create_keyboard_tab(self):
        """Create keyboard settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Key selection
        keys_group = QGroupBox("Key Configuration")
        keys_layout = QVBoxLayout(keys_group)
        
        # Available keys
        available_keys = [
            'space', 'w', 'a', 's', 'd', 'shift', 'ctrl', 'alt',
            'tab', 'escape', 'enter', 'f1', 'f2', 'f3', 'f4',
            '1', '2', '3', '4', '5', 'q', 'e', 'r', 't', 'y'
        ]
        
        keys_layout.addWidget(QLabel("Select keys to use for Anti-AFK:"))
        
        # Key checkboxes in a grid
        from PySide6.QtWidgets import QGridLayout
        keys_grid = QGridLayout()
        self.key_checkboxes = {}
        
        for i, key in enumerate(available_keys):
            checkbox = QCheckBox(key.upper())
            self.key_checkboxes[key] = checkbox
            keys_grid.addWidget(checkbox, i // 5, i % 5)
        
        keys_widget = QWidget()
        keys_widget.setLayout(keys_grid)
        keys_layout.addWidget(keys_widget)
        
        # Custom key input
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom key:"))
        self.custom_key_input = QLineEdit()
        self.custom_key_input.setPlaceholderText("Enter custom key name")
        custom_layout.addWidget(self.custom_key_input)
        
        add_key_btn = QPushButton("Add")
        add_key_btn.clicked.connect(self._add_custom_key)
        custom_layout.addWidget(add_key_btn)
        
        keys_layout.addLayout(custom_layout)
        layout.addWidget(keys_group)
        
        # Key press settings
        press_group = QGroupBox("Key Press Settings")
        press_layout = QFormLayout(press_group)
        
        self.key_hold_time = QSpinBox()
        self.key_hold_time.setRange(10, 500)
        self.key_hold_time.setSuffix(" ms")
        press_layout.addRow("Key hold time:", self.key_hold_time)
        
        self.key_sequence_enabled = QCheckBox("Enable key sequences")
        press_layout.addRow(self.key_sequence_enabled)
        
        layout.addWidget(press_group)
        
        self.tab_widget.addTab(tab, "Keyboard")
    
    def _create_mouse_tab(self):
        """Create mouse settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Movement settings
        movement_group = QGroupBox("Mouse Movement")
        movement_layout = QFormLayout(movement_group)
        
        self.mouse_range_slider = QSlider(Qt.Horizontal)
        self.mouse_range_slider.setRange(1, 50)
        self.mouse_range_label = QLabel("10 pixels")
        movement_layout.addRow("Movement range:", self.mouse_range_slider)
        movement_layout.addRow("", self.mouse_range_label)
        
        self.mouse_return_enabled = QCheckBox("Return to original position")
        movement_layout.addRow(self.mouse_return_enabled)
        
        self.mouse_return_delay = QSpinBox()
        self.mouse_return_delay.setRange(50, 1000)
        self.mouse_return_delay.setSuffix(" ms")
        movement_layout.addRow("Return delay:", self.mouse_return_delay)
        
        layout.addWidget(movement_group)
        
        # Click settings
        click_group = QGroupBox("Mouse Clicks")
        click_layout = QFormLayout(click_group)
        
        self.mouse_clicks_enabled = QCheckBox("Enable mouse clicks")
        click_layout.addRow(self.mouse_clicks_enabled)
        
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["Left Click", "Right Click", "Middle Click"])
        click_layout.addRow("Click type:", self.click_type_combo)
        
        self.click_probability = QSlider(Qt.Horizontal)
        self.click_probability.setRange(0, 100)
        self.click_probability_label = QLabel("10%")
        click_layout.addRow("Click probability:", self.click_probability)
        click_layout.addRow("", self.click_probability_label)
        
        layout.addWidget(click_group)
        
        self.tab_widget.addTab(tab, "Mouse")
    
    def _create_games_tab(self):
        """Create games configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Game whitelist
        whitelist_group = QGroupBox("Game Whitelist")
        whitelist_layout = QVBoxLayout(whitelist_group)
        
        whitelist_layout.addWidget(QLabel("Anti-AFK will ONLY work with these games:"))
        
        self.whitelist_widget = QListWidget()
        whitelist_layout.addWidget(self.whitelist_widget)
        
        whitelist_controls = QHBoxLayout()
        self.whitelist_input = QLineEdit()
        self.whitelist_input.setPlaceholderText("Game name or process")
        whitelist_controls.addWidget(self.whitelist_input)
        
        add_whitelist_btn = QPushButton("Add")
        add_whitelist_btn.clicked.connect(self._add_whitelist_game)
        whitelist_controls.addWidget(add_whitelist_btn)
        
        remove_whitelist_btn = QPushButton("Remove")
        remove_whitelist_btn.clicked.connect(self._remove_whitelist_game)
        whitelist_controls.addWidget(remove_whitelist_btn)
        
        whitelist_layout.addLayout(whitelist_controls)
        layout.addWidget(whitelist_group)
        
        # Game blacklist
        blacklist_group = QGroupBox("Game Blacklist")
        blacklist_layout = QVBoxLayout(blacklist_group)
        
        blacklist_layout.addWidget(QLabel("Anti-AFK will NOT work with these games:"))
        
        self.blacklist_widget = QListWidget()
        blacklist_layout.addWidget(self.blacklist_widget)
        
        blacklist_controls = QHBoxLayout()
        self.blacklist_input = QLineEdit()
        self.blacklist_input.setPlaceholderText("Game name or process")
        blacklist_controls.addWidget(self.blacklist_input)
        
        add_blacklist_btn = QPushButton("Add")
        add_blacklist_btn.clicked.connect(self._add_blacklist_game)
        blacklist_controls.addWidget(add_blacklist_btn)
        
        remove_blacklist_btn = QPushButton("Remove")
        remove_blacklist_btn.clicked.connect(self._remove_blacklist_game)
        blacklist_controls.addWidget(remove_blacklist_btn)
        
        blacklist_layout.addLayout(blacklist_controls)
        layout.addWidget(blacklist_group)
        
        self.tab_widget.addTab(tab, "Games")
    
    def _create_advanced_tab(self):
        """Create advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Detection settings
        detection_group = QGroupBox("Detection Settings")
        detection_layout = QFormLayout(detection_group)
        
        self.activity_threshold = QSpinBox()
        self.activity_threshold.setRange(5, 300)
        self.activity_threshold.setSuffix(" seconds")
        detection_layout.addRow("User activity threshold:", self.activity_threshold)
        
        self.window_check_interval = QSpinBox()
        self.window_check_interval.setRange(1, 10)
        self.window_check_interval.setSuffix(" seconds")
        detection_layout.addRow("Window check interval:", self.window_check_interval)
        
        layout.addWidget(detection_group)
        
        # Safety settings
        safety_group = QGroupBox("Safety Settings")
        safety_layout = QFormLayout(safety_group)
        
        self.max_actions_per_minute = QSpinBox()
        self.max_actions_per_minute.setRange(1, 20)
        safety_layout.addRow("Max actions per minute:", self.max_actions_per_minute)
        
        self.emergency_stop_enabled = QCheckBox("Enable emergency stop on user input")
        safety_layout.addRow(self.emergency_stop_enabled)
        
        layout.addWidget(safety_group)
        
        # Logging settings
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_actions = QCheckBox("Log Anti-AFK actions")
        logging_layout.addRow(self.log_actions)
        
        self.detailed_logging = QCheckBox("Enable detailed logging")
        logging_layout.addRow(self.detailed_logging)
        
        layout.addWidget(logging_group)
        
        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        layout.addWidget(reset_btn)
        
        self.tab_widget.addTab(tab, "Advanced")
    
    def _load_settings(self):
        """Load current settings into the dialog."""
        config = self.plugin.plugin_config
        
        # Keyboard settings
        selected_keys = config.get('keyboard_keys', ['space'])
        for key, checkbox in self.key_checkboxes.items():
            checkbox.setChecked(key in selected_keys)
        
        self.key_hold_time.setValue(config.get('key_hold_time', 50))
        self.key_sequence_enabled.setChecked(config.get('key_sequence_enabled', False))
        
        # Mouse settings
        self.mouse_range_slider.setValue(config.get('mouse_movement_range', 10))
        self.mouse_range_label.setText(f"{config.get('mouse_movement_range', 10)} pixels")
        self.mouse_return_enabled.setChecked(config.get('mouse_return_enabled', True))
        self.mouse_return_delay.setValue(config.get('mouse_return_delay', 100))
        
        self.mouse_clicks_enabled.setChecked(config.get('mouse_clicks_enabled', False))
        click_types = {"left": 0, "right": 1, "middle": 2}
        self.click_type_combo.setCurrentIndex(click_types.get(config.get('click_type', 'left'), 0))
        self.click_probability.setValue(config.get('click_probability', 10))
        self.click_probability_label.setText(f"{config.get('click_probability', 10)}%")
        
        # Games settings
        whitelist = config.get('game_whitelist', [])
        for game in whitelist:
            self.whitelist_widget.addItem(game)
        
        blacklist = config.get('game_blacklist', [])
        for game in blacklist:
            self.blacklist_widget.addItem(game)
        
        # Advanced settings
        self.activity_threshold.setValue(config.get('last_activity_threshold', 30))
        self.window_check_interval.setValue(config.get('window_check_interval', 2))
        self.max_actions_per_minute.setValue(config.get('max_actions_per_minute', 5))
        self.emergency_stop_enabled.setChecked(config.get('emergency_stop_enabled', True))
        self.log_actions.setChecked(config.get('log_actions', False))
        self.detailed_logging.setChecked(config.get('detailed_logging', False))
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.mouse_range_slider.valueChanged.connect(
            lambda v: self.mouse_range_label.setText(f"{v} pixels")
        )
        self.click_probability.valueChanged.connect(
            lambda v: self.click_probability_label.setText(f"{v}%")
        )
    
    def _add_custom_key(self):
        """Add a custom key to the list."""
        key = self.custom_key_input.text().strip().lower()
        if key and key not in self.key_checkboxes:
            # Add the key dynamically (simplified for this example)
            QMessageBox.information(self, "Custom Key", f"Custom key '{key}' noted. "
                                  "It will be added to the configuration.")
            self.custom_key_input.clear()
    
    def _add_whitelist_game(self):
        """Add a game to the whitelist."""
        game = self.whitelist_input.text().strip()
        if game:
            self.whitelist_widget.addItem(game)
            self.whitelist_input.clear()
    
    def _remove_whitelist_game(self):
        """Remove selected game from whitelist."""
        current_row = self.whitelist_widget.currentRow()
        if current_row >= 0:
            self.whitelist_widget.takeItem(current_row)
    
    def _add_blacklist_game(self):
        """Add a game to the blacklist."""
        game = self.blacklist_input.text().strip()
        if game:
            self.blacklist_widget.addItem(game)
            self.blacklist_input.clear()
    
    def _remove_blacklist_game(self):
        """Remove selected game from blacklist."""
        current_row = self.blacklist_widget.currentRow()
        if current_row >= 0:
            self.blacklist_widget.takeItem(current_row)
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults (simplified)
            for checkbox in self.key_checkboxes.values():
                checkbox.setChecked(False)
            self.key_checkboxes['space'].setChecked(True)
            
            self.mouse_range_slider.setValue(10)
            self.activity_threshold.setValue(30)
            # ... reset other values
    
    def _apply_settings(self):
        """Apply settings without closing dialog."""
        self._save_settings()
    
    def _save_settings(self):
        """Save settings to plugin configuration."""
        config = self.plugin.plugin_config
        
        # Keyboard settings
        selected_keys = [key for key, checkbox in self.key_checkboxes.items() 
                        if checkbox.isChecked()]
        config['keyboard_keys'] = selected_keys if selected_keys else ['space']
        config['key_hold_time'] = self.key_hold_time.value()
        config['key_sequence_enabled'] = self.key_sequence_enabled.isChecked()
        
        # Mouse settings
        config['mouse_movement_range'] = self.mouse_range_slider.value()
        config['mouse_return_enabled'] = self.mouse_return_enabled.isChecked()
        config['mouse_return_delay'] = self.mouse_return_delay.value()
        config['mouse_clicks_enabled'] = self.mouse_clicks_enabled.isChecked()
        
        click_types = {0: "left", 1: "right", 2: "middle"}
        config['click_type'] = click_types.get(self.click_type_combo.currentIndex(), "left")
        config['click_probability'] = self.click_probability.value()
        
        # Games settings
        whitelist = [self.whitelist_widget.item(i).text() 
                    for i in range(self.whitelist_widget.count())]
        blacklist = [self.blacklist_widget.item(i).text() 
                    for i in range(self.blacklist_widget.count())]
        
        config['game_whitelist'] = whitelist
        config['game_blacklist'] = blacklist
        
        # Advanced settings
        config['last_activity_threshold'] = self.activity_threshold.value()
        config['window_check_interval'] = self.window_check_interval.value()
        config['max_actions_per_minute'] = self.max_actions_per_minute.value()
        config['emergency_stop_enabled'] = self.emergency_stop_enabled.isChecked()
        config['log_actions'] = self.log_actions.isChecked()
        config['detailed_logging'] = self.detailed_logging.isChecked()
        
        # Save to file
        self.plugin.save_config()
    
    def accept(self):
        """Accept and save settings."""
        self._save_settings()
        super().accept()
