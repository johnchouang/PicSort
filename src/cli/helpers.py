"""CLI helper functions for user interaction and output formatting."""
import sys
import click
from typing import Dict, Any, List, Optional


def confirm_action(message: str, default: bool = False, force_yes: bool = False) -> bool:
    """Ask user for confirmation of an action.

    Args:
        message: Message to display to user
        default: Default value if user just presses Enter
        force_yes: If True, skip prompt and return True

    Returns:
        True if user confirmed, False otherwise
    """
    if force_yes:
        return True

    return click.confirm(message, default=default)


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if bytes_size == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            if unit == 'B':
                return f"{bytes_size} {unit}"
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024

    return f"{bytes_size:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "2m 30s")
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def print_success(message: str, quiet: bool = False) -> None:
    """Print success message with formatting.

    Args:
        message: Success message to display
        quiet: If True, suppress output
    """
    if not quiet:
        click.echo(click.style("✓ " + message, fg='green'))


def print_warning(message: str, quiet: bool = False) -> None:
    """Print warning message with formatting.

    Args:
        message: Warning message to display
        quiet: If True, suppress output
    """
    if not quiet:
        click.echo(click.style("⚠ " + message, fg='yellow'), err=True)


def print_error(message: str, quiet: bool = False) -> None:
    """Print error message with formatting.

    Args:
        message: Error message to display
        quiet: If True, suppress output
    """
    if not quiet:
        click.echo(click.style("✗ " + message, fg='red'), err=True)


def print_error_with_recovery(error_info, show_details: bool = False, quiet: bool = False) -> None:
    """Print enhanced error message with recovery suggestions.

    Args:
        error_info: PicSortError object with recovery information
        show_details: Whether to show technical details
        quiet: If True, suppress output
    """
    if quiet:
        return

    from ..lib.error_handler import ErrorHandler
    handler = ErrorHandler()
    error_report = handler.format_error_report(error_info, show_details)
    click.echo(error_report, err=True)


def print_error_summary(errors: list, quiet: bool = False) -> None:
    """Print summary of multiple errors with suggestions.

    Args:
        errors: List of PicSortError objects
        quiet: If True, suppress output
    """
    if quiet or not errors:
        return

    from ..lib.error_handler import ErrorHandler
    handler = ErrorHandler()
    summary = handler.create_error_summary(errors)

    click.echo(f"\n📊 Error Summary ({summary['total']} errors):", err=True)

    # Show error categories
    for category, info in summary['categories'].items():
        click.echo(f"  {category}: {info['count']} errors", err=True)

    # Show suggestions
    click.echo("\n💡 Recommended next steps:", err=True)
    for i, suggestion in enumerate(summary['suggestions'], 1):
        click.echo(f"  {i}. {suggestion}", err=True)

    click.echo("", err=True)


def print_info(message: str, quiet: bool = False) -> None:
    """Print info message with formatting.

    Args:
        message: Info message to display
        quiet: If True, suppress output
    """
    if not quiet:
        click.echo("ℹ " + message)


def create_progress_bar(length: int, label: str = "") -> Any:
    """Create a progress bar for long-running operations.

    Args:
        length: Total number of items to process
        label: Label to show with progress bar

    Returns:
        Click progress bar object
    """
    return click.progressbar(
        length=length,
        label=label,
        show_percent=True,
        show_pos=True,
        fill_char='█',
        empty_char='░'
    )


def format_table(data: List[Dict[str, Any]], headers: List[str]) -> str:
    """Format data as a simple table.

    Args:
        data: List of dictionaries with table data
        headers: Column headers

    Returns:
        Formatted table string
    """
    if not data:
        return ""

    # Calculate column widths
    widths = {}
    for header in headers:
        widths[header] = len(header)

    for row in data:
        for header in headers:
            value = str(row.get(header, ""))
            widths[header] = max(widths[header], len(value))

    # Build table
    lines = []

    # Header
    header_line = " | ".join(header.ljust(widths[header]) for header in headers)
    lines.append(header_line)

    # Separator
    sep_line = " | ".join("-" * widths[header] for header in headers)
    lines.append(sep_line)

    # Data rows
    for row in data:
        data_line = " | ".join(str(row.get(header, "")).ljust(widths[header]) for header in headers)
        lines.append(data_line)

    return "\n".join(lines)


def validate_path_exists(ctx, param, value):
    """Click callback to validate that a path exists.

    Args:
        ctx: Click context
        param: Click parameter
        value: Path value to validate

    Returns:
        Path value if valid

    Raises:
        click.BadParameter: If path doesn't exist
    """
    if value is None:
        return value

    from pathlib import Path
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"Path does not exist: {value}")
    return value


def validate_directory(ctx, param, value):
    """Click callback to validate that a path is a directory.

    Args:
        ctx: Click context
        param: Click parameter
        value: Path value to validate

    Returns:
        Path value if valid

    Raises:
        click.BadParameter: If path is not a directory
    """
    if value is None:
        return value

    from pathlib import Path
    path = Path(value)
    if path.exists() and not path.is_dir():
        raise click.BadParameter(f"Path is not a directory: {value}")
    return value


def get_terminal_width() -> int:
    """Get terminal width for formatting output.

    Returns:
        Terminal width in characters, defaults to 80
    """
    try:
        return click.get_terminal_size()[0]
    except:
        return 80


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to fit within specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_list(files: List[str], max_files: int = 10, indent: str = "  ") -> str:
    """Format a list of files for display.

    Args:
        files: List of file names
        max_files: Maximum number of files to show before truncating
        indent: Indentation for each file

    Returns:
        Formatted file list string
    """
    if not files:
        return f"{indent}(no files)"

    lines = []
    for i, file in enumerate(files):
        if i >= max_files:
            remaining = len(files) - max_files
            lines.append(f"{indent}... and {remaining} more files")
            break
        lines.append(f"{indent}- {file}")

    return "\n".join(lines)