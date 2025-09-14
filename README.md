# PicSort

A user-friendly CLI application that organizes media files (photos and videos) into date-based folders.

## Features

- Organize photos and videos by creation date into MM.YYYY folders
- Safe file operations with verification before deletion
- Dry-run mode to preview changes
- Handle duplicate filenames automatically
- Support for EXIF data extraction from images
- Interactive configuration wizard
- Undo functionality for reversing operations

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Organize files in current directory (dry-run by default)
picsort organize

# Organize files in specific directory
picsort organize /path/to/photos

# Execute the organization (not dry-run)
picsort organize /path/to/photos --execute

# Scan directory to preview organization
picsort scan /path/to/photos

# Interactive configuration
picsort config init

# Undo last operation
picsort undo
```

## Building Standalone Executables

PicSort can be built as a standalone executable that runs without Python installation:

```bash
# Build executable for your platform
python build_executable.py

# Build with clean environment
python build_executable.py --clean

# Build with debug information
python build_executable.py --debug
```

For comprehensive instructions, see [Building Executables Guide](docs/BUILDING_EXECUTABLES.md).

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run specific test category
pytest -m unit
pytest -m integration
pytest -m contract
```

## License

MIT