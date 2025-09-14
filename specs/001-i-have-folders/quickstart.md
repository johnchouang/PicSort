# PicSort Quick Start Guide

## Installation

### Option 1: Standalone Executable (Easiest)
Download the executable for your platform:
- Windows: `picsort.exe`
- macOS: `picsort`
- Linux: `picsort`

No installation needed - just run it!

### Option 2: Python Package
```bash
pip install picsort
```

## First Time Setup

Run the interactive setup:
```bash
picsort config init
```

This will ask you a few questions:
1. Default folder to organize? (optional)
2. Which file types to process? (defaults to common media)
3. Use dry-run by default? (recommended: yes)
4. Create operation logs? (recommended: yes)

## Basic Usage

### 1. Preview What Will Happen (Dry Run)
Always start with a dry run to see what PicSort will do:

```bash
picsort organize --dry-run ~/Pictures/Camera
```

Output:
```
🔍 Scanning ~/Pictures/Camera...
Found 1,523 media files

📋 Preview of changes:
  03.2024: 245 files
  04.2024: 389 files
  05.2024: 156 files
  ...

No files will be moved (dry run mode)
```

### 2. Organize Your Files
When you're ready, run without `--dry-run`:

```bash
picsort organize ~/Pictures/Camera
```

Output:
```
🔍 Scanning ~/Pictures/Camera...
Found 1,523 media files

⚠️  This will organize 1,523 files into date folders.
Continue? [y/N]: y

📁 Creating folders...
✓ Created 03.2024
✓ Created 04.2024
...

📦 Moving files...
[████████████████████] 100% 1523/1523 files

✅ Organization complete!
Files processed: 1,523
Time taken: 2m 15s
Log saved to: ~/.picsort/logs/operation_20240115_103000.log
```

## Common Scenarios

### Organize Photos from Multiple Devices
```bash
# Process each device folder
picsort organize ~/Pictures/iPhone
picsort organize ~/Pictures/Camera
picsort organize ~/Pictures/GoPro
```

### Include Videos and RAW Files
```bash
picsort organize ~/Pictures --file-types .jpg .mp4 .mov .raw .dng
```

### Process All Subfolders
```bash
picsort organize ~/Pictures --recursive
```

### Custom Date Format
```bash
# Use YYYY-MM format instead of MM.YYYY
picsort organize ~/Pictures --date-format "YYYY-MM"
```

### Organize All File Types (Not Just Media)
```bash
picsort organize ~/Documents --all-files
```

## Safety Features

### 1. Automatic Verification
PicSort verifies every file is copied correctly before deleting the original:
- ✓ File size matches
- ✓ Checksum verification
- ✓ File is readable

### 2. Detailed Logs
Every operation is logged:
```bash
# View the log
cat ~/.picsort/logs/operation_20240115_103000.log
```

### 3. Undo Operations
Made a mistake? Undo the last operation:
```bash
picsort undo --operation-id op_20240115_103000
```

## Tips & Best Practices

### 1. Always Start with Scan
See what PicSort will do before organizing:
```bash
picsort scan ~/Pictures/Camera
```

### 2. Use Configuration File for Batch Processing
Create `batch.yaml`:
```yaml
folders:
  - path: ~/Pictures/iPhone
    recursive: false
  - path: ~/Pictures/Camera
    recursive: true
  - path: ~/Videos/GoPro
    file_types: [.mp4, .mov]
```

Run batch:
```bash
picsort organize --config batch.yaml
```

### 3. Handle Duplicates Safely
PicSort automatically renames duplicates:
- `IMG_1234.jpg` → `IMG_1234_1.jpg`
- `IMG_1234.jpg` → `IMG_1234_2.jpg`

### 4. Check Available Space First
```bash
# Check disk space
df -h ~/Pictures

# Run scan to see how many folders will be created
picsort scan ~/Pictures
```

## Troubleshooting

### "Permission Denied" Errors
Some files may be locked or protected:
```bash
# Skip locked files and continue
picsort organize ~/Pictures --skip-errors
```

### Files Not Moving
Check the log for details:
```bash
# View recent errors
grep ERROR ~/.picsort/logs/operation_*.log
```

### Wrong Date Detection
For files without EXIF data, PicSort uses file modification date:
```bash
# Force use of modification date
picsort organize ~/Pictures --use-modified-date
```

## Advanced Usage

### Custom Progress Reporting
```bash
# JSON output for scripts
picsort organize ~/Pictures --format json

# Quiet mode (errors only)
picsort organize ~/Pictures --quiet

# Verbose debugging
PICSORT_DEBUG=1 picsort organize ~/Pictures --verbose
```

### Integration with Other Tools
```bash
# Find and organize old photos
find ~ -name "*.jpg" -mtime +365 | xargs picsort organize

# Organize after importing from camera
gphoto2 --get-all-files --folder /store_00010001
picsort organize ./
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `picsort organize PATH` | Organize files in PATH |
| `picsort organize --dry-run PATH` | Preview without moving |
| `picsort scan PATH` | Show organization preview |
| `picsort config init` | Interactive setup |
| `picsort undo` | Undo last operation |
| `picsort --help` | Show all options |

## Getting Help

- Run `picsort --help` for all commands
- Run `picsort organize --help` for organize options
- Check logs in `~/.picsort/logs/`
- Report issues: [GitHub Issues]

## Example Workflow

1. **Scan** to preview:
   ```bash
   picsort scan ~/Pictures/Vacation2024
   ```

2. **Dry run** to confirm:
   ```bash
   picsort organize --dry-run ~/Pictures/Vacation2024
   ```

3. **Organize** when ready:
   ```bash
   picsort organize ~/Pictures/Vacation2024
   ```

4. **Verify** results:
   ```bash
   ls ~/Pictures/Vacation2024/
   # Should see: 01.2024/ 02.2024/ 03.2024/ etc.
   ```

That's it! Your media files are now organized by date. 📸 📅