"""Integration test: dry-run preview functionality.

This test verifies that the --dry-run mode provides accurate previews
of what would be done without actually moving files, as specified
in the user experience requirements.
"""
import pytest
import tempfile
import os
import subprocess
from pathlib import Path
from datetime import datetime
import json


class TestDryRunPreview:
    """Integration tests for dry-run preview functionality."""

    def create_test_scenario(self, test_dir):
        """Create a test scenario with various files and dates."""
        files_info = []

        # Create files with different dates and types
        test_files = [
            ("vacation_1.jpg", datetime(2024, 6, 15)),
            ("vacation_2.png", datetime(2024, 6, 15)),
            ("birthday.gif", datetime(2024, 3, 20)),
            ("wedding.mp4", datetime(2023, 9, 10)),
            ("graduation.mov", datetime(2024, 5, 25)),
            ("document.pdf", datetime(2024, 7, 5))  # Non-media file
        ]

        for filename, file_date in test_files:
            file_path = os.path.join(test_dir, filename)
            Path(file_path).touch()
            os.utime(file_path, (file_date.timestamp(), file_date.timestamp()))

            files_info.append({
                'path': file_path,
                'name': filename,
                'date': file_date,
                'expected_folder': f"{file_date.month:02d}.{file_date.year}"
            })

        return files_info

    def test_dry_run_no_files_moved(self):
        """Test that dry-run mode doesn't actually move any files."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test scenario
            files_info = self.create_test_scenario(test_dir)

            # Run organize in dry-run mode
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run organize failed: {result.stderr}"

            # All original files should still exist in their original locations
            for file_info in files_info:
                assert os.path.exists(file_info['path']), f"Original file {file_info['name']} should still exist"

            # No date folders should be created
            folders = [f for f in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, f))]
            assert len(folders) == 0, "No folders should be created in dry-run mode"

    def test_dry_run_shows_preview_information(self):
        """Test that dry-run mode shows what would be done."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test scenario
            files_info = self.create_test_scenario(test_dir)

            # Run organize in dry-run mode
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run organize failed: {result.stderr}"

            output = result.stdout.lower()

            # Should indicate this is a preview/dry-run
            preview_indicators = ["dry", "preview", "would", "simulation", "plan"]
            assert any(indicator in output for indicator in preview_indicators), f"Should indicate dry-run: {result.stdout}"

            # Should show information about files that would be processed
            for file_info in files_info:
                if file_info['name'].endswith(('.jpg', '.png', '.gif', '.mp4', '.mov')):  # Media files
                    assert file_info['name'] in result.stdout or file_info['expected_folder'] in result.stdout

    def test_dry_run_shows_folder_creation_preview(self):
        """Test that dry-run shows which folders would be created."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test files
            files_info = self.create_test_scenario(test_dir)

            # Run organize in dry-run mode
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run organize failed: {result.stderr}"

            # Should show expected date folders
            media_files = [f for f in files_info if f['name'].endswith(('.jpg', '.png', '.gif', '.mp4', '.mov'))]
            expected_folders = set([f['expected_folder'] for f in media_files])

            for folder in expected_folders:
                assert folder in result.stdout, f"Should mention folder {folder} in dry-run output"

    def test_dry_run_vs_actual_consistency(self):
        """Test that dry-run preview matches actual execution results."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test scenario
            files_info = self.create_test_scenario(test_dir)

            # First, run dry-run
            dry_result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )
            assert dry_result.returncode == 0, f"Dry-run failed: {dry_result.stderr}"

            # Recreate the same scenario (files were not moved)
            # Run actual organize
            actual_result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )
            assert actual_result.returncode == 0, f"Actual organize failed: {actual_result.stderr}"

            # Check that actual results match dry-run predictions
            created_folders = [f for f in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, f))]

            # All folders mentioned in dry-run should exist after actual run
            for folder in created_folders:
                assert folder in dry_result.stdout, f"Folder {folder} should have been mentioned in dry-run"

    def test_dry_run_with_duplicates_preview(self):
        """Test that dry-run shows duplicate file handling preview."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create duplicate files (same name, same date)
            subdir = os.path.join(test_dir, "subfolder")
            os.makedirs(subdir)

            file1 = os.path.join(test_dir, "duplicate.jpg")
            file2 = os.path.join(subdir, "duplicate.jpg")

            Path(file1).touch()
            Path(file2).touch()

            # Same modification time
            test_date = datetime(2024, 4, 10)
            timestamp = test_date.timestamp()
            os.utime(file1, (timestamp, timestamp))
            os.utime(file2, (timestamp, timestamp))

            # Run dry-run with recursive
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run with duplicates failed: {result.stderr}"

            # Should mention duplicate handling
            output = result.stdout.lower()
            duplicate_indicators = ["duplicate", "rename", "conflict", "_1", "_2", "numbering"]
            assert any(indicator in output for indicator in duplicate_indicators), f"Should mention duplicate handling: {result.stdout}"

    def test_dry_run_file_count_accuracy(self):
        """Test that dry-run shows accurate file counts."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create known number of media files
            media_files = [
                "photo1.jpg", "photo2.png", "video1.mp4", "image.gif"
            ]
            non_media_files = [
                "document.pdf", "text.txt", "data.csv"
            ]

            all_files = media_files + non_media_files
            for filename in all_files:
                file_path = os.path.join(test_dir, filename)
                Path(file_path).touch()
                # Same date for simplicity
                test_date = datetime(2024, 1, 15)
                os.utime(file_path, (test_date.timestamp(), test_date.timestamp()))

            # Run dry-run (should only process media files by default)
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run failed: {result.stderr}"

            # Should show correct count of media files to be processed
            output = result.stdout
            # Look for file count information
            assert str(len(media_files)) in output or "4" in output, f"Should mention processing {len(media_files)} files"

    def test_dry_run_with_all_files_option(self):
        """Test dry-run with --all-files option shows all file types."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create mixed file types
            test_files = [
                "image.jpg", "document.pdf", "script.py", "data.json", "video.mp4"
            ]

            for filename in test_files:
                file_path = os.path.join(test_dir, filename)
                Path(file_path).touch()
                test_date = datetime(2024, 2, 20)
                os.utime(file_path, (test_date.timestamp(), test_date.timestamp()))

            # Run dry-run with --all-files
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--all-files", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run with --all-files failed: {result.stderr}"

            # Should mention all file types
            output = result.stdout
            for filename in test_files:
                assert filename in output, f"Should mention {filename} in --all-files dry-run"

    def test_dry_run_with_verbose_output(self):
        """Test that dry-run with --verbose shows detailed preview information."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test files
            files_info = self.create_test_scenario(test_dir)

            # Run dry-run with verbose
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--verbose", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Verbose dry-run failed: {result.stderr}"

            output = result.stdout.lower()

            # Should show detailed information
            verbose_indicators = [
                "analyzing", "scanning", "would move", "would create", "processing", "target", "source"
            ]
            assert any(indicator in output for indicator in verbose_indicators), f"Should show verbose details: {result.stdout}"

    def test_dry_run_empty_directory(self):
        """Test dry-run behavior with empty directory."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Run dry-run on empty directory
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Empty directory dry-run failed: {result.stderr}"

            # Should indicate no files to process
            output = result.stdout.lower()
            empty_indicators = ["no files", "0 files", "nothing to", "empty", "no media files"]
            assert any(indicator in output for indicator in empty_indicators), f"Should indicate empty directory: {result.stdout}"

    def test_dry_run_with_different_date_formats(self):
        """Test that dry-run shows correct folder names for different date formats."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file
            test_file = os.path.join(test_dir, "test.jpg")
            Path(test_file).touch()
            test_date = datetime(2024, 3, 15)
            os.utime(test_file, (test_date.timestamp(), test_date.timestamp()))

            # Test different date formats
            format_tests = [
                ("MM.YYYY", "03.2024"),
                ("YYYY.MM", "2024.03"),
                ("YYYY-MM", "2024-03"),
                ("MMM_YYYY", "Mar_2024")
            ]

            for date_format, expected_folder in format_tests:
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", "organize", "--date-format", date_format, "--dry-run", "--yes", test_dir],
                    capture_output=True,
                    text=True
                )

                assert result.returncode == 0, f"Dry-run with format {date_format} failed: {result.stderr}"
                assert expected_folder in result.stdout, f"Should show folder {expected_folder} for format {date_format}"