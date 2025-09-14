# Research Findings: Media File Organization

## Clarifications from Spec

### 1. File Creation Date Fallback
**Decision**: Use modification date as fallback when creation date unavailable
**Rationale**: 
- Creation date may not be available on all filesystems (especially Linux)
- Modification date is universally available
- Better to organize by approximate date than skip files
**Alternatives considered**: 
- Skip files: Rejected - leaves files unorganized
- Use current date: Rejected - misleading organization

### 2. Duplicate Filename Handling
**Decision**: Append incrementing number to filename (file_1.jpg, file_2.jpg)
**Rationale**:
- Preserves all files (no data loss)
- Clear naming pattern
- Common industry practice
**Alternatives considered**:
- Overwrite: Rejected - potential data loss
- Skip: Rejected - incomplete organization
- Use hash: Rejected - less user-friendly names

### 3. Insufficient Disk Space
**Decision**: Pre-check available space, stop gracefully with clear error
**Rationale**:
- Prevents partial operations
- Clear user communication
- Allows user to free space and retry
**Alternatives considered**:
- Continue until full: Rejected - leaves incomplete state
- Automatic cleanup: Rejected - too risky without user consent

### 4. Locked Files
**Decision**: Skip locked files, log them, continue with others
**Rationale**:
- Doesn't block entire operation
- User can close applications and retry
- Clear reporting of skipped files
**Alternatives considered**:
- Wait for unlock: Rejected - could hang indefinitely
- Force unlock: Rejected - could corrupt files or crash applications

### 5. File Type Filtering
**Decision**: Process image and video files only by default, with option for all files
**Rationale**:
- Matches primary use case (media organization)
- Prevents accidental movement of system files
- User can opt-in to all files if needed
**Alternatives considered**:
- All files always: Rejected - too risky
- Hard-coded list only: Rejected - too restrictive

### 6. Corrupted Files
**Decision**: Skip corrupted files, log them, continue processing
**Rationale**:
- Doesn't stop entire operation
- User awareness through logging
- Corrupted files need special handling anyway
**Alternatives considered**:
- Attempt repair: Rejected - out of scope, risky
- Stop on error: Rejected - too disruptive

### 7. Progress Indication
**Decision**: Real-time progress bar with file count and current file name
**Rationale**:
- Clear visual feedback
- User knows operation is working
- Can estimate completion time
**Alternatives considered**:
- Simple spinner: Rejected - no progress indication
- Percentage only: Rejected - less informative

### 8. Nested Folders
**Decision**: Process top-level only by default, recursive with --recursive flag
**Rationale**:
- Safer default behavior
- User control over scope
- Preserves existing folder organization
**Alternatives considered**:
- Always recursive: Rejected - might process unwanted folders
- Never recursive: Rejected - too limiting

### 9. Error Reporting
**Decision**: Create operation log file with summary at end
**Rationale**:
- Persistent record of operations
- User can review what happened
- Useful for troubleshooting
**Alternatives considered**:
- Console only: Rejected - lost after closing
- Email report: Rejected - unnecessary complexity

### 10. Batch Processing
**Decision**: Single folder with option to provide multiple via config file
**Rationale**:
- Simple default usage
- Power users can batch via config
- Clear separation of concerns
**Alternatives considered**:
- Always batch: Rejected - complex for simple use case
- GUI folder picker: Rejected - adds GUI dependency

### 11. File Naming Conflicts
**Decision**: Append counter before extension (photo.jpg → photo_1.jpg)
**Rationale**:
- Preserves file extension
- Clear pattern
- Sortable names
**Alternatives considered**:
- Timestamp suffix: Rejected - long filenames
- Random suffix: Rejected - not user-friendly

## Technology Choices

### CLI Framework: Click
**Decision**: Use Click for command-line interface
**Rationale**:
- Excellent documentation and community
- Built-in help generation
- Easy to create user-friendly CLIs
- Supports configuration files
**Best Practices**:
- Use command groups for organization
- Provide sensible defaults
- Include --dry-run option
- Use progress bars from click

### File Metadata: Pillow + OS Stats
**Decision**: Pillow for EXIF data, fall back to OS file stats
**Rationale**:
- Pillow reads EXIF data from images
- OS stats work for all file types
- Two-tier approach ensures coverage
**Best Practices**:
- Try EXIF first for images
- Cache metadata to avoid re-reading
- Handle timezone properly

### Configuration: YAML
**Decision**: YAML configuration file with CLI overrides
**Rationale**:
- Human-readable and editable
- Supports comments for documentation
- Common format users understand
**Best Practices**:
- Provide example config
- Validate on load
- CLI args override config values

### Distribution: PyInstaller
**Decision**: Create standalone executables with PyInstaller
**Rationale**:
- No Python installation required for users
- Single file distribution
- Cross-platform support
**Best Practices**:
- Test on target platforms
- Include version info
- Sign executables if possible

### Testing: Pytest with Fixtures
**Decision**: Pytest with temporary directory fixtures
**Rationale**:
- Powerful fixture system for file operations
- Good assertion messages
- Parallel test execution
**Best Practices**:
- Use tmp_path fixture
- Create realistic test files
- Test error conditions

## User Experience Decisions

### First Run Experience
1. Interactive setup wizard if no config exists
2. Ask for common preferences (file types, date format)
3. Save config for future runs
4. Offer --quick mode to skip setup

### Safety Features
1. Dry run by default on first use
2. Confirmation prompt for large operations (>1000 files)
3. Verification of each file move
4. Automatic backup of file list before operations

### Error Recovery
1. Resume capability after interruption
2. Undo log for reverting operations
3. Clear error messages with suggested fixes
4. Non-zero exit codes for scripting

### Performance Optimizations
1. Parallel processing for scanning (not moving)
2. Batch folder creation
3. Progress estimation based on file count
4. Memory-efficient streaming for large folders

## Implementation Notes

### File Safety Protocol
1. Copy file to destination
2. Verify copy (size and checksum)
3. Only then delete source
4. Log each operation
5. Rollback on failure

### Date Extraction Priority
1. EXIF DateTimeOriginal (photos)
2. Media metadata creation date (videos)
3. File system creation date
4. File system modification date
5. Skip if no date available

### Folder Naming
- Format: MM.YYYY (e.g., "03.2024")
- Leading zero for months < 10
- Full 4-digit year
- Period separator (not slash or dash)

### Supported Media Types
**Images**: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .raw, .heic, .webp
**Videos**: .mp4, .avi, .mov, .wmv, .mkv, .flv, .webm, .m4v, .mpg
**Raw Photos**: .arw, .cr2, .nef, .orf, .rw2, .dng

---

*Research completed: All NEEDS CLARIFICATION items resolved with practical decisions*