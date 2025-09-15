#!/usr/bin/env python3
"""
Build script for creating PicSort standalone executables.

This script automates the process of building PicSort executables for distribution
using PyInstaller. It handles platform detection, dependency checking, and build
optimization.

Usage:
    python build_executable.py [--clean] [--debug] [--no-upx]

Options:
    --clean     Clean build directories before building
    --debug     Build with debug symbols and console output
    --no-upx    Disable UPX compression (faster build, larger executable)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class ExecutableBuilder:
    """Builder for PicSort standalone executables."""

    def __init__(self):
        """Initialize builder."""
        self.project_root = Path(__file__).parent
        self.spec_file = self.project_root / "picsort.spec"
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"

    def check_requirements(self) -> bool:
        """Check if all build requirements are available.

        Returns:
            True if all requirements are met
        """
        print("Checking build requirements...")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"[FAIL] Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")

        # Check PyInstaller
        try:
            import PyInstaller
            print(f"[OK] PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("[FAIL] PyInstaller not found. Install with: pip install pyinstaller")
            return False

        # Check required dependencies
        required_packages = [
            ('click', 'Click'),
            ('PIL', 'Pillow'),
            ('yaml', 'PyYAML'),
            ('tqdm', 'tqdm'),
        ]

        for package, display_name in required_packages:
            try:
                __import__(package)
                print(f"[OK] {display_name}")
            except ImportError:
                print(f"[FAIL] {display_name} not found. Install with: pip install {display_name.lower()}")
                return False

        # Check UPX (optional but recommended)
        try:
            subprocess.run(['upx', '--version'], capture_output=True, check=True)
            print("[OK] UPX (compression available)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[WARNING] UPX not found (executable will be larger)")

        return True

    def clean_build_directories(self) -> None:
        """Clean build directories."""
        print("Cleaning build directories...")

        directories_to_clean = [self.build_dir, self.dist_dir]
        for directory in directories_to_clean:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"  Removed {directory}")

    def modify_spec_for_options(self, debug: bool, no_upx: bool) -> None:
        """Modify spec file based on build options.

        Args:
            debug: Enable debug mode
            no_upx: Disable UPX compression
        """
        if not (debug or no_upx):
            return  # No modifications needed

        print("Modifying build configuration...")

        # Read current spec file
        with open(self.spec_file, 'r') as f:
            spec_content = f.read()

        # Modify for debug mode
        if debug:
            spec_content = spec_content.replace('debug=False', 'debug=True')
            spec_content = spec_content.replace('strip=False', 'strip=False')  # Keep symbols
            print("  Enabled debug mode")

        # Modify for no UPX
        if no_upx:
            spec_content = spec_content.replace('upx=True', 'upx=False')
            print("  Disabled UPX compression")

        # Write modified spec file
        spec_backup = self.spec_file.with_suffix('.spec.backup')
        shutil.copy2(self.spec_file, spec_backup)

        with open(self.spec_file, 'w') as f:
            f.write(spec_content)

    def restore_spec_file(self) -> None:
        """Restore original spec file."""
        spec_backup = self.spec_file.with_suffix('.spec.backup')
        if spec_backup.exists():
            shutil.move(spec_backup, self.spec_file)

    def build_executable(self) -> bool:
        """Build the executable using PyInstaller.

        Returns:
            True if build succeeded
        """
        print("Building executable...")
        print(f"Platform: {platform.system()} {platform.machine()}")

        try:
            # Run PyInstaller
            cmd = ['pyinstaller', '--clean', str(self.spec_file)]
            result = subprocess.run(cmd, cwd=self.project_root, check=True)

            print("[OK] Build completed successfully!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Build failed with exit code {e.returncode}")
            return False

    def verify_executable(self) -> bool:
        """Verify the built executable works.

        Returns:
            True if executable works
        """
        print("Verifying executable...")

        # Find the executable
        platform_name = platform.system()
        if platform_name == "Windows":
            exe_path = self.dist_dir / "picsort.exe"
        elif platform_name == "Darwin":
            exe_path = self.dist_dir / "PicSort.app" / "Contents" / "MacOS" / "picsort"
        else:
            exe_path = self.dist_dir / "picsort"

        if not exe_path.exists():
            print(f"[FAIL] Executable not found at {exe_path}")
            return False

        try:
            # Test basic functionality
            result = subprocess.run([str(exe_path), '--version'],
                                    capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("[OK] Executable verified successfully")
                return True
            else:
                print(f"[FAIL] Executable test failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("[FAIL] Executable test timed out")
            return False
        except Exception as e:
            print(f"[FAIL] Executable test failed: {e}")
            return False

    def get_build_info(self) -> dict:
        """Get information about the built executable.

        Returns:
            Dictionary with build information
        """
        platform_name = platform.system()
        if platform_name == "Windows":
            exe_path = self.dist_dir / "picsort.exe"
        elif platform_name == "Darwin":
            exe_path = self.dist_dir / "PicSort.app"
        else:
            exe_path = self.dist_dir / "picsort"

        info = {
            'platform': f"{platform.system()} {platform.machine()}",
            'executable_path': str(exe_path),
            'exists': exe_path.exists(),
        }

        if exe_path.exists():
            if platform_name == "Darwin" and exe_path.is_dir():
                # For macOS app bundle, get size of entire bundle
                size = sum(f.stat().st_size for f in exe_path.rglob('*') if f.is_file())
            else:
                size = exe_path.stat().st_size

            info['size_mb'] = size / (1024 * 1024)

        return info

    def print_build_summary(self, success: bool, build_info: dict) -> None:
        """Print build summary.

        Args:
            success: Whether build was successful
            build_info: Build information dictionary
        """
        print("\n" + "=" * 60)
        print("BUILD SUMMARY")
        print("=" * 60)

        if success:
            print("Status: [SUCCESS]")
            print(f"Platform: {build_info['platform']}")
            print(f"Executable: {build_info['executable_path']}")

            if 'size_mb' in build_info:
                print(f"Size: {build_info['size_mb']:.1f} MB")

            print("\nNext steps:")
            print("1. Test the executable with your media files")
            print("2. Distribute the executable to target systems")
            print("3. Consider creating an installer for easier distribution")

        else:
            print("Status: [FAILED]")
            print("\nTroubleshooting:")
            print("1. Check that all dependencies are installed")
            print("2. Ensure you have write permissions in the project directory")
            print("3. Try building with --clean flag")
            print("4. Check PyInstaller documentation for platform-specific issues")

        print("=" * 60)

    def build(self, clean: bool = False, debug: bool = False, no_upx: bool = False) -> bool:
        """Main build method.

        Args:
            clean: Clean build directories first
            debug: Build with debug symbols
            no_upx: Disable UPX compression

        Returns:
            True if build succeeded
        """
        try:
            # Check requirements
            if not self.check_requirements():
                return False

            # Clean if requested
            if clean:
                self.clean_build_directories()

            # Modify spec file for options
            self.modify_spec_for_options(debug, no_upx)

            # Build executable
            success = self.build_executable()

            if success:
                # Verify executable works
                success = self.verify_executable()

            # Get build info and print summary
            build_info = self.get_build_info()
            self.print_build_summary(success, build_info)

            return success

        finally:
            # Always restore original spec file
            self.restore_spec_file()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build PicSort standalone executable")
    parser.add_argument('--clean', action='store_true',
                        help='Clean build directories before building')
    parser.add_argument('--debug', action='store_true',
                        help='Build with debug symbols and console output')
    parser.add_argument('--no-upx', action='store_true',
                        help='Disable UPX compression (faster build, larger executable)')

    args = parser.parse_args()

    builder = ExecutableBuilder()
    success = builder.build(clean=args.clean, debug=args.debug, no_upx=args.no_upx)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()