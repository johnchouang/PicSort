"""Configuration manager for PicSort."""
from pathlib import Path
import yaml
try:
    from src.models.configuration import Configuration
except ImportError:
    from models.configuration import Configuration


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_path=None):
        """Initialize config manager."""
        self.config_path = config_path or Path.home() / '.picsort' / 'config.yaml'
        self.config = {}

    @property
    def default_config_path(self):
        """Get the default configuration path."""
        return Path.home() / '.picsort' / 'config.yaml'

    def load(self):
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        return self.config

    def save(self):
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)

    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value."""
        self.config[key] = value

    def init_default(self):
        """Initialize with default configuration."""
        self.config = {
            'version': '1.0.0',
            'default_source': '',
            'file_types': ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'],
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
            'duplicate_handling': 'increment',
            'verbose': False
        }
        return self.config

    def load_config(self, config_path=None):
        """Load configuration from file or use defaults."""
        if config_path:
            self.config_path = Path(config_path)

        if self.config_path.exists():
            self.load()
        else:
            self.init_default()

        # Return a Configuration dataclass with the loaded data
        return Configuration(**self.config)

    def merge_with_cli_args(self, base_config, cli_args):
        """Merge CLI arguments with base configuration."""
        from dataclasses import asdict
        # Convert Configuration object to dict, then merge CLI args
        merged = asdict(base_config)
        merged.update(cli_args)
        # Return a new Configuration object with merged data
        return Configuration(**merged)

    def backup_config(self, config_path):
        """Create backup of configuration file."""
        config_path = Path(config_path)
        if config_path.exists():
            backup_path = config_path.with_suffix('.yaml.backup')
            import shutil
            shutil.copy(config_path, backup_path)
            return backup_path
        return None

    def validate_config_file(self, config_path):
        """Validate configuration file."""
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                return {
                    'valid': False,
                    'error': 'File does not exist',
                    'warnings': [],
                    'config': None
                }

            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            return {
                'valid': True,
                'warnings': [],
                'config': config_data
            }
        except yaml.YAMLError as e:
            return {
                'valid': False,
                'error': f'YAML error: {e}',
                'warnings': [],
                'config': None
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error: {e}',
                'warnings': [],
                'config': None
            }

    def create_default_config(self, config_path):
        """Create default configuration at specified path."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        self.init_default()
        with open(config_path, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)

        return Configuration(**self.config)

    def list_available_configs(self):
        """List available configuration files."""
        configs = []
        default_path = self.default_config_path

        if default_path.exists():
            configs.append({
                'name': 'default',
                'path': str(default_path)
            })

        return configs

    def get_config_info(self, config):
        """Get configuration information for validation output."""
        file_types = config.get('file_types', [])
        image_types = [ft for ft in file_types if ft.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']]
        video_types = [ft for ft in file_types if ft.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v']]
        other_types = [ft for ft in file_types if ft not in image_types and ft not in video_types]
        
        processing_mode = "Media files only"
        if config.get('process_all_files'):
            processing_mode = "All files"
        
        return {
            'processing_mode': processing_mode,
            'file_types_count': len(file_types),
            'image_types_count': len(image_types),
            'video_types_count': len(video_types),
            'other_types_count': len(other_types)
        }

    def save_config(self, configuration, config_path):
        """Save configuration object to file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert dataclass to dict
        config_data = {
            'version': configuration.version,
            'default_source': configuration.default_source,
            'file_types': configuration.file_types,
            'process_all_files': configuration.process_all_files,
            'date_format': configuration.date_format,
            'recursive': configuration.recursive,
            'dry_run_default': configuration.dry_run_default,
            'create_log': configuration.create_log,
            'log_path': configuration.log_path,
            'verify_checksum': configuration.verify_checksum,
            'batch_size': configuration.batch_size,
            'parallel_scan': configuration.parallel_scan,
            'confirm_large_operations': configuration.confirm_large_operations,
            'duplicate_handling': configuration.duplicate_handling
        }
        
        with open(config_path, 'w') as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)
