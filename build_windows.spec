# PyInstaller spec file for Windows executable
# Usage: pyinstaller build_windows.spec

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
    name='SystemMonitor(Windows)',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(base, 'Monitor.png'),
)
