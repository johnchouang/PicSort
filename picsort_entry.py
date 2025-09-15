#!/usr/bin/env python3
"""Entry point for PicSort executable."""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# For PyInstaller, also add the src directory to path
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# When bundled by PyInstaller, we need to set the working directory appropriately
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    bundle_dir = sys._MEIPASS
    # Add both the bundle and src directories to the path
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    src_bundle_path = os.path.join(bundle_dir, 'src')
    if src_bundle_path not in sys.path:
        sys.path.insert(0, src_bundle_path)

try:
    from src.cli.main import cli
except ImportError:
    # Fallback for PyInstaller bundled executable
    try:
        from cli.main import cli
    except ImportError:
        # Final fallback - add all necessary paths
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        sys.path.insert(0, os.path.join(current_dir, 'src'))
        from src.cli.main import cli

if __name__ == '__main__':
    sys.exit(cli())