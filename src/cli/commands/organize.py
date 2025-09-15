"""Organize command for moving files into date folders."""
import os
import sys
import logging
from pathlib import Path
from typing import Optional, List
import uuid
from datetime import datetime

import click

try:
    # Try absolute imports first (development)
    from src.lib.config_manager import ConfigManager
    from src.lib.file_scanner import FileScanner
    from src.lib.date_organizer import DateOrganizer
    from src.lib.file_mover import FileMover
    from src.lib.progress_reporter import ProgressReporter
    from src.lib.operation_logger import OperationLogger, create_console_callback
    from src.lib.resume_manager import ResumeManager
    from src.models.operation_log import OperationLog
    from src.models.file_operation import FileOperation
except ImportError:
    # Fallback for PyInstaller bundle (relative imports)
    from lib.config_manager import ConfigManager
    from lib.file_scanner import FileScanner
    from lib.date_organizer import DateOrganizer
    from lib.file_mover import FileMover
    from lib.progress_reporter import ProgressReporter
    from lib.operation_logger import OperationLogger, create_console_callback
    from lib.resume_manager import ResumeManager
    from models.operation_log import OperationLog
    from models.file_operation import FileOperation

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
    
    # Generate unique operation ID for this organize operation
    operation_id = str(uuid.uuid4())

    # Initialize operation logging
    op_logger = OperationLogger()

    # Initialize resume manager
    resume_manager = ResumeManager()

    # Log operation start
    logger.info(f"Starting organize operation on {path}")

    try:
        # Load configuration with enhanced error handling
        config_manager = ConfigManager()
        try:
            user_config = config_manager.load_config(config)
            logger.info("Configuration loaded successfully")
        except Exception as config_error:
            logger.error(f"Failed to load configuration: {config_error}")
            raise
        
        # Apply CLI overrides
        cli_args = {}
        if recursive is not None:
            cli_args['recursive'] = recursive
        # Override dry_run based on CLI flag
        # If --dry-run is explicitly provided, set to True
        # Otherwise, set to False to actually perform operations
        import sys
        if '--dry-run' in sys.argv or '-d' in sys.argv:
            cli_args['dry_run_default'] = True
        else:
            # Default to actual operations when no --dry-run flag
            cli_args['dry_run_default'] = False
        if file_types:
            cli_args['file_types'] = list(file_types)
        if all_files is not None:
            cli_args['process_all_files'] = all_files
        if date_format is not None:
            cli_args['date_format'] = date_format
        if no_verify:
            cli_args['verify_checksum'] = False
        
        final_config = config_manager.merge_with_cli_args(user_config, cli_args)

        # Log final configuration
        logger.info("Final configuration prepared")

        # Initialize components with operation logging
        def scanner_logger_callback(log_entry):
            """Callback to handle scanner log entries."""
            if hasattr(log_entry, 'level'):
                if log_entry.level == 'INFO':
                    logger.info(log_entry.message)
                elif log_entry.level == 'WARNING':
                    logger.warning(log_entry.message)
                elif log_entry.level == 'ERROR':
                    logger.error(log_entry.message)
            else:
                # Legacy callback format
                logger.info(str(log_entry))

        scanner = FileScanner(final_config)
        organizer = DateOrganizer(final_config)
        mover = FileMover(final_config)

        # Create resume point for non-dry-run operations
        resume_data = None
        if not final_config.dry_run_default:
            config_snapshot = {
                'version': final_config.version,
                'file_types': final_config.file_types,
                'process_all_files': final_config.process_all_files,
                'date_format': final_config.date_format,
                'recursive': final_config.recursive,
                'dry_run_default': final_config.dry_run_default,
                'verify_checksum': final_config.verify_checksum,
                'duplicate_handling': final_config.duplicate_handling
            }
            resume_data = resume_manager.create_resume_point(
                operation_id=operation_id,
                operation_type='organize',
                source_path=str(path),
                config_snapshot=config_snapshot
            )
            logger.info("Resume point created for operation")
        
        # Report starting operation with multi-phase progress
        operation_mode = "dry run" if final_config.dry_run_default else "organization"

        # Phase 1: Scanning
        with reporter.phase("Scanning directory") as scan_phase:
            scan_phase.start_indeterminate_phase("Discovering files")
            scan_start_time = datetime.now()

            try:
                media_files = scanner.scan_directory(str(path))
                scan_duration = (datetime.now() - scan_start_time).total_seconds()

                if media_files:
                    scan_phase.success(f"Found {len(media_files)} files in {scan_duration:.1f}s")
                else:
                    scan_phase.info("No files found")

                logger.info(f"Directory scan completed successfully - found {len(media_files)} files")

            except Exception as scan_error:
                scan_phase.report_error(f"Directory scan failed: {scan_error}")
                logger.error(f"Directory scan failed: {scan_error}")
                raise

        if not media_files:
            if not quiet:
                print("Organization complete - no files found to organize.")
            return 0

        # Phase 2: Analyzing files
        with reporter.phase("Analyzing files", len(media_files)) as analysis_phase:
            analysis_phase.set_status("Filtering processable files")

            # Filter files that should be processed
            processable_files = [f for f in media_files if f.should_process()]
            analysis_phase.update(len(media_files) // 2)

            # Log file filtering results
            error_files = [f for f in media_files if f.error]
            skipped_files = [f for f in media_files if not f.should_process() and not f.error]

            logger.info(f"File filtering completed - {len(processable_files)} processable files")

            if not processable_files:
                analysis_phase.warning("No files match processing criteria")
                if not quiet:
                    if len(media_files) > 0:
                        print(f"Found {len(media_files)} files, but none match processing criteria.")
                    else:
                        print("Organization complete - no files found to organize.")

                logger.info("Operation completed - no processable files found")

                # Clean up resume data if no work to do
                if resume_data:
                    resume_manager.cleanup_completed_operation(operation_id)

                return 0

            analysis_phase.set_status("Creating organization plan")

            # Organize files with logging
            logger.info(f"Starting file organization for {len(processable_files)} files")

            try:
                organization = organizer.organize_files(processable_files, str(path))
                analysis_phase.update(len(media_files) // 4)

                organization_summary = organizer.get_organization_summary(organization)
                analysis_phase.update(len(media_files) // 4)

                analysis_phase.success(f"Plan ready: {organization_summary.get('total_files', 0)} files → {organization_summary.get('total_folders', 0)} folders")
                logger.info("File organization plan created")

            except Exception as org_error:
                analysis_phase.report_error(f"Planning failed: {org_error}")
                logger.error(f"File organization failed: {org_error}")
                raise
        
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
                    logger.info("Operation cancelled by user")
                    if resume_data:
                        resume_manager.cleanup_completed_operation(operation_id)
                    print("Operation cancelled.")
                    return 1
        
        # Phase 3: Moving files (only for real operations, not dry run)
        if not final_config.dry_run_default:
            with reporter.phase("Moving files", organization_summary['total_files']) as move_phase:
                move_phase.set_status("Preparing file operations")

                logger.info(f"Starting file move operations for {organization_summary['total_files']} files")

                move_start_time = datetime.now()
                operations = []

                try:
                    # Create FileOperation objects from organization data
                    file_operations = []
                    for target_folder, media_files in organization.items():
                        for media_file in media_files:
                            # Get the final destination path (handling duplicates)
                            destination_path = mover._get_destination_path(media_file, target_folder, dry_run=False)

                            # Create FileOperation with required parameters
                            file_op = FileOperation(
                                source_file=media_file,
                                destination_path=destination_path,
                                status='pending',
                                error_message=None,
                                checksum_source=None,
                                checksum_dest=None,
                                operation_time=datetime.now(),
                                duration_ms=0
                            )
                            file_operations.append(file_op)

                    # Update resume data with pending operations if this is not a dry run
                    if resume_data:
                        resume_manager.update_resume_point(
                            resume_data,
                            pending_operations=file_operations
                        )

                    move_phase.set_status("Moving files")

                    # Process operations with resume support
                    for i, operation in enumerate(file_operations):
                        try:
                            completed_op = mover.move_file(operation, dry_run=False)
                            operations.append(completed_op)

                            # Update resume data after each successful operation
                            if resume_data:
                                remaining_ops = file_operations[i+1:]
                                resume_manager.update_resume_point(
                                    resume_data,
                                    completed_operation=completed_op,
                                    pending_operations=remaining_ops
                                )

                            # Update progress as files are processed
                            if completed_op.is_successful():
                                move_phase.update_with_status(1, f"✓ {completed_op.source_file.filename}")
                            elif completed_op.status == 'failed':
                                move_phase.update_with_status(1, f"✗ {completed_op.source_file.filename}")
                                logger.error(f"File move failed: {completed_op.error_message}")

                        except KeyboardInterrupt:
                            # Save current state before exiting
                            if resume_data:
                                remaining_ops = file_operations[i:]
                                resume_manager.update_resume_point(
                                    resume_data,
                                    pending_operations=remaining_ops
                                )

                            logger.warning("Operation interrupted by user - state saved for resume")
                            raise

                    move_duration = (datetime.now() - move_start_time).total_seconds()

                    # Analyze operation results
                    successful_ops = [op for op in operations if op.is_successful()]
                    failed_ops = [op for op in operations if op.status == 'failed']

                    if failed_ops:
                        move_phase.warning(f"Completed with {len(failed_ops)} failures")
                    else:
                        move_phase.success(f"All {len(successful_ops)} files moved successfully in {move_duration:.1f}s")

                    logger.info(f"File move operations completed - {len(successful_ops)} successful, {len(failed_ops)} failed")

                except Exception as move_error:
                    move_phase.report_error(f"Move operations failed: {move_error}")
                    logger.error(f"File move operations failed: {move_error}")
                    raise
        
        # Report results
        reporter.report_operation_results(operations)
        
        # Check if all operations succeeded and log final results
        failed_count = len([op for op in operations if op.status == 'failed'])
        success_count = len([op for op in operations if op.is_successful()])

        # Save operation log using basic logger
        if hasattr(final_config, 'create_log') and final_config.create_log:
            try:
                log_file_path = op_logger.save_log(operation_id)
                if not quiet:
                    print(f"Operation log saved to: {log_file_path}")
            except Exception as log_error:
                logger.warning(f"Failed to save operation log: {log_error}")

        # Clean up resume data for successful operations
        if resume_data and failed_count == 0:
            resume_manager.cleanup_completed_operation(operation_id)

        # Log final operation status
        if failed_count > 0:
            logger.warning(f"Organization completed with {failed_count} failures")
            return 1  # Some operations failed
        else:
            logger.info(f"Organization completed successfully")
            return 0  # Success
        
    except KeyboardInterrupt:
        # Log cancellation
        try:
            logger.warning("Operation cancelled by user (SIGINT)")
        except:
            pass  # Don't fail on logging during cancellation

        if not quiet:
            print("\nOperation cancelled by user.")
            if 'resume_data' in locals() and resume_data:
                print(f"Operation state saved. Resume with: picsort resume {operation_id[:12]}")
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        # Log critical error
        try:
            logger.error(f"Critical error in organize command: {e}")
        except:
            pass  # Don't fail on logging during error handling

        reporter.report_error(str(e))
        logger.error(f"Organize command failed: {e}", exc_info=verbose)
        return 1
