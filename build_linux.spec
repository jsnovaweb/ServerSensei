# PyInstaller spec file for Linux (onedir)
# Usage: pyinstaller build_linux.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('icon/Monitor.png', '.'),
    ],
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
    name='SystemMonitor(Linux)',
    debug=False,
    strip=True,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon='icon/Monitor.png',
    onefile=False
)
