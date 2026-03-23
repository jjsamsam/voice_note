"""
Voice Note Application — Entry Point

IMPORTANT: On Windows PyInstaller bundles, the runtime hook (rthook_torch.py)
copies DLLs into torch/lib before this script runs. torch must still be
imported before PyQt6 to avoid DLL conflicts.
"""

import sys
import os
import traceback

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _save_error_log(module_name, error):
    """Save detailed error log to file and show popup directing user to it."""
    lines = [
        f"=== Voice Note Error Log ===",
        f"Module: {module_name}",
        f"Error: {error}",
        f"",
        f"--- Traceback ---",
        traceback.format_exc(),
        f"",
        f"--- Environment ---",
        f"Python: {sys.version}",
        f"Platform: {sys.platform}",
        f"Frozen: {getattr(sys, 'frozen', False)}",
    ]

    if getattr(sys, "frozen", False):
        _base = sys._MEIPASS
        lines.append(f"MEIPASS: {_base}")
        lines.append(f"")

        for subdir in ["", "torch/lib", "numpy/.libs", "numpy.libs"]:
            full = os.path.join(_base, subdir) if subdir else _base
            if os.path.isdir(full):
                dlls = sorted(f for f in os.listdir(full) if f.lower().endswith(".dll"))
                lines.append(f"--- {subdir or '_internal'} ({len(dlls)} DLLs) ---")
                for d in dlls:
                    lines.append(f"  {d}")
                lines.append("")

    log_text = "\n".join(lines)

    if getattr(sys, "frozen", False):
        log_path = os.path.join(os.path.dirname(sys.executable), "error_log.txt")
    else:
        log_path = os.path.join(os.path.dirname(__file__), "error_log.txt")

    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(log_text)
    except Exception:
        log_path = os.path.join(os.path.expanduser("~"), "VoiceNote_error_log.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(log_text)

    print(log_text, file=sys.stderr)

    if sys.platform == "win32":
        try:
            import ctypes
            short_msg = (
                f"{module_name} 로딩 실패!\n\n"
                f"에러: {error}\n\n"
                f"상세 로그 파일:\n{log_path}\n\n"
                f"이 파일을 개발자에게 공유해 주세요."
            )
            ctypes.windll.user32.MessageBoxW(0, short_msg, "Voice Note - Error", 0x10)
        except Exception:
            pass

    sys.exit(1)


# ── Import torch BEFORE PyQt6 ──
try:
    import torch  # noqa: F401
except Exception as e:
    _save_error_log("PyTorch", e)

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
