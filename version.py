"""
Gaming Helper Overlay - Version Information
"""

__version__ = "1.0.0"
__author__ = "PartyBrasil"
__email__ = "contact@partybrasil.dev"
__description__ = "Una aplicación de overlay modular para gaming con paneles flotantes y sistema de plugins extensible, construida con PySide6 para Windows 11."
__url__ = "https://github.com/partybrasil/gaming-helper-overlay"
__license__ = "MIT"

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_BUILD = "stable"

# Build information
BUILD_DATE = "2025-07-13"
BUILD_TYPE = "release"  # release, beta, alpha, dev

# Compatibility information
MIN_PYTHON_VERSION = (3, 10)
RECOMMENDED_PYTHON_VERSION = (3, 11)

# Dependencies versions
DEPENDENCIES = {
    "PySide6": ">=6.5.0",
    "PyYAML": ">=6.0",
    "psutil": ">=5.9.0",
    "requests": ">=2.28.0"
}

# Application metadata
APP_NAME = "Gaming Helper Overlay"
APP_DISPLAY_NAME = "Gaming Helper Overlay"
APP_DESCRIPTION = "Una aplicación de overlay modular para gaming con paneles flotantes y sistema de plugins extensible, construida con PySide6 para Windows 11."
APP_KEYWORDS = ["gaming", "overlay", "helper", "crosshair", "fps", "monitor", "streaming"]

# API version for plugins
PLUGIN_API_VERSION = "1.0"
CONFIG_VERSION = "1.0"

def get_version_string():
    """Return a formatted version string."""
    base_version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
    if VERSION_BUILD and VERSION_BUILD != "stable":
        return f"{base_version}-{VERSION_BUILD}"
    return base_version

def get_full_version_info():
    """Return complete version information."""
    return {
        "version": get_version_string(),
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "build": VERSION_BUILD,
        "build_date": BUILD_DATE,
        "build_type": BUILD_TYPE,
        "plugin_api": PLUGIN_API_VERSION,
        "config_version": CONFIG_VERSION
    }

def is_compatible_python():
    """Check if current Python version is compatible."""
    import sys
    return sys.version_info >= MIN_PYTHON_VERSION

def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    for dep_name, version_spec in DEPENDENCIES.items():
        try:
            __import__(dep_name.lower().replace("-", "_"))
        except ImportError:
            missing_deps.append(f"{dep_name}{version_spec}")
    
    return missing_deps

# For backward compatibility
VERSION = get_version_string()
