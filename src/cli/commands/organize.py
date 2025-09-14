"""Organize command for moving files into date folders."""
import os
import sys
import logging
from pathlib import Path
from typing import Optional, List

import click

from ...lib.config_manager import ConfigManager
from ...lib.file_scanner import FileScanner
from ...lib.date_organizer import DateOrganizer
from ...lib.file_mover import FileMover
from ...lib.progress_reporter import ProgressReporter

logger = logging.getLogger(__name__)


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories recursively')
@click.option('--dry-run', '-d', is_flag=True, help='Show what would be done without making changes')
@click.option('--file-types', '-t', multiple=True, help='File extensions to process (e.g., --file-types .jpg --file-types .png)')
@click.option('--all-files', '-a', is_flag=True, help='Process all files, not just media files')
@click.option('--date-format', '-f', help='Date folder format (default: MM.YYYY)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompts')
@click.option('--no-verify', is_flag=True, help='Skip checksum verification for faster operation')
@click.option('--log-file', '-l', type=click.Path(), help='Log file path')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def organize(ctx, path, recursive, dry_run, file_types, all_files, date_format, 
             verbose, quiet, yes, no_verify, log_file, config):
    """Organize media files into date-based folders.
    
    Scans PATH for media files and moves them into folders named with 
    creation date (MM.YYYY format). Files are verified before deletion
    to ensure safe operation.
    
    Examples:
      picsort organize /path/to/photos
      picsort organize --recursive --dry-run ~/Pictures
      picsort organize --file-types .jpg .png /path/to/files
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
        # Override dry_run based on CLI flag
        # If --dry-run is explicitly provided, set to True
        # Otherwise, set to False to actually perform operations
        import sys
        if '--dry-run' in sys.argv or '-d' in sys.argv:
            cli_args['dry_run'] = True
        else:
            # Default to actual operations when no --dry-run flag
            cli_args['dry_run'] = False
        if file_types:
            cli_args['file_types'] = list(file_types)
        if all_files is not None:
            cli_args['process_all_files'] = all_files
        if date_format is not None:
            cli_args['date_format'] = date_format
        if no_verify:
            cli_args['verify_checksum'] = False
        
        final_config = config_manager.merge_with_cli_args(user_config, cli_args)
        
        # Initialize components
        scanner = FileScanner(final_config)
        organizer = DateOrganizer(final_config)
        mover = FileMover(final_config)
        
        # Report starting operation
        operation_mode = "dry run" if final_config.dry_run_default else "organization"
        reporter.start_operation(f"Starting {operation_mode}", 0)
        
        # Scan for files
        reporter.set_status(f"Scanning {path}...")
        media_files = scanner.scan_directory(str(path))
        
        if not media_files:
            if not quiet:
                print("Organization complete - no files found to organize.")
            return 0
        
        # Filter files that should be processed
        processable_files = [f for f in media_files if f.should_process()]
        
        if not processable_files:
            if not quiet:
                if len(media_files) > 0:
                    print(f"Found {len(media_files)} files, but none match processing criteria.")
                else:
                    print("Organization complete - no files found to organize.")
            return 0
        
        reporter.set_status(f"Found {len(processable_files)} files to organize")
        
        # Organize files
        organization = organizer.organize_files(processable_files, str(path))
        organization_summary = organizer.get_organization_summary(organization)
        
        # Show preview
        reporter.report_organization_preview(organization_summary)
        
        if final_config.dry_run_default:
            # Dry run mode - get preview with duplicate info
            preview = organizer.preview_organization(processable_files, str(path))
            reporter.report_dry_run_results(organization_summary)

            # Show folder names that would be created
            if not quiet and preview:
                print("\nFolders that would be created:")
                for folder_info in preview:
                    print(f"  {folder_info['folder']} ({folder_info['file_count']} files)")

            # Show duplicate information if any
            for folder_info in preview:
                if folder_info['duplicates']:
                    if not quiet:
                        print(f"\nDuplicate files in {folder_info['folder']} would be renamed:")
                        for dup in folder_info['duplicates']:
                            print(f"  {dup['original']} -> {dup['renamed']}")

            return 0
        
        # Ask for confirmation if not in yes mode
        if not yes and final_config.confirm_large_operations:
            total_files = organization_summary['total_files']
            if total_files > 10:  # Confirm for large operations
                if not reporter.ask_confirmation(f"Proceed to organize {total_files} files?"):
                    print("Operation cancelled.")
                    return 1
        
        # Perform the actual move operations
        reporter.start_operation("Organizing files", organization_summary['total_files'])
        
        operations = mover.move_files(organization, dry_run=False)
        
        # Update progress as files are processed
        for i, operation in enumerate(operations, 1):
            status_msg = None
            if operation.is_successful():
                status_msg = f"Moved {operation.source_file.filename}"
            elif operation.status == 'failed':
                status_msg = f"Failed: {operation.source_file.filename}"
            
            reporter.update_progress(1, status_msg)
        
        reporter.finish_operation(success=True)
        
        # Report results
        reporter.report_operation_results(operations)
        
        # Check if all operations succeeded
        failed_count = len([op for op in operations if op.status == 'failed'])
        if failed_count > 0:
            return 1  # Some operations failed
        
        return 0  # Success
        
    except KeyboardInterrupt:
        if not quiet:
            print("\nOperation cancelled by user.")
        return 130  # Standard exit code for SIGINT
        
    except Exception as e:
        reporter.report_error(str(e))
        logger.error(f"Organize command failed: {e}", exc_info=verbose)
        return 1
