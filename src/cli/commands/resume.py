"""Resume command for resuming interrupted operations."""
import sys
import logging
from pathlib import Path
from typing import Optional

import click

try:
    # Try absolute imports first (development)
    from src.lib.config_manager import ConfigManager
    from src.lib.resume_manager import ResumeManager
    from src.lib.file_mover import FileMover
    from src.lib.progress_reporter import ProgressReporter
    from src.lib.operation_logger import OperationLogger, create_console_callback
    from src.models.configuration import Configuration
except ImportError:
    # Fallback for PyInstaller bundle (relative imports)
    from lib.config_manager import ConfigManager
    from lib.resume_manager import ResumeManager
    from lib.file_mover import FileMover
    from lib.progress_reporter import ProgressReporter
    from lib.operation_logger import OperationLogger, create_console_callback
    from models.configuration import Configuration

logger = logging.getLogger(__name__)


@click.command()
@click.argument('operation_id', required=False)
@click.option('--list', '-l', 'list_operations', is_flag=True,
              help='List all resumable operations')
@click.option('--validate', '-v', is_flag=True,
              help='Validate resumable operation before resuming')
@click.option('--cleanup', '-c', is_flag=True,
              help='Clean up old resume files')
@click.option('--max-age', default=7, type=int,
              help='Maximum age in days for cleanup (default: 7)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompts')
