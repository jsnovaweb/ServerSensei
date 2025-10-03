# PyInstaller spec file for macOS .app bundle
# Usage: pyinstaller build_macos.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('icon/Monitor.png', '.'),   # <-- FIXED PATH
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
    name='SystemMonitor(macOS)',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/Monitor.png',   # <-- FIXED PATH
)

app = BUNDLE(
    exe,
    name='SystemMonitor(macOS).app',
    icon='icon/Monitor.png',   # <-- FIXED PATH
    bundle_identifier=None,
)
