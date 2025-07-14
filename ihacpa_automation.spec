# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for IHACPA Python Package Review Automation
Creates a single executable file with all dependencies bundled
"""

import sys
import os
from pathlib import Path

# Get the directory containing this spec file
spec_dir = Path(SPECPATH)
src_dir = spec_dir / 'src'

# Collect all source files
source_files = [
    'standalone_app.py',
    'src/excel_handler.py',
    'src/pypi_client.py', 
    'src/vulnerability_scanner.py',
    'src/ai_cve_analyzer.py',
    'src/config.py',
    'src/config_manager.py',
    'src/logger.py',
    'src/__init__.py'
]

# Data files to include
datas = [
    # Include configuration templates
    ('config.yaml', '.'),
    # Include any icon file if exists
    # ('icon.ico', '.'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'openpyxl',
    'openpyxl.styles',
    'openpyxl.utils',
    'openpyxl.worksheet',
    'requests',
    'aiohttp',
    'asyncio',
    'yaml',
    'openai',
    'dotenv',
    'certifi',
    'charset_normalizer',
    'urllib3',
    'idna',
    'dateutil',
    'tkinter',
    'queue',
    'threading'
]

# Analysis
a = Analysis(
    ['standalone_app.py'],
    pathex=[str(spec_dir), str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove unnecessary binaries to reduce size
excluded_binaries = [
    'mfc140u.dll',
    'api-ms-win-*.dll',
    'd3dcompiler_47.dll',
    'libGLESv2.dll',
    'libEGL.dll',
    'opengl32sw.dll',
    'Qt5*.dll',
    'Qt6*.dll'
]

a.binaries = [x for x in a.binaries if not any(excl in x[0] for excl in excluded_binaries)]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IHACPA_Automation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.py' if os.path.exists('version_info.py') else None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    uac_admin=False,
    uac_uiaccess=False,
)