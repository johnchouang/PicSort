"""Configuration manager for PicSort."""
from pathlib import Path
import yaml


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_path=None):
        """Initialize config manager."""
        self.config_path = config_path or Path.home() / '.picsort' / 'config.yaml'
        self.config = {}

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
            'dry_run': True,
            'file_types': ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'],
            'date_format': 'MM.YYYY',
            'recursive': False,
            'verbose': False
        }
        return self.config

    def load_config(self, config_path=None):
        """Load configuration from file or use defaults."""
        if config_path:
            self.config_path = Path(config_path)

        if self.config_path.exists():
            return self.load()
        else:
            return self.init_default()

    def merge_with_cli_args(self, base_config, cli_args):
        """Merge CLI arguments with base configuration."""
        merged = base_config.copy()
        merged.update(cli_args)
        return merged