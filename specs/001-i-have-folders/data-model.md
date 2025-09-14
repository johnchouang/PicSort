# Data Model: Media File Organization

## Core Entities

### MediaFile
Represents a single media file to be processed.

**Fields**:
- `path` (str): Absolute path to the file
- `filename` (str): Original filename
- `size` (int): File size in bytes
- `creation_date` (datetime): Creation date extracted from metadata or filesystem
- `modification_date` (datetime): Last modified date
- `file_type` (str): File extension/type (e.g., 'jpg', 'mp4')
- `is_media` (bool): Whether file is recognized media type
- `metadata_source` (str): Source of date ('exif', 'filesystem', 'modification')
- `error` (str, optional): Error message if file couldn't be processed

**Validation Rules**:
- `path` must exist and be readable
- `size` must be > 0
- `creation_date` must be valid datetime or None
- `file_type` must be non-empty string

**Methods**:
- `get_target_folder()` → str: Returns "MM.YYYY" folder name
- `is_image()` → bool: Check if file is image type
- `is_video()` → bool: Check if file is video type
- `should_process()` → bool: Whether file should be organized

### FolderOperation
Represents a folder being processed.

**Fields**:
- `source_path` (str): Path to folder being organized
- `total_files` (int): Total number of files found
- `media_files` (int): Number of media files to process
- `processed_files` (int): Files successfully moved
- `skipped_files` (int): Files skipped (errors, locked, etc.)
- `start_time` (datetime): When operation started
- `end_time` (datetime, optional): When operation completed
- `dry_run` (bool): Whether this is a dry run

**Validation Rules**:
- `source_path` must exist and be a directory
- `total_files` >= 0
- `processed_files` <= `media_files`
- `end_time` must be after `start_time` if set

**Methods**:
- `duration()` → timedelta: Time taken for operation
- `success_rate()` → float: Percentage of successfully processed files
- `is_complete()` → bool: Whether operation finished

### FileOperation
Represents a single file move operation.

**Fields**:
- `source_file` (MediaFile): File being moved
- `destination_path` (str): Target path for file
- `status` (str): 'pending', 'copying', 'verifying', 'completed', 'failed', 'skipped'
- `error_message` (str, optional): Error details if failed
- `checksum_source` (str, optional): Source file checksum
- `checksum_dest` (str, optional): Destination file checksum
- `operation_time` (datetime): When operation occurred
- `duration_ms` (int): Time taken in milliseconds

**Validation Rules**:
- `destination_path` must be valid path format
- `status` must be valid enum value
- `checksum_source` == `checksum_dest` when status is 'completed'
- `error_message` required when status is 'failed'

**State Transitions**:
```
pending → copying → verifying → completed
          ↓          ↓
        failed     failed
          
pending → skipped (for locked/corrupted files)
```

### Configuration
User configuration and preferences.

**Fields**:
- `version` (str): Config version for migration
- `default_source` (str, optional): Default folder to organize
- `file_types` (list[str]): Extensions to process
- `process_all_files` (bool): Whether to process non-media files
- `date_format` (str): Folder naming format (default "MM.YYYY")
- `recursive` (bool): Process nested folders
- `dry_run_default` (bool): Default to dry run mode
- `create_log` (bool): Whether to create operation logs
- `log_path` (str): Where to save logs
- `verify_checksum` (bool): Whether to verify file integrity
- `batch_size` (int): Files to process before updating progress
- `parallel_scan` (bool): Use parallel scanning
- `confirm_large_operations` (bool): Prompt for >1000 files
- `duplicate_handling` (str): 'increment', 'skip', 'overwrite'

**Validation Rules**:
- `version` must match current schema version
- `file_types` must be non-empty list
- `date_format` must contain MM and YYYY placeholders
- `batch_size` must be > 0
- `duplicate_handling` must be valid enum

**Methods**:
- `load_from_file(path)` → Configuration
- `save_to_file(path)` → None
- `merge_with_args(args)` → Configuration: CLI args override config

### OperationLog
Log entry for tracking operations.

**Fields**:
- `timestamp` (datetime): When entry was logged
- `level` (str): 'INFO', 'WARNING', 'ERROR'
- `operation_id` (str): Unique ID for this run
- `message` (str): Log message
- `file_path` (str, optional): Related file path
- `error_type` (str, optional): Type of error if applicable
- `context` (dict): Additional context data

**Validation Rules**:
- `level` must be valid log level
- `operation_id` must be non-empty
- `message` must be non-empty

## Relationships

```
FolderOperation
    ↓ contains many
FileOperation
    ↓ references
MediaFile

Configuration
    ↓ governs
FolderOperation

OperationLog
    ↓ tracks
FileOperation
```

## Data Flow

1. **Scan Phase**:
   - Create `FolderOperation` for source folder
   - Scan and create `MediaFile` instances for each file
   - Filter based on `Configuration` settings

2. **Organization Phase**:
   - For each `MediaFile`, create `FileOperation`
   - Determine destination based on creation date
   - Execute move operation with verification

3. **Logging Phase**:
   - Create `OperationLog` entries for each significant event
   - Track failures and successes
   - Generate summary report

## Persistence

### Configuration File (config.yaml)
```yaml
version: "1.0.0"
default_source: "/Users/photos"
file_types: [".jpg", ".jpeg", ".png", ".mp4", ".mov"]
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

### Operation Log (JSON Lines)
```json
{"timestamp": "2024-01-15T10:30:00Z", "level": "INFO", "operation_id": "op_123", "message": "Started organizing /Users/photos"}
{"timestamp": "2024-01-15T10:30:01Z", "level": "INFO", "operation_id": "op_123", "message": "Found 1523 media files", "context": {"total": 2000, "media": 1523}}
{"timestamp": "2024-01-15T10:30:05Z", "level": "ERROR", "operation_id": "op_123", "message": "Failed to move file", "file_path": "/Users/photos/IMG_001.jpg", "error_type": "PermissionError"}
```

### Resume State (resume.json)
For resuming interrupted operations:
```json
{
  "operation_id": "op_123",
  "source_path": "/Users/photos",
  "processed_files": ["IMG_001.jpg", "IMG_002.jpg"],
  "pending_files": ["IMG_003.jpg", "IMG_004.jpg"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Constraints

1. **Memory Efficiency**: 
   - Stream files rather than loading all into memory
   - Process in batches of `batch_size`
   - Lazy load metadata only when needed

2. **Concurrency**:
   - Scanning can be parallel (read-only)
   - Moving must be sequential (file safety)
   - Logging must be thread-safe

3. **Error Handling**:
   - Never leave files in inconsistent state
   - Always log errors with context
   - Provide recovery mechanisms

4. **Performance Targets**:
   - Scan: 10,000 files/minute
   - Process: 1,000 files/minute
   - Memory: < 100MB for 100,000 files