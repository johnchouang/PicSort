# PicSort API Reference

This document provides a complete reference for PicSort's command-line interface, configuration options, and programmatic usage.

## Command Line Interface

### Global Options

All commands support these global options:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Enable verbose output | `false` |
| `--quiet` | `-q` | Suppress output | `false` |
| `--version` | | Show version and exit | |
| `--help` | | Show help and exit | |

### Main Commands

#### `picsort organize`

Organize media files into date-based folders.

**Syntax:**
```bash
picsort organize [OPTIONS] PATH
```

**Arguments:**
- `PATH`: Directory to organize (required, must exist)

**Options:**

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--recursive` | `-r` | Flag | Process subdirectories recursively | `false` |
| `--dry-run` | `-d` | Flag | Show what would be done without making changes | `true` |
| `--file-types` | `-t` | Multiple | File extensions to process (e.g., `.jpg .png`) | From config |
| `--all-files` | `-a` | Flag | Process all files, not just media files | `false` |
| `--date-format` | `-f` | String | Date folder format | From config |
| `--verbose` | `-v` | Flag | Enable verbose output | `false` |
| `--quiet` | `-q` | Flag | Suppress output | `false` |
| `--yes` | `-y` | Flag | Skip confirmation prompts | `false` |
| `--no-verify` | | Flag | Skip checksum verification | `false` |
| `--log-file` | `-l` | Path | Custom log file path | From config |
| `--config` | `-c` | Path | Custom configuration file | `~/.picsort/config.yaml` |

**Examples:**
```bash
# Basic organization (dry-run)
picsort organize /path/to/photos

# Recursive with specific file types
picsort organize /path/to/photos --recursive --file-types .jpg .png .mp4

# Actually perform operation
picsort organize /path/to/photos --execute

# Custom date format
picsort organize /path/to/photos --date-format "YYYY-MM"
```

**Exit Codes:**
- `0`: Success
- `1`: General error or some operations failed
- `130`: Interrupted by user (Ctrl+C)

#### `picsort scan`

Preview file organization without making changes.

**Syntax:**
```bash
picsort scan [OPTIONS] PATH
```

**Arguments:**
- `PATH`: Directory to scan (required, must exist)

**Options:**

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--recursive` | `-r` | Flag | Process subdirectories recursively | `false` |
| `--file-types` | `-t` | Multiple | File extensions to process | From config |
| `--format` | | Choice | Output format (`table`, `json`, `csv`) | `table` |
| `--verbose` | `-v` | Flag | Enable verbose output | `false` |
| `--quiet` | `-q` | Flag | Suppress output | `false` |
| `--config` | `-c` | Path | Custom configuration file | Default |

**Output Formats:**

**Table Format (default):**
```
Scan Results for: /path/to/photos
---------------------------------
Total files: 150
Media files: 142
Date range: 2023-01-15 to 2024-03-22

Folders to create:
  01.2023
  02.2023
  ...

Files by month:
  01.2023: 25 files
  02.2023: 18 files
  ...
```

**JSON Format:**
```json
{
  "scan_path": "/path/to/photos",
  "total_files": 150,
  "media_files": 142,
  "folders_to_create": ["01.2023", "02.2023", ...],
  "files_by_folder": {
    "01.2023": {
      "file_count": 25,
      "files": ["IMG_001.jpg", "IMG_002.jpg", ...]
    }
  },
  "date_range": {
    "oldest": "2023-01-15",
    "newest": "2024-03-22"
  }
}
```

**CSV Format:**
```csv
folder,file_count,files
01.2023,25,"IMG_001.jpg;IMG_002.jpg;..."
02.2023,18,"IMG_050.jpg;IMG_051.jpg;..."
```

**Examples:**
```bash
# Basic scan
picsort scan /path/to/photos

# JSON output for scripting
picsort scan /path/to/photos --format json > scan_results.json

# Recursive scan with specific file types
picsort scan /path/to/photos --recursive --file-types .mp4 .mov
```

#### `picsort config`

Manage PicSort configuration.

**Subcommands:**

##### `picsort config show`

Display current configuration.

**Options:**
- `--config-path, -c PATH`: Configuration file path
- `--json`: Output as JSON

**Examples:**
```bash
picsort config show
picsort config show --json
picsort config show --config /path/to/config.yaml
```

##### `picsort config init`

Initialize configuration with default settings.

**Options:**
- `--config-path, -c PATH`: Configuration file path
- `--backup`: Create backup of existing config

**Examples:**
```bash
picsort config init
picsort config init --backup
picsort config init --config /path/to/config.yaml
```

##### `picsort config validate`

Validate configuration file.

**Options:**
- `--config-path, -c PATH`: Configuration file path

