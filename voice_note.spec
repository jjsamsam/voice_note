# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Voice Note application.
Bundles ffmpeg/ffprobe and handles PyTorch DLL issues on Windows.
"""

import os
import sys
import shutil
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

block_cipher = None

# ── Collect PyTorch & Whisper fully (critical for Windows DLLs) ──
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
    runtime_hooks=["hooks/rthook_torch.py"],  # Fix Windows DLL search paths
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="VoiceNote",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
