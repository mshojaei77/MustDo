# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import logging
from pathlib import Path

# Configure logging to show only errors
logging.getLogger().setLevel(logging.ERROR)

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),

    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    cache_dir=os.path.join(os.path.expanduser('~'), '.pyinstaller', 'cache')
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MustDo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('assets', 'app.png'),
    log_level='ERROR',
    optimize=2
)

# Add COLLECT to create the directory with all dependencies
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MustDo'
)
