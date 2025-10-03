# PyInstaller spec file for macOS .app
# Usage: pyinstaller build_macos.spec
from pathlib import Path
block_cipher = None

project_root = Path(__file__).parent
icon_path = project_root / "icon" / "Monitor.png"

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[(str(icon_path), '.')],
    hiddenimports=['psutil', 'matplotlib', 'numpy', 'PIL', 'paramiko', 'cryptography', 'fpdf'],
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
    icon=str(icon_path),   # macOS bundle icon
    bundle_identifier=None,
)
