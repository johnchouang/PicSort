"""Integration test: create date folders automatically.

This test verifies that the system automatically creates date-based folders
in the correct MM.YYYY format and organizes files into them appropriately.
"""
import pytest
import tempfile
import os
import subprocess
from pathlib import Path
from datetime import datetime
import calendar


class TestFolderCreation:
    """Integration tests for automatic date folder creation."""

    def create_files_with_different_dates(self, test_dir):
        """Create test files with different modification dates."""
        files_info = []

        # Create files for different months/years
        dates_and_files = [
            (datetime(2023, 1, 15), "jan_2023.jpg"),
            (datetime(2023, 6, 20), "jun_2023.png"),
            (datetime(2024, 3, 10), "mar_2024.gif"),
            (datetime(2024, 12, 25), "dec_2024.mp4"),
            (datetime(2022, 11, 5), "nov_2022.mov")
        ]

        for date_obj, filename in dates_and_files:
            file_path = os.path.join(test_dir, filename)
            Path(file_path).touch()

            # Set modification time
            timestamp = date_obj.timestamp()
            os.utime(file_path, (timestamp, timestamp))

            files_info.append({
                'path': file_path,
                'name': filename,
                'date': date_obj,
                'expected_folder': f"{date_obj.month:02d}.{date_obj.year}"
            })

        return files_info

    def test_automatic_folder_creation_mm_yyyy_format(self):
        """Test that date folders are created in MM.YYYY format."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create files with different dates
            files_info = self.create_files_with_different_dates(test_dir)

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Check that correct folders were created
            created_folders = []
            for item in os.listdir(test_dir):
                item_path = os.path.join(test_dir, item)
                if os.path.isdir(item_path):
                    created_folders.append(item)

            expected_folders = list(set([f['expected_folder'] for f in files_info]))
            assert len(created_folders) == len(expected_folders), f"Should create {len(expected_folders)} folders"

            # Verify folder names follow MM.YYYY format
            for folder in created_folders:
                assert folder in expected_folders, f"Unexpected folder: {folder}"
                # Validate MM.YYYY format
                assert "." in folder, f"Folder {folder} should contain dot"
                month_str, year_str = folder.split(".")
                assert len(month_str) == 2, f"Month should be 2 digits: {month_str}"
                assert len(year_str) == 4, f"Year should be 4 digits: {year_str}"
                assert 1 <= int(month_str) <= 12, f"Month should be 1-12: {month_str}"
                assert int(year_str) >= 2000, f"Year should be reasonable: {year_str}"

    def test_files_placed_in_correct_date_folders(self):
        """Test that files are placed in their corresponding date folders."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create files with known dates
            files_info = self.create_files_with_different_dates(test_dir)

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Verify each file is in the correct folder
            for file_info in files_info:
                expected_folder = os.path.join(test_dir, file_info['expected_folder'])
                expected_file_path = os.path.join(expected_folder, file_info['name'])

                assert os.path.exists(expected_folder), f"Folder {file_info['expected_folder']} should exist"
                assert os.path.exists(expected_file_path), f"File {file_info['name']} should be in {file_info['expected_folder']}"

                # Original file should be gone
                assert not os.path.exists(file_info['path']), f"Original file {file_info['path']} should be moved"

    def test_folder_creation_with_different_date_formats(self):
        """Test folder creation with different --date-format options."""
        format_tests = [
            ("MM.YYYY", datetime(2024, 5, 15), "05.2024"),
            ("YYYY.MM", datetime(2024, 5, 15), "2024.05"),
            ("YYYY-MM", datetime(2024, 5, 15), "2024-05"),
            ("MMM_YYYY", datetime(2024, 5, 15), "May_2024")
        ]

        for date_format, test_date, expected_folder in format_tests:
            with tempfile.TemporaryDirectory() as test_dir:
                # Create test file
                test_file = os.path.join(test_dir, "test.jpg")
                Path(test_file).touch()
                os.utime(test_file, (test_date.timestamp(), test_date.timestamp()))

                # Run organize with specific date format
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", "organize", "--date-format", date_format, "--yes", test_dir],
                    capture_output=True,
                    text=True
                )

                assert result.returncode == 0, f"Organize with format {date_format} failed: {result.stderr}"

                # Check folder was created with correct format
                folders = [f for f in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, f))]
                assert len(folders) == 1, f"Should create exactly one folder for format {date_format}"
                assert folders[0] == expected_folder, f"Expected folder {expected_folder}, got {folders[0]}"

    def test_no_folders_created_for_dry_run(self):
        """Test that no folders are created in dry-run mode."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test files
            files_info = self.create_files_with_different_dates(test_dir)

            # Run organize in dry-run mode
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run organize failed: {result.stderr}"

            # No folders should be created
            folders = [f for f in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, f))]
            assert len(folders) == 0, "No folders should be created in dry-run mode"

            # Original files should still exist
            for file_info in files_info:
                assert os.path.exists(file_info['path']), f"Original file {file_info['name']} should still exist"

    def test_folder_creation_with_existing_folders(self):
        """Test behavior when target date folders already exist."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file
            test_file = os.path.join(test_dir, "test.png")
            Path(test_file).touch()

            test_date = datetime(2024, 7, 10)
            os.utime(test_file, (test_date.timestamp(), test_date.timestamp()))

            # Pre-create the target folder
            target_folder = os.path.join(test_dir, "07.2024")
            os.makedirs(target_folder)

            # Add existing file in the folder
            existing_file = os.path.join(target_folder, "existing.jpg")
            Path(existing_file).touch()

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize with existing folder failed: {result.stderr}"

            # Test file should be moved to existing folder
            moved_test_file = os.path.join(target_folder, "test.png")
            assert os.path.exists(moved_test_file), "Test file should be moved to existing folder"

            # Existing file should still be there
            assert os.path.exists(existing_file), "Existing file should remain"

            # Should have both files in the folder
            files_in_folder = os.listdir(target_folder)
            assert len(files_in_folder) == 2, "Folder should contain both files"
            assert "test.png" in files_in_folder and "existing.jpg" in files_in_folder

    def test_folder_creation_permissions(self):
        """Test that created folders have appropriate permissions."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file
            test_file = os.path.join(test_dir, "permission_test.gif")
            Path(test_file).touch()

            test_date = datetime(2024, 8, 20)
            os.utime(test_file, (test_date.timestamp(), test_date.timestamp()))

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Check created folder permissions
            created_folder = os.path.join(test_dir, "08.2024")
            assert os.path.exists(created_folder), "Date folder should be created"

            # Should be able to read and write to the folder
            folder_stat = os.stat(created_folder)
            # Check owner has read, write, execute permissions
            assert folder_stat.st_mode & 0o700, "Owner should have read/write/execute permissions"

    def test_nested_folder_structure_with_recursive(self):
        """Test folder creation with recursive processing of nested directories."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create nested directory structure
            subdir1 = os.path.join(test_dir, "photos", "2024")
            subdir2 = os.path.join(test_dir, "videos")
            os.makedirs(subdir1)
            os.makedirs(subdir2)

            # Create files in different subdirectories
            file1 = os.path.join(subdir1, "photo.jpg")
            file2 = os.path.join(subdir2, "video.mp4")
            file3 = os.path.join(test_dir, "root.png")

            for file_path in [file1, file2, file3]:
                Path(file_path).touch()
                # Same date so they go to same folder
                test_date = datetime(2024, 9, 15)
                os.utime(file_path, (test_date.timestamp(), test_date.timestamp()))

            # Run organize with recursive option
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Recursive organize failed: {result.stderr}"

            # Should create one date folder at the root level
            date_folder = os.path.join(test_dir, "09.2024")
            assert os.path.exists(date_folder), "Date folder should be created at root level"

            # All files should be moved to the date folder
            files_in_date_folder = os.listdir(date_folder)
            expected_files = ["photo.jpg", "video.mp4", "root.png"]
            assert set(files_in_date_folder) == set(expected_files), "All files should be in date folder"

    def test_folder_naming_edge_cases(self):
        """Test folder naming for edge cases (leap year, different months)."""
        edge_cases = [
            (datetime(2020, 2, 29), "02.2020"),  # Leap year
            (datetime(2024, 1, 1), "01.2024"),   # New Year's Day
            (datetime(2024, 12, 31), "12.2024"), # New Year's Eve
            (datetime(2000, 1, 1), "01.2000"),   # Y2K
        ]

        for test_date, expected_folder in edge_cases:
            with tempfile.TemporaryDirectory() as test_dir:
                # Create test file
                test_file = os.path.join(test_dir, f"edge_case_{test_date.strftime('%Y%m%d')}.jpg")
                Path(test_file).touch()
                os.utime(test_file, (test_date.timestamp(), test_date.timestamp()))

                # Run organize
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                    capture_output=True,
                    text=True
                )

                assert result.returncode == 0, f"Edge case organize failed for {test_date}: {result.stderr}"

                # Check correct folder was created
                folders = [f for f in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, f))]
                assert len(folders) == 1, f"Should create exactly one folder for {test_date}"
                assert folders[0] == expected_folder, f"Expected {expected_folder}, got {folders[0]} for {test_date}"