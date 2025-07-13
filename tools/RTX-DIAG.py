"""
RTX Diagnostic Tool
Advanced diagnostic and monitoring tool for NVIDIA RTX graphics cards.

Author: Party Brasil
Version: 2.0.0
Category: GPU/Graphics
Description: Comprehensive RTX GPU diagnostic tool with real-time monitoring, fan control analysis, and RTX feature detection.
Requires Admin: True
"""

import sys
import math
import time
import os
import re
import winreg
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import psutil
import subprocess
import json

# Try to import nvidia-ml-py for more accurate GPU data
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    print("Warning: pynvml not available. Install with: pip install nvidia-ml-py")

class FanWidget(QWidget):
    def __init__(self, fan_name="Fan"):
        super().__init__()
        self.fan_name = fan_name
        self.rpm = 0
        self.angle = 0
        self.setFixedSize(60, 60)  # Reduced from 120x120 to 60x60
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # 20 FPS
        
    def set_rpm(self, rpm):
        self.rpm = rpm
        
    def update_animation(self):
        if self.rpm > 0:
            # Calculate rotation speed based on RPM
            self.angle += (self.rpm / 1000) * 2
            if self.angle >= 360:
                self.angle = 0
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        radius = 22  # Reduced from 45 to 22 (roughly half)
        
        # Fan housing
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.setPen(QPen(QColor(100, 100, 100), 1))  # Reduced pen width from 2 to 1
        painter.drawEllipse(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        
        # Fan blades
        painter.setBrush(QBrush(QColor(150, 150, 150)))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        
        painter.translate(center)
        painter.rotate(self.angle)
        
        for i in range(3):
            painter.rotate(120)
            blade_path = QPainterPath()
            blade_path.moveTo(0, 0)
            blade_path.quadTo(15, -4, 17, 0)  # Reduced from (30, -8, 35, 0) to (15, -4, 17, 0)
            blade_path.quadTo(15, 4, 0, 0)   # Reduced from (30, 8, 0, 0) to (15, 4, 0, 0)
            painter.fillPath(blade_path, QBrush(QColor(180, 180, 180)))
            
        painter.resetTransform()

class MetricWidget(QWidget):
    def __init__(self, title, value="--", unit="", color="#00BCD4"):
        super().__init__()
        self.title = title
        self.value = value
        self.unit = unit
        self.color = color
        self.setFixedHeight(80)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
        """)
        
        # Value container
        value_container = QHBoxLayout()
        value_container.setContentsMargins(0, 0, 0, 0)
        
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        self.unit_label = QLabel(self.unit)
        self.unit_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14px;
                margin-left: 5px;
            }
        """)
        
        value_container.addWidget(self.value_label)
        value_container.addWidget(self.unit_label)
        value_container.addStretch()
        
        layout.addWidget(title_label)
        layout.addLayout(value_container)
        
        self.setLayout(layout)
        self.setStyleSheet(f"""
            MetricWidget {{
                background-color: #2E2E2E;
                border-radius: 8px;
                border-left: 4px solid {self.color};
            }}
        """)
        
    def update_value(self, value, unit=None):
        self.value_label.setText(str(value))
        if unit:
            self.unit_label.setText(unit)

class ProgressBarWidget(QWidget):
    def __init__(self, title, max_value=100, color="#4CAF50"):
        super().__init__()
        self.title = title
        self.max_value = max_value
        self.color = color
        self.current_value = 0
        self.setFixedHeight(60)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Header with title and value
        header = QHBoxLayout()
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        
        self.value_label = QLabel("0%")
        self.value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.value_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.max_value)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #444;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {self.color};
                border-radius: 4px;
            }}
        """)
        
        layout.addLayout(header)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            ProgressBarWidget {
                background-color: #2E2E2E;
                border-radius: 8px;
            }
        """)
        
    def update_value(self, value):
        self.current_value = value
        self.progress_bar.setValue(value)
        percentage = (value / self.max_value) * 100
        self.value_label.setText(f"{percentage:.1f}%")

class GPUValidator:
    """Validates if detected GPU is RTX and gets hardware info"""
    
    @staticmethod
    def is_rtx_gpu(gpu_name):
        """Check if GPU is RTX series"""
        if not gpu_name:
            return False
        gpu_name_lower = gpu_name.lower()
        rtx_patterns = [
            r'rtx\s*20\d+',  # RTX 20xx series
            r'rtx\s*30\d+',  # RTX 30xx series  
            r'rtx\s*40\d+',  # RTX 40xx series
            r'rtx\s*a\d+',   # RTX Axx series (professional)
            r'geforce\s*rtx', # GeForce RTX
            r'quadro\s*rtx'   # Quadro RTX
        ]
        return any(re.search(pattern, gpu_name_lower) for pattern in rtx_patterns)
    
    @staticmethod
    def get_gpu_fan_count(gpu_name):
        """Get expected fan count based on GPU model"""
        if not gpu_name:
            return 1
            
        gpu_name_lower = gpu_name.lower()
        
        # RTX 40 series - more specific detection
        if re.search(r'rtx\s*4090', gpu_name_lower):
            return 3  # RTX 4090 typically has 3 fans
        elif re.search(r'rtx\s*4080', gpu_name_lower):
            return 3  # RTX 4080 typically has 3 fans
        elif re.search(r'rtx\s*4070\s*ti', gpu_name_lower):
            return 3  # RTX 4070 Ti typically has 3 fans
        elif re.search(r'rtx\s*4070', gpu_name_lower):
            return 2  # RTX 4070 typically has 2 fans
        elif re.search(r'rtx\s*40[56]0', gpu_name_lower):
            return 2  # RTX 4050/4060 typically have 2 fans
            
        # RTX 30 series - more specific detection
        elif re.search(r'rtx\s*3090\s*ti', gpu_name_lower):
            return 3  # RTX 3090 Ti typically has 3 fans
        elif re.search(r'rtx\s*3090', gpu_name_lower):
            return 3  # RTX 3090 typically has 3 fans
        elif re.search(r'rtx\s*3080\s*ti', gpu_name_lower):
            return 3  # RTX 3080 Ti typically has 3 fans
        elif re.search(r'rtx\s*3080', gpu_name_lower):
            return 3  # RTX 3080 typically has 3 fans
        elif re.search(r'rtx\s*3070\s*ti', gpu_name_lower):
            return 3  # RTX 3070 Ti typically has 3 fans
        elif re.search(r'rtx\s*3070', gpu_name_lower):
            return 2  # RTX 3070 typically has 2 fans
        elif re.search(r'rtx\s*30[56]0', gpu_name_lower):
            return 2  # RTX 3050/3060 typically have 2 fans
            
        # RTX 20 series
        elif re.search(r'rtx\s*2080\s*ti', gpu_name_lower):
            return 3  # RTX 2080 Ti typically has 3 fans
        elif re.search(r'rtx\s*2080', gpu_name_lower):
            return 2  # RTX 2080 typically has 2 fans
        elif re.search(r'rtx\s*20[67]0', gpu_name_lower):
            return 2  # RTX 2060/2070 typically have 2 fans
            
        # Professional/Workstation cards
        elif 'quadro' in gpu_name_lower or 'tesla' in gpu_name_lower:
            return 1  # Usually single blower fan
            
        return 3  # Default to 3 for unknown RTX cards (most high-end have 3)

