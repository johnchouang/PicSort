# Building Standalone Executables for PicSort

This guide provides comprehensive instructions for creating standalone executables of PicSort that can run on systems without Python installed.

## Overview

PicSort uses PyInstaller to create standalone executables that bundle the Python interpreter, all dependencies, and the application code into a single distributable file. The build process is automated through the `build_executable.py` script.

## Quick Start

For most users, building an executable is as simple as:

```bash
python build_executable.py
```

This will:
- Check all build requirements
- Build the executable using PyInstaller
- Verify the executable works
- Provide a build summary with next steps

## Prerequisites

### Python Requirements
- **Python 3.8 or higher** (3.11+ recommended)
- **pip** package manager

### Required Dependencies

Install all dependencies first:

```bash
pip install -r requirements.txt
pip install pyinstaller
```

The following packages are required for building:
- **PyInstaller**: For creating standalone executables
- **Click**: CLI framework
- **Pillow**: Image processing and EXIF data
- **PyYAML**: Configuration file handling
- **tqdm**: Progress bars

### Optional Dependencies

For smaller executable sizes:
- **UPX** (Universal Packer for eXecutables): Compresses the final executable
  - Windows: Download from https://upx.github.io/
  - macOS: `brew install upx`
  - Linux: `sudo apt install upx` (Ubuntu/Debian) or `sudo yum install upx` (CentOS/RHEL)

## Build Options

### Basic Build
```bash
python build_executable.py
```

### Clean Build
Removes previous build artifacts before building:
```bash
python build_executable.py --clean
```

### Debug Build
Creates an executable with debug information and console output:
```bash
python build_executable.py --debug
```

### No Compression Build
Builds without UPX compression (faster build, larger file):
```bash
python build_executable.py --no-upx
```

### Combined Options
```bash
python build_executable.py --clean --debug --no-upx
```

## Build Process Details

### 1. Requirements Check

The build script automatically verifies:
- Python version (3.8+)
- PyInstaller installation
- All required dependencies (Click, Pillow, PyYAML, tqdm)
- UPX availability (optional)

If any requirements are missing, the script will provide installation instructions.

### 2. Build Configuration

The build uses `picsort.spec`, a PyInstaller specification file that defines:

- **Entry point**: `src/cli/main.py`
- **Hidden imports**: Modules that PyInstaller might not auto-detect
- **Data files**: Configuration templates, documentation
- **Excludes**: Unnecessary modules to reduce size
- **Platform-specific settings**: Windows, macOS, and Linux configurations

### 3. Compilation

PyInstaller creates:
- **Windows**: `dist/picsort.exe` (single executable)
- **macOS**: `dist/PicSort.app` (application bundle)
- **Linux**: `dist/picsort` (single executable)

### 4. Verification

The script automatically tests the built executable by running:
```bash
./picsort --version
```

## Platform-Specific Notes

### Windows

**Output**: `dist/picsort.exe`

**Features**:
- Single executable file
- Console application
- Optional icon embedding
- UPX compression supported

**Distribution**:
- Can be run directly on any Windows system
- No Python installation required
- Antivirus software may flag PyInstaller executables (false positive)

**Troubleshooting**:
- If Windows Defender blocks the executable, add it to exclusions
- For corporate environments, consider code signing

### macOS

**Output**: `dist/PicSort.app`

**Features**:
- Application bundle format
- Includes Info.plist metadata
- Optional icon embedding
- Universal binary support

**Distribution**:
- Double-click to run, or use from command line
- May show "unidentified developer" warning
- Users can bypass by right-clicking → Open

**Code Signing** (Optional):
```bash
# Sign the application (requires Apple Developer account)
codesign --deep --sign "Developer ID Application: Your Name" dist/PicSort.app
```

**Notarization** (For distribution):
```bash
# Notarize with Apple (requires Apple Developer account)
xcrun altool --notarize-app --primary-bundle-id "com.picsort.app" \
             --username "your@email.com" --password "@keychain:AC_PASSWORD" \
             --file PicSort.app.zip
```

### Linux

**Output**: `dist/picsort`

**Features**:
- Single executable file
- Statically linked libraries
- Cross-distribution compatibility

**Distribution**:
- Mark as executable: `chmod +x picsort`
- Can be run on most Linux distributions
- May require `glibc` compatibility

**System Integration**:
Create a desktop entry (`~/.local/share/applications/picsort.desktop`):
```ini
[Desktop Entry]
Name=PicSort
Comment=Organize media files by date
Exec=/path/to/picsort
Icon=/path/to/icon.png
Terminal=true
Type=Application
Categories=Utility;
```

## File Size Optimization

### Default Size Expectations
- **Windows**: ~25-35 MB
- **macOS**: ~30-40 MB
- **Linux**: ~25-35 MB

### Optimization Strategies

1. **Enable UPX Compression** (default):
   - Reduces size by 30-50%
   - Slightly slower startup time
   - Not available on all platforms

2. **Review Excluded Modules**:
   The `picsort.spec` file excludes unnecessary modules. You can add more to the `excludes` list:
   ```python
   excludes = [
       'pytest', 'black', 'flake8',  # Development tools
       'jupyter', 'notebook',        # Jupyter notebooks
       'tkinter', 'matplotlib',      # GUI frameworks
       'numpy', 'scipy', 'pandas',   # Scientific computing
   ]
   ```

