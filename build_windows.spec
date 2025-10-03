# PyInstaller spec file for Windows executable
# Usage: pyinstaller build_windows.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('icon/Monitor.png', '.')],
    hiddenimports=[
        'psutil',
        'matplotlib',
        'numpy',
        'PIL',
        'paramiko',
        'cryptography',
        'fpdf',
    ],
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
    name='SystemMonitor(Windows)',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon='icon/Monitor.png',
)
