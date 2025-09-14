"""Main CLI entry point for PicSort."""
import sys
import logging
from pathlib import Path

import click

from .commands.organize import organize
from .commands.scan import scan
from .commands.config import config
from .commands.undo import undo

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@click.group()
@click.version_option(version='1.0.0', prog_name='picsort')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.pass_context
def cli(ctx, verbose, quiet):
    """PicSort - Organize your media files by date.
    
    Organize photos and videos into date-based folders (MM.YYYY format) for easy browsing.
    Files are moved safely with verification to prevent data loss.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    
    # Store global options
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    
    # Adjust logging level based on verbosity
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(logging.INFO)


# Add version command
@cli.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def version(ctx, output_json):
    """Show version information.

    Display the current version of PicSort along with build and Python information.

    Examples:
      picsort version
      picsort version --json
    """
    import sys
    import platform

    version_info = {
        'version': '1.0.0',
        'build': 'development',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': platform.system()
    }

    if output_json:
        import json
        print(json.dumps(version_info, indent=2))
    else:
        quiet = ctx.obj.get('quiet', False)
        if not quiet:
            print(f"PicSort v{version_info['version']}")
            print(f"Build: {version_info['build']}")
            print(f"Python: {version_info['python_version']}")

    return 0


# Add commands
cli.add_command(organize)
cli.add_command(scan)
cli.add_command(config)
cli.add_command(undo)
cli.add_command(version)


if __name__ == '__main__':
    cli()
