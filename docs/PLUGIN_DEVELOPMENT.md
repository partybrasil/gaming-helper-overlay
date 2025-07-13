# Plugin Development Guide

This guide explains how to create custom plugins for the Gaming Helper Overlay application.

## 🧩 Plugin Architecture

All plugins inherit from the `BasePlugin` class and follow a standard lifecycle:

1. **Discovery**: Plugin files are automatically discovered in the `plugins/` directory
2. **Loading**: Plugin classes are instantiated when loaded
3. **Initialization**: Plugin resources are set up
4. **Activation**: Plugin becomes active and visible
5. **Deactivation**: Plugin is hidden but remains loaded
6. **Shutdown**: Plugin resources are cleaned up

## 📝 Basic Plugin Template

```python
from core.plugin_manager import BasePlugin
from ui.floating_panel import FloatingPanel
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MyPlugin(BasePlugin):
    # Plugin metadata
    name = "My Custom Plugin"
    description = "A sample plugin that demonstrates basic functionality"
    version = "1.0.0"
    author = "Your Name"
    
    def __init__(self, config_manager, thread_manager):
        super().__init__(config_manager, thread_manager)
        
        # Plugin-specific variables
        self.my_widget = None
        
        # Default configuration
        default_config = {
            'enabled': True,
            'setting1': 'default_value',
            'setting2': 42
        }
        
        # Merge with existing config
        for key, value in default_config.items():
            if key not in self.plugin_config:
                self.plugin_config[key] = value
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        try:
            # Create your custom widget
            self.my_widget = QWidget()
            layout = QVBoxLayout(self.my_widget)
            layout.addWidget(QLabel("Hello from My Plugin!"))
            
            # Create floating panel
            self.panel_widget = FloatingPanel(self.config_manager, self.name)
            self.panel_widget.add_content_widget(self.my_widget)
            
            # Connect signals
            self.panel_widget.close_requested.connect(self.deactivate)
            
            return super().initialize()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize: {e}")
            return False
    
    def activate(self) -> bool:
        """Activate the plugin."""
        try:
            if super().activate():
                if self.panel_widget:
                    self.panel_widget.show()
                return True
            return False
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to activate: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the plugin."""
        try:
            if self.panel_widget:
                self.panel_widget.hide()
            
            return super().deactivate()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to deactivate: {e}")
            return False
    
    def get_panel_widget(self):
        """Return the plugin's main panel widget."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Return a configuration widget for the control panel."""
        # Optional: Create a configuration widget
        return None
```

## 🎛️ Configuration Management

### Plugin Configuration

Each plugin automatically gets its own configuration namespace:

```python
# Get configuration value
value = self.plugin_config.get('setting_name', default_value)

# Set configuration value
self.plugin_config['setting_name'] = new_value

# Save configuration
self.save_config()
```

### Global Configuration

Access global application settings:

```python
# Get global setting
theme = self.config_manager.get('app.theme', 'dark')

# Set global setting (use carefully)
self.config_manager.set('app.setting', value)
```

## 🧵 Threading

Use the thread manager for background tasks:

```python
def start_background_task(self):
    """Start a background task."""
    self.thread_manager.start_thread(
        name=f"{self.name}_background",
        target=self.background_work,
        arg1="value1",
        arg2="value2"
    )

def background_work(self, arg1, arg2):
    """Background task function."""
    # Do work here
    # This runs in a separate thread
    result = perform_long_operation()
    
    # Emit signal to update UI (thread-safe)
    self.data_updated.emit({"result": result})
```

## 📱 UI Components

### Using Floating Panels

All plugins should use `FloatingPanel` for consistent behavior:

```python
from ui.floating_panel import FloatingPanel

# Create panel
self.panel_widget = FloatingPanel(self.config_manager, "Panel Title")

# Add your content
self.panel_widget.add_content_widget(your_widget)

# Connect signals
self.panel_widget.close_requested.connect(self.deactivate)
self.panel_widget.transparency_changed.connect(self.on_transparency_changed)
```

### Configuration Widgets

Create configuration widgets for the control panel:

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QSpinBox

