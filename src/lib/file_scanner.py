"""File scanner for PicSort."""
from pathlib import Path
from datetime import datetime
import os
try:
    from src.models.media_file import MediaFile
    from src.lib.exif_reader import ExifReader
except ImportError:
    from models.media_file import MediaFile
    from lib.exif_reader import ExifReader


class FileScanner:
    """Scans directories for media files."""

    def __init__(self, config=None):
        """Initialize file scanner."""
        self.config = config or {}
        # Handle both dict and Configuration objects
        if hasattr(config, 'file_types'):
            self.file_types = config.file_types
            self.recursive = config.recursive
        else:
            self.file_types = self.config.get('file_types', ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'])
            self.recursive = self.config.get('recursive', False)

        # Initialize EXIF reader for image metadata extraction
        self.exif_reader = ExifReader()

    def scan_directory(self, path):
        """Scan directory for media files and return MediaFile objects."""
        return self.scan(path, self.recursive)

    def scan(self, path, recursive=None):
        """Scan directory for media files."""
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        if recursive is None:
            recursive = self.recursive

        files = []
        if recursive:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    media_file = self._create_media_file(file_path)
                    if media_file:
                        files.append(media_file)
        else:
            for file_path in path.iterdir():
                if file_path.is_file():
                    media_file = self._create_media_file(file_path)
                    if media_file:
                        files.append(media_file)

        return files

    def _create_media_file(self, file_path):
        """Create a MediaFile object from a file path."""
        try:
            stat = file_path.stat()
            file_ext = file_path.suffix.lower()
            is_media = file_ext in self.file_types

            # Try to get creation date from different sources
            creation_date = None
            exif_date = None
            metadata_source = "filesystem"

            try:
                # On Windows, st_ctime is creation time
                # On Unix, we'll need to check EXIF for images
                if os.name == 'nt':
                    creation_date = datetime.fromtimestamp(stat.st_ctime)
                else:
                    # For now, use modification time as fallback
                    creation_date = datetime.fromtimestamp(stat.st_mtime)
            except:
                creation_date = None

            # Try to extract EXIF date for images
            if is_media and self.exif_reader.can_extract_metadata(str(file_path)):
                try:
                    exif_date = self.exif_reader.extract_creation_date(file_path)
                    if exif_date:
                        metadata_source = "exif"
                except Exception:
                    # EXIF extraction failed, continue with filesystem dates
                    pass

            return MediaFile(
                path=str(file_path),
                filename=file_path.name,
                size=stat.st_size,
                creation_date=creation_date,
                modification_date=datetime.fromtimestamp(stat.st_mtime),
                file_type=file_ext,
                is_media=is_media,
                metadata_source=metadata_source,
                error=None,
                exif_date=exif_date
            )
        except Exception as e:
            # Return MediaFile with error for problematic files
            try:
                return MediaFile(
                    path=str(file_path),
                    filename=file_path.name,
                    size=1,  # Default size to avoid validation error
                    creation_date=None,
                    modification_date=datetime.now(),
                    file_type=file_path.suffix.lower() if file_path.suffix else '',
                    is_media=False,
                    metadata_source="error",
                    error=str(e),
                    exif_date=None
                )
            except:
                # If we can't even create an error MediaFile, skip this file
                return None

    def _get_file_info(self, file_path):
        """Get file information (legacy method for compatibility)."""
        stat = file_path.stat()
        return {
            'path': file_path,
            'name': file_path.name,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime)
        }