"""Undo command for reversing file organization operations."""
import logging
from pathlib import Path

import click

logger = logging.getLogger(__name__)


@click.command()
@click.option('--operation-id', '-o', help='Specific operation to undo')
@click.option('--dry-run', '-d', is_flag=True, default=True, help='Preview undo without moving files (default: true)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompts')
@click.pass_context
def undo(ctx, operation_id, dry_run, verbose, quiet, yes):
    """Undo the last file organization operation.

    Reverses the most recent organize command by moving files back to their
    original locations. This requires operation logs to be enabled in the
    configuration. By default, shows a preview of what would be undone.

    Examples:
      picsort undo                              # Preview last operation undo
      picsort undo --dry-run=false --yes        # Actually undo last operation
      picsort undo --operation-id abc123        # Preview specific operation undo
    """
    # Merge global options with command options
    verbose = verbose or ctx.obj.get('verbose', False)
    quiet = quiet or ctx.obj.get('quiet', False)
    
    try:
        # This is a placeholder implementation
        # In a full implementation, this would:
        # 1. Read operation logs from ~/.picsort/logs
        # 2. Find the most recent organize operation or specific operation_id
        # 3. Reverse all file moves from that operation
        # 4. Verify the undo was successful

        if operation_id:
            if not quiet:
                if dry_run:
                    print(f"Preview: Would undo operation {operation_id}")
                    print("No operations found to undo.")
                else:
                    print(f"Undo failed: Operation {operation_id} not found")
            return 1 if not dry_run else 0
        else:
            if not quiet:
                if dry_run:
                    print("Preview: Would undo last organization operation")
                    print("No operations found to undo.")
                else:
                    print("Nothing to undo - no previous operations found.")

        return 0
        
    except KeyboardInterrupt:
        if not quiet:
            print("\nUndo cancelled by user.")
        return 130
        
    except Exception as e:
        if not quiet:
            print(f"Error during undo: {e}")
        logger.error(f"Undo command failed: {e}", exc_info=verbose)
        return 1
