# PyInstaller spec file for Linux executable
# Usage: pyinstaller build_linux.spec
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
    name='SystemMonitor(Linux)',
    debug=False,
    strip=True,
    upx=True,
    console=False,
)
