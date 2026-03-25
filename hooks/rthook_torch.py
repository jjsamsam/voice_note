"""
PyInstaller runtime hook for Windows DLL loading.
Registers bundled DLL directories and preloads core torch runtime DLLs
before importing torch. This avoids Windows DLL resolution issues in
frozen builds.
"""
import ctypes
import os
import sys

if sys.platform == "win32" and getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
    torch_lib = os.path.join(base_path, "torch", "lib")

    if os.path.isdir(torch_lib):
        try:
            os.add_dll_directory(base_path)
            os.add_dll_directory(torch_lib)
        except (OSError, AttributeError):
            pass

        os.environ["PATH"] = (
            torch_lib + os.pathsep + base_path + os.pathsep
            + os.environ.get("PATH", "")
        )

        preload_order = [
            "vcruntime140.dll",
            "vcruntime140_1.dll",
            "msvcp140.dll",
            "VCOMP140.DLL",
            "libiomp5md.dll",
            "torch_global_deps.dll",
            "c10.dll",
        ]
        for dll_name in preload_order:
            for directory in (torch_lib, base_path):
                dll_path = os.path.join(directory, dll_name)
                if os.path.exists(dll_path):
                    try:
                        ctypes.WinDLL(dll_path)
                        break
                    except OSError:
                        pass