**Examples:**
```bash
picsort config validate
picsort config validate --config /path/to/config.yaml
```

##### `picsort config set`

Set configuration value.

**Syntax:**
```bash
picsort config set KEY VALUE [OPTIONS]
```

**Arguments:**
- `KEY`: Configuration key to set
- `VALUE`: Value to set

**Options:**
- `--config-path, -c PATH`: Configuration file path

**Valid Keys:**
- `recursive`: Boolean (`true`, `false`)
- `date_format`: String (must contain MM and YYYY)
- `file_types`: Comma-separated extensions (`.jpg,.png,.mp4`)
- `process_all_files`: Boolean
- `dry_run_default`: Boolean
- `create_log`: Boolean
- `log_path`: String (path)
- `verify_checksum`: Boolean
- `batch_size`: Integer (> 0)
- `parallel_scan`: Boolean
- `confirm_large_operations`: Boolean
- `duplicate_handling`: String (`increment`, `skip`, `overwrite`)

**Examples:**
```bash
picsort config set recursive true
picsort config set date_format "YYYY-MM"
picsort config set file_types .jpg,.png,.mp4
```

##### `picsort config reset`

Reset configuration to defaults.

**Options:**
- `--yes`: Confirm reset (required)
- `--config-path, -c PATH`: Configuration file path

**Examples:**
```bash
picsort config reset --yes
```

##### `picsort config list`

List available configuration files.

**Examples:**
```bash
picsort config list
```

#### `picsort undo`

Reverse the last file organization operation.

**Syntax:**
```bash
picsort undo [OPTIONS]
```

**Options:**

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--operation-id` | `-o` | String | Specific operation to undo | Latest |
| `--dry-run` | `-d` | Flag | Preview undo without moving files | `true` |
| `--verbose` | `-v` | Flag | Enable verbose output | `false` |
| `--quiet` | `-q` | Flag | Suppress output | `false` |
| `--yes` | `-y` | Flag | Skip confirmation prompts | `false` |

**Examples:**
```bash
# Preview undo of last operation
picsort undo

# Actually undo last operation
picsort undo --dry-run=false --yes

# Undo specific operation
picsort undo --operation-id abc123def456
```

**Note:** Requires operation logging to be enabled.

#### `picsort version`

Show version information.

**Options:**
- `--json`: Output as JSON

**Examples:**
```bash
picsort version
picsort version --json
```

**JSON Output:**
```json
{
  "version": "1.0.0",
  "build": "development",
  "python_version": "3.11.0",
  "platform": "Windows"
}
```

#### `picsort resume`

Resume interrupted operations.

**Syntax:**
```bash
picsort resume [OPTIONS] [OPERATION_ID]
```

**Arguments:**
- `OPERATION_ID`: Specific operation to resume (optional)

**Options:**
- `--list`: List resumable operations
- `--latest`: Resume most recent operation
- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress output

**Examples:**
```bash
# List resumable operations
picsort resume --list

# Resume specific operation
picsort resume abc123def456

# Resume latest operation
picsort resume --latest
```

## Configuration File Reference

### File Location

- **Windows**: `C:\Users\{username}\.picsort\config.yaml`
- **macOS/Linux**: `~/.picsort/config.yaml`

### Configuration Schema

```yaml
# Schema version (required)
version: "1.0.0"

# Default source directory (optional)
default_source: null

# File types to process
file_types:
  - .jpg
  - .jpeg
  - .png
  # ... more extensions

# Process all files, not just media
process_all_files: false

# Date folder format (must contain MM and YYYY)
date_format: "MM.YYYY"

# Process subdirectories by default
recursive: false

# Default to dry-run mode for safety
dry_run_default: true

# Enable operation logging
create_log: true

# Log file directory
log_path: "~/.picsort/logs"

# Verify file integrity with checksums
verify_checksum: true

# Number of files to process in batches
batch_size: 100

# Enable parallel scanning for performance
parallel_scan: true

# Confirm large operations
confirm_large_operations: true

