"""
PyInstaller runtime hook for Windows DLL loading.
Must run BEFORE any torch imports to set up DLL search paths.
"""
import os
import sys

if sys.platform == "win32" and getattr(sys, "frozen", False):
    base_path = sys._MEIPASS

    # Add base extraction dir to DLL search path
    try:
        os.add_dll_directory(base_path)
    except (OSError, AttributeError):
        pass

    # Add torch/lib directory specifically (c10.dll and dependencies live here)
    torch_lib = os.path.join(base_path, "torch", "lib")
    if os.path.isdir(torch_lib):
        try:
            os.add_dll_directory(torch_lib)
        except (OSError, AttributeError):
            pass

    # Also prepend to PATH as a fallback
    os.environ["PATH"] = (
        torch_lib + os.pathsep + base_path + os.pathsep + os.environ.get("PATH", "")
    )