class NVMLInterface:
    """Interface for NVML (NVIDIA Management Library)"""
    
    def __init__(self):
        self.initialized = False
        self.device_handle = None
        self.init_nvml()
    
    def init_nvml(self):
        """Initialize NVML if available"""
        if not PYNVML_AVAILABLE:
            return False
            
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                self.device_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self.initialized = True
                return True
        except Exception as e:
            print(f"Failed to initialize NVML: {e}")
        return False
    
    def get_fan_count(self):
        """Get actual fan count from NVML"""
        if not self.initialized:
            return None
        try:
            # Try to get fan count - this might not be supported on all cards
            return pynvml.nvmlDeviceGetNumFans(self.device_handle)
        except pynvml.NVMLError:
            # Fallback: try to query individual fans to count them
            fan_count = 0
            for i in range(10):  # Check up to 10 fans
                try:
                    pynvml.nvmlDeviceGetFanSpeed_v2(self.device_handle, i)
                    fan_count += 1
                except:
                    break
            return fan_count if fan_count > 0 else None
    
    def get_fan_speeds(self):
        """Get fan speeds for all fans"""
        if not self.initialized:
            return []
        
        fan_speeds = []
        fan_count = self.get_fan_count()
        
        if fan_count is None:
            # Try legacy single fan speed
            try:
                speed = pynvml.nvmlDeviceGetFanSpeed(self.device_handle)
                return [speed]
            except:
                return []
        
        # Get individual fan speeds
        for i in range(fan_count):
            try:
                speed = pynvml.nvmlDeviceGetFanSpeed_v2(self.device_handle, i)
                fan_speeds.append(speed)
            except:
                # Fallback to general fan speed for this index
                try:
                    speed = pynvml.nvmlDeviceGetFanSpeed(self.device_handle)
                    fan_speeds.append(speed)
                except:
                    fan_speeds.append(0)
        
        return fan_speeds
    
    def get_fan_speed(self, fan_id=0):
        """Get fan speed percentage for specific fan"""
        if not self.initialized:
            return None
        try:
            return pynvml.nvmlDeviceGetFanSpeed_v2(self.device_handle, fan_id)
        except:
            # Fallback to general fan speed
            try:
                return pynvml.nvmlDeviceGetFanSpeed(self.device_handle)
            except:
                return None
    
    def get_power_usage(self):
        """Get power usage in watts"""
        if not self.initialized:
            return None
        try:
            return pynvml.nvmlDeviceGetPowerUsage(self.device_handle) / 1000.0
        except:
            return None
    
    def get_temperature(self):
        """Get GPU temperature"""
        if not self.initialized:
            return None
        try:
            return pynvml.nvmlDeviceGetTemperature(self.device_handle, pynvml.NVML_TEMPERATURE_GPU)
        except:
            return None
    
    def cleanup(self):
        """Cleanup NVML"""
        if self.initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass

