# PyInstaller spec file for macOS .app bundle
# Usage: pyinstaller build_macos.spec
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
    name='SystemMonitor(macOS)',
    console=False,
    argv_emulation=True,
)

app = BUNDLE(
    exe,
    name='SystemMonitor(macOS).app',
    icon='icon/Monitor.png',
    bundle_identifier=None,
)
