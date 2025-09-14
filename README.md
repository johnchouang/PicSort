# PicSort

**PicSort** is a powerful, user-friendly CLI application that automatically organizes your media files (photos and videos) into date-based folders. It intelligently extracts creation dates from file metadata and safely moves files into a clean folder structure for easy browsing and management.

## 🌟 Key Features

### Smart Organization
- **Date-based folder structure**: Organizes files into `MM.YYYY` format (e.g., `01.2023`, `12.2024`)
- **EXIF metadata extraction**: Reads creation dates from photo EXIF data
- **Video metadata support**: Extracts dates from video file metadata
- **Fallback to file dates**: Uses file modification dates when metadata isn't available

### Safety First
- **Dry-run by default**: Preview changes before making them
- **File verification**: Checksums verify successful copies before deletion
- **Duplicate handling**: Automatically renames duplicates (e.g., `photo_1.jpg`)
- **Comprehensive logging**: Track all operations with detailed logs
- **Resume functionality**: Resume interrupted operations

### User Experience
- **Progress bars**: Visual feedback during long operations
- **Multiple output formats**: Table, JSON, and CSV output for scan results
- **Flexible configuration**: YAML-based configuration with CLI overrides
- **Interactive setup**: Guided configuration wizard
- **Cross-platform**: Windows, macOS, and Linux support

### Advanced Features
- **Recursive processing**: Process subdirectories with `--recursive`
- **File type filtering**: Process specific file types or all files
- **Batch operations**: Efficient processing of large file collections
- **Operation logging**: Complete audit trail of all file operations
- **Undo support**: Reverse operations (requires logging to be enabled)

## 🚀 Quick Start

### Installation

#### Option 1: Install from Source
```bash
git clone https://github.com/johnchouang/PicSort.git
cd PicSort
pip install -e .
```

#### Option 2: Use Standalone Executable
Download the pre-built executable for your platform from the [releases page](releases) or build it yourself:

```bash
python build_executable.py
```

### First Run

1. **Initialize configuration** (recommended):
   ```bash
   picsort config init
   ```

2. **Preview what would be organized** (dry-run):
   ```bash
   picsort scan /path/to/your/photos
   ```

3. **Organize your files**:
   ```bash
   # Dry-run first (safe preview)
   picsort organize /path/to/your/photos --dry-run

   # When ready, perform actual organization
   picsort organize /path/to/your/photos
   ```

## 📖 Detailed Usage

### Core Commands

#### `organize` - Main Organization Command

Organize media files into date-based folders:

```bash
# Basic usage - dry-run by default for safety
picsort organize /path/to/photos

# Actually perform the organization
picsort organize /path/to/photos --execute

# Process subdirectories recursively
picsort organize /path/to/photos --recursive

# Process specific file types only
picsort organize /path/to/photos --file-types .jpg .png .mp4

# Process all files (not just media)
picsort organize /path/to/photos --all-files

# Use custom date format
picsort organize /path/to/photos --date-format "YYYY-MM"

# Skip verification for faster processing (less safe)
picsort organize /path/to/photos --no-verify

# Auto-confirm prompts
picsort organize /path/to/photos --yes
```

**Options:**
- `--recursive, -r`: Process subdirectories
- `--dry-run, -d`: Show what would be done without making changes
- `--file-types, -t`: Specific file extensions to process
- `--all-files, -a`: Process all files, not just media files
- `--date-format, -f`: Custom date folder format
- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress output
- `--yes, -y`: Skip confirmation prompts
- `--no-verify`: Skip checksum verification
- `--log-file, -l`: Custom log file path
- `--config, -c`: Custom configuration file

#### `scan` - Preview Organization

Preview how files would be organized without making changes:

```bash
# Basic scan
picsort scan /path/to/photos

# Scan with different output formats
picsort scan /path/to/photos --format table    # Default
picsort scan /path/to/photos --format json     # JSON output
picsort scan /path/to/photos --format csv      # CSV output

# Scan recursively
picsort scan /path/to/photos --recursive

# Scan specific file types
picsort scan /path/to/photos --file-types .jpg .png
```

