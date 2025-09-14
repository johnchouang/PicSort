"""Configuration model for user preferences and settings."""
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import yaml
import os
from pathlib import Path


@dataclass
class Configuration:
    """User configuration and preferences."""
    
    version: str
    default_source: Optional[str]
    file_types: List[str]
    process_all_files: bool
    date_format: str
    recursive: bool
    dry_run_default: bool
    create_log: bool
    log_path: str
    verify_checksum: bool
    batch_size: int
    parallel_scan: bool
    confirm_large_operations: bool
    duplicate_handling: str
    
    # Current schema version
    CURRENT_VERSION = "1.0.0"
    
    # Valid duplicate handling options
    VALID_DUPLICATE_HANDLING = {'increment', 'skip', 'overwrite'}
    
    # Default configuration
    DEFAULT_CONFIG = {
        'version': CURRENT_VERSION,
        'default_source': None,
        'file_types': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
                       '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'],
        'process_all_files': False,
        'date_format': 'MM.YYYY',
        'recursive': False,
        'dry_run_default': True,
        'create_log': True,
        'log_path': '~/.picsort/logs',
        'verify_checksum': True,
        'batch_size': 100,
        'parallel_scan': True,
        'confirm_large_operations': True,
        'duplicate_handling': 'increment'
    }
    
    def __post_init__(self):
        """Validate fields after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all fields according to specification rules."""
        # version must match current schema version
        if self.version != self.CURRENT_VERSION:
            raise ValueError(f"Invalid version: {self.version}. Expected: {self.CURRENT_VERSION}")
        
        # file_types must be non-empty list
        if not isinstance(self.file_types, list) or len(self.file_types) == 0:
            raise ValueError("file_types must be non-empty list")
        
        # date_format must contain MM and YYYY placeholders
        if 'MM' not in self.date_format or 'YYYY' not in self.date_format:
            raise ValueError(f"date_format must contain MM and YYYY placeholders: {self.date_format}")
        
        # batch_size must be > 0
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be > 0, got: {self.batch_size}")
        
        # duplicate_handling must be valid enum
        if self.duplicate_handling not in self.VALID_DUPLICATE_HANDLING:
            raise ValueError(f"Invalid duplicate_handling: {self.duplicate_handling}. Must be one of {self.VALID_DUPLICATE_HANDLING}")
    
    @classmethod
    def load_from_file(cls, path: str) -> 'Configuration':
        """Load configuration from YAML file.
        
        Args:
            path: Path to YAML configuration file
        
        Returns:
            Configuration instance loaded from file
        
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If file is invalid YAML
            ValueError: If configuration is invalid
        """
        config_path = Path(path).expanduser()
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        if not isinstance(config_data, dict):
            raise ValueError("Configuration file must contain a YAML object")
        
        # Merge with defaults
        merged_config = cls.DEFAULT_CONFIG.copy()

        # Handle legacy field names
        legacy_mappings = {
            'dry_run': 'dry_run_default',
            'verify': 'verify_checksum',
        }

        # Apply legacy mappings
        for legacy_key, new_key in legacy_mappings.items():
            if legacy_key in config_data:
                config_data[new_key] = config_data.pop(legacy_key)

        merged_config.update(config_data)
        
        return cls(**merged_config)
    
    def save_to_file(self, path: str) -> None:
        """Save configuration to YAML file.
        
        Args:
            path: Path where to save configuration file
        
        Raises:
            OSError: If file cannot be written
        """
        config_path = Path(path).expanduser()
        
        # Create parent directories if they don't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary and save
        config_dict = asdict(self)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=True)
    
    def merge_with_args(self, args: Dict[str, Any]) -> 'Configuration':
        """Create new configuration with CLI args overriding config values.
        
        Args:
            args: Dictionary of CLI arguments to override config
        
        Returns:
            New Configuration instance with overridden values
        """
        config_dict = asdict(self)
        
        # Map CLI argument names to config field names
        arg_mapping = {
            'date_format': 'date_format',
            'file_types': 'file_types',
            'recursive': 'recursive',
            'dry_run': 'dry_run_default',
            'verify': 'verify_checksum',
            'batch_size': 'batch_size',
            'parallel': 'parallel_scan',
            'confirm_large': 'confirm_large_operations',
            'duplicate_handling': 'duplicate_handling'
        }
        
        # Apply overrides
        for arg_name, config_field in arg_mapping.items():
            if arg_name in args and args[arg_name] is not None:
                config_dict[config_field] = args[arg_name]
        
        return Configuration(**config_dict)
    
    @classmethod
    def create_default(cls) -> 'Configuration':
        """Create configuration with default values.
        
        Returns:
            Configuration instance with default values
        """
        return cls(**cls.DEFAULT_CONFIG)
    
    def get_default_config_path(self) -> Path:
        """Get the default configuration file path.
        
        Returns:
            Path to default config file (~/.picsort/config.yaml)
        """
        return Path.home() / '.picsort' / 'config.yaml'
