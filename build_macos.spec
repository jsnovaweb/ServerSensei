# PyInstaller spec file for macOS executable
# Usage: pyinstaller build_macos.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('Monitor.png', '.'),   # app icon
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
    name='SystemMonitor(macOS)',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    argv_emulation=True,   # macOS-specific for GUI apps
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
