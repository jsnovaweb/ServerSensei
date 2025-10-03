# PyInstaller spec file for macOS app bundle
# Usage: pyinstaller build_macos.spec

import os
base = os.path.abspath(os.path.dirname(__file__))
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[(os.path.join(base, 'Monitor.png'), '.')],
    hiddenimports=[
        'psutil', 'matplotlib', 'numpy', 'PIL',
        'paramiko', 'cryptography', 'fpdf', 'GPUtil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
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
    strip=True,
    upx=False,
    console=False,
    argv_emulation=True,
    icon=os.path.join(base, 'Monitor.png'),
)

app = BUNDLE(
    exe,
    name='SystemMonitor(macOS).app',
    icon=os.path.join(base, 'Monitor.png'),
    bundle_identifier='com.system.monitor',
)
