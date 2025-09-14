# Claude Code Context - PicSort

## Current Feature
**Branch**: 001-i-have-folders  
**Task**: Media file organization by creation date

## Project Overview
PicSort is a user-friendly CLI application that organizes media files (photos/videos) into date-based folders (MM.YYYY format). It prioritizes file safety with verification before deletion.

## Tech Stack
- **Language**: Python 3.11+
- **CLI Framework**: Click
- **Image Processing**: Pillow (EXIF data)
- **Testing**: Pytest
- **Distribution**: PyInstaller (standalone executables)

## Project Structure
```
src/
├── models/          # Data models (MediaFile, FolderOperation)
├── services/        # Business logic
├── cli/            # Click CLI commands
└── lib/            # Core libraries

tests/
├── contract/       # API contract tests
├── integration/    # End-to-end tests
└── unit/          # Unit tests
```

## Key Libraries
1. **file_scanner**: Scan folders and read file metadata
2. **date_organizer**: Organize files by date into folders
3. **file_mover**: Safe file move with verification
4. **config_manager**: User configuration and preferences

## Current Implementation Status
- [x] Specification complete
- [x] Research and decisions documented
- [x] Data model defined
- [x] CLI interface contract defined
- [ ] Tests to be written (TDD approach)
- [ ] Implementation pending

## Testing Approach
Following TDD strictly:
1. Write failing tests first
2. Implement to make tests pass
3. Real file operations (no mocks)
4. Test with temporary directories

## User Experience Focus
- Interactive setup wizard on first run
- Dry-run by default for safety
- Progress bars with clear feedback
- Comprehensive error messages
- Operation logs for troubleshooting

## Safety Requirements
1. Verify file copy before deletion
2. Handle locked/corrupted files gracefully
3. Support undo operations
4. Automatic duplicate renaming

## Key Decisions
- Use modification date when creation date unavailable
- Append numbers for duplicate filenames (file_1.jpg)
- Skip locked files with logging
- Process images/videos by default, all files optional
- Top-level only by default, recursive optional

## CLI Commands
```bash
picsort organize [PATH]        # Main command - organize files by date
picsort scan [PATH]           # Preview organization without changes
picsort config                # Manage configuration (show, init, set, reset)
picsort undo                  # Undo last operation
picsort version               # Show version information
```

Available scan options:
- `--recursive, -r`: Process subdirectories recursively
- `--file-types, -t`: File extensions to process (e.g., .jpg .png)
- `--format`: Output format (table, json, csv)
- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress output

## Configuration (YAML)
Located at `~/.picsort/config.yaml`
- File types to process
- Date format (MM.YYYY)
- Dry run defaults
- Logging preferences

## Recent Changes
- Initial project setup
- Created comprehensive specification
- Defined data models and contracts
- Established user-friendly CLI interface

## Next Steps
1. Create failing contract tests
2. Implement file_scanner library
3. Add progress indication
4. Build interactive config wizard

## Important Notes
- Maintain cross-platform compatibility
- Keep memory usage under 100MB
- Process 1000 files/minute target
- Ensure graceful error handling