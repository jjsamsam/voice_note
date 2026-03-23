# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Voice Note application.
Uses --onedir mode for reliable PyTorch DLL handling on Windows.

CRITICAL: Excludes api-ms-win-* and ucrtbase DLLs — these are Windows
system DLLs that MUST NOT be bundled. Bundling them from the build server
causes DLL initialization failures on different Windows versions.
"""

import os
import sys
import shutil
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

block_cipher = None

# ── Collect PyTorch & Whisper fully ──
torch_datas, torch_binaries, torch_hiddenimports = collect_all('torch')
whisper_datas, whisper_binaries, whisper_hiddenimports = collect_all('whisper')

# ── Find ffmpeg / ffprobe ──
ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")

added_binaries = []
if ffmpeg_path:
    added_binaries.append((ffmpeg_path, "ffmpeg"))
if ffprobe_path:
    added_binaries.append((ffprobe_path, "ffmpeg"))

# Merge binaries
added_binaries += torch_binaries + whisper_binaries

# ── Filter out Windows system DLLs that cause conflicts ──
# These are collected from the build server but conflict with the user's Windows.
EXCLUDE_DLLS = {
    'api-ms-win-',          # Windows API sets
    'ucrtbase',             # Universal C Runtime (system)
    'vcruntime',            # VC++ Runtime (user should have installed)
    'msvcp',                # VC++ Runtime
    'concrt',               # Concurrency Runtime
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
hiddenimports += torch_hiddenimports + whisper_hiddenimports

# ── Datas ──
added_datas = torch_datas + whisper_datas

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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # Back to False — DLL issue fixed
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
    upx=True,
    upx_exclude=[],
    name="VoiceNote",
)
