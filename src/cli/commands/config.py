"""Config command for managing user configuration."""
import json
import logging
from pathlib import Path

import click

from ...lib.config_manager import ConfigManager
from ...models.configuration import Configuration

logger = logging.getLogger(__name__)


@click.group()
def config():
    """Manage PicSort configuration.
    
    Configuration files are stored in YAML format at ~/.picsort/config.yaml
    by default. You can also specify custom config files using --config option
    with other commands.
    """
    pass


@config.command()
@click.option('--config-path', '-c', type=click.Path(), help='Configuration file path')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def show(ctx, config_path, output_json):
    """Show current configuration settings.
    
    Examples:
      picsort config show
      picsort config show --json
      picsort config show --config /path/to/config.yaml
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)
    
    try:
        config_manager = ConfigManager()
        user_config = config_manager.load_config(config_path)
        
        if output_json:
            # Output as JSON
            config_dict = {
                'version': user_config.version,
                'default_source': user_config.default_source,
                'file_types': user_config.file_types,
                'process_all_files': user_config.process_all_files,
                'date_format': user_config.date_format,
                'recursive': user_config.recursive,
                'dry_run_default': user_config.dry_run_default,
                'create_log': user_config.create_log,
                'log_path': user_config.log_path,
                'verify_checksum': user_config.verify_checksum,
                'batch_size': user_config.batch_size,
                'parallel_scan': user_config.parallel_scan,
                'confirm_large_operations': user_config.confirm_large_operations,
                'duplicate_handling': user_config.duplicate_handling
            }
            print(json.dumps(config_dict, indent=2))
        else:
            # Output as human-readable format
            if not quiet:
                print("PicSort Configuration:")
                print(f"  Version: {user_config.version}")
                print(f"  Date format: {user_config.date_format}")
                print(f"  File types: {', '.join(user_config.file_types)}")
                print(f"  Process all files: {user_config.process_all_files}")
                print(f"  Recursive: {user_config.recursive}")
                print(f"  Dry run by default: {user_config.dry_run_default}")
                print(f"  Verify checksums: {user_config.verify_checksum}")
                print(f"  Duplicate handling: {user_config.duplicate_handling}")
                print(f"  Create logs: {user_config.create_log}")
                print(f"  Log path: {user_config.log_path}")
                print(f"  Batch size: {user_config.batch_size}")
                print(f"  Parallel scan: {user_config.parallel_scan}")
                print(f"  Confirm large operations: {user_config.confirm_large_operations}")
                
                if user_config.default_source:
                    print(f"  Default source: {user_config.default_source}")
        
        return 0
        
    except Exception as e:
        if not quiet:
            print(f"Error showing configuration: {e}")
        logger.error(f"Config show failed: {e}", exc_info=verbose)
        return 1


@config.command()
@click.option('--config-path', '-c', type=click.Path(), help='Configuration file path')
@click.option('--backup', is_flag=True, help='Create backup of existing config')
@click.pass_context
def init(ctx, config_path, backup):
    """Initialize configuration with default settings.
    
    Creates a new configuration file with default values. If a configuration
    file already exists, it will be backed up if --backup is specified.
    
    Examples:
      picsort config init
      picsort config init --backup
      picsort config init --config /path/to/config.yaml
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)
    
    try:
        config_manager = ConfigManager()
        
        # Determine config path
        target_path = config_path or str(config_manager.default_config_path)
        target_path_obj = Path(target_path)
        
        # Check if config already exists
        if target_path_obj.exists():
            if backup:
                backup_path = config_manager.backup_config(target_path)
                if not quiet:
                    print(f"Existing configuration backed up to: {backup_path}")
                # Continue with creation after backup
            else:
                if not quiet:
                    print(f"Configuration file already exists: {target_path}")
                    print("Use --backup to create a backup, or specify a different path.")
                return 1
        
        # Create default configuration
        default_config = config_manager.create_default_config(target_path)

        if not quiet:
            print(f"Configuration created at: {target_path}")
            print("\nYou can now customize the configuration by editing the file or using")
            print("command-line options with the organize command.")
        
        return 0
        
    except Exception as e:
        if not quiet:
            print(f"Error initializing configuration: {e}")
        logger.error(f"Config init failed: {e}", exc_info=verbose)
        return 1


