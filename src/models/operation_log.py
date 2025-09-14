"""OperationLog model for tracking operation events."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class OperationLog:
    """Log entry for tracking operations."""
    
    timestamp: datetime
    level: str
    operation_id: str
    message: str
    file_path: Optional[str]
    error_type: Optional[str]
    context: Dict[str, Any]
    
    # Valid log levels
    VALID_LEVELS = {'INFO', 'WARNING', 'ERROR', 'DEBUG'}
    
    def __post_init__(self):
        """Validate fields after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all fields according to specification rules."""
        # level must be valid log level
        if self.level not in self.VALID_LEVELS:
            raise ValueError(f"Invalid level: {self.level}. Must be one of {self.VALID_LEVELS}")
        
        # operation_id must be non-empty
        if not isinstance(self.operation_id, str) or not self.operation_id.strip():
            raise ValueError("operation_id must be non-empty string")
        
        # message must be non-empty
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be non-empty string")
    
    def to_json_line(self) -> str:
        """Convert log entry to JSON line format for storage.
        
        Returns:
            JSON string representation of the log entry
        """
        log_dict = asdict(self)
        
        # Convert datetime to ISO format string
        log_dict['timestamp'] = self.timestamp.isoformat()
        
        return json.dumps(log_dict, separators=(',', ':'))
    
    @classmethod
    def from_json_line(cls, json_line: str) -> 'OperationLog':
        """Create OperationLog from JSON line.
        
        Args:
            json_line: JSON string representation of log entry
        
        Returns:
            OperationLog instance
        
        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If data is invalid
        """
        log_dict = json.loads(json_line)
        
        # Convert timestamp string back to datetime
        if 'timestamp' in log_dict:
            log_dict['timestamp'] = datetime.fromisoformat(log_dict['timestamp'])
        
        # Ensure context is present
        if 'context' not in log_dict:
            log_dict['context'] = {}
        
        return cls(**log_dict)
    
    @classmethod
    def create_info(cls, operation_id: str, message: str, 
                   file_path: Optional[str] = None, 
                   context: Optional[Dict[str, Any]] = None) -> 'OperationLog':
        """Create INFO level log entry.
        
        Args:
            operation_id: Unique operation identifier
            message: Log message
            file_path: Optional file path related to the log
            context: Optional additional context data
        
        Returns:
            OperationLog instance with INFO level
        """
        return cls(
            timestamp=datetime.now(),
            level='INFO',
            operation_id=operation_id,
            message=message,
            file_path=file_path,
            error_type=None,
            context=context or {}
        )
    
    @classmethod
    def create_warning(cls, operation_id: str, message: str, 
                      file_path: Optional[str] = None, 
                      context: Optional[Dict[str, Any]] = None) -> 'OperationLog':
        """Create WARNING level log entry.
        
        Args:
            operation_id: Unique operation identifier
            message: Log message
            file_path: Optional file path related to the log
            context: Optional additional context data
        
        Returns:
            OperationLog instance with WARNING level
        """
        return cls(
            timestamp=datetime.now(),
            level='WARNING',
            operation_id=operation_id,
            message=message,
            file_path=file_path,
            error_type=None,
            context=context or {}
        )
    
    @classmethod
    def create_error(cls, operation_id: str, message: str, 
                    error_type: Optional[str] = None,
                    file_path: Optional[str] = None, 
                    context: Optional[Dict[str, Any]] = None) -> 'OperationLog':
        """Create ERROR level log entry.
        
        Args:
            operation_id: Unique operation identifier
            message: Log message
            error_type: Type of error that occurred
            file_path: Optional file path related to the log
            context: Optional additional context data
        
        Returns:
            OperationLog instance with ERROR level
        """
        return cls(
            timestamp=datetime.now(),
            level='ERROR',
            operation_id=operation_id,
            message=message,
            file_path=file_path,
            error_type=error_type,
            context=context or {}
        )
    
    def is_error(self) -> bool:
        """Check if this is an error log entry.
        
        Returns:
            True if level is ERROR
        """
        return self.level == 'ERROR'
    
    def is_warning(self) -> bool:
        """Check if this is a warning log entry.
        
        Returns:
            True if level is WARNING
        """
        return self.level == 'WARNING'
    
    def is_info(self) -> bool:
        """Check if this is an info log entry.
        
        Returns:
            True if level is INFO
        """
        return self.level == 'INFO'
