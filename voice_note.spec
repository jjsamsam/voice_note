# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Voice Note application.
Bundles ffmpeg and ffprobe for full audio format support.
"""

import os
import shutil

block_cipher = None

# Find ffmpeg and ffprobe paths
ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")

# Prepare data files to bundle
added_files = []
if ffmpeg_path:
    added_files.append((ffmpeg_path, "ffmpeg"))
if ffprobe_path:
    added_files.append((ffprobe_path, "ffmpeg"))

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=added_files,
    datas=[],
    hiddenimports=[
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    icon=None,  # Add .icns (Mac) or .ico (Win) path here for custom icon
)
