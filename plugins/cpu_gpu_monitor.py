"""
CPU/GPU Monitor Plugin
Monitors and displays CPU and GPU usage, temperature, and memory.
"""

import psutil
import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QProgressBar, QGroupBox, QCheckBox, QSpinBox,
                              QComboBox, QGridLayout)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor

from core.plugin_manager import BasePlugin
from ui.floating_panel import FloatingPanel


class SystemMonitorDisplay(QWidget):
    """Display widget for system monitoring information."""
    
    def __init__(self, monitor_plugin):
        super().__init__()
        
        self.monitor_plugin = monitor_plugin
        self._setup_ui()
        
        # System information
        self.cpu_count = psutil.cpu_count()
        self.cpu_count_logical = psutil.cpu_count(logical=True)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_info)
        self.update_timer.start(1000)  # Update every second
    
    def _setup_ui(self):
        """Setup the system monitor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # CPU Group
        self.cpu_group = QGroupBox("CPU")
        cpu_layout = QGridLayout(self.cpu_group)
        
        # CPU Usage
        cpu_layout.addWidget(QLabel("Usage:"), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setFormat("%p%")
        cpu_layout.addWidget(self.cpu_progress, 0, 1)
        
        # CPU Temperature (if available)
        cpu_layout.addWidget(QLabel("Temp:"), 1, 0)
        self.cpu_temp_label = QLabel("N/A")
        cpu_layout.addWidget(self.cpu_temp_label, 1, 1)
        
        # CPU Frequency
        cpu_layout.addWidget(QLabel("Freq:"), 2, 0)
        self.cpu_freq_label = QLabel("N/A")
        cpu_layout.addWidget(self.cpu_freq_label, 2, 1)
        
        layout.addWidget(self.cpu_group)
        
        # Memory Group
        self.memory_group = QGroupBox("Memory")
        memory_layout = QGridLayout(self.memory_group)
        
        # RAM Usage
        memory_layout.addWidget(QLabel("RAM:"), 0, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setFormat("%p%")
        memory_layout.addWidget(self.memory_progress, 0, 1)
        
        # RAM Amount
        self.memory_amount_label = QLabel("0 / 0 GB")
        memory_layout.addWidget(self.memory_amount_label, 1, 0, 1, 2)
        
        # SWAP Usage
        memory_layout.addWidget(QLabel("Swap:"), 2, 0)
        self.swap_progress = QProgressBar()
        self.swap_progress.setRange(0, 100)
        self.swap_progress.setFormat("%p%")
        memory_layout.addWidget(self.swap_progress, 2, 1)
        
        layout.addWidget(self.memory_group)
        
        # GPU Group (if available)
        self.gpu_group = QGroupBox("GPU")
        gpu_layout = QGridLayout(self.gpu_group)
        
        # GPU Usage
        gpu_layout.addWidget(QLabel("Usage:"), 0, 0)
        self.gpu_progress = QProgressBar()
        self.gpu_progress.setRange(0, 100)
        self.gpu_progress.setFormat("%p%")
        gpu_layout.addWidget(self.gpu_progress, 0, 1)
        
        # GPU Memory
        gpu_layout.addWidget(QLabel("VRAM:"), 1, 0)
        self.gpu_memory_progress = QProgressBar()
        self.gpu_memory_progress.setRange(0, 100)
        self.gpu_memory_progress.setFormat("%p%")
        gpu_layout.addWidget(self.gpu_memory_progress, 1, 1)
        
        # GPU Temperature
        gpu_layout.addWidget(QLabel("Temp:"), 2, 0)
        self.gpu_temp_label = QLabel("N/A")
        gpu_layout.addWidget(self.gpu_temp_label, 2, 1)
        
        layout.addWidget(self.gpu_group)
        
        # Network Group
        self.network_group = QGroupBox("Network")
        network_layout = QGridLayout(self.network_group)
        
        # Download/Upload speeds
        network_layout.addWidget(QLabel("Down:"), 0, 0)
        self.download_label = QLabel("0 KB/s")
        network_layout.addWidget(self.download_label, 0, 1)
        
        network_layout.addWidget(QLabel("Up:"), 1, 0)
        self.upload_label = QLabel("0 KB/s")
        network_layout.addWidget(self.upload_label, 1, 1)
        
        layout.addWidget(self.network_group)
        
        # Style the progress bars
        self._style_progress_bars()
        
        # Initialize network counters
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = psutil.time.time()
    
    def _style_progress_bars(self):
        """Apply styling to progress bars."""
        style = """
        QProgressBar {
            border: 1px solid #3498db;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            background-color: rgba(52, 73, 94, 100);
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                       stop:0 #3498db, stop:1 #2980b9);
            border-radius: 3px;
        }
        """
        
        for progress_bar in [self.cpu_progress, self.memory_progress, 
                           self.swap_progress, self.gpu_progress, 
                           self.gpu_memory_progress]:
            progress_bar.setStyleSheet(style)
    
    def _update_system_info(self):
        """Update all system information."""
        config = self.monitor_plugin.plugin_config
        
        # Update CPU info
        if config.get('show_cpu', True):
            self._update_cpu_info()
        
        # Update memory info
        if config.get('show_memory', True):
            self._update_memory_info()
        
        # Update GPU info
        if config.get('show_gpu', True):
            self._update_gpu_info()
        
        # Update network info
        if config.get('show_network', True):
            self._update_network_info()
        
        # Show/hide groups based on configuration
        self.cpu_group.setVisible(config.get('show_cpu', True))
        self.memory_group.setVisible(config.get('show_memory', True))
        self.gpu_group.setVisible(config.get('show_gpu', True))
        self.network_group.setVisible(config.get('show_network', True))
    
    def _update_cpu_info(self):
        """Update CPU information."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_progress.setValue(int(cpu_percent))
            
            # CPU temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Try to find CPU temperature
                    cpu_temp = None
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            if entries:
                                cpu_temp = entries[0].current
                                break
                    
                    if cpu_temp:
                        self.cpu_temp_label.setText(f"{cpu_temp:.1f}°C")
                    else:
                        self.cpu_temp_label.setText("N/A")
                else:
                    self.cpu_temp_label.setText("N/A")
            except:
                self.cpu_temp_label.setText("N/A")
            
            # CPU frequency
            try:
                freq = psutil.cpu_freq()
                if freq:
                    self.cpu_freq_label.setText(f"{freq.current:.0f} MHz")
                else:
                    self.cpu_freq_label.setText("N/A")
            except:
                self.cpu_freq_label.setText("N/A")
                
        except Exception as e:
            self.monitor_plugin.logger.error(f"Error updating CPU info: {e}")
    
    def _update_memory_info(self):
        """Update memory information."""
        try:
            # RAM usage
            memory = psutil.virtual_memory()
            self.memory_progress.setValue(int(memory.percent))
            
            # RAM amount
            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)
            self.memory_amount_label.setText(f"{used_gb:.1f} / {total_gb:.1f} GB")
            
            # SWAP usage
            swap = psutil.swap_memory()
            self.swap_progress.setValue(int(swap.percent))
            
        except Exception as e:
            self.monitor_plugin.logger.error(f"Error updating memory info: {e}")
    
    def _update_gpu_info(self):
        """Update GPU information."""
        try:
            # Try to get GPU info using different methods
            # This is a simplified version - in practice, you might use
            # libraries like GPUtil, nvidia-ml-py, or pynvml
            
            # For now, show placeholder values
            self.gpu_progress.setValue(0)
            self.gpu_memory_progress.setValue(0)
            self.gpu_temp_label.setText("N/A")
            
            # Note: To implement real GPU monitoring, you would need:
            # - For NVIDIA: nvidia-ml-py or pynvml
            # - For AMD: appropriate AMD SDK
            # - For Intel: Intel GPU SDK
            
        except Exception as e:
            self.monitor_plugin.logger.error(f"Error updating GPU info: {e}")
    
    def _update_network_info(self):
        """Update network information."""
        try:
            current_net_io = psutil.net_io_counters()
            current_time = psutil.time.time()
            
            # Calculate time difference
            time_diff = current_time - self.last_net_time
            
            if time_diff > 0:
                # Calculate bytes per second
                bytes_sent_per_sec = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
                bytes_recv_per_sec = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
                
                # Convert to human readable format
                download_str = self._format_bytes_per_sec(bytes_recv_per_sec)
                upload_str = self._format_bytes_per_sec(bytes_sent_per_sec)
                
                self.download_label.setText(download_str)
                self.upload_label.setText(upload_str)
            
            # Update last values
            self.last_net_io = current_net_io
            self.last_net_time = current_time
            
        except Exception as e:
            self.monitor_plugin.logger.error(f"Error updating network info: {e}")
    
    def _format_bytes_per_sec(self, bytes_per_sec):
        """Format bytes per second to human readable string."""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.1f} B/s"
        elif bytes_per_sec < 1024**2:
            return f"{bytes_per_sec/1024:.1f} KB/s"
        elif bytes_per_sec < 1024**3:
            return f"{bytes_per_sec/(1024**2):.1f} MB/s"
        else:
            return f"{bytes_per_sec/(1024**3):.1f} GB/s"