@click.pass_context
def resume(ctx, operation_id, list_operations, validate, cleanup, max_age,
           verbose, quiet, yes):
    """Resume interrupted organize operations.

    If OPERATION_ID is provided, attempts to resume that specific operation.
    Otherwise, lists available operations to resume.

    Examples:
      picsort resume --list
      picsort resume abc123def
      picsort resume --cleanup --max-age 3
    """
    # Merge global options with command options
    verbose = verbose or ctx.obj.get('verbose', False)
    quiet = quiet or ctx.obj.get('quiet', False)

    # Initialize resume manager and reporter
    resume_manager = ResumeManager()
    reporter = ProgressReporter(verbose=verbose, quiet=quiet)

    # Create operation logger with console callback
    console_callback = create_console_callback(verbose=verbose, quiet=quiet)
    op_logger = OperationLogger(console_callback=console_callback)

    try:
        # Handle cleanup
        if cleanup:
            if not quiet:
                print(f"Cleaning up resume files older than {max_age} days...")

            resume_manager.cleanup_old_resume_files(max_age_days=max_age)
            op_logger.log_info(f"Cleaned up old resume files (max age: {max_age} days)")

            if not quiet:
                print("Cleanup completed.")
            return 0

        # Handle list operations
        if list_operations:
            operations = resume_manager.list_resumable_operations()

            if not operations:
                if not quiet:
                    print("No resumable operations found.")
                return 0

            if not quiet:
                print(f"Found {len(operations)} resumable operations:")
                print()

                for i, op in enumerate(operations, 1):
                    print(f"{i}. Operation ID: {op['operation_id'][:12]}...")
                    print(f"   Type: {op['operation_type']}")
                    print(f"   Source: {op['source_path']}")
                    print(f"   Started: {op['start_time']}")
                    print(f"   Progress: {op['completed_count']} completed, {op['pending_count']} pending")
                    print()

            return 0

        # Handle specific operation resume
        if not operation_id:
            # No operation ID provided, try to detect interrupted operations
            interrupted = resume_manager.detect_interrupted_operations()

            if not interrupted:
                if not quiet:
                    print("No interrupted operations detected.")
                    print("Use --list to see all resumable operations.")
                return 0

            if len(interrupted) == 1:
                operation_id = interrupted[0]
                if not quiet:
                    print(f"Detected interrupted operation: {operation_id[:12]}...")
            else:
                if not quiet:
                    print(f"Multiple interrupted operations detected: {len(interrupted)}")
                    print("Use --list to see all operations and specify one to resume.")
                return 1

        # Load resume data
        resume_data = resume_manager.load_resume_data(operation_id)
        if not resume_data:
            if not quiet:
                print(f"No resume data found for operation: {operation_id}")
            return 1

        # Validate resume data if requested
        if validate:
            validation = resume_manager.validate_resume_data(resume_data)

            if not quiet:
                print(f"Validating resume data for operation {operation_id[:12]}...")

                if validation['valid']:
                    print("✓ Resume data is valid")
                else:
                    print("✗ Resume data validation failed:")
                    for error in validation['errors']:
                        print(f"  • {error}")

                if validation['warnings']:
                    print("Warnings:")
                    for warning in validation['warnings']:
                        print(f"  • {warning}")

            if not validation['valid']:
                return 1

            if not quiet:
                print("Validation completed successfully.")
            return 0

        # Check if operation can be resumed
        if not resume_manager.can_resume_operation(operation_id):
            if not quiet:
                print(f"Operation {operation_id[:12]}... cannot be resumed (no pending operations)")
            return 1

        # Show resume summary
        summary = resume_manager.get_resume_summary(operation_id)

        if not quiet:
            print(f"Resuming operation: {operation_id[:12]}...")
            print(f"Type: {summary['operation_type']}")
            print(f"Source: {summary['source_path']}")
            print(f"Progress: {summary['completed_operations']} completed, {summary['pending_operations']} pending")

        # Ask for confirmation if not in yes mode
        if not yes:
            if not reporter.ask_confirmation(f"Resume operation with {summary['pending_operations']} pending files?"):
                print("Resume cancelled.")
                return 1

        # Load configuration and initialize components
        config_manager = ConfigManager()
        config = Configuration(**resume_data.config_snapshot)

        # Create file operations from resume data
        pending_operations = resume_manager.create_pending_operations(resume_data)

        if not pending_operations:
            if not quiet:
                print("No pending operations to resume.")

            # Clean up completed operation
            resume_manager.cleanup_completed_operation(operation_id)
            return 0

        # Initialize file mover
        mover = FileMover(config)

        # Resume operation
        op_logger.log_info(f"Resuming operation {operation_id} with {len(pending_operations)} pending files")

        reporter.start_operation("Resuming file organization", len(pending_operations))

        results = []

        try:
            for i, operation in enumerate(pending_operations):
                # Perform move operation
                completed_op = mover.move_file(operation, dry_run=False)
                results.append(completed_op)

                # Update resume data
                remaining_operations = pending_operations[i+1:]
                resume_manager.update_resume_point(
                    resume_data,
                    completed_operation=completed_op,
                    pending_operations=remaining_operations
                )

                # Update progress
                status_msg = None
                if completed_op.is_successful():
                    status_msg = f"Moved {completed_op.source_file.filename}"
                elif completed_op.status == 'failed':
                    status_msg = f"Failed: {completed_op.source_file.filename}"
                    op_logger.log_error(
                        f"File move failed: {completed_op.error_message}",
                        file_path=completed_op.source_file.path
                    )

                reporter.update_progress(1, status_msg)

        except KeyboardInterrupt:
            op_logger.log_warning("Resume operation cancelled by user")
            if not quiet:
                print("\\nResume operation cancelled. Progress has been saved.")
            return 130

        except Exception as e:
            op_logger.log_error(f"Resume operation failed: {e}")
            if not quiet:
                print(f"\\nResume operation failed: {e}")
            return 1

        reporter.finish_operation(success=True)

        # Report results
        reporter.report_operation_results(results)

        # Clean up completed operation
        resume_manager.cleanup_completed_operation(operation_id)

        op_logger.log_info(f"Resume operation completed successfully for {operation_id}")

        # Check if all operations succeeded
        failed_count = len([op for op in results if op.status == 'failed'])
        if failed_count > 0:
            return 1  # Some operations failed

        return 0  # Success

    except Exception as e:
        op_logger.log_error(f"Resume command failed: {e}")
        reporter.report_error(str(e))
        logger.error(f"Resume command failed: {e}", exc_info=verbose)
        return 1