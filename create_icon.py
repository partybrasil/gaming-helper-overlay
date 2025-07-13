#!/usr/bin/env python3
"""
Create app icon
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtCore import Qt

def create_icon():
    app = QApplication([])
    
    # Create a proper PNG icon
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw circle background
    painter.setBrush(QBrush(QColor(100, 150, 255, 220)))
    painter.setPen(QPen(QColor(255, 255, 255, 150), 3))
    painter.drawEllipse(4, 4, size - 8, size - 8)

    # Draw inner design
    painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
    painter.setPen(QPen(QColor(100, 150, 255), 2))
    painter.drawEllipse(16, 16, 32, 32)

    # Draw text
    painter.setPen(QPen(QColor(255, 255, 255), 1))
    painter.setFont(QFont('Arial', 14, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, 'GH')

    painter.end()

    # Save icon
    icon_path = project_root / "assets" / "icons" / "app_icon.png"
    icon_path.parent.mkdir(parents=True, exist_ok=True)
    pixmap.save(str(icon_path), 'PNG')
    print(f'Icon created at: {icon_path}')

if __name__ == "__main__":
    create_icon()