class NvidiaSMIInterface:
    """Interface for nvidia-smi command line tool"""
    
    def __init__(self):
        self.available = self.check_nvidia_smi()
    
    def check_nvidia_smi(self):
        """Check if nvidia-smi is available"""
        try:
            result = subprocess.run(['nvidia-smi', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def get_gpu_data(self):
        """Get GPU data using nvidia-smi"""
        if not self.available:
            return {}
        
        try:
            result = subprocess.run([
                'nvidia-smi', 
                '--query-gpu=name,driver_version,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw,power.limit,clocks.current.graphics,clocks.max.graphics,clocks.current.memory,clocks.max.memory,fan.speed',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                return self.parse_nvidia_smi_output(result.stdout.strip())
        except Exception as e:
            print(f"nvidia-smi error: {e}")
        
        return {}
    
    def parse_nvidia_smi_output(self, output):
        """Parse nvidia-smi output with validation"""
        try:
            values = [v.strip() for v in output.split(',')]
            if len(values) < 13:
                return {}
            
            data = {}
            
            # Validate and convert each value
            try:
                data['power_draw'] = self.safe_float(values[6])
                data['power_limit'] = self.safe_float(values[7])
                data['gpu_clock'] = self.safe_int(values[8])
                data['gpu_clock_max'] = self.safe_int(values[9])
                data['memory_clock'] = self.safe_int(values[10])
                data['memory_clock_max'] = self.safe_int(values[11])
                data['fan_speed'] = self.safe_int(values[12])
            except (ValueError, IndexError) as e:
                print(f"Error parsing nvidia-smi values: {e}")
                
            return data
            
        except Exception as e:
            print(f"Error parsing nvidia-smi output: {e}")
            return {}
    
    @staticmethod
    def safe_float(value, default=0.0):
        """Safely convert to float"""
        if value in ['[N/A]', 'N/A', '', '[Not Supported]']:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value, default=0):
        """Safely convert to int"""
        if value in ['[N/A]', 'N/A', '', '[Not Supported]']:
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default
    
    def get_fan_data(self):
        """Get detailed fan data using nvidia-smi"""
        if not self.available:
            return {}
        
        try:
            # Try to get fan speeds for multiple fans
            result = subprocess.run([
                'nvidia-smi', 
                '--query-gpu=fan.speed',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=10)
            
            fan_data = {}
            if result.returncode == 0 and result.stdout.strip():
                fan_speeds_str = result.stdout.strip()
                # Some GPUs return multiple fan speeds separated by commas
                if ',' in fan_speeds_str:
                    speeds = [self.safe_int(s.strip()) for s in fan_speeds_str.split(',')]
                    fan_data['fan_speeds'] = speeds
                else:
                    speed = self.safe_int(fan_speeds_str)
                    fan_data['fan_speeds'] = [speed]
            
            return fan_data
            
        except Exception as e:
            print(f"nvidia-smi fan data error: {e}")
            return {}
    
class DirectGPUInterface:
    """Direct GPU interface without GPUtil dependency"""
    
    def __init__(self):
        self.nvidia_smi = NvidiaSMIInterface()
        self.nvml = NVMLInterface()
        
    def get_gpus(self):
        """Get GPU list using available methods"""
        gpus = []
        
        # Try NVML first
        if self.nvml.initialized:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    gpu_info = self.get_gpu_info_nvml(handle)
                    if gpu_info:
                        gpus.append(gpu_info)
            except Exception as e:
                print(f"NVML GPU enumeration failed: {e}")
        
        # Fallback to nvidia-smi
        if not gpus and self.nvidia_smi.available:
            gpu_info = self.get_gpu_info_smi()
            if gpu_info:
                gpus.append(gpu_info)
        
        return gpus
    
    def get_gpu_info_nvml(self, handle):
        """Get GPU info using NVML"""
        try:
            # Handle both bytes and string returns from pynvml
            name_raw = pynvml.nvmlDeviceGetName(handle)
            name = name_raw.decode('utf-8') if isinstance(name_raw, bytes) else name_raw
            
            driver_raw = pynvml.nvmlSystemGetDriverVersion()
            driver_version = driver_raw.decode('utf-8') if isinstance(driver_raw, bytes) else driver_raw
            
            # Memory info
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_total = mem_info.total // (1024 * 1024)  # Convert to MB
            memory_used = mem_info.used // (1024 * 1024)
            
            # Temperature
            try:
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except:
                temperature = 0
            
            # Utilization
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                load = util.gpu / 100.0  # Convert to fraction
            except:
                load = 0.0
            
            return {
                'name': name,
                'driver': driver_version,
                'memoryTotal': memory_total,
                'memoryUsed': memory_used,
                'temperature': temperature,
                'load': load
            }
        except Exception as e:
            print(f"Error getting NVML GPU info: {e}")
            return None
    
    def get_gpu_info_smi(self):
        """Get GPU info using nvidia-smi as fallback"""
        try:
            result = subprocess.run([
                'nvidia-smi', 
                '--query-gpu=name,driver_version,memory.total,memory.used,temperature.gpu,utilization.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                values = [v.strip() for v in result.stdout.strip().split(',')]
                if len(values) >= 6:
                    return {
                        'name': values[0],
                        'driver': values[1],
                        'memoryTotal': self.safe_int(values[2]),
                        'memoryUsed': self.safe_int(values[3]),
                        'temperature': self.safe_float(values[4]),
                        'load': self.safe_float(values[5]) / 100.0  # Convert to fraction
                    }
        except Exception as e:
            print(f"nvidia-smi GPU info failed: {e}")
        
        return None
    
    @staticmethod
    def safe_float(value, default=0.0):
        """Safely convert to float"""
        if value in ['[N/A]', 'N/A', '', '[Not Supported]']:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value, default=0):
        """Safely convert to int"""
        if value in ['[N/A]', 'N/A', '', '[Not Supported]']:
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

class GPUMonitor(QThread):
    data_updated = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.nvml = NVMLInterface()
        self.nvidia_smi = NvidiaSMIInterface()
        self.direct_gpu = DirectGPUInterface()
        self.rtx_gpu_detected = False
        self.gpu_name = ""
        
    def run(self):
        while self.running:
            try:
                data = self.get_gpu_data()
                if data:
                    self.data_updated.emit(data)
                else:
                    self.error_occurred.emit("No valid GPU data available")
                self.msleep(1000)
            except Exception as e:
                self.error_occurred.emit(f"Monitor error: {str(e)}")
                self.msleep(2000)
                
    def get_gpu_data(self):
        """Get comprehensive GPU data with validation"""
        data = {}
        
        # Get basic GPU info using direct interface (replaces GPUtil)
        gpus = self.direct_gpu.get_gpus()
        if not gpus:
            return self.get_fallback_data("No GPU detected")
        
        gpu = gpus[0]  # Use first GPU
        self.gpu_name = gpu['name']
        
        # Validate RTX GPU
        if not GPUValidator.is_rtx_gpu(gpu['name']):
            self.rtx_gpu_detected = False
            return self.get_fallback_data(f"Non-RTX GPU detected: {gpu['name']}")
        
        self.rtx_gpu_detected = True
        
        # Base data from direct GPU interface
        data.update({
            'name': gpu['name'],
            'driver': gpu['driver'],
            'temperature': self.validate_temperature(gpu['temperature']),
            'load': self.validate_percentage(gpu['load'] * 100),
            'memory_used_mb': gpu['memoryUsed'],
            'memory_total_mb': gpu['memoryTotal'],
            'memory_used_gb': gpu['memoryUsed'] / 1024,
            'memory_total_gb': gpu['memoryTotal'] / 1024,
            'memory_percent': self.validate_percentage((gpu['memoryUsed'] / gpu['memoryTotal']) * 100 if gpu['memoryTotal'] > 0 else 0)
        })
        
        # Get fan data from multiple sources
        fan_speeds = []
        fan_count = self.get_actual_fan_count()
        
        # Enhanced data from NVML if available
        if self.nvml.initialized:
            nvml_temp = self.nvml.get_temperature()
            if nvml_temp is not None:
                data['temperature'] = self.validate_temperature(nvml_temp)
            
            nvml_power = self.nvml.get_power_usage()
            if nvml_power is not None:
                data['power_draw'] = nvml_power
            
            # Get individual fan speeds from NVML
            nvml_fan_speeds = self.nvml.get_fan_speeds()
            if nvml_fan_speeds:
                fan_speeds = nvml_fan_speeds
        
        # Additional data from nvidia-smi
        smi_data = self.nvidia_smi.get_gpu_data()
        data.update(smi_data)
        
        # Get fan data from nvidia-smi if NVML didn't provide it
        if not fan_speeds:
            smi_fan_data = self.nvidia_smi.get_fan_data()
            if 'fan_speeds' in smi_fan_data:
                fan_speeds = smi_fan_data['fan_speeds']
        
        # Ensure we have the right number of fan speeds
        if len(fan_speeds) < fan_count:
            # Pad with zeros or duplicate last speed
            if fan_speeds:
                # Duplicate the last known speed for missing fans
                last_speed = fan_speeds[-1]
                while len(fan_speeds) < fan_count:
                    fan_speeds.append(last_speed)
            else:
                # No fan data available, use general fan speed if available
                general_fan_speed = data.get('fan_speed', 0)
                fan_speeds = [general_fan_speed] * fan_count
        elif len(fan_speeds) > fan_count:
            # Trim to expected count
            fan_speeds = fan_speeds[:fan_count]
        
        # Calculate individual fan RPMs
        fan_rpms = []
        for i, speed_percent in enumerate(fan_speeds):
            rpm = self.calculate_fan_rpm(gpu['name'], self.validate_percentage(speed_percent))
            fan_rpms.append(rpm)
        
        data['fan_count'] = fan_count
        data['fan_speeds'] = fan_speeds  # Individual fan speeds
        data['fan_rpms'] = fan_rpms      # Individual fan RPMs
        
        # Keep legacy single fan data for compatibility
        data['fan_speed'] = max(fan_speeds) if fan_speeds else 0
        data['fan_rpm'] = max(fan_rpms) if fan_rpms else 0
        
        # Validate all data
        return self.validate_data(data)
    
    def get_actual_fan_count(self):
        """Get actual fan count from hardware or model database"""
        # Try NVML first
        if self.nvml.initialized:
            nvml_fan_count = self.nvml.get_fan_count()
            if nvml_fan_count is not None and nvml_fan_count > 0:
                return nvml_fan_count
        
        # Fallback to model-based detection
        model_fan_count = GPUValidator.get_gpu_fan_count(self.gpu_name)
        print(f"GPU {self.gpu_name} detected fan count: {model_fan_count}")
        return model_fan_count
    
    def calculate_fan_rpm(self, gpu_name, fan_speed_percent):
        """Calculate realistic fan RPM based on GPU model and fan speed"""
        if fan_speed_percent <= 0:
            return 0
        
        # Model-specific max RPM values (based on manufacturer specs)
        gpu_lower = gpu_name.lower()
        
        if 'rtx 4090' in gpu_lower:
            max_rpm = 2400  # Typical for RTX 4090
        elif 'rtx 4080' in gpu_lower:
            max_rpm = 2200
        elif 'rtx 4070' in gpu_lower:
            max_rpm = 2000
        elif 'rtx 3090' in gpu_lower:
            max_rpm = 2300
        elif 'rtx 3080' in gpu_lower:
            max_rpm = 2100
        elif 'rtx 3070' in gpu_lower:
            max_rpm = 1900
        elif 'rtx 3060' in gpu_lower:
            max_rpm = 1800
        elif 'rtx 20' in gpu_lower:
            max_rpm = 2000  # RTX 20 series average
        else:
            max_rpm = 2000  # Conservative fallback
        
        # Apply curve for more realistic RPM calculation
        # Most GPUs don't spin fans until 30-40% and have non-linear curves
        if fan_speed_percent < 30:
            return 0  # Zero RPM mode
        
        # Non-linear fan curve
        normalized_speed = (fan_speed_percent - 30) / 70
        rpm = int(max_rpm * (0.3 + 0.7 * normalized_speed))
        
        return max(0, min(rpm, max_rpm))
    
    def get_fallback_data(self, message):
        """Return fallback data when GPU detection fails"""
        return {
            'name': message,
            'driver': 'N/A',
            'temperature': 0,
            'load': 0,
            'memory_used_mb': 0,
            'memory_total_mb': 0,
            'memory_used_gb': 0,
            'memory_total_gb': 0,
            'memory_percent': 0,
            'power_draw': 0,
            'power_limit': 0,
            'gpu_clock': 0,
            'gpu_clock_max': 0,
            'memory_clock': 0,
            'memory_clock_max': 0,
            'fan_speed': 0,
            'fan_count': 1,
            'fan_rpm': 0,
            'is_rtx': False
        }
    
    def validate_data(self, data):
        """Validate and sanitize all data values"""
        validated = {}
        
        for key, value in data.items():
            if key in ['temperature']:
                validated[key] = self.validate_temperature(value)
            elif key in ['load', 'memory_percent', 'fan_speed']:
                validated[key] = self.validate_percentage(value)
            elif key in ['fan_speeds']:
                # Validate array of fan speeds
                validated[key] = [self.validate_percentage(speed) for speed in (value if value else [])]
            elif key in ['fan_rpms']:
                # Validate array of fan RPMs
                validated[key] = [max(0, int(rpm) if rpm else 0) for rpm in (value if value else [])]
            elif key in ['memory_used_mb', 'memory_total_mb', 'memory_used_gb', 'memory_total_gb']:
                validated[key] = max(0, float(value) if value else 0)
            elif key in ['power_draw', 'power_limit']:
                validated[key] = max(0, float(value) if value else 0)
            elif key in ['gpu_clock', 'gpu_clock_max', 'memory_clock', 'memory_clock_max', 'fan_rpm', 'fan_count']:
                validated[key] = max(0, int(value) if value else 0)
            else:
                validated[key] = value
        
        validated['is_rtx'] = self.rtx_gpu_detected
        return validated
    
    @staticmethod
    def validate_temperature(temp):
        """Validate temperature value"""
        try:
            temp_val = float(temp) if temp else 0
            return max(0, min(150, temp_val))  # Cap at reasonable limits
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def validate_percentage(percent):
        """Validate percentage value"""
        try:
            percent_val = float(percent) if percent else 0
            return max(0, min(100, percent_val))
        except (ValueError, TypeError):
            return 0
        
    def stop(self):
        self.running = False
        if self.nvml:
            self.nvml.cleanup()

class FeatureStatusWidget(QWidget):
    """Widget to display individual GPU feature status"""
    
    def __init__(self, feature_name, status="Unknown", description="", parent=None):
        super().__init__(parent)
        self.feature_name = feature_name
        self.status = status
        self.description = description
        self.setFixedHeight(50)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFixedSize(16, 16)
        self.status_indicator.setAlignment(Qt.AlignCenter)
        
        # Feature name
        feature_label = QLabel(self.feature_name)
        feature_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-width: 180px;
            }
        """)
        
        # Status text
        self.status_label = QLabel(self.status)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                min-width: 80px;
            }
        """)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
            }
        """)
        desc_label.setWordWrap(True)
        
        layout.addWidget(self.status_indicator)
        layout.addWidget(feature_label)
        layout.addWidget(self.status_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.update_status(self.status)
    
    def update_status(self, status):
        """Update the status and visual indicator"""
        self.status = status
        self.status_label.setText(status)
        
        if status.lower() in ["active", "enabled", "supported", "on"]:
            color = "#4CAF50"  # Green
            self.status_label.setStyleSheet("QLabel { color: #4CAF50; font-size: 12px; min-width: 80px; }")
        elif status.lower() in ["inactive", "disabled", "off"]:
            color = "#FFC107"  # Amber
            self.status_label.setStyleSheet("QLabel { color: #FFC107; font-size: 12px; min-width: 80px; }")
        elif status.lower() in ["error", "not supported", "unavailable"]:
            color = "#F44336"  # Red
            self.status_label.setStyleSheet("QLabel { color: #F44336; font-size: 12px; min-width: 80px; }")
        else:
            color = "#666"  # Gray
            self.status_label.setStyleSheet("QLabel { color: #666; font-size: 12px; min-width: 80px; }")
        
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
                font-weight: bold;
            }}
        """)

class NVIDIARegistryInterface:
    """Interface to read NVIDIA settings from Windows registry"""
    
    def __init__(self):
        self.nvidia_key_paths = [
            r"SYSTEM\CurrentControlSet\Control\Video",
            r"SOFTWARE\NVIDIA Corporation\Global",
            r"SOFTWARE\NVIDIA Corporation\Global\NVTweak",
        ]
    
    def read_registry_value(self, hkey, key_path, value_name):
        """Safely read a registry value"""
        try:
            with winreg.OpenKey(hkey, key_path) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
        except (FileNotFoundError, OSError, PermissionError):
            return None
    
    def get_nvidia_settings(self):
        """Get NVIDIA settings from registry"""
        settings = {}
        
        # Common NVIDIA registry locations
        registry_queries = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "Vsync"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "PowerMizerEnable"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "DisplayGamma"),
        ]
        
        for hkey, path, value_name in registry_queries:
            result = self.read_registry_value(hkey, path, value_name)
            if result is not None:
                settings[value_name] = result
        
        return settings