# How to handle duplicate filenames
duplicate_handling: "increment"  # or "skip", "overwrite"
```

### Configuration Validation Rules

- `version`: Must match current schema version (1.0.0)
- `file_types`: Must be non-empty list of strings
- `date_format`: Must contain "MM" and "YYYY" placeholders
- `batch_size`: Must be integer > 0
- `duplicate_handling`: Must be one of: `increment`, `skip`, `overwrite`

### Environment Variable Overrides

Configuration can be overridden with environment variables:

| Variable | Config Key | Example |
|----------|------------|---------|
| `PICSORT_CONFIG` | config file path | `/path/to/config.yaml` |
| `PICSORT_RECURSIVE` | recursive | `true` |
| `PICSORT_DRY_RUN` | dry_run_default | `false` |
| `PICSORT_LOG_LEVEL` | log level | `DEBUG` |

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | Operation completed successfully |
| `1` | General Error | Configuration error, file operation failed, etc. |
| `2` | Invalid Arguments | Invalid command line arguments |
| `130` | Interrupted | Operation interrupted by user (Ctrl+C) |

## Error Handling

### Common Error Types

#### Configuration Errors
- Invalid YAML syntax
- Missing required fields
- Invalid field values

#### File Operation Errors
- Permission denied
- File not found
- Disk full
- Checksum mismatch

#### Runtime Errors
- Out of memory
- Network timeout (for remote paths)
- Interrupted operation

### Error Output Format

**Standard Error Format:**
```
ERROR: [error_type] error_message
  Context: additional_context
  File: /path/to/file (if applicable)
  Suggestion: how_to_fix
```

**JSON Error Format (when --json used):**
```json
{
  "error": {
    "type": "configuration_error",
    "message": "Invalid date format",
    "context": {
      "config_file": "/path/to/config.yaml",
      "field": "date_format",
      "value": "INVALID"
    },
    "suggestions": [
      "Use format containing MM and YYYY",
      "Example: MM.YYYY or YYYY-MM"
    ]
  }
}
```

## Logging

### Log File Structure

Log files are stored as JSON with the following structure:

```json
{
  "operation_id": "abc123def456",
  "operation_type": "organize",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:35:30Z",
  "source_path": "/path/to/source",
  "configuration": {
    "date_format": "MM.YYYY",
    "file_types": [".jpg", ".png"],
    // ... full config snapshot
  },
  "operations": [
    {
      "type": "file_move",
      "source": "/path/to/source/IMG_001.jpg",
      "destination": "/path/to/source/01.2024/IMG_001.jpg",
      "timestamp": "2024-01-15T10:30:15Z",
      "checksum_source": "sha256:abc123...",
      "checksum_dest": "sha256:abc123...",
      "status": "success"
    },
    // ... more operations
  ],
  "summary": {
    "total_files": 100,
    "successful": 98,
    "failed": 2,
    "skipped": 0
  },
  "errors": [
    {
      "file": "/path/to/problem.jpg",
      "error": "Permission denied",
      "timestamp": "2024-01-15T10:32:00Z"
    }
  ]
}
```

### Log Levels

| Level | Description | When Used |
|-------|-------------|-----------|
| `DEBUG` | Detailed diagnostic info | Development, troubleshooting |
| `INFO` | General information | Normal operation progress |
| `WARNING` | Warning messages | Non-fatal issues |
| `ERROR` | Error messages | Operation failures |

## Programmatic Usage

### Python API (Advanced)

While primarily a CLI tool, PicSort's core functionality can be used programmatically:

```python
from picsort.lib.config_manager import ConfigManager
from picsort.lib.file_scanner import FileScanner
from picsort.lib.date_organizer import DateOrganizer

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Scan files
scanner = FileScanner(config)
files = scanner.scan_directory("/path/to/photos")

# Organize files
organizer = DateOrganizer(config)
organization = organizer.organize_files(files, "/path/to/photos")

# Preview results
summary = organizer.get_organization_summary(organization)
print(f"Would organize {summary['total_files']} files into {summary['new_folders']} folders")
```

### Shell Integration

#### Bash Completion

Add to your `.bashrc` or `.bash_profile`:

```bash
# PicSort bash completion
eval "$(_PICSORT_COMPLETE=bash_source picsort)"
```

#### PowerShell Completion

Add to your PowerShell profile:

```powershell
# PicSort PowerShell completion
$scriptBlock = {
    param($commandName, $wordToComplete, $cursorPosition)
    picsort completion powershell $wordToComplete
}
Register-ArgumentCompleter -Native -CommandName picsort -ScriptBlock $scriptBlock
```

## Performance Considerations

### Memory Usage

- **Small collections** (< 1,000 files): ~10-20 MB
- **Medium collections** (1,000-10,000 files): ~20-50 MB
- **Large collections** (10,000+ files): ~50-100 MB

### Processing Speed

Typical processing speeds on modern hardware:

- **File scanning**: 1,000-5,000 files/second
- **File moving**: 100-500 files/second (depends on storage)
- **Checksum verification**: 50-200 files/second

### Optimization Settings

For different scenarios:

**Fast processing (less safety):**
```yaml
verify_checksum: false
batch_size: 1000
parallel_scan: true
```

**Safe processing (slower):**
```yaml
verify_checksum: true
batch_size: 50
parallel_scan: false
```

**Network storage:**
```yaml
verify_checksum: true
batch_size: 25
parallel_scan: false
```

This completes the API reference. For usage examples and workflows, see the [User Guide](USER_GUIDE.md).