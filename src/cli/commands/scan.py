"""Scan command for previewing file organization."""
import logging
from pathlib import Path

import click

from ...lib.config_manager import ConfigManager
from ...lib.file_scanner import FileScanner
from ...lib.date_organizer import DateOrganizer
from ...lib.progress_reporter import ProgressReporter

logger = logging.getLogger(__name__)


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories recursively')
@click.option('--file-types', '-t', multiple=True, help='File extensions to process (e.g., .jpg .png)')
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), default='table', help='Output format (default: table)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def scan(ctx, path, recursive, file_types, format, verbose, quiet, config):
    """Scan directory and preview how files would be organized.
    
    Shows what the organize command would do without making any changes.
    Useful for testing different settings and understanding the organization
    structure before committing to changes.
    
    Examples:
      picsort scan /path/to/photos
      picsort scan --recursive ~/Pictures
      picsort scan --date-format YYYY-MM /path/to/files
    """
    # Merge global options with command options
    verbose = verbose or ctx.obj.get('verbose', False)
    quiet = quiet or ctx.obj.get('quiet', False)
    
    # Initialize progress reporter
    reporter = ProgressReporter(verbose=verbose, quiet=quiet)
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        user_config = config_manager.load_config(config)
        
        # Apply CLI overrides
        cli_args = {}
        if recursive is not None:
            cli_args['recursive'] = recursive
        if file_types:
            cli_args['file_types'] = list(file_types)
        
        final_config = config_manager.merge_with_cli_args(user_config, cli_args)
        
        # Initialize components
        scanner = FileScanner(final_config)
        organizer = DateOrganizer(final_config)
        
        # Report starting operation (only for table format)
        if format == 'table':
            reporter.start_operation("Scanning directory", 0)
            reporter.set_status(f"Scanning {path}...")

        # Scan for files
        media_files = scanner.scan_directory(str(path))
        
        if not media_files:
            if format == 'json':
                _output_json_format([], [], {'date_range': None}, [], path, quiet)
            elif format == 'csv':
                _output_csv_format([], [], {'date_range': None}, [], path, quiet)
            else:
                if not quiet:
                    print(f"\nScan Results for: {path}")
                    print("-" * 29)
                    print("Total files: 0")
                    print("Media files: 0")
            return 0
        
        # Filter files that would be processed
        processable_files = [f for f in media_files if f.should_process()]
        
        if not processable_files:
            if format == 'json':
                _output_json_format(media_files, processable_files, {'date_range': None}, [], path, quiet)
            elif format == 'csv':
                _output_csv_format(media_files, processable_files, {'date_range': None}, [], path, quiet)
            else:
                if not quiet:
                    print(f"\nScan Results for: {path}")
                    print("-" * 29)
                    print(f"Total files: {len(media_files)}")
                    print(f"Media files: 0")
                    if len(media_files) > 0:
                        print(f"\nFound {len(media_files)} files, but none match processing criteria.")
                        if verbose:
                            print("\nFiles found but not processed:")
                            for f in media_files[:10]:  # Show first 10
                                reason = f.error if f.error else "Not a media file"
                                print(f"  - {f.filename}: {reason}")
                            if len(media_files) > 10:
                                print(f"  ... and {len(media_files) - 10} more")
            return 0
        
        if format == 'table':
            reporter.set_status(f"Found {len(processable_files)} files to organize")
        
        # Organize files (preview mode)
        organization = organizer.organize_files(processable_files, str(path))
        organization_summary = organizer.get_organization_summary(organization)
        
        # Get detailed preview
        preview = organizer.preview_organization(processable_files, str(path))
        
        if format == 'table':
            reporter.finish_operation(success=True)
        
        # Show results based on format
        if format == 'json':
            _output_json_format(media_files, processable_files, organization_summary, preview, path, quiet)
        elif format == 'csv':
            _output_csv_format(media_files, processable_files, organization_summary, preview, path, quiet)
        else:  # table format (default)
            _output_table_format(media_files, processable_files, organization_summary, preview, path, final_config, verbose, quiet, recursive, file_types)
        
        return 0
        
    except KeyboardInterrupt:
        if not quiet:
            print("\nScan cancelled by user.")
        return 130
        
    except Exception as e:
        reporter.report_error(str(e))
        logger.error(f"Scan command failed: {e}", exc_info=verbose)
        return 1


def _output_table_format(media_files, processable_files, organization_summary, preview, path, final_config, verbose, quiet, recursive, file_types):
    """Output scan results in table format."""
    if not quiet:
        print(f"\nScan Results for: {path}")
        print("-" * 29)
        print(f"Total files: {len(media_files)}")
        print(f"Media files: {len(processable_files)}")

        if organization_summary['date_range']:
            min_date, max_date = organization_summary['date_range']
            print(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

        print("\nFolders to create:")
        for folder_info in preview:
            print(f"  {folder_info['folder']}")

        print("\nFiles by month:")
        for folder_info in preview:
            print(f"  {folder_info['folder']}: {folder_info['file_count']} files")

            if verbose:
                for file_info in folder_info['files']:
                    print(f"    - {file_info['name']}")

                if folder_info['more_files'] > 0:
                    print(f"    ... and {folder_info['more_files']} more files")

        # Show files with issues
        error_files = [f for f in media_files if f.error]
        if error_files and verbose:
            print("\nFiles with issues:")
            for f in error_files[:5]:  # Show first 5
                print(f"  ❌ {f.filename}: {f.error}")
            if len(error_files) > 5:
                print(f"  ... and {len(error_files) - 5} more files with errors")

        print("\nTo perform this organization, run:")
        cmd_parts = ["picsort organize"]
        if recursive:
            cmd_parts.append("--recursive")
        if file_types:
            cmd_parts.extend(["--file-types"] + list(file_types))
        cmd_parts.append(str(path))

        print(f"  {' '.join(cmd_parts)}")


def _output_json_format(media_files, processable_files, organization_summary, preview, path, quiet):
    """Output scan results in JSON format."""
    import json

    result = {
        "scan_path": str(path),
        "total_files": len(media_files),
        "media_files": len(processable_files),
        "folders_to_create": [folder_info['folder'] for folder_info in preview],
        "files_by_folder": {
            folder_info['folder']: {
                "file_count": folder_info['file_count'],
                "files": [f['name'] for f in folder_info['files']]
            }
            for folder_info in preview
        }
    }

    if organization_summary['date_range']:
        min_date, max_date = organization_summary['date_range']
        result["date_range"] = {
            "oldest": min_date.strftime('%Y-%m-%d'),
            "newest": max_date.strftime('%Y-%m-%d')
        }

    if not quiet:
        print(json.dumps(result, indent=2))


def _output_csv_format(media_files, processable_files, organization_summary, preview, path, quiet):
    """Output scan results in CSV format."""
    if not quiet:
        print("folder,file_count,files")
        for folder_info in preview:
            files_list = ";".join([f['name'] for f in folder_info['files']])
            print(f"{folder_info['folder']},{folder_info['file_count']},\"{files_list}\"")