class GPUFeaturesDetector:
    """Detector for GPU features and capabilities"""
    
    def __init__(self):
        self.nvml = None
        self.nvidia_smi = NvidiaSMIInterface()
        self.registry = NVIDIARegistryInterface()
        
        # Initialize NVML if available
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                if pynvml.nvmlDeviceGetCount() > 0:
                    self.nvml = pynvml.nvmlDeviceGetHandleByIndex(0)
            except:
                pass
    
    def detect_resizable_bar(self):
        """Detect Resizable BAR (Smart Access Memory) status"""
        try:
            if self.nvml:
                # Try to get BAR1 memory info as indicator
                bar1_info = pynvml.nvmlDeviceGetBAR1MemoryInfo(self.nvml)
                if bar1_info.bar1Total > 256 * 1024 * 1024:  # > 256MB suggests ReBAR
                    return "Enabled"
            
            # Fallback: check via nvidia-smi or system detection
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=pci.bar1_memory_usage.total',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                bar_size = int(result.stdout.strip() or 0)
                if bar_size > 256:  # MB
                    return "Enabled"
            
            return "Disabled"
        except:
            return "Unknown"
    
    def detect_ray_tracing(self, gpu_name):
        """Detect Ray Tracing support"""
        if not gpu_name:
            return "Unknown"
        
        gpu_lower = gpu_name.lower()
        if any(series in gpu_lower for series in ['rtx 20', 'rtx 30', 'rtx 40']):
            return "Supported"
        elif 'gtx' in gpu_lower:
            return "Not Supported"
        else:
            return "Unknown"
    
    def detect_dlss(self, gpu_name):
        """Detect DLSS support"""
        if not gpu_name:
            return "Unknown"
        
        gpu_lower = gpu_name.lower()
        # DLSS requires RTX 20 series or newer
        if any(series in gpu_lower for series in ['rtx 20', 'rtx 30', 'rtx 40']):
            return "Supported"
        else:
            return "Not Supported"
    
    def detect_dsr_support(self):
        """Detect Dynamic Super Resolution support"""
        try:
            # Check nvidia-smi for DSR capability
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=name',
                '--format=csv,noheader'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                gpu_name = result.stdout.strip()
                # Most modern NVIDIA GPUs support DSR
                if any(series in gpu_name.lower() for series in ['gtx 9', 'gtx 10', 'gtx 16', 'rtx']):
                    return "Supported"
            
            return "Unknown"
        except:
            return "Unknown"
    
    def detect_power_management(self):
        """Detect power management mode"""
        try:
            # Check current power management mode
            if self.nvml:
                try:
                    power_mode = pynvml.nvmlDeviceGetPowerManagementMode(self.nvml)
                    return "Enabled" if power_mode else "Disabled"
                except:
                    pass
            
            # Fallback to registry or default
            settings = self.registry.get_nvidia_settings()
            power_setting = settings.get("PowerMizerEnable", None)
            if power_setting is not None:
                return "Enabled" if power_setting else "Disabled"
            
            return "Adaptive"  # Default mode
        except:
            return "Unknown"
    
    def detect_vsync_status(self):
        """Detect V-Sync status"""
        try:
            settings = self.registry.get_nvidia_settings()
            vsync_setting = settings.get("Vsync", None)
            
            if vsync_setting is not None:
                if vsync_setting == 0:
                    return "Disabled"
                elif vsync_setting == 1:
                    return "Enabled"
                elif vsync_setting == 2:
                    return "Adaptive"
            
            return "Application Controlled"
        except:
            return "Unknown"
    
    def detect_low_latency_mode(self):
        """Detect Low Latency Mode (Ultra Low Latency/Reflex)"""
        try:
            # Check if GPU supports NVIDIA Reflex
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=name',
                '--format=csv,noheader'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                gpu_name = result.stdout.strip().lower()
                # Reflex requires RTX 20 series or newer
                if any(series in gpu_name for series in ['rtx 20', 'rtx 30', 'rtx 40']):
                    return "Available"
                else:
                    return "Not Supported"
            
            return "Unknown"
        except:
            return "Unknown"
    
    def detect_cuda_cores(self, gpu_name):
        """Detect approximate CUDA core count"""
        if not gpu_name:
            return "Unknown"
        
        gpu_lower = gpu_name.lower()
        
        # RTX 40 series
        if 'rtx 4090' in gpu_lower:
            return "16384"
        elif 'rtx 4080' in gpu_lower:
            return "9728"
        elif 'rtx 4070 ti' in gpu_lower:
            return "7680"
        elif 'rtx 4070' in gpu_lower:
            return "5888"
        elif 'rtx 4060 ti' in gpu_lower:
            return "4352"
        elif 'rtx 4060' in gpu_lower:
            return "3072"
        
        # RTX 30 series
        elif 'rtx 3090 ti' in gpu_lower:
            return "10752"
        elif 'rtx 3090' in gpu_lower:
            return "10496"
        elif 'rtx 3080 ti' in gpu_lower:
            return "10240"
        elif 'rtx 3080' in gpu_lower:
            return "8704"
        elif 'rtx 3070 ti' in gpu_lower:
            return "6144"
        elif 'rtx 3070' in gpu_lower:
            return "5888"
        elif 'rtx 3060 ti' in gpu_lower:
            return "4864"
        elif 'rtx 3060' in gpu_lower:
            return "3584"
        
        # RTX 20 series
        elif 'rtx 2080 ti' in gpu_lower:
            return "4352"
        elif 'rtx 2080' in gpu_lower:
            return "2944"
        elif 'rtx 2070' in gpu_lower:
            return "2304"
        elif 'rtx 2060' in gpu_lower:
            return "1920"
        
        return "Unknown"
    
    def get_all_features(self, gpu_name):
        """Get all GPU features and their status"""
        features = {}
        
        # Hardware capabilities
        features['Resizable BAR'] = {
            'status': self.detect_resizable_bar(),
            'description': 'Allows CPU to access entire GPU memory for better performance'
        }
        
        features['Ray Tracing'] = {
            'status': self.detect_ray_tracing(gpu_name),
            'description': 'Hardware-accelerated ray tracing for realistic lighting'
        }
        
        features['DLSS'] = {
            'status': self.detect_dlss(gpu_name),
            'description': 'AI-powered super resolution for better performance'
        }
        
        features['DSR Support'] = {
            'status': self.detect_dsr_support(),
            'description': 'Dynamic Super Resolution for enhanced image quality'
        }
        
        features['CUDA Cores'] = {
            'status': self.detect_cuda_cores(gpu_name),
            'description': 'Parallel processing units for compute workloads'
        }
        
        # Power and performance
        features['Power Management'] = {
            'status': self.detect_power_management(),
            'description': 'Adaptive power scaling for efficiency'
        }
        
        features['Low Latency Mode'] = {
            'status': self.detect_low_latency_mode(),
            'description': 'NVIDIA Reflex for reduced input lag'
        }
        
        # Display features
        features['V-Sync'] = {
            'status': self.detect_vsync_status(),
            'description': 'Vertical synchronization to prevent screen tearing'
        }
        
        # Additional features
        features['GPU Boost'] = {
            'status': "Active" if any(series in gpu_name.lower() for series in ['gtx 9', 'gtx 10', 'rtx']) else "Not Supported",
            'description': 'Automatic GPU clock boosting for better performance'
        }
        
        features['Multi-Display'] = {
            'status': "Supported",
            'description': 'Support for multiple simultaneous displays'
        }
        
        features['HDR Support'] = {
            'status': "Supported" if 'rtx' in gpu_name.lower() else "Limited",
            'description': 'High Dynamic Range display support'
        }
        
        features['G-Sync Compatible'] = {
            'status': "Supported" if any(series in gpu_name.lower() for series in ['gtx 10', 'gtx 16', 'rtx']) else "Not Supported",
            'description': 'Variable refresh rate technology'
        }
        
        return features