@config.command()
@click.option('--config-path', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def validate(ctx, config_path):
    """Validate configuration file.
    
    Checks configuration file for syntax errors and invalid values.
    Also reports warnings for potentially problematic settings.
    
    Examples:
      picsort config validate
      picsort config validate --config /path/to/config.yaml
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)
    
    try:
        config_manager = ConfigManager()
        
        # Determine config path
        target_path = config_path or str(config_manager.default_config_path)
        
        if not Path(target_path).exists():
            if not quiet:
                print(f"Configuration file not found: {target_path}")
            return 1
        
        # Validate configuration
        validation_result = config_manager.validate_config_file(target_path)
        
        if not quiet:
            print(f"Validating configuration: {target_path}")
            
            if validation_result['valid']:
                print("✓ Configuration is valid")
                
                if validation_result['warnings']:
                    print("\nWarnings:")
                    for warning in validation_result['warnings']:
                        print(f"  ⚠️  {warning}")
                
                if verbose and validation_result['config']:
                    config_info = config_manager.get_config_info(validation_result['config'])
                    print(f"\nConfiguration details:")
                    print(f"  Processing mode: {config_info['processing_mode']}")
                    print(f"  File types: {config_info['file_types_count']} total")
                    print(f"    - Images: {config_info['image_types_count']}")
                    print(f"    - Videos: {config_info['video_types_count']}")
                    print(f"    - Others: {config_info['other_types_count']}")
            else:
                print("❌ Configuration is invalid")
                print("\nErrors:")
                for error in validation_result['errors']:
                    print(f"  ❌ {error}")
                return 1
        
        return 0
        
    except Exception as e:
        if not quiet:
            print(f"Error validating configuration: {e}")
        logger.error(f"Config validate failed: {e}", exc_info=verbose)
        return 1


@config.command()
@click.argument('key')
@click.argument('value')
@click.option('--config-path', '-c', type=click.Path(), help='Configuration file path')
@click.pass_context
def set(ctx, key, value, config_path):
    """Set configuration value.

    Sets a specific configuration key to the provided value.
    If the configuration file doesn't exist, it will be created.

    Examples:
      picsort config set recursive true
      picsort config set date_format "YYYY-MM"
      picsort config set file_types .jpg,.png,.mp4
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)

    try:
        config_manager = ConfigManager()

        # Determine config path
        target_path = config_path or str(config_manager.default_config_path)
        target_path_obj = Path(target_path)

        # Load existing config or create default
        if target_path_obj.exists():
            user_config = config_manager.load_config(target_path)
        else:
            user_config = Configuration.create_default()
            if not quiet:
                print(f"Creating new configuration file: {target_path}")

        # Convert value to appropriate type
        converted_value = _convert_config_value(key, value)

        # Update configuration
        config_dict = {
            'version': user_config.version,
            'default_source': user_config.default_source,
            'file_types': user_config.file_types,
            'process_all_files': user_config.process_all_files,
            'date_format': user_config.date_format,
            'recursive': user_config.recursive,
            'dry_run_default': user_config.dry_run_default,
            'create_log': user_config.create_log,
            'log_path': user_config.log_path,
            'verify_checksum': user_config.verify_checksum,
            'batch_size': user_config.batch_size,
            'parallel_scan': user_config.parallel_scan,
            'confirm_large_operations': user_config.confirm_large_operations,
            'duplicate_handling': user_config.duplicate_handling
        }

        # Apply the update
        if key in config_dict:
            config_dict[key] = converted_value
            updated_config = Configuration(**config_dict)
            config_manager.save_config(updated_config, target_path)

            if not quiet:
                print(f"Configuration updated: {key} = {converted_value}")
                print(f"Saved to: {target_path}")
        else:
            if not quiet:
                print(f"Unknown configuration key: {key}")
                print(f"Available keys: {', '.join(config_dict.keys())}")
            return 1

        return 0

    except Exception as e:
        if not quiet:
            print(f"Error setting configuration: {e}")
        logger.error(f"Config set failed: {e}", exc_info=verbose)
        return 1


@config.command()
@click.option('--yes', is_flag=True, required=True, help='Confirm reset (required)')
@click.option('--config-path', '-c', type=click.Path(), help='Configuration file path')
@click.pass_context
def reset(ctx, yes, config_path):
    """Reset configuration to defaults.

    Resets the configuration file to default values. This action cannot be undone
    unless you have a backup. The --yes flag is required to confirm this operation.

    Examples:
      picsort config reset --yes
      picsort config reset --yes --config /path/to/config.yaml
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)

    if not yes:
        if not quiet:
            print("Reset operation requires --yes flag to confirm")
        return 1

    try:
        config_manager = ConfigManager()

        # Determine config path
        target_path = config_path or str(config_manager.default_config_path)
        target_path_obj = Path(target_path)

        # Create backup if file exists
        if target_path_obj.exists():
            backup_path = config_manager.backup_config(target_path)
            if not quiet:
                print(f"Configuration backed up to: {backup_path}")

        # Create default configuration
        default_config = config_manager.create_default_config(target_path)

        if not quiet:
            print(f"Configuration reset to defaults: {target_path}")

        return 0

    except Exception as e:
        if not quiet:
            print(f"Error resetting configuration: {e}")
        logger.error(f"Config reset failed: {e}", exc_info=verbose)
        return 1


@config.command(name='list')
@click.pass_context
def list_configs(ctx):
    """List available configuration files.
    
    Shows configuration files found in standard locations.
    
    Example:
      picsort config list
    """
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)
    
    try:
        config_manager = ConfigManager()
        available_configs = config_manager.list_available_configs()
        
        if not quiet:
            if available_configs:
                print("Available configuration files:")
                for config_info in available_configs:
                    print(f"  {config_info['name']}: {config_info['path']}")
            else:
                print("No configuration files found.")
                print(f"Default location: {config_manager.default_config_path}")
                print("Run 'picsort config init' to create a default configuration.")
        
        return 0
        
    except Exception as e:
        if not quiet:
            print(f"Error listing configurations: {e}")
        logger.error(f"Config list failed: {e}", exc_info=verbose)
        return 1


def _convert_config_value(key: str, value: str):
    """Convert string value to appropriate type for configuration key.

    Args:
        key: Configuration key name
        value: String value to convert

    Returns:
        Converted value with appropriate type
    """
    # Boolean values
    if key in ['process_all_files', 'recursive', 'dry_run_default', 'create_log',
               'verify_checksum', 'parallel_scan', 'confirm_large_operations']:
        if value.lower() in ['true', '1', 'yes', 'on']:
            return True
        elif value.lower() in ['false', '0', 'no', 'off']:
            return False
        else:
            raise ValueError(f"Invalid boolean value for {key}: {value}")

    # Integer values
    elif key in ['batch_size']:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid integer value for {key}: {value}")

    # List values (file_types)
    elif key == 'file_types':
        if ',' in value:
            return [ext.strip() for ext in value.split(',')]
        else:
            return [value.strip()]

    # String values
    else:
        return value
