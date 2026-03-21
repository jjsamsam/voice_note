"""
Monochrome Dark Theme Stylesheet for PyQt6
"""

DARK_STYLE = """
/* ============================================
   MONOCHROME DARK THEME
   ============================================ */

/* --- Global --- */
QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

/* --- Main Window --- */
QMainWindow {
    background-color: #1a1a1a;
}

QMainWindow::separator {
    background-color: #333333;
    width: 1px;
    height: 1px;
}

/* --- Menu Bar --- */
QMenuBar {
    background-color: #222222;
    color: #e0e0e0;
    border-bottom: 1px solid #333333;
    padding: 2px;
}

QMenuBar::item:selected {
    background-color: #3a3a3a;
    border-radius: 4px;
}

QMenu {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item:selected {
    background-color: #4a4a4a;
    border-radius: 4px;
}

/* --- Buttons --- */
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #3a3a3a;
    border-color: #555555;
}

QPushButton:pressed {
    background-color: #4a4a4a;
}

QPushButton:disabled {
    background-color: #1e1e1e;
    color: #555555;
    border-color: #2a2a2a;
}

QPushButton#recordButton {
    background-color: #3a3a3a;
    border: 2px solid #666666;
    border-radius: 25px;
    min-width: 50px;
    min-height: 50px;
    max-width: 50px;
    max-height: 50px;
    font-size: 18px;
}

QPushButton#recordButton:hover {
    background-color: #4a4a4a;
    border-color: #888888;
}

QPushButton#recordButton[recording="true"] {
    background-color: #555555;
    border-color: #aaaaaa;
}

QPushButton#stopButton {
    background-color: #3a3a3a;
    border: 2px solid #666666;
    border-radius: 20px;
    min-width: 40px;
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
}

/* --- Labels --- */
QLabel {
    color: #e0e0e0;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    padding: 10px 0;
}

QLabel#sectionLabel {
    font-size: 14px;
    font-weight: 600;
    color: #b0b0b0;
    padding: 5px 0;
    border-bottom: 1px solid #333333;
}

QLabel#statusLabel {
    color: #888888;
    font-size: 12px;
    padding: 4px 8px;
}

QLabel#timerLabel {
    font-size: 28px;
    font-weight: 300;
    color: #ffffff;
    font-family: "SF Mono", "Consolas", "Courier New", monospace;
}

/* --- Text Areas --- */
QTextEdit, QPlainTextEdit {
    background-color: #222222;
    color: #e0e0e0;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    line-height: 1.5;
    selection-background-color: #4a4a4a;
    selection-color: #ffffff;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #555555;
}

/* --- Combo Box --- */
QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #555555;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #888888;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    selection-background-color: #4a4a4a;
    outline: none;
}

/* --- Progress Bar --- */
QProgressBar {
    background-color: #222222;
    border: 1px solid #333333;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #888888;
    border-radius: 3px;
}

/* --- Scroll Bar --- */
QScrollBar:vertical {
    background-color: #1a1a1a;
    width: 10px;
    margin: 0;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #3a3a3a;
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a4a4a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #1a1a1a;
    height: 10px;
    margin: 0;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #3a3a3a;
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}

/* --- Status Bar --- */
QStatusBar {
    background-color: #1e1e1e;
    color: #888888;
    border-top: 1px solid #2a2a2a;
    font-size: 12px;
}

/* --- Tab Widget --- */
QTabWidget::pane {
    background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #222222;
    color: #888888;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 20px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
    color: #ffffff;
    border-color: #444444;
}

QTabBar::tab:hover:!selected {
    background-color: #2a2a2a;
    color: #b0b0b0;
}

/* --- Group Box --- */
QGroupBox {
    background-color: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    margin-top: 12px;
    padding: 20px 15px 15px 15px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: #b0b0b0;
}

/* --- Splitter --- */
QSplitter::handle {
    background-color: #2a2a2a;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* --- File Info Panel --- */
QFrame#fileInfoPanel {
    background-color: #222222;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 10px;
}

/* --- Tool Tip --- */
QToolTip {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 4px 8px;
}
"""
