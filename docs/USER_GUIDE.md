# PicSort User Guide

This comprehensive guide will help you master PicSort, from basic photo organization to advanced workflows.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Operations](#basic-operations)
3. [Configuration](#configuration)
4. [Advanced Features](#advanced-features)
5. [Workflows and Examples](#workflows-and-examples)
6. [Troubleshooting](#troubleshooting)
7. [Tips and Best Practices](#tips-and-best-practices)

## Getting Started

### What is PicSort?

PicSort is a command-line tool that automatically organizes your media files (photos and videos) into date-based folders. Instead of having thousands of files scattered across directories, PicSort creates a clean structure like:

```
Photos/
├── 01.2023/     # January 2023 photos
├── 02.2023/     # February 2023 photos
├── 12.2023/     # December 2023 photos
├── 01.2024/     # January 2024 photos
└── ...
```

### Installation Options

#### Option 1: Python Installation (Recommended for developers)

```bash
# Clone the repository
git clone https://github.com/johnchouang/PicSort.git
cd PicSort

# Install in development mode
pip install -e .
```

#### Option 2: Standalone Executable (Recommended for end users)

Download the executable for your platform:
- **Windows**: `picsort.exe`
- **macOS**: `PicSort.app`
- **Linux**: `picsort`

Or build it yourself:
```bash
python build_executable.py
```

### First Time Setup

1. **Open your terminal/command prompt**

2. **Initialize PicSort configuration**:
   ```bash
   picsort config init
   ```
   This creates a configuration file at `~/.picsort/config.yaml` with sensible defaults.

3. **Verify installation**:
   ```bash
   picsort --version
   ```

## Basic Operations

### Understanding Dry-Run Mode

**Important**: PicSort defaults to dry-run mode for safety. This means it will show you what it *would* do without actually moving any files.

- **Dry-run**: Shows preview, no files moved
- **Execute**: Actually moves files

### Your First Organization

#### Step 1: Preview What Will Happen

```bash
# Basic scan to see what files would be organized
picsort scan /path/to/your/photos
```

This shows:
- How many files were found
- What date folders would be created
- Which files have issues

#### Step 2: Run a Dry-Run Organization

```bash
# Preview the organization
picsort organize /path/to/your/photos --dry-run
```

This shows exactly what would happen:
- Which files would be moved where
- Any duplicates that would be renamed
- Folders that would be created

#### Step 3: Execute the Organization

When you're satisfied with the preview:

```bash
# Actually perform the organization
picsort organize /path/to/your/photos
```

**Note**: The `--dry-run` flag is on by default. Not specifying it will perform the actual operation.

### Core Commands

#### `picsort organize`

The main command that moves files into date folders.

**Basic usage**:
```bash
picsort organize /path/to/photos
```

**Common options**:
```bash
# Process subdirectories too
picsort organize /path/to/photos --recursive

# Only process specific file types
picsort organize /path/to/photos --file-types .jpg .png

# Use a different date format
picsort organize /path/to/photos --date-format "YYYY-MM"

# Skip confirmation prompts
picsort organize /path/to/photos --yes

# Enable detailed output
picsort organize /path/to/photos --verbose
```

#### `picsort scan`

Preview organization without making changes.

**Basic usage**:
```bash
picsort scan /path/to/photos
```

**Output formats**:
```bash
# Human-readable table (default)
picsort scan /path/to/photos --format table

# Machine-readable JSON
picsort scan /path/to/photos --format json

# CSV for spreadsheets
picsort scan /path/to/photos --format csv
```

#### `picsort config`

Manage your configuration settings.

```bash
# Show current configuration
picsort config show

# Set a configuration value
picsort config set recursive true

# Reset to defaults
picsort config reset --yes

# Validate your configuration
picsort config validate
```

#### `picsort undo`

Reverse the last organization operation (requires logging enabled).

```bash
# Preview what would be undone
picsort undo

# Actually undo the last operation
picsort undo --dry-run=false --yes
```

## Configuration

### Configuration File Location

PicSort stores its configuration at:
- **Windows**: `C:\Users\YourName\.picsort\config.yaml`
- **macOS/Linux**: `~/.picsort/config.yaml`

### Key Configuration Options

#### File Types

Control which files are processed:

```yaml
# Default media file types
file_types:
  - .jpg
  - .jpeg
  - .png
  - .mp4
  - .mov
  # Add more as needed

# Process all files, not just media
process_all_files: false
```

**CLI override**:
```bash
picsort organize photos/ --file-types .jpg .png .mp4
picsort organize photos/ --all-files
```

#### Date Format

Choose how date folders are named:

```yaml
# Month.Year (default)
date_format: "MM.YYYY"    # Results in: 01.2023, 02.2023

# Year-Month
date_format: "YYYY-MM"    # Results in: 2023-01, 2023-02

# Year only
date_format: "YYYY"       # Results in: 2023, 2024

# Full date (creates many folders)
date_format: "YYYY-MM-DD" # Results in: 2023-01-15
```

#### Safety Settings

```yaml
# Default to dry-run for safety
dry_run_default: true

# Verify file integrity with checksums
verify_checksum: true

# Confirm before large operations
confirm_large_operations: true

# How to handle duplicate filenames
duplicate_handling: "increment"  # photo.jpg -> photo_1.jpg
# duplicate_handling: "skip"      # Skip duplicates
# duplicate_handling: "overwrite" # Overwrite (dangerous)
```

#### Performance Settings

```yaml
# Process files in batches of this size
batch_size: 100

# Enable parallel scanning for speed
parallel_scan: true

# Process subdirectories by default
recursive: false
```

#### Logging

```yaml
# Enable operation logging (required for undo)
create_log: true

# Where to store logs
log_path: "~/.picsort/logs"
```

### Managing Configuration

#### View Current Settings

```bash
# Human-readable format
picsort config show

# JSON format for scripting
picsort config show --json
```

#### Change Settings

```bash
# Enable recursive processing by default
picsort config set recursive true

# Change date format
picsort config set date_format "YYYY-MM"

# Add more file types
picsort config set file_types .jpg,.png,.mp4,.avi

# Disable checksum verification for speed
picsort config set verify_checksum false
```

#### Validate Configuration

```bash
picsort config validate
```

This checks for:
- Invalid file formats
- Missing required fields
- Conflicting settings

## Advanced Features

### Resume Interrupted Operations

If PicSort is interrupted (power loss, Ctrl+C, etc.), you can resume:

```bash
# List resumable operations
picsort resume --list

# Resume a specific operation
picsort resume abc123def456

# Resume the most recent operation
picsort resume --latest
```

### Custom Date Extraction

PicSort tries multiple methods to determine file dates:

1. **EXIF data** (for photos) - most accurate
2. **File metadata** (creation/modification dates)
3. **Filename parsing** (if filename contains date)

You can see what date was extracted:
```bash
picsort scan /path/to/photos --verbose
```

### Handling Duplicates

When files have the same name in a destination folder:

#### Increment (Default)
```
photo.jpg -> photo.jpg
photo.jpg -> photo_1.jpg
photo.jpg -> photo_2.jpg
```

#### Skip
```
photo.jpg -> photo.jpg (first file)
photo.jpg -> (skipped)
```

#### Overwrite (Dangerous)
```
photo.jpg -> photo.jpg (overwrites existing)
```

### Batch Processing

Process multiple directories:

```bash
# Using a loop
for dir in ~/Photos/2023 ~/Photos/2024; do
    picsort organize "$dir" --recursive --yes
done

# Using find (Linux/macOS)
find ~/Photos -name "*.jpg" -execdir picsort organize {} --yes \;
```

### Integration with Other Tools

#### Export Scan Results

```bash
# Create a report of all photos
picsort scan ~/Photos --recursive --format json > photo_inventory.json

# CSV for Excel
picsort scan ~/Photos --recursive --format csv > photo_inventory.csv
```

#### Use with File Watchers

Monitor a directory and auto-organize new files:

```bash
# Linux/macOS with inotify-tools
inotifywait -m -r -e create ~/Downloads/Photos --format '%w%f' | while read file; do
    picsort organize "$(dirname "$file")" --yes --quiet
done
```

## Workflows and Examples

### Workflow 1: Organizing Phone Photos

**Scenario**: You have thousands of photos from your phone in various folders.

```bash
# Step 1: See what you have
picsort scan ~/Phone_Backup --recursive --format table

# Step 2: Preview organization
picsort organize ~/Phone_Backup --recursive --dry-run

# Step 3: Execute if satisfied
picsort organize ~/Phone_Backup --recursive --yes
```

**Result**: All photos organized by month and year.

### Workflow 2: Professional Photography

**Scenario**: RAW files and JPEGs from photo shoots.

```bash
# Configure for professional workflow
picsort config set date_format "YYYY-MM-DD"
picsort config set file_types .cr2,.jpg,.dng,.tiff

# Organize by specific shoot date
picsort organize ~/Photoshoots/Client_Wedding_2024 --recursive --yes

# Generate client delivery report
picsort scan ~/Photoshoots/Client_Wedding_2024 --recursive --format json > delivery_report.json
```

### Workflow 3: Video Organization

**Scenario**: Mix of video files from different sources.

```bash
# Focus on video files only
picsort organize ~/Videos --file-types .mp4,.mov,.avi --recursive --yes

# Check for any missed files
picsort scan ~/Videos --recursive --verbose | grep -i "error"
```

### Workflow 4: Recovering from Disorganized Folders

**Scenario**: Years of unorganized media files.

```bash
# Step 1: Comprehensive scan to understand scope
picsort scan ~/Pictures --recursive --format json > full_scan.json

# Step 2: Start with photos only for first pass
picsort organize ~/Pictures --file-types .jpg,.jpeg,.png --recursive --dry-run

# Step 3: Execute photos organization
picsort organize ~/Pictures --file-types .jpg,.jpeg,.png --recursive --yes

# Step 4: Handle videos separately
picsort organize ~/Pictures --file-types .mp4,.mov,.avi --recursive --yes

# Step 5: Clean up any remaining files
picsort organize ~/Pictures --all-files --recursive --dry-run
```

### Workflow 5: Continuous Organization

**Scenario**: Keep Downloads folder organized automatically.

Set up a script that runs periodically:

```bash
#!/bin/bash
# organize_downloads.sh

DOWNLOAD_DIR="$HOME/Downloads"
PHOTOS_DIR="$HOME/Photos/From_Downloads"

# Move media files to photos directory and organize
if [ -d "$DOWNLOAD_DIR" ]; then
    # Find media files and organize them
    picsort organize "$DOWNLOAD_DIR" --file-types .jpg,.jpeg,.png,.mp4,.mov --yes --quiet

    # Log the operation
    echo "$(date): Organized downloads" >> ~/.picsort/auto_organize.log
fi
```

Run with cron:
```bash
# Add to crontab (run every hour)
0 * * * * /home/user/organize_downloads.sh
```

## Troubleshooting

### Common Issues and Solutions

#### "No files found to organize"

**Causes**:
- Wrong directory path
- Files don't match configured file types
- Permission issues

**Solutions**:
```bash
# Check if directory exists
ls -la /path/to/photos

# See what files PicSort finds
picsort scan /path/to/photos --verbose

# Try with all file types
picsort scan /path/to/photos --all-files
```

#### "Permission denied" errors

**Causes**:
- No write permission to destination
- Files locked by other applications

**Solutions**:
```bash
# Check permissions
ls -la /path/to/photos

# Run with appropriate permissions
sudo picsort organize /path/to/photos  # Linux/macOS
# Or run as administrator on Windows

# Close applications that might lock files
```

#### Slow performance

**Causes**:
- Many files to process
- Slow disk
- Checksum verification enabled

**Solutions**:
```bash
# Increase batch size
picsort config set batch_size 500

# Enable parallel processing
picsort config set parallel_scan true

# Disable checksums for speed (less safe)
picsort organize /path --no-verify

# Process in smaller chunks
picsort organize /path/2023 --yes
picsort organize /path/2024 --yes
```

#### Files not organizing correctly

**Causes**:
- No metadata in files
- Wrong date in metadata
- Files from different time zones

**Solutions**:
```bash
# Check what dates are being detected
picsort scan /path/to/photos --verbose

# Use file modification dates as fallback
# (This is automatic if EXIF data is missing)

# For timezone issues, files will use their stored timezone
# or fall back to system timezone
```

#### Undo not working

**Causes**:
- Logging not enabled
- Log files deleted or moved
- Operation was from different PicSort version

**Solutions**:
```bash
# Enable logging
picsort config set create_log true

# Check if logs exist
ls ~/.picsort/logs/

# Manually check log files
cat ~/.picsort/logs/operation_*.json
```

### Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Configuration file not found` | No config file exists | Run `picsort config init` |
| `Invalid date format` | Bad date_format in config | Check format has MM and YYYY |
| `Checksum mismatch` | File corruption during copy | Re-run operation, check disk |
| `Destination file exists` | Duplicate handling issue | Check duplicate_handling setting |
| `EXIF data corrupt` | Bad photo metadata | File will use modification date |

### Debug Mode

For detailed troubleshooting:

```bash
# Maximum verbosity
picsort organize /path/to/photos --verbose

# Check configuration
picsort config validate

# Test with small subset first
picsort organize /path/to/photos/test_folder --dry-run --verbose
```

## Tips and Best Practices

### Before You Start

1. **Always backup your files first**
   ```bash
   cp -r ~/Photos ~/Photos_backup
   ```

2. **Start with a dry-run**
   ```bash
   picsort organize ~/Photos --dry-run
   ```

3. **Test with a small folder first**
   ```bash
   mkdir test_photos
   cp ~/Photos/*.jpg test_photos/
   picsort organize test_photos --dry-run
   ```

### Configuration Best Practices

1. **Enable logging for undo capability**
   ```bash
   picsort config set create_log true
   ```

2. **Choose appropriate date format**
   - `MM.YYYY` - Good for general use, easy browsing
   - `YYYY-MM` - Better for chronological sorting
   - `YYYY` - Fewer folders, good for spanning many years

3. **Configure file types carefully**
   ```bash
   # For photographers - include RAW formats
   picsort config set file_types .cr2,.nef,.arw,.jpg,.jpeg

   # For general users - stick to common formats
   picsort config set file_types .jpg,.jpeg,.png,.mp4,.mov
   ```

### Organization Strategy

1. **Organize by purpose**
   ```bash
   # Personal photos
   picsort organize ~/Photos/Personal --date-format "MM.YYYY"

   # Work/client photos
   picsort organize ~/Photos/Work --date-format "YYYY-MM-DD"
   ```

2. **Handle different media types separately**
   ```bash
   # Photos first
   picsort organize ~/Media --file-types .jpg,.png --recursive

   # Videos second
   picsort organize ~/Media --file-types .mp4,.mov --recursive
   ```

3. **Use descriptive directory names**
   ```
   Photos/
   ├── Organized/          # PicSort organized files
   ├── To_Process/         # New files to organize
   └── Archive/           # Long-term storage
   ```

### Performance Tips

1. **For large collections (10,000+ files)**
   ```bash
   picsort config set batch_size 500
   picsort config set parallel_scan true
   ```

2. **For slow storage (network drives)**
   ```bash
   picsort config set batch_size 50
   picsort config set verify_checksum false  # Less safe but faster
   ```

3. **For SSDs**
   ```bash
   picsort config set batch_size 1000
   picsort config set parallel_scan true
   ```

### Maintenance

1. **Regular cleanup**
   ```bash
   # Clean old logs (optional)
   find ~/.picsort/logs -name "*.json" -mtime +30 -delete
   ```

2. **Backup configuration**
   ```bash
   cp ~/.picsort/config.yaml ~/config_backup.yaml
   ```

3. **Monitor disk space**
   ```bash
   # Check space before large operations
   df -h ~/Photos
   ```

### Advanced Tips

1. **Scripting with PicSort**
   ```bash
   #!/bin/bash
   # Process each year separately
   for year in 2020 2021 2022 2023 2024; do
       if [ -d "~/Photos/$year" ]; then
           echo "Processing $year..."
           picsort organize ~/Photos/$year --recursive --yes
       fi
   done
   ```

2. **Integration with photo management tools**
   ```bash
   # Generate reports for other tools
   picsort scan ~/Photos --recursive --format json | jq '.files_by_folder'
   ```

3. **Monitoring organization**
   ```bash
   # Check organization completeness
   find ~/Photos -maxdepth 1 -name "*.jpg" | wc -l  # Should be 0 after organization
   ```

Remember: PicSort is designed to be safe and predictable. When in doubt, use dry-run mode and always keep backups of your precious photos and videos!