**Output formats:**
- `table`: Human-readable table format (default)
- `json`: Machine-readable JSON format
- `csv`: Comma-separated values format

#### `config` - Configuration Management

Manage PicSort configuration:

```bash
# Initialize default configuration
picsort config init

# Show current configuration
picsort config show
picsort config show --json    # JSON format

# Set configuration values
picsort config set recursive true
picsort config set date_format "YYYY-MM"
picsort config set file_types .jpg,.png,.mp4

# Validate configuration
picsort config validate

# Reset to defaults (requires confirmation)
picsort config reset --yes

# List available configurations
picsort config list
```

#### `undo` - Reverse Operations

Reverse the last organization operation:

```bash
# Preview what would be undone
picsort undo

# Actually perform the undo
picsort undo --dry-run=false --yes

# Undo specific operation
picsort undo --operation-id abc123
```

**Note:** Requires operation logging to be enabled in configuration.

#### `version` - Version Information

Display version and system information:

```bash
# Basic version info
picsort version

# Detailed JSON format
picsort version --json
```

### Configuration

PicSort uses a YAML configuration file located at `~/.picsort/config.yaml`. You can customize behavior through this file or command-line options.

#### Default Configuration

```yaml
version: "1.0.0"
default_source: null
file_types:
  - .jpg
  - .jpeg
  - .png
  - .gif
  - .bmp
  - .tiff
  - .tif
  - .webp
  - .mp4
  - .mov
  - .avi
  - .mkv
  - .wmv
  - .flv
  - .webm
  - .m4v
process_all_files: false
date_format: "MM.YYYY"
recursive: false
dry_run_default: true
create_log: true
log_path: "~/.picsort/logs"
verify_checksum: true
batch_size: 100
parallel_scan: true
confirm_large_operations: true
duplicate_handling: "increment"
```

#### Configuration Options

- **file_types**: List of file extensions to process
- **process_all_files**: Process all files, not just media files
- **date_format**: Format for date folders (must contain MM and YYYY)
- **recursive**: Process subdirectories by default
- **dry_run_default**: Default to dry-run mode for safety
- **create_log**: Enable operation logging
- **log_path**: Directory for log files
- **verify_checksum**: Verify files with checksums before deletion
- **batch_size**: Number of files to process in each batch
- **parallel_scan**: Enable parallel scanning for better performance
- **confirm_large_operations**: Prompt for confirmation on large operations
- **duplicate_handling**: How to handle duplicate filenames (increment/skip/overwrite)

### Examples

#### Basic Photo Organization

```bash
# Organize photos from your phone
picsort organize ~/Photos/iPhone --recursive

# Preview first
picsort scan ~/Photos/iPhone --recursive
```

#### Professional Workflow

```bash
# Process only RAW and JPEG files
picsort organize ~/Photos/Shoot2024 --file-types .cr2 .jpg --recursive

# With custom date format for client folders
picsort organize ~/Photos/ClientWork --date-format "YYYY-MM-DD" --recursive
```

#### Video Organization

```bash
# Organize all video files
picsort organize ~/Videos --file-types .mp4 .mov .avi --recursive

# Quick scan to see what would be organized
picsort scan ~/Videos --format json > video_scan.json
```

#### Batch Processing

```bash
# Process multiple directories
for dir in ~/Photos/2023 ~/Photos/2024; do
    picsort organize "$dir" --recursive --yes
done
```

## 🛠️ Advanced Features

### Resume Interrupted Operations

If an organization operation is interrupted, you can resume it:

```bash
# Check for resumable operations
picsort resume --list

# Resume specific operation
picsort resume abc123def456
```

### Custom Date Formats

PicSort supports various date folder formats:

