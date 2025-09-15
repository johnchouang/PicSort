"""MediaFile model for representing media files to be organized."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import os


@dataclass
class MediaFile:
    """Represents a single media file to be processed."""

    path: str
    filename: str
    size: int
    creation_date: Optional[datetime]
    modification_date: datetime
    file_type: str
    is_media: bool
    metadata_source: str
    error: Optional[str] = None
    exif_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate fields after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all fields according to specification rules."""
        # path must exist and be readable
        if not os.path.exists(self.path):
            raise ValueError(f"Path does not exist: {self.path}")
        
        if not os.access(self.path, os.R_OK):
            raise ValueError(f"Path is not readable: {self.path}")
        
        # size must be > 0
        if self.size <= 0:
            raise ValueError(f"Size must be > 0, got: {self.size}")
        
        # file_type must be non-empty string
        if not isinstance(self.file_type, str) or not self.file_type.strip():
            raise ValueError("file_type must be non-empty string")
        
        # creation_date validation handled by Optional[datetime] typing
    
    def get_oldest_date(self) -> datetime:
        """Returns the oldest date among all available dates.

        Checks EXIF date, creation date, and modification date to find the oldest.
        Falls back to modification date if no other dates are available.
        """
        available_dates = []

        if self.exif_date is not None:
            available_dates.append(self.exif_date)
        if self.creation_date is not None:
            available_dates.append(self.creation_date)

        # Always have modification date as fallback
        available_dates.append(self.modification_date)

        return min(available_dates)

    def get_target_folder(self) -> str:
        """Returns MM.YYYY folder name based on oldest available date.

        Uses the oldest date among EXIF date, creation date, and modification date.
        """
        date_to_use = self.get_oldest_date()
        return f"{date_to_use.month:02d}.{date_to_use.year}"
    
    def is_image(self) -> bool:
        """Check if file is image type."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
        return self.file_type.lower() in image_extensions
    
    def is_video(self) -> bool:
        """Check if file is video type."""
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        return self.file_type.lower() in video_extensions
    
    def should_process(self) -> bool:
        """Whether file should be organized.
        
        Returns True if file is media type and has no errors.
        """
        return self.is_media and self.error is None