class GPUFeaturesWidget(QWidget):
    """Widget to display comprehensive GPU features and status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.features_detector = GPUFeaturesDetector()
        self.feature_widgets = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("GPU Features & Capabilities")
        title_label.setStyleSheet("""
            QLabel {
                color: #00BCD4;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setFixedSize(100, 30)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E2E2E;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3E3E3E;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_features)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area for features
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.features_layout = QVBoxLayout(scroll_widget)
        self.features_layout.setSpacing(5)
        
        # Status summary
        self.status_summary = QLabel("Initializing feature detection...")
        self.status_summary.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                margin-bottom: 10px;
                padding: 10px;
                background-color: #2A2A2A;
                border-radius: 4px;
            }
        """)
        self.features_layout.addWidget(self.status_summary)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        layout.addWidget(scroll_area)
        self.setLayout(layout)
        
        # Initialize with placeholder features
        self.update_features("Unknown GPU")
    
    def update_features(self, gpu_name):
        """Update features based on GPU name"""
        # Clear existing widgets
        for widget in self.feature_widgets.values():
            widget.setParent(None)
        self.feature_widgets.clear()
        
        # Get all features
        features = self.features_detector.get_all_features(gpu_name)
        
        # Count statuses for summary
        supported_count = 0
        active_count = 0
        total_count = len(features)
        
        # Create feature widgets
        for feature_name, feature_data in features.items():
            status = feature_data['status']
            description = feature_data['description']
            
            feature_widget = FeatureStatusWidget(feature_name, status, description)
            feature_widget.setStyleSheet("""
                FeatureStatusWidget {
                    background-color: #2E2E2E;
                    border-radius: 6px;
                    margin: 2px;
                }
                FeatureStatusWidget:hover {
                    background-color: #3E3E3E;
                }
            """)
            
            self.feature_widgets[feature_name] = feature_widget
            self.features_layout.addWidget(feature_widget)
            
            # Count for summary
            if status.lower() in ["supported", "active", "enabled", "available"]:
                supported_count += 1
                if status.lower() in ["active", "enabled"]:
                    active_count += 1
        
        # Update status summary
        self.status_summary.setText(
            f"GPU: {gpu_name} | "
            f"Features: {total_count} total, {supported_count} supported, {active_count} active | "
            f"Last updated: {time.strftime('%H:%M:%S')}"
        )
        
        # Add stretch to push everything to top
        self.features_layout.addStretch()
    
    def refresh_features(self):
        """Refresh feature detection"""
        # Get current GPU name from main monitor
        # This is a placeholder - in real implementation, get from parent
        self.refresh_btn.setText("🔄 Refreshing...")
        self.refresh_btn.setEnabled(False)
        
        # Reinitialize detector
        self.features_detector = GPUFeaturesDetector()
        
        # Update features (placeholder GPU name)
        self.update_features("RTX 4090")  # This should come from parent
        
        self.refresh_btn.setText("🔄 Refresh")
        self.refresh_btn.setEnabled(True)

class RTXDiagApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTX Diagnostic Tool")
        self.setGeometry(100, 100, 1400, 900)  # Increased width for new panel
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: white;
            }
            QScrollArea {
                border: none;
                background-color: #1E1E1E;
            }
            QScrollBar:vertical {
                background-color: #2E2E2E;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
        """)
        
        self.setup_ui()
        self.setup_monitoring()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("RTX Diagnostic Dashboard")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #00BCD4;
                margin-bottom: 10px;
            }
        """)
        
        self.gpu_name_label = QLabel("Detecting GPU...")
        self.gpu_name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #888;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.gpu_name_label)
        
        main_layout.addLayout(header_layout)
        
        # Main content with horizontal split
        content_layout = QHBoxLayout()
        
        # Left side - existing monitoring panels
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(800)
        
        # Scroll area for left content
        left_scroll = QScrollArea()
        left_scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(left_scroll_widget)
        
        # Fan section - Replace animated fans with metric widgets
        fans_group = QGroupBox("Cooling System")
        fans_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #00BCD4;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create a grid layout for fan metrics
        fans_layout = QGridLayout(fans_group)
        fans_layout.setSpacing(15)
        fans_layout.setContentsMargins(15, 20, 15, 15)
        
        # Initialize fan widgets storage
        self.fan_speed_widgets = []
        self.fan_rpm_widgets = []
        self.fan_temp_widgets = []
        self.fans_layout = fans_layout
        
        # Define colors for different fans
        self.fan_colors = [
            "#00BCD4",  # Cyan for Fan 1
            "#4CAF50",  # Green for Fan 2  
            "#FF9800",  # Orange for Fan 3
            "#9C27B0",  # Purple for Fan 4
            "#E91E63",  # Pink for Fan 5
            "#607D8B"   # Blue Grey for Fan 6
        ]
        
        scroll_layout.addWidget(fans_group)
        
        # Metrics grid
        metrics_group = QGroupBox("GPU Metrics")
        metrics_group.setStyleSheet(fans_group.styleSheet())
        
        metrics_grid = QGridLayout(metrics_group)
        metrics_grid.setSpacing(15)
        
        # Create metric widgets
        self.temp_widget = MetricWidget("Temperature", "--", "°C", "#FF5722")
        self.load_widget = ProgressBarWidget("GPU Usage", 100, "#4CAF50")
        self.memory_widget = ProgressBarWidget("Memory Usage", 100, "#2196F3")
        self.power_widget = MetricWidget("Power Draw", "--", "W", "#FF9800")
        self.gpu_clock_widget = MetricWidget("GPU Clock", "--", "MHz", "#9C27B0")
        self.memory_clock_widget = MetricWidget("Memory Clock", "--", "MHz", "#E91E63")
        self.fan_speed_widget = ProgressBarWidget("Fan Speed", 100, "#00BCD4")
        self.driver_widget = MetricWidget("Driver Version", "--", "", "#607D8B")
        
        # Add to grid
        metrics_grid.addWidget(self.temp_widget, 0, 0)
        metrics_grid.addWidget(self.power_widget, 0, 1)
        metrics_grid.addWidget(self.gpu_clock_widget, 0, 2)
        metrics_grid.addWidget(self.load_widget, 1, 0)
        metrics_grid.addWidget(self.memory_widget, 1, 1)
        metrics_grid.addWidget(self.fan_speed_widget, 1, 2)
        metrics_grid.addWidget(self.memory_clock_widget, 2, 0)
        metrics_grid.addWidget(self.driver_widget, 2, 1, 1, 2)
        
        scroll_layout.addWidget(metrics_group)
        
        # Additional info section
        info_group = QGroupBox("Detailed Information")
        info_group.setStyleSheet(fans_group.styleSheet())
        
        info_layout = QGridLayout(info_group)
        info_layout.setSpacing(10)
        
        self.memory_used_widget = MetricWidget("Memory Used", "--", "MB", "#03DAC6")
        self.memory_total_widget = MetricWidget("Memory Total", "--", "MB", "#BB86FC")
        self.power_limit_widget = MetricWidget("Power Limit", "--", "W", "#CF6679")
        self.gpu_clock_max_widget = MetricWidget("Max GPU Clock", "--", "MHz", "#9C27B0")
        
        info_layout.addWidget(self.memory_used_widget, 0, 0)
        info_layout.addWidget(self.memory_total_widget, 0, 1)
        info_layout.addWidget(self.power_limit_widget, 1, 0)
        info_layout.addWidget(self.gpu_clock_max_widget, 1, 1)
        
        scroll_layout.addWidget(info_group)
        
        left_scroll.setWidget(left_scroll_widget)
        left_scroll.setWidgetResizable(True)
        left_layout.addWidget(left_scroll)
        
        # Right side - GPU Features panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setMinimumWidth(550)
        right_widget.setMaximumWidth(600)
        
        # GPU Features widget
        features_group = QGroupBox("GPU Features & Status")
        features_group.setStyleSheet(fans_group.styleSheet())
        features_layout = QVBoxLayout(features_group)
        
        self.gpu_features_widget = GPUFeaturesWidget()
        features_layout.addWidget(self.gpu_features_widget)
        
        right_layout.addWidget(features_group)
        
        # Add both sides to content layout
        content_layout.addWidget(left_widget, stretch=2)
        content_layout.addWidget(right_widget, stretch=1)
        
        main_layout.addLayout(content_layout)
        
    def setup_monitoring(self):
        self.monitor = GPUMonitor()
        self.monitor.data_updated.connect(self.update_gpu_data)
        self.monitor.error_occurred.connect(self.handle_monitor_error)
        self.monitor.start()
    
    def handle_monitor_error(self, error_message):
        """Handle monitoring errors"""
        print(f"GPU Monitor Error: {error_message}")
        self.gpu_name_label.setText(f"Error: {error_message}")
        
    def setup_fans(self, fan_count):
        """Setup fan metric widgets based on actual fan count"""
        # Clear existing fan widgets
        for widget in self.fan_speed_widgets:
            widget.setParent(None)
        for widget in self.fan_rpm_widgets:
            widget.setParent(None)
        for widget in self.fan_temp_widgets:
            widget.setParent(None)
        
        # Clear layout
        while self.fans_layout.count():
            child = self.fans_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
            elif child.layout():
                self.clear_layout(child.layout())
        
        self.fan_speed_widgets = []
        self.fan_rpm_widgets = []
        self.fan_temp_widgets = []
        
        # Calculate grid layout (2 columns for up to 6 fans)
        cols = 2
        rows = (fan_count + 1) // 2
        
        # Create fan metric widgets
        for i in range(fan_count):
            fan_color = self.fan_colors[i % len(self.fan_colors)]
            
            # Fan Speed Progress Bar
            fan_speed_widget = ProgressBarWidget(
                f"Fan {i+1} Speed", 
                100, 
                fan_color
            )
            self.fan_speed_widgets.append(fan_speed_widget)
            
            # Fan RPM Metric
            fan_rpm_widget = MetricWidget(
                f"Fan {i+1} RPM", 
                "--", 
                "RPM", 
                fan_color
            )
            self.fan_rpm_widgets.append(fan_rpm_widget)
            
            # Calculate grid position
            row = i // cols
            col = (i % cols) * 2  # Each fan takes 2 columns (speed + rpm)
            
            # Add widgets to grid
            self.fans_layout.addWidget(fan_speed_widget, row, col)
            self.fans_layout.addWidget(fan_rpm_widget, row, col + 1)
        
        # Add fan summary if more than 3 fans
        if fan_count > 3:
            # Overall cooling efficiency widget
            self.cooling_efficiency_widget = ProgressBarWidget(
                "Cooling Efficiency", 
                100, 
                "#00E676"  # Light green
            )
            
            # Average fan speed widget  
            self.avg_fan_speed_widget = MetricWidget(
                "Average Speed", 
                "--", 
                "%", 
                "#00E676"
            )
            
            # Add summary widgets at the bottom
            summary_row = rows
            self.fans_layout.addWidget(self.cooling_efficiency_widget, summary_row, 0)
            self.fans_layout.addWidget(self.avg_fan_speed_widget, summary_row, 1)
    
    def clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
            elif child.layout():
                self.clear_layout(child.layout())
        
    def update_gpu_data(self, data):
        # Setup fans if count changed
        fan_count = data.get('fan_count', 1)
        if len(self.fan_speed_widgets) != fan_count:
            self.setup_fans(fan_count)
        
        # Update GPU name with RTX validation indicator
        gpu_name = data.get('name', 'Unknown GPU')
        is_rtx = data.get('is_rtx', False)
        if is_rtx:
            self.gpu_name_label.setText(f"✓ {gpu_name}")
            self.gpu_name_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #4CAF50;
                }
            """)
        else:
            self.gpu_name_label.setText(f"⚠ {gpu_name}")
            self.gpu_name_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #FF9800;
                }
            """)
        
        # Update metrics with proper units
        if 'temperature' in data:
            self.temp_widget.update_value(f"{data['temperature']:.1f}")
            
        if 'load' in data:
            self.load_widget.update_value(int(data['load']))
            
        if 'memory_percent' in data:
            self.memory_widget.update_value(int(data['memory_percent']))
            
        if 'power_draw' in data:
            self.power_widget.update_value(f"{data['power_draw']:.1f}")
            
        if 'gpu_clock' in data:
            self.gpu_clock_widget.update_value(data['gpu_clock'])
            
        if 'memory_clock' in data:
            self.memory_clock_widget.update_value(data['memory_clock'])
            
        if 'fan_speed' in data:
            self.fan_speed_widget.update_value(data['fan_speed'])
            
        if 'driver' in data:
            self.driver_widget.update_value(data['driver'])
            
        # Use consistent GB units for memory
        if 'memory_used_gb' in data:
            self.memory_used_widget.update_value(f"{data['memory_used_gb']:.1f}", "GB")
            
        if 'memory_total_gb' in data:
            self.memory_total_widget.update_value(f"{data['memory_total_gb']:.1f}", "GB")
            
        if 'power_limit' in data:
            self.power_limit_widget.update_value(f"{data['power_limit']:.1f}")
            
        if 'gpu_clock_max' in data:
            self.gpu_clock_max_widget.update_value(data['gpu_clock_max'])
            
        # Update individual fan metrics
        fan_speeds = data.get('fan_speeds', [])
        fan_rpms = data.get('fan_rpms', [])
        
        total_speed = 0
        active_fans = 0
        
        for i in range(len(self.fan_speed_widgets)):
            # Get individual fan data
            if i < len(fan_speeds) and i < len(fan_rpms):
                fan_speed = fan_speeds[i]
                fan_rpm = fan_rpms[i]
            else:
                # Fallback to general fan data
                fan_speed = data.get('fan_speed', 0)
                fan_rpm = data.get('fan_rpm', 0)
            
            # Update fan speed progress bar
            if i < len(self.fan_speed_widgets):
                self.fan_speed_widgets[i].update_value(int(fan_speed))
            
            # Update fan RPM metric
            if i < len(self.fan_rpm_widgets):
                self.fan_rpm_widgets[i].update_value(f"{fan_rpm}")
            
            # Calculate totals for summary
            total_speed += fan_speed
            if fan_rpm > 0:
                active_fans += 1
        
        # Update summary widgets if they exist
        if hasattr(self, 'cooling_efficiency_widget') and len(fan_speeds) > 0:
            avg_speed = total_speed / len(fan_speeds)
            max_temp = data.get('temperature', 0)
            
            # Calculate cooling efficiency (inverse relationship with temperature)
            # Efficiency = (100 - normalized_temp) * (avg_speed / 100)
            normalized_temp = min(max_temp / 90 * 100, 100)  # Normalize to 90°C max
            efficiency = max(0, (100 - normalized_temp) * (avg_speed / 100))
            
            self.cooling_efficiency_widget.update_value(int(efficiency))
            
        if hasattr(self, 'avg_fan_speed_widget') and len(fan_speeds) > 0:
            avg_speed = total_speed / len(fan_speeds)
            self.avg_fan_speed_widget.update_value(f"{avg_speed:.0f}")
            
        # Update GPU features panel with current GPU name
        gpu_name = data.get('name', 'Unknown GPU')
        if hasattr(self, 'gpu_features_widget'):
            self.gpu_features_widget.update_features(gpu_name)
            
    def closeEvent(self, event):
        if hasattr(self, 'monitor'):
            self.monitor.stop()
            self.monitor.wait()
        event.accept()

    def get_gpu_fan_count(self):
        """Dynamic fan count - will be updated by monitor"""
        return 1  # Initial placeholder

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Check for GPU compatibility on startup
    direct_gpu = DirectGPUInterface()
    gpus = direct_gpu.get_gpus()
    
    if not gpus:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("GPU Detection")
        msg.setText("No NVIDIA GPU detected or drivers not installed.")
        msg.setInformativeText("This application requires:\n• NVIDIA RTX GPU\n• NVIDIA drivers\n• nvidia-smi utility")
        msg.exec()
    
    # Set application icon
    app.setWindowIcon(QIcon())
    
    window = RTXDiagApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    main()
