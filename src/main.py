"""
Voice Note Application — Entry Point

IMPORTANT: On Windows PyInstaller bundles, DLL directories must be set up
before importing torch, and torch must be imported before PyQt6.
"""

import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Setup DLL search paths for PyInstaller bundle (Windows) ──
if sys.platform == "win32" and getattr(sys, "frozen", False):
    _base = sys._MEIPASS
    _torch_lib = os.path.join(_base, "torch", "lib")

    # Add DLL directories using BOTH methods for maximum compatibility
    for _dir in [_base, _torch_lib]:
        if os.path.isdir(_dir):
            try:
                os.add_dll_directory(_dir)
            except (OSError, AttributeError):
                pass

    # Also prepend PATH (fallback for some DLL loading mechanisms)
    os.environ["PATH"] = (
        _torch_lib + os.pathsep + _base + os.pathsep + os.environ.get("PATH", "")
    )

    # Use Win32 API to ensure DLL directories are in search order
    try:
        import ctypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        # SetDefaultDllDirectories: enable LOAD_LIBRARY_SEARCH_USER_DIRS
        LOAD_LIBRARY_SEARCH_DEFAULT_DIRS = 0x00001000
        LOAD_LIBRARY_SEARCH_USER_DIRS = 0x00000400
        kernel32.SetDefaultDllDirectories(
            LOAD_LIBRARY_SEARCH_DEFAULT_DIRS | LOAD_LIBRARY_SEARCH_USER_DIRS
        )

        # AddDllDirectory for each path
        _AddDllDir = kernel32.AddDllDirectory
        _AddDllDir.restype = ctypes.c_void_p
        _AddDllDir.argtypes = [ctypes.c_wchar_p]
        for _dir in [_base, _torch_lib]:
            if os.path.isdir(_dir):
                _AddDllDir(_dir)
    except Exception:
        pass

# ── Import torch BEFORE PyQt6 ──
try:
    import torch  # noqa: F401
except OSError as e:
    # If still failing, show diagnostic info
    msg = f"PyTorch DLL 로딩 실패: {e}\n\n"
    if getattr(sys, "frozen", False):
        _base = sys._MEIPASS
        _tlib = os.path.join(_base, "torch", "lib")
        msg += f"MEIPASS: {_base}\n"
        msg += f"torch/lib exists: {os.path.isdir(_tlib)}\n"
        if os.path.isdir(_tlib):
            dlls = [f for f in os.listdir(_tlib) if f.endswith(".dll")]
            msg += f"torch/lib DLLs ({len(dlls)}): {', '.join(dlls)}\n"
        base_dlls = [f for f in os.listdir(_base) if f.endswith(".dll")]
        msg += f"_internal DLLs ({len(base_dlls)}): {', '.join(base_dlls[:10])}...\n"
    print(msg, file=sys.stderr)
    # Try to show a message box even without PyQt
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "Voice Note - DLL Error", 0x10)
    except Exception:
        pass
    sys.exit(1)

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
