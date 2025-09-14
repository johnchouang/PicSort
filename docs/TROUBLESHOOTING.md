# PicSort Troubleshooting Guide

This guide helps you diagnose and resolve common issues with PicSort.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Configuration Problems](#configuration-problems)
4. [File Operation Issues](#file-operation-issues)
5. [Performance Problems](#performance-problems)
6. [Platform-Specific Issues](#platform-specific-issues)
7. [Error Messages Reference](#error-messages-reference)
8. [Getting Help](#getting-help)

## Quick Diagnostics

Before diving into specific issues, run these commands to gather basic information:

```bash
# Check PicSort version and system info
picsort version --json

# Validate your configuration
picsort config validate

# Test with verbose output
picsort scan /path/to/test/folder --verbose
```

## Installation Issues

### Python Installation Issues

#### "picsort command not found"

**Symptoms:**
- Command line shows "picsort: command not found"
- Fresh installation

**Causes:**
- PicSort not installed
- Not in PATH
- Virtual environment not activated

**Solutions:**

1. **Verify installation:**
   ```bash
   pip list | grep picsort
   ```

2. **Install if missing:**
   ```bash
   pip install -e .
   ```

3. **Check PATH:**
   ```bash
   # Linux/macOS
   echo $PATH
   which picsort

   # Windows
   echo %PATH%
   where picsort
   ```

4. **Try running directly:**
   ```bash
   python -m picsort.cli.main --version
   ```

#### "ImportError: No module named 'picsort'"

**Symptoms:**
- Import errors when running
- Python can't find PicSort modules

**Solutions:**

1. **Install in development mode:**
   ```bash
   pip install -e .
   ```

2. **Check Python environment:**
   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   ```

3. **Verify working directory:**
   ```bash
   pwd  # Should be in PicSort root directory
   ls src/  # Should show PicSort source files
   ```

### Standalone Executable Issues

#### Executable won't start (Windows)

**Symptoms:**
- Double-click does nothing
- "Windows protected your PC" warning
- Antivirus blocks execution

**Solutions:**

1. **Bypass Windows Defender SmartScreen:**
   - Click "More info"
   - Click "Run anyway"

2. **Add antivirus exclusion:**
   - Add `picsort.exe` to antivirus exclusions
   - Add the entire PicSort directory

3. **Run from command prompt:**
   ```cmd
   cd C:\path\to\picsort
   picsort.exe --version
   ```

4. **Check dependencies:**
   - Install Visual C++ Redistributable 2019+
   - Update Windows

#### "Permission denied" on Linux/macOS

**Symptoms:**
- `bash: ./picsort: Permission denied`
- Executable downloads but won't run

**Solutions:**

1. **Make executable:**
   ```bash
   chmod +x picsort
   ```

2. **Check file type:**
   ```bash
   file picsort  # Should show: ELF executable (Linux) or Mach-O executable (macOS)
   ```

3. **Run with explicit path:**
   ```bash
   ./picsort --version
   ```

#### macOS "Cannot verify developer" warning

**Symptoms:**
- "Cannot verify that this app is free from malware"
- Gatekeeper blocks execution

**Solutions:**

1. **Bypass Gatekeeper (temporary):**
   - Right-click the app
   - Select "Open"
   - Click "Open" in the dialog

2. **System Preferences method:**
   - System Preferences > Security & Privacy
   - Click "Open Anyway" (appears after first attempt)

3. **Command line bypass:**
   ```bash
   xattr -d com.apple.quarantine PicSort.app
   ```

## Configuration Problems

### Configuration File Issues

#### "Configuration file not found"

**Symptoms:**
- Error on first run
- Commands fail to start

**Solutions:**

1. **Initialize configuration:**
   ```bash
   picsort config init
   ```

2. **Check default location:**
   ```bash
   # Linux/macOS
   ls ~/.picsort/config.yaml

   # Windows
   dir "%USERPROFILE%\.picsort\config.yaml"
   ```

3. **Create manually if needed:**
   ```bash
   mkdir -p ~/.picsort
   picsort config init --config ~/.picsort/config.yaml
   ```

#### "Invalid YAML syntax"

**Symptoms:**
- Configuration validation fails
- "YAML syntax error" messages

**Common YAML Issues:**

1. **Indentation problems:**
   ```yaml
   # WRONG
   file_types:
     - .jpg
    - .png  # Bad indentation

   # RIGHT
   file_types:
     - .jpg
     - .png
   ```

2. **Missing quotes for special characters:**
   ```yaml
   # WRONG
   date_format: MM.YYYY  # Period needs quotes

   # RIGHT
   date_format: "MM.YYYY"
   ```

3. **Boolean values:**
   ```yaml
   # WRONG
   recursive: True  # Capital T

   # RIGHT
   recursive: true  # Lowercase
   ```

**Solutions:**
1. **Validate YAML online:** Use yamllint.com
2. **Reset to defaults:**
   ```bash
   picsort config reset --yes
   ```
3. **Use config commands:**
   ```bash
   picsort config set recursive true
   ```

### Configuration Validation Errors

#### "Invalid date format"

**Symptoms:**
- Config validation fails
- Error mentions date_format

**Requirements:**
- Must contain "MM" (month)
- Must contain "YYYY" (year)

**Valid Examples:**
```yaml
date_format: "MM.YYYY"     # 01.2023, 12.2024
date_format: "YYYY-MM"     # 2023-01, 2024-12
date_format: "YYYY/MM"     # 2023/01, 2024/12
```

**Invalid Examples:**
```yaml
date_format: "MM.YY"       # Missing YYYY
date_format: "YYYY"        # Missing MM
date_format: "DD.MM.YYYY"  # DD not supported for folders
```

#### "Empty file_types list"

**Symptoms:**
- No files processed
- "file_types must be non-empty list"

**Solutions:**
```bash
# Add common media types
picsort config set file_types .jpg,.jpeg,.png,.mp4,.mov

# Or reset to defaults
picsort config reset --yes
```

## File Operation Issues

### No Files Found

#### "No files found to organize"

**Symptoms:**
- Scan returns 0 files
- Directory clearly contains files

**Diagnostic Steps:**

1. **Check directory exists:**
   ```bash
   ls -la /path/to/photos
   ```

2. **Check file types:**
   ```bash
   picsort scan /path/to/photos --all-files --verbose
   ```

3. **Check permissions:**
   ```bash
   # Linux/macOS
   ls -la /path/to/photos

   # Windows
   icacls "C:\path\to\photos"
   ```

**Common Causes:**

1. **File types not configured:**
   ```bash
   # Check current file types
   picsort config show | grep file_types

   # Add missing types
   picsort config set file_types .jpg,.jpeg,.png,.heic,.mp4
   ```

2. **Case sensitivity (Linux/macOS):**
   ```bash
   # Add both cases
   picsort config set file_types .jpg,.JPG,.jpeg,.JPEG
   ```

3. **Hidden files:**
   ```bash
   # Show hidden files
   ls -la /path/to/photos
   ```

### Permission Errors

#### "Permission denied" when organizing

**Symptoms:**
- Files can't be read or moved
- "Access denied" errors

**Solutions:**

1. **Check directory permissions:**
   ```bash
   # Linux/macOS
   ls -ld /path/to/photos
   chmod 755 /path/to/photos  # If needed

   # Windows
   icacls "C:\path\to\photos" /grant Users:F
   ```

2. **Check file permissions:**
   ```bash
   # Make files readable
   find /path/to/photos -type f -exec chmod 644 {} \;
   ```

3. **Run with elevated privileges (if needed):**
   ```bash
   # Linux/macOS
   sudo picsort organize /path/to/photos

   # Windows (run as Administrator)
   picsort organize "C:\path\to\photos"
   ```

4. **Check file locks:**
   - Close photo editing software
   - Close file explorers showing the directory
   - Check for antivirus scans

### File Movement Failures

#### "Checksum mismatch" errors

**Symptoms:**
- Files copied but checksum verification fails
- Operation stops with verification error

**Causes:**
- Disk corruption
- Network issues (for network drives)
- Insufficient disk space

**Solutions:**

1. **Check disk space:**
   ```bash
   # Linux/macOS
   df -h /path/to/photos

   # Windows
   dir "C:\path\to\photos"
   ```

2. **Check disk health:**
   ```bash
   # Linux
   sudo fsck /dev/sdX

   # macOS
   diskutil verifyDisk disk1

   # Windows
   chkdsk C: /f
   ```

3. **Disable verification temporarily:**
   ```bash
   picsort organize /path/to/photos --no-verify
   ```

4. **Copy files manually to test:**
   ```bash
   cp /path/to/photos/test.jpg /tmp/
   sha256sum /path/to/photos/test.jpg /tmp/test.jpg
   ```

#### Duplicate filename handling issues

**Symptoms:**
- Files with same name conflict
- Unexpected renaming behavior

**Solutions:**

1. **Check duplicate handling setting:**
   ```bash
   picsort config show | grep duplicate_handling
   ```

2. **Change handling method:**
   ```bash
   # Increment numbers (default)
   picsort config set duplicate_handling increment

   # Skip duplicates
   picsort config set duplicate_handling skip

   # Overwrite (dangerous)
   picsort config set duplicate_handling overwrite
   ```

3. **Preview duplicates:**
   ```bash
   picsort scan /path/to/photos --verbose | grep -i duplicate
   ```

### Date Detection Issues

#### Files organized with wrong dates

**Symptoms:**
- Photos appear in wrong date folders
- Dates don't match when photos were taken

**Diagnostic:**
```bash
# Check what dates are detected
picsort scan /path/to/photos --verbose
```

**Common Causes:**

1. **No EXIF data:**
   - Files don't have creation date metadata
   - Falls back to file modification time

2. **Wrong timezone:**
   - EXIF timezone different from system
   - Mixed timezones in photo collection

3. **Modified files:**
   - File modification time changed
   - Original EXIF data lost

**Solutions:**

1. **Check EXIF data:**
   ```bash
   # Linux/macOS with exiftool
   exiftool photo.jpg | grep -i date

   # Python way
   python -c "from PIL import Image; from PIL.ExifTags import TAGS; img=Image.open('photo.jpg'); print(img._getexif())"
   ```

2. **Fix file timestamps (if needed):**
   ```bash
   # Linux/macOS - set file time from EXIF
   exiftool "-FileModifyDate<DateTimeOriginal" *.jpg
   ```

## Performance Problems

### Slow Processing

#### PicSort is very slow

**Symptoms:**
- Takes long time to scan files
- File operations are slow
- High CPU/memory usage

**Diagnostic:**
```bash
# Time the operation
time picsort scan /path/to/photos --verbose

# Check system resources
top  # Linux/macOS
taskmgr  # Windows
```

**Performance Tuning:**

1. **Increase batch size:**
   ```bash
   picsort config set batch_size 500
   ```

2. **Enable parallel processing:**
   ```bash
   picsort config set parallel_scan true
   ```

3. **Disable checksum verification:**
   ```bash
   picsort organize /path/to/photos --no-verify
   ```

4. **Process in smaller chunks:**
   ```bash
   # By year
   picsort organize /path/photos/2023 --yes
   picsort organize /path/photos/2024 --yes

   # By subdirectory
   for dir in /path/photos/*/; do
       picsort organize "$dir" --yes
   done
   ```

### Memory Issues

#### "Out of memory" errors

**Symptoms:**
- PicSort crashes with memory error
- System becomes unresponsive

**Solutions:**

1. **Reduce batch size:**
   ```bash
   picsort config set batch_size 50
   ```

2. **Disable parallel processing:**
   ```bash
   picsort config set parallel_scan false
   ```

3. **Process smaller directories:**
   ```bash
   find /path/photos -mindepth 1 -maxdepth 1 -type d -exec picsort organize {} --yes \;
   ```

4. **Close other applications:**
   - Close browsers, photo editors
   - Free system memory

### Network Drive Issues

#### Slow performance on network drives

**Symptoms:**
- Much slower on network/cloud drives
- Timeouts or connection errors

**Solutions:**

1. **Optimize for network:**
   ```bash
   picsort config set batch_size 25
   picsort config set parallel_scan false
   picsort config set verify_checksum false
   ```

2. **Copy locally first:**
   ```bash
   # Copy to local drive, organize, then copy back
   rsync -av /network/photos/ /local/temp/photos/
   picsort organize /local/temp/photos --yes
   rsync -av /local/temp/photos/ /network/photos/
   ```

## Platform-Specific Issues

### Windows Issues

#### Path length limitations

**Symptoms:**
- "Path too long" errors
- Files can't be accessed with long paths

**Solutions:**

1. **Enable long path support:**
   - Windows 10/11: Enable in Group Policy or Registry
   - Use short directory names

2. **Use shorter paths:**
   ```bash
   # Instead of deep nesting
   picsort organize C:\Users\VeryLongUsername\Documents\MyPhotoCollection\FamilyPhotos\2023\Summer\

   # Use shorter path
   picsort organize C:\Photos\2023\
   ```

#### Windows Defender issues

**Symptoms:**
- Antivirus blocks PicSort
- Files disappear after processing

**Solutions:**

1. **Add exclusions:**
   - Add PicSort executable to exclusions
   - Add photo directories to exclusions

2. **Temporarily disable real-time protection:**
   - Only during PicSort operations
   - Re-enable afterwards

### macOS Issues

#### Finder integration problems

**Symptoms:**
- Folders don't appear in Finder immediately
- Thumbnail generation slow

**Solutions:**

1. **Refresh Finder:**
   ```bash
   # Force Finder refresh
   killall Finder
   ```

2. **Clear Finder cache:**
   ```bash
   sudo find /private/var/folders/ -name com.apple.finder.plist -delete
   ```

### Linux Issues

#### File system compatibility

**Symptoms:**
- Issues with different file systems
- Permission problems on mounted drives

**Solutions:**

1. **Check mount options:**
   ```bash
   mount | grep /path/to/photos
   ```

2. **Remount with proper options:**
   ```bash
   # For NTFS drives
   sudo mount -t ntfs-3g -o uid=1000,gid=1000,umask=0022 /dev/sdX1 /mnt/photos
   ```

## Error Messages Reference

### Common Error Patterns

#### Configuration Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Configuration file not found` | No config file | `picsort config init` |
| `Invalid YAML syntax` | Malformed config | Check YAML syntax, reset config |
| `Invalid date format` | Bad date_format | Use format with MM and YYYY |
| `Empty file_types list` | No file types | Add file types to config |

#### File Operation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Permission denied` | No file access | Check permissions, run as admin |
| `File not found` | Missing file | Check path, file existence |
| `Disk full` | No space | Free disk space |
| `Checksum mismatch` | File corruption | Check disk, disable verification |

#### Runtime Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Out of memory` | Large dataset | Reduce batch size, process smaller chunks |
| `Network timeout` | Slow connection | Optimize for network, copy locally |
| `Interrupted` | User stopped | Resume operation if supported |

### Exit Code Meanings

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Normal completion |
| 1 | General error | Check error message and logs |
| 2 | Invalid arguments | Check command syntax |
| 130 | User interrupted | Resume if needed |

## Getting Help

### Collecting Debug Information

When reporting issues, collect this information:

```bash
# System information
picsort version --json

# Configuration
picsort config show --json

# Verbose output of the problem
picsort organize /problem/path --dry-run --verbose 2>&1 | tee debug.log
```

### Enable Debug Logging

```bash
# Maximum verbosity
picsort organize /path --verbose

# With logging enabled
picsort config set create_log true
picsort organize /path --verbose --log-file debug.log
```

### Where to Get Help

1. **GitHub Issues**: [Project Issues](https://github.com/johnchouang/PicSort/issues)
   - Search existing issues first
   - Include debug information
   - Describe steps to reproduce

2. **Documentation**:
   - [User Guide](USER_GUIDE.md)
   - [API Reference](API_REFERENCE.md)
   - [Building Guide](BUILDING_EXECUTABLES.md)

3. **Community**:
   - Project discussions
   - Stack Overflow (tag: picsort)

### Issue Report Template

When reporting issues, include:

```
## Problem Description
Brief description of the issue

## Environment
- OS: [Windows 10/macOS 13/Ubuntu 22.04]
- PicSort version: [output of picsort version]
- Python version: [if applicable]

## Steps to Reproduce
1. Command run: `picsort organize ...`
2. Expected behavior: What should happen
3. Actual behavior: What actually happened

## Error Output
```
[paste error messages here]
```

## Debug Information
[paste output of debug commands]

## Additional Context
Any other relevant information
```

This troubleshooting guide should help you resolve most common issues with PicSort. If you encounter problems not covered here, please report them so we can improve the documentation.