class MyConfigWidget(QWidget):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Add configuration controls
        self.enable_cb = QCheckBox("Enable Feature")
        self.enable_cb.toggled.connect(self._on_setting_changed)
        layout.addWidget(self.enable_cb)
        
        self.value_spin = QSpinBox()
        self.value_spin.setRange(1, 100)
        self.value_spin.valueChanged.connect(self._on_setting_changed)
        layout.addWidget(self.value_spin)
    
    def _load_settings(self):
        config = self.plugin.plugin_config
        self.enable_cb.setChecked(config.get('enabled', True))
        self.value_spin.setValue(config.get('value', 50))
    
    def _on_setting_changed(self):
        # Update plugin configuration
        self.plugin.plugin_config['enabled'] = self.enable_cb.isChecked()
        self.plugin.plugin_config['value'] = self.value_spin.value()
        self.plugin.save_config()
```

## 🔔 Signals and Events

### Plugin Signals

Base plugin provides these signals:

```python
# Status updates
self.status_changed.emit("Plugin ready")

# Data updates
self.data_updated.emit({"key": "value"})

# Error reporting
self.error_occurred.emit("Something went wrong")
```

### Listening to Events

Connect to other plugin or application events:

```python
def initialize(self):
    # Connect to application events
    self.config_manager.config_changed.connect(self.on_config_changed)
    
    # Connect to thread events
    self.thread_manager.thread_finished.connect(self.on_thread_finished)
    
    return super().initialize()

def on_config_changed(self, key, value):
    """Handle configuration changes."""
    if key.startswith('app.theme'):
        self.update_theme()

def on_thread_finished(self, thread_name, result):
    """Handle thread completion."""
    if thread_name.startswith(self.name):
        self.process_background_result(result)
```

## 🎨 Styling and Themes

### Custom Styling

Apply custom styles to your widgets:

```python
def apply_custom_style(self):
    style = """
    QWidget {
        background: rgba(30, 30, 30, 180);
        border: 2px solid rgba(255, 255, 255, 30);
        border-radius: 10px;
        color: white;
    }
    
    QPushButton {
        background: rgba(70, 70, 70, 180);
        border: 1px solid rgba(255, 255, 255, 50);
        border-radius: 4px;
        padding: 5px;
    }
    
    QPushButton:hover {
        background: rgba(90, 90, 90, 200);
    }
    """
    
    self.my_widget.setStyleSheet(style)
```

### Theme Integration

Respond to theme changes:

```python
def update_theme(self):
    """Update widget appearance based on current theme."""
    theme = self.config_manager.get('app.theme', 'dark')
    
    if theme == 'dark':
        self.apply_dark_theme()
    elif theme == 'light':
        self.apply_light_theme()
```

## 💾 Data Management

### Persistent Data

Store persistent data in plugin configuration:

```python
def save_user_data(self, data):
    """Save user data to configuration."""
    self.plugin_config['user_data'] = data
    self.save_config()

def load_user_data(self):
    """Load user data from configuration."""
    return self.plugin_config.get('user_data', {})
```

### Temporary Data

Use instance variables for temporary data:

```python
def __init__(self, config_manager, thread_manager):
    super().__init__(config_manager, thread_manager)
    
    # Temporary data (not saved)
    self.session_data = {}
    self.current_state = "idle"
    self.temp_results = []
```

## 🔧 Advanced Features

### System Integration

Access system information:

```python
import psutil

def get_system_info(self):
    """Get system information."""
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
```

### External APIs

Make API calls in background threads:

```python
import requests

def fetch_external_data(self):
    """Fetch data from external API."""
    self.thread_manager.start_thread(
        name=f"{self.name}_api_call",
        target=self._api_worker
    )

def _api_worker(self):
    """Background API worker."""
    try:
        response = requests.get('https://api.example.com/data')
        data = response.json()
        
        # Update UI in main thread
        self.data_updated.emit(data)
        
    except Exception as e:
        self.error_occurred.emit(f"API call failed: {e}")
```

### Game Integration

Detect and interact with games:

```python
import win32gui
import win32process

def get_active_window_info(self):
    """Get information about the active window."""
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    
    # Get process information
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process = psutil.Process(pid)
    
    return {
        'title': window_title,
        'process_name': process.name(),
        'pid': pid
    }
