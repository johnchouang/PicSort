# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for building PicSort standalone executable.

This file defines how to build a standalone executable for PicSort that includes
all dependencies and can run on systems without Python installed.

Usage:
    pyinstaller picsort.spec

Output:
    - Windows: picsort.exe
    - macOS: picsort.app
    - Linux: picsort
"""

import os
import sys
from pathlib import Path

# Get the directory containing this spec file
SPEC_DIR = Path(__file__).parent
SRC_DIR = SPEC_DIR / "src"

# Define the main script path
MAIN_SCRIPT = str(SRC_DIR / "cli" / "main.py")

# Define additional data files to include
data_files = [
    # Include configuration templates
    (str(SPEC_DIR / "templates" / "config-template.yaml"), "templates"),

    # Include any documentation that should be bundled
    (str(SPEC_DIR / "README.md"), "."),

    # Include quickstart guide if it exists
]

# Add quickstart if it exists
quickstart_path = SPEC_DIR / "docs" / "quickstart.md"
if quickstart_path.exists():
    data_files.append((str(quickstart_path), "docs"))

# Define hidden imports (modules not automatically detected)
hidden_imports = [
    # PIL/Pillow modules that may not be auto-detected
    'PIL._tkinter_finder',
    'PIL._imaging',
    'PIL.Image',
    'PIL.ExifTags',

    # Click modules for CLI
    'click',
    'click.core',
    'click.decorators',
    'click.exceptions',

    # YAML parsing
    'yaml',
    'yaml.loader',
    'yaml.dumper',

    # Date and time utilities
    'dateutil',
    'dateutil.parser',

    # Progress bars and console output
    'tqdm',

    # Standard library modules that might be missed
    'json',
    'pathlib',
    'logging',
    'logging.handlers',
    'tempfile',
    'shutil',
    'hashlib',
    'platform',
    'subprocess',
    'concurrent.futures',

    # PicSort internal modules
    'src.models',
    'src.lib',
    'src.cli',
]

# Exclude unnecessary modules to reduce size
excludes = [
    # Development tools
    'pytest',
    'pytest-cov',
    'black',
    'flake8',
    'mypy',

    # Documentation tools
    'sphinx',
    'sphinx-rtd-theme',

    # Jupyter/IPython
    'jupyter',
    'ipython',
    'notebook',

    # GUI frameworks not needed
    'tkinter',
    'pygame',
    'matplotlib',

    # Web frameworks
    'flask',
    'django',
    'tornado',

    # Scientific computing (unless specifically needed)
    'numpy',
    'scipy',
    'pandas',

    # Other large packages not needed
    'sympy',
    'nltk',
]

# Binary excludes (platform-specific libraries not needed)
binary_excludes = []

# Analysis configuration
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[str(SPEC_DIR), str(SRC_DIR)],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove excluded binaries
for binary_exclude in binary_excludes:
    a.binaries = [x for x in a.binaries if not x[0].startswith(binary_exclude)]

# PYZ configuration (Python archive)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Platform-specific executable configuration
if sys.platform == "win32":
    # Windows executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='picsort',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,  # Enable UPX compression to reduce size
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True,  # Console application
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        # Windows-specific metadata
        version_file=None,  # Can be added later
        icon='assets/picsort.ico' if (SPEC_DIR / 'assets' / 'picsort.ico').exists() else None,
    )

elif sys.platform == "darwin":
    # macOS executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='picsort',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )

    # Create macOS application bundle
    app = BUNDLE(
        exe,
        name='PicSort.app',
        icon='assets/picsort.icns' if (SPEC_DIR / 'assets' / 'picsort.icns').exists() else None,
        bundle_identifier='com.picsort.app',
        info_plist={
            'CFBundleDisplayName': 'PicSort',
            'CFBundleExecutable': 'picsort',
            'CFBundleIdentifier': 'com.picsort.app',
            'CFBundleName': 'PicSort',
            'CFBundlePackageType': 'APPL',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'LSApplicationCategoryType': 'public.app-category.utilities',
            'NSHumanReadableCopyright': 'Copyright © 2023 PicSort',
            'NSHighResolutionCapable': True,
        },
    )

else:
    # Linux executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='picsort',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )

# Build configuration summary
print("=" * 60)
print("PicSort PyInstaller Build Configuration")
print("=" * 60)
print(f"Main script: {MAIN_SCRIPT}")
print(f"Platform: {sys.platform}")
print(f"Data files: {len(data_files)} files")
print(f"Hidden imports: {len(hidden_imports)} modules")
print(f"Excludes: {len(excludes)} modules")
print("=" * 60)