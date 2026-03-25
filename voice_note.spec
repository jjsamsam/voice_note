# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Voice Note application.
Uses --onedir mode for reliable PyTorch DLL handling on Windows.

CRITICAL: Excludes api-ms-win-* and ucrtbase DLLs — these are Windows
system DLLs that MUST NOT be bundled. Bundling them from the build server
causes DLL initialization failures on different Windows versions.
"""

import os
import shutil
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

block_cipher = None

# ── Collect PyTorch & Whisper fully ──
# On Windows, explicitly collect torch DLLs into torch/lib so that the
# package layout matches what torch expects at runtime.
torch_datas, _, torch_hiddenimports = collect_all('torch')
whisper_datas, whisper_binaries, whisper_hiddenimports = collect_all('whisper')
numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
torch_binaries = collect_dynamic_libs('torch', destdir='torch/lib')

# ── Find ffmpeg / ffprobe ──
ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")

added_binaries = []
if ffmpeg_path:
    added_binaries.append((ffmpeg_path, "ffmpeg"))
if ffprobe_path:
    added_binaries.append((ffprobe_path, "ffmpeg"))

# Merge binaries
added_binaries += torch_binaries + whisper_binaries + numpy_binaries

# ── Filter out Windows system DLLs that cause conflicts ──
# These are collected from the build server but should be provided by the
# target Windows installation instead.
EXCLUDE_DLLS = {
    'api-ms-win-',          # Windows API sets — always provided by the OS
    'ucrtbase.dll',         # Do not bundle UCRT from the CI host
}

def should_exclude(name):
    """Check if a binary should be excluded from bundling."""
    lower = name.lower()
    return any(lower.startswith(prefix) for prefix in EXCLUDE_DLLS)

# Filter binaries
added_binaries = [
    (src, dst) for src, dst in added_binaries
    if not should_exclude(os.path.basename(src))
]

# ── Datas (include numpy) ──
added_datas = torch_datas + whisper_datas + numpy_datas

# ── Hidden imports ──
hiddenimports = [
    "sounddevice",
    "soundfile",
    "pydub",
    "numpy",
    "whisper",
    "torch",
    "tiktoken",
    "tiktoken_ext",
    "tiktoken_ext.openai_public",
    "numba",
    "deep_translator",
    "audioop",
]
hiddenimports += torch_hiddenimports + whisper_hiddenimports + numpy_hiddenimports

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=added_binaries,
    datas=added_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["hooks/rthook_torch.py"],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── Also filter from Analysis.binaries (catches DLLs added by hooks) ──
a.binaries = [
    (name, src, typ) for name, src, typ in a.binaries
    if not should_exclude(os.path.basename(name))
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VoiceNote",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # Keep True until all DLL issues resolved
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="VoiceNote",
)
