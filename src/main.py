"""
Voice Note Application — Entry Point
"""

import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.ui.style import DARK_STYLE
from src.audio_utils import setup_ffmpeg


def main():
    # High-DPI support
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    # Configure ffmpeg (bundled or system)
    setup_ffmpeg()

    app = QApplication(sys.argv)
    app.setApplicationName("Voice Note")
    app.setApplicationVersion("1.0.0")

    # Apply monochrome dark theme
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