```bash
# Year-Month format
picsort organize photos/ --date-format "YYYY-MM"

# Month-Year format (default)
picsort organize photos/ --date-format "MM.YYYY"

# Year only
picsort organize photos/ --date-format "YYYY"

# Full date
picsort organize photos/ --date-format "YYYY-MM-DD"
```

### Handling Duplicates

Configure how duplicate filenames are handled:

```bash
# Increment numbers (photo.jpg -> photo_1.jpg) - default
picsort config set duplicate_handling increment

# Skip duplicate files
picsort config set duplicate_handling skip

# Overwrite existing files (dangerous)
picsort config set duplicate_handling overwrite
```

### Operation Logging

All operations can be logged for audit trails and undo functionality:

```bash
# Enable logging (default)
picsort config set create_log true

# Set custom log location
picsort config set log_path "/path/to/logs"

# View log of specific operation
picsort log show abc123def456
```

## 📦 Building Standalone Executables

PicSort can be packaged as a standalone executable that runs without Python installation:

```bash
# Build for your current platform
python build_executable.py

# Clean build (recommended for distribution)
python build_executable.py --clean

# Debug build (larger but with debug info)
python build_executable.py --debug

# Build without compression (faster build, larger file)
python build_executable.py --no-upx
```

**Output locations:**
- Windows: `dist/picsort.exe`
- macOS: `dist/PicSort.app`
- Linux: `dist/picsort`

For detailed build instructions, see [Building Executables Guide](docs/BUILDING_EXECUTABLES.md).

## 🧪 Testing

PicSort includes comprehensive tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m contract       # API contract tests only

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=src --cov-report=html
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/johnchouang/PicSort.git
cd PicSort

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-build.txt
```

### Project Structure

```
PicSort/
├── src/
│   ├── cli/            # Command-line interface
│   │   ├── commands/   # Individual CLI commands
│   │   └── main.py     # Main CLI entry point
│   ├── lib/            # Core libraries
│   │   ├── file_scanner.py      # File discovery and metadata
│   │   ├── date_organizer.py    # Organization logic
│   │   ├── file_mover.py        # Safe file operations
│   │   ├── config_manager.py    # Configuration handling
│   │   └── ...
│   ├── models/         # Data models
│   │   ├── media_file.py        # Media file representation
│   │   ├── configuration.py     # Configuration model
│   │   └── ...
│   └── services/       # Business logic services
├── tests/              # Comprehensive test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── contract/       # API contract tests
├── docs/               # Documentation
└── build_executable.py # Standalone executable builder
```

## ❓ Troubleshooting

### Common Issues

**"No files found to organize"**
- Check file permissions
- Verify file types are supported
- Use `--verbose` to see what files are being skipped

**"Permission denied" errors**
- Ensure write permissions to destination folders
- Check that files aren't locked by other applications
- Try running as administrator (Windows) or with sudo (Linux/macOS)

**Slow performance with many files**
- Enable parallel scanning: `picsort config set parallel_scan true`
- Increase batch size: `picsort config set batch_size 500`
- Disable checksum verification for speed: `--no-verify`

**Executable won't run on Windows**
- Add to antivirus exclusions (PyInstaller false positive)
- Ensure all Visual C++ redistributables are installed

### Getting Help

```bash
# Get help for any command
picsort --help
picsort organize --help
picsort config --help

# Enable verbose output for debugging
picsort organize /path/to/photos --verbose

# Check version and system info
picsort version --json
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/PicSort.git
cd PicSort

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest

# Submit pull request
```

## 📄 License

PicSort is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI interface
- Uses [Pillow](https://pillow.readthedocs.io/) for image processing
- Progress bars powered by [tqdm](https://tqdm.github.io/)
- Executable building with [PyInstaller](https://pyinstaller.org/)

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/johnchouang/PicSort/issues)
- **Releases**: [GitHub Releases](https://github.com/johnchouang/PicSort/releases)
- **PyPI Package**: Coming soon!