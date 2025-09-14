"""FolderOperation model for representing folder processing operations."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import os


@dataclass
class FolderOperation:
    """Represents a folder being processed."""
    
    source_path: str
    total_files: int
    media_files: int
    processed_files: int
    skipped_files: int
    start_time: datetime
    end_time: Optional[datetime]
    dry_run: bool
    
    def __post_init__(self):
        """Validate fields after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all fields according to specification rules."""
        # source_path must exist and be a directory
        if not os.path.exists(self.source_path):
            raise ValueError(f"Source path does not exist: {self.source_path}")
        
        if not os.path.isdir(self.source_path):
            raise ValueError(f"Source path is not a directory: {self.source_path}")
        
        # total_files >= 0
        if self.total_files < 0:
            raise ValueError(f"total_files must be >= 0, got: {self.total_files}")
        
        # processed_files <= media_files
        if self.processed_files > self.media_files:
            raise ValueError(f"processed_files ({self.processed_files}) cannot exceed media_files ({self.media_files})")
        
        # end_time must be after start_time if set
        if self.end_time and self.end_time <= self.start_time:
            raise ValueError(f"end_time ({self.end_time}) must be after start_time ({self.start_time})")
    
    def duration(self) -> timedelta:
        """Time taken for operation.
        
        If operation is not complete, returns time elapsed so far.
        """
        end_time = self.end_time if self.end_time else datetime.now()
        return end_time - self.start_time
    
    def success_rate(self) -> float:
        """Percentage of successfully processed files.
        
        Returns 0.0 if no media files to process.
        """
        if self.media_files == 0:
            return 0.0
        return (self.processed_files / self.media_files) * 100.0
    
    def is_complete(self) -> bool:
        """Whether operation finished."""
        return self.end_time is not None