class SystemMonitorConfigWidget(QWidget):
    """Configuration widget for system monitor settings."""
    
    settings_changed = Signal()
    
    def __init__(self, monitor_plugin):
        super().__init__()
        
        self.monitor_plugin = monitor_plugin
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the configuration UI."""
        layout = QVBoxLayout(self)
        
        # Display settings
        display_group = QGroupBox("Display Components")
        display_layout = QVBoxLayout(display_group)
        
        # Component checkboxes
        self.show_cpu_cb = QCheckBox("Show CPU")
        self.show_cpu_cb.toggled.connect(self._on_setting_changed)
        display_layout.addWidget(self.show_cpu_cb)
        
        self.show_memory_cb = QCheckBox("Show Memory")
        self.show_memory_cb.toggled.connect(self._on_setting_changed)
        display_layout.addWidget(self.show_memory_cb)
        
        self.show_gpu_cb = QCheckBox("Show GPU")
        self.show_gpu_cb.toggled.connect(self._on_setting_changed)
        display_layout.addWidget(self.show_gpu_cb)
        
        self.show_network_cb = QCheckBox("Show Network")
        self.show_network_cb.toggled.connect(self._on_setting_changed)
        display_layout.addWidget(self.show_network_cb)
        
        layout.addWidget(display_group)
        
        # Update settings
        update_group = QGroupBox("Update Settings")
        update_layout = QVBoxLayout(update_group)
        
        # Update interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Update Interval (ms):"))
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(100, 10000)
        self.update_interval_spin.setValue(1000)
        self.update_interval_spin.valueChanged.connect(self._on_setting_changed)
        interval_layout.addWidget(self.update_interval_spin)
        interval_layout.addStretch()
        update_layout.addLayout(interval_layout)
        
        layout.addWidget(update_group)
        
        layout.addStretch()
    
    def _load_settings(self):
        """Load settings from plugin configuration."""
        config = self.monitor_plugin.plugin_config
        
        self.show_cpu_cb.setChecked(config.get('show_cpu', True))
        self.show_memory_cb.setChecked(config.get('show_memory', True))
        self.show_gpu_cb.setChecked(config.get('show_gpu', True))
        self.show_network_cb.setChecked(config.get('show_network', True))
        self.update_interval_spin.setValue(config.get('update_interval', 1000))
    
    def _on_setting_changed(self):
        """Handle setting changes."""
        # Update plugin configuration
        config = self.monitor_plugin.plugin_config
        config['show_cpu'] = self.show_cpu_cb.isChecked()
        config['show_memory'] = self.show_memory_cb.isChecked()
        config['show_gpu'] = self.show_gpu_cb.isChecked()
        config['show_network'] = self.show_network_cb.isChecked()
        config['update_interval'] = self.update_interval_spin.value()
        
        # Save and update
        self.monitor_plugin.save_config()
        self.monitor_plugin.update_display()
        self.settings_changed.emit()


class CPUGPUMonitorPlugin(BasePlugin):
    """CPU/GPU monitoring plugin."""
    
    name = "CPU/GPU Monitor"
    description = "Monitors CPU, GPU, memory, and network usage"
    version = "1.0.0"
    author = "Party Brasil"
    
    def __init__(self, config_manager, thread_manager):
        super().__init__(config_manager, thread_manager)
        
        # Plugin widgets
        self.monitor_display = None
        self.config_widget = None
        
        # Default configuration
        default_config = {
            'show_cpu': True,
            'show_memory': True,
            'show_gpu': True,
            'show_network': True,
            'update_interval': 1000
        }
        
        # Merge with existing config
        for key, value in default_config.items():
            if key not in self.plugin_config:
                self.plugin_config[key] = value
    
    def initialize(self) -> bool:
        """Initialize the CPU/GPU monitor plugin."""
        try:
            # Create monitor display
            self.monitor_display = SystemMonitorDisplay(self)
            
            # Create configuration widget
            self.config_widget = SystemMonitorConfigWidget(self)
            
            # Create panel
            self.panel_widget = FloatingPanel(self.config_manager, "System Monitor")
            self.panel_widget.add_content_widget(self.monitor_display)
            
            # Connect signals
            self.panel_widget.close_requested.connect(self.deactivate)
            
            return super().initialize()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize CPU/GPU monitor: {e}")
            return False
    
    def activate(self) -> bool:
        """Activate the CPU/GPU monitor plugin."""
        try:
            if super().activate():
                # Show panel
                if self.panel_widget:
                    self.panel_widget.show()
                    self.panel_widget.resize(280, 400)
                
                # Start monitoring
                if self.monitor_display:
                    interval = self.plugin_config.get('update_interval', 1000)
                    self.monitor_display.update_timer.start(interval)
                
                return True
            return False
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to activate CPU/GPU monitor: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the CPU/GPU monitor plugin."""
        try:
            # Stop monitoring
            if self.monitor_display and self.monitor_display.update_timer:
                self.monitor_display.update_timer.stop()
            
            # Hide panel
            if self.panel_widget:
                self.panel_widget.hide()
            
            return super().deactivate()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to deactivate CPU/GPU monitor: {e}")
            return False
    
    def update_display(self):
        """Update the monitor display with current settings."""
        if self.monitor_display:
            # Update timer interval
            interval = self.plugin_config.get('update_interval', 1000)
            if self.monitor_display.update_timer.isActive():
                self.monitor_display.update_timer.stop()
                self.monitor_display.update_timer.start(interval)
            
            # Force update display
            self.monitor_display._update_system_info()
    
    def get_panel_widget(self):
        """Get the plugin's panel widget."""
        return self.panel_widget
    
    def get_config_widget(self):
        """Get the plugin's configuration widget."""
        return self.config_widget