3. **Minimize Data Files**:
   Only essential files are included. Remove unused templates or documentation from the `datas` list.

## Advanced Configuration

### Custom PyInstaller Options

To modify build behavior, edit `picsort.spec`:

```python
# Example: Add custom icon
exe = EXE(
    # ... other parameters ...
    icon='path/to/custom/icon.ico',  # Windows
)

# Example: Add version information (Windows)
exe = EXE(
    # ... other parameters ...
    version_file='version_info.txt',
)
```

### Hidden Imports

If the executable fails with import errors, add missing modules to `hidden_imports` in `picsort.spec`:

```python
hidden_imports = [
    # Existing imports...
    'your.missing.module',
]
```

### Data Files

To include additional files in the executable:

```python
data_files = [
    # Existing files...
    ('path/to/source/file', 'destination/folder'),
]
```

## Troubleshooting

### Common Build Issues

**PyInstaller Not Found**:
```bash
pip install pyinstaller
```

**Missing Dependencies**:
```bash
pip install -r requirements.txt
```

**Permission Errors**:
- Ensure write permissions in project directory
- Close any running instances of the executable
- Try running as administrator (Windows) or with sudo (Linux/macOS)

**Large Executable Size**:
- Enable UPX compression
- Review and expand the `excludes` list
- Remove unnecessary data files

### Runtime Issues

**Import Errors**:
- Add missing modules to `hidden_imports`
- Check that all dependencies are installed in build environment

**File Not Found Errors**:
- Verify data files are correctly specified in `data_files`
- Use resource path helpers for bundled files

**Slow Startup**:
- Disable UPX compression with `--no-upx`
- Consider using `--onedir` mode instead of `--onefile`

### Platform-Specific Issues

**Windows Antivirus Detection**:
- Add executable to antivirus exclusions
- Consider code signing for distribution

**macOS Gatekeeper**:
- Users can bypass with right-click → Open
- Consider code signing and notarization

**Linux Library Dependencies**:
- Build on oldest supported distribution
- Check `ldd picsort` for library dependencies

## Distribution

### Single File Distribution

The built executables are self-contained and can be distributed as single files:

1. **Windows**: Share `picsort.exe`
2. **macOS**: Share `PicSort.app` (zip it for easier transfer)
3. **Linux**: Share `picsort` (ensure executable permissions)

### Installer Creation

For professional distribution, consider creating installers:

**Windows (NSIS)**:
```nsis
; Example NSIS installer script
OutFile "PicSortSetup.exe"
InstallDir "$PROGRAMFILES\PicSort"
Section
    SetOutPath $INSTDIR
    File "picsort.exe"
SectionEnd
```

**macOS (DMG)**:
```bash
# Create a DMG file
hdiutil create -srcfolder dist/PicSort.app -volname "PicSort" PicSort.dmg
```

**Linux (Package)**:
```bash
# Create a .deb package
mkdir -p picsort_1.0.0/usr/local/bin
cp dist/picsort picsort_1.0.0/usr/local/bin/
dpkg-deb --build picsort_1.0.0
```

### Automated Building

For CI/CD pipelines, you can automate the build process:

**GitHub Actions Example**:
```yaml
name: Build Executables
on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build executable
      run: python build_executable.py --clean

    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: picsort-${{ matrix.os }}
        path: dist/
```

## Security Considerations

### Code Signing

For production distribution:

1. **Windows**: Use SignTool with a code signing certificate
2. **macOS**: Use codesign with Apple Developer certificate
3. **Linux**: Use gpg signatures for package verification

### Antivirus False Positives

PyInstaller executables may trigger false positives:

- **Solution**: Submit to antivirus vendors for whitelisting
- **Prevention**: Use code signing certificates
- **Alternative**: Distribute as Python package with installation instructions

## Testing Built Executables

### Automated Testing

Create a test script to verify executable functionality:

```bash
#!/bin/bash
# test_executable.sh

EXECUTABLE="./dist/picsort"

# Test basic functionality
echo "Testing version..."
$EXECUTABLE --version || exit 1

echo "Testing help..."
$EXECUTABLE --help || exit 1

echo "Testing config..."
$EXECUTABLE config --help || exit 1

echo "All tests passed!"
```

### Manual Testing Checklist

- [ ] Executable runs without errors
- [ ] All CLI commands work
- [ ] Configuration file creation works
- [ ] File organization functionality works
- [ ] Undo functionality works
- [ ] Help and documentation display correctly

## Support and Maintenance

### Updating the Build

When updating PicSort:

1. Update version numbers in relevant files
2. Run tests to ensure functionality
3. Rebuild executable with `python build_executable.py --clean`
4. Test the new executable thoroughly
5. Update documentation if needed

### Monitoring Executable Performance

Track metrics for continuous improvement:
- Executable size over time
- Build time duration
- Startup performance
- User feedback on functionality

## Conclusion

This build system provides a robust foundation for creating and distributing PicSort as standalone executables. The automated build script handles most complexities, while the PyInstaller specification file allows for detailed customization when needed.

For questions or issues with the build process, please refer to:
- PyInstaller documentation: https://pyinstaller.readthedocs.io/
- PicSort project issues: [GitHub Issues]
- Build script source code: `build_executable.py` and `picsort.spec`