```

## 🧪 Testing

### Basic Testing

Test your plugin functionality:

```python
def test_plugin_basic_functionality(self):
    """Test basic plugin operations."""
    # Test initialization
    assert self.initialize() == True
    assert self.is_initialized == True
    
    # Test activation
    assert self.activate() == True
    assert self.is_active == True
    
    # Test deactivation
    assert self.deactivate() == True
    assert self.is_active == False
    
    # Test shutdown
    assert self.shutdown() == True
    assert self.is_initialized == False
```

### Configuration Testing

Test configuration handling:

```python
def test_configuration(self):
    """Test plugin configuration."""
    # Test default values
    assert self.plugin_config.get('setting1') == 'default_value'
    
    # Test setting values
    self.plugin_config['setting1'] = 'new_value'
    assert self.plugin_config['setting1'] == 'new_value'
    
    # Test saving/loading
    self.save_config()
    # Verify config was saved...
```

## 📚 Best Practices

### 1. Error Handling

Always handle exceptions gracefully:

```python
def risky_operation(self):
    try:
        # Potentially failing operation
        result = dangerous_function()
        return result
    except Exception as e:
        self.error_occurred.emit(f"Operation failed: {e}")
        self.logger.error(f"Error in {self.name}: {e}")
        return None
```

### 2. Resource Management

Clean up resources properly:

```python
def shutdown(self):
    try:
        # Stop timers
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        # Close files
        if hasattr(self, 'log_file'):
            self.log_file.close()
        
        # Cancel threads
        self.thread_manager.stop_thread(f"{self.name}_worker")
        
        return super().shutdown()
    except Exception as e:
        self.logger.error(f"Error during shutdown: {e}")
        return False
```

### 3. Performance

Keep the UI responsive:

```python
def heavy_computation(self):
    """Perform heavy computation in background thread."""
    # DON'T do this in the main thread
    # result = expensive_operation()  # BAD
    
    # DO this instead
    self.thread_manager.start_thread(
        name=f"{self.name}_computation",
        target=self._compute_worker
    )

def _compute_worker(self):
    """Background computation worker."""
    result = expensive_operation()
    
    # Update UI safely
    self.data_updated.emit({"result": result})
```

### 4. User Experience

Provide feedback and configuration options:

```python
def long_operation(self):
    """Perform a long operation with user feedback."""
    self.status_changed.emit("Starting operation...")
    
    # Show progress if possible
    for i in range(100):
        # Do work
        progress = i / 100.0
        self.data_updated.emit({"progress": progress})
    
    self.status_changed.emit("Operation completed")
```

## 📁 File Structure for Plugins

Organize complex plugins in subdirectories:

```
plugins/
├── my_plugin/
│   ├── __init__.py         # Plugin entry point
│   ├── plugin.py           # Main plugin class
│   ├── ui/
│   │   ├── main_widget.py  # Main UI component
│   │   └── config_widget.py # Configuration UI
│   ├── workers/
│   │   └── background.py   # Background workers
│   └── assets/
│       ├── icons/
│       └── styles/
└── simple_plugin.py       # Simple single-file plugin
```

For complex plugins, use the subdirectory approach and import from `__init__.py`:

```python
# plugins/my_plugin/__init__.py
from .plugin import MyComplexPlugin

# Make the plugin discoverable
__all__ = ['MyComplexPlugin']
```

## 🔗 Example Plugins

Study the built-in plugins for examples:

- **`crosshair.py`**: Custom drawing and overlay techniques
- **`fps_counter.py`**: Performance monitoring and display
- **`cpu_gpu_monitor.py`**: System integration and data visualization

## 🆘 Getting Help

1. Check the existing plugin implementations
2. Review the base classes in `core/plugin_manager.py`
3. Examine the UI components in `ui/`
4. Look at the application logs for debugging information

## 📋 Plugin Checklist

Before submitting a plugin:

- [ ] Inherits from `BasePlugin`
- [ ] Implements required methods (`initialize`, `activate`, `deactivate`)
- [ ] Handles errors gracefully
- [ ] Uses threading for heavy operations
- [ ] Provides configuration options
- [ ] Cleans up resources on shutdown
- [ ] Follows naming conventions
- [ ] Includes documentation strings
- [ ] Tested with different configurations

Happy plugin development! 🚀
