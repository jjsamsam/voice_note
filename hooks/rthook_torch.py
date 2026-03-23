"""
PyInstaller runtime hook for Windows DLL loading.
Copies necessary DLLs into torch/lib so c10.dll can find all dependencies
in its own directory. This is the most reliable approach.
"""
import os
import sys
import shutil

if sys.platform == "win32" and getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
    torch_lib = os.path.join(base_path, "torch", "lib")

    if os.path.isdir(torch_lib):
        # Copy all DLLs from _internal root INTO torch/lib
        # so c10.dll can find them in its own directory
        for fname in os.listdir(base_path):
            if fname.lower().endswith(".dll"):
                src = os.path.join(base_path, fname)
                dst = os.path.join(torch_lib, fname)
                if not os.path.exists(dst):
                    try:
                        shutil.copy2(src, dst)
                    except Exception:
                        pass

        # Also add to PATH and os.add_dll_directory as fallback
        try:
            os.add_dll_directory(base_path)
            os.add_dll_directory(torch_lib)
        except (OSError, AttributeError):
            pass

        os.environ["PATH"] = (
            torch_lib + os.pathsep + base_path + os.pathsep
            + os.environ.get("PATH", "")
        )
