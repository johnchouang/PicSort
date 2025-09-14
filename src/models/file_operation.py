"""FileOperation model for representing individual file move operations."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pathlib import Path

from .media_file import MediaFile


@dataclass
class FileOperation:
    """Represents a single file move operation."""
    
    source_file: MediaFile
    destination_path: str
    status: str
    error_message: Optional[str]
    checksum_source: Optional[str]
    checksum_dest: Optional[str]
    operation_time: datetime
    duration_ms: int
    
    # Valid status values
    VALID_STATUSES = {'pending', 'copying', 'verifying', 'completed', 'failed', 'skipped'}
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        'pending': {'copying', 'skipped', 'failed'},
        'copying': {'verifying', 'failed'},
        'verifying': {'completed', 'failed'},
        'completed': set(),  # Terminal state
        'failed': set(),     # Terminal state
        'skipped': set()     # Terminal state
    }
    
    def __post_init__(self):
        """Validate fields after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all fields according to specification rules."""
        # destination_path must be valid path format
        try:
            Path(self.destination_path)
        except Exception as e:
            raise ValueError(f"Invalid destination path format: {self.destination_path}") from e
        
        # status must be valid enum value
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {self.VALID_STATUSES}")
        
        # checksum_source == checksum_dest when status is 'completed'
        if self.status == 'completed':
            if not self.checksum_source or not self.checksum_dest:
                raise ValueError("Both checksums required when status is 'completed'")
            if self.checksum_source != self.checksum_dest:
                raise ValueError("Checksums must match when status is 'completed'")
        
        # error_message required when status is 'failed'
        if self.status == 'failed' and not self.error_message:
            raise ValueError("error_message required when status is 'failed'")
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition to new status is valid."""
        if new_status not in self.VALID_STATUSES:
            return False
        return new_status in self.VALID_TRANSITIONS.get(self.status, set())
    
    def transition_to(self, new_status: str, error_message: Optional[str] = None) -> None:
        """Transition to new status with validation.
        
        Args:
            new_status: The status to transition to
            error_message: Error message if transitioning to 'failed'
        
        Raises:
            ValueError: If transition is invalid
        """
        if not self.can_transition_to(new_status):
            raise ValueError(f"Invalid transition from '{self.status}' to '{new_status}'")
        
        self.status = new_status
        if new_status == 'failed' and error_message:
            self.error_message = error_message
        
        # Validate after transition
        self._validate()
    
    def is_terminal(self) -> bool:
        """Check if operation is in a terminal state."""
        return self.status in {'completed', 'failed', 'skipped'}
    
    def is_successful(self) -> bool:
        """Check if operation completed successfully."""
        return self.status == 'completed'
