#!/usr/bin/env python3
"""
Gaming Helper Overlay - Main Entry Point
A modular gaming helper overlay application with floating panels and plugins.

Author: Party Brasil
Version: 1.0.0
Framework: PySide6
Python: 3.10+
Target OS: Windows 11
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QIcon

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.app_core import GamingHelperApp

def setup_application():
    """Setup the main QApplication with necessary configurations."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Gaming Helper Overlay")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Party Brasil")
    app.setOrganizationDomain("partybrasil.dev")
    
    # Set application icon if available
    icon_path = project_root / "assets" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app

def main():
    """Main function to start the Gaming Helper Overlay application."""
    try:
        # Setup QApplication
        app = setup_application()
        
        # Create and start the main application
        gaming_helper = GamingHelperApp()
        gaming_helper.initialize()
        
        # Start the Qt event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Critical error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
