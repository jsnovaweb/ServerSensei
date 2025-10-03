# build_macos.spec

# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# Define the project root (directory containing this .spec file)
project_root = Path(__file__).parent

block_cipher = None

a = Analysis(
    ['main.py'],  # entry point
    pathex=[str(project_root)],
    binaries=[],
    datas=[(str(project_root / 'Monitor.png'), '.')],  # relative path fix
    hiddenimports=collect_submodules(''),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SystemMonitor(macOS)',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app on macOS
    disable_windowed_traceback=False,
    argv_emulation=True,  # macOS fix for argv
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # you can replace with .icns if you want
)

app = BUNDLE(
    exe,
    name='SystemMonitor(macOS).app',
    icon=None,
    bundle_identifier=None,
)
