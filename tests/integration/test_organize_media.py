"""Integration test: organize folder with mixed media files.

This test verifies the end-to-end user story of organizing a folder
containing various media files by creation date into MM.YYYY folders.
"""
import pytest
import tempfile
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import time


class TestOrganizeMedia:
    """Integration tests for organizing mixed media files."""

    def create_test_media_files(self, test_dir):
        """Create test media files with different dates."""
        files_created = []

        # Create different media file types
        media_files = [
            "photo1.jpg",
            "image2.jpeg",
            "picture3.png",
            "graphic4.gif",
            "video1.mp4",
            "movie2.mov",
            "clip3.avi"
        ]

        # Create files with different modification times
        base_date = datetime(2024, 1, 15)  # January 2024

        for i, filename in enumerate(media_files):
            file_path = os.path.join(test_dir, filename)
            Path(file_path).touch()

            # Set different modification times for each file
            file_date = base_date + timedelta(days=i * 30)  # Spread across months
            timestamp = file_date.timestamp()
            os.utime(file_path, (timestamp, timestamp))

            files_created.append({
                'path': file_path,
                'name': filename,
                'date': file_date
            })

        return files_created

    def test_organize_mixed_media_dry_run(self):
        """Test organizing mixed media files in dry-run mode."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test media files
            files = self.create_test_media_files(test_dir)

            # Run organize command in dry-run mode
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            # Should succeed
            assert result.returncode == 0, f"Organize dry-run failed: {result.stderr}"

            # Original files should still be in place (dry-run)
            for file_info in files:
                assert os.path.exists(file_info['path']), f"File {file_info['name']} should still exist"

            # Should show what would be organized
            output = result.stdout.lower()
            assert "would" in output or "preview" in output or "dry" in output

    def test_organize_mixed_media_actual_move(self):
        """Test actually organizing mixed media files (not dry-run)."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test media files
            files = self.create_test_media_files(test_dir)
            original_files = [f['name'] for f in files]

            # Run organize command (actual move)
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            # Should succeed
            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Original files should be moved (not in root anymore)
            for file_info in files:
                assert not os.path.exists(file_info['path']), f"File {file_info['name']} should be moved"

            # Should create date-based folders
            date_folders = []
            for item in os.listdir(test_dir):
                item_path = os.path.join(test_dir, item)
                if os.path.isdir(item_path):
                    date_folders.append(item)

            assert len(date_folders) > 0, "Should create date-based folders"

            # Check MM.YYYY format
            for folder in date_folders:
                assert "." in folder, f"Folder {folder} should use MM.YYYY format"
                parts = folder.split(".")
                assert len(parts) == 2, f"Folder {folder} should have MM.YYYY format"
                assert len(parts[0]) == 2, f"Month part should be 2 digits: {folder}"
                assert len(parts[1]) == 4, f"Year part should be 4 digits: {folder}"

    def test_organize_preserves_file_content(self):
        """Test that organizing preserves file content."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file with content
            test_file = os.path.join(test_dir, "test.jpg")
            test_content = b"fake JPEG content for testing"
            with open(test_file, "wb") as f:
                f.write(test_content)

            # Set modification time
            past_date = datetime(2024, 3, 15).timestamp()
            os.utime(test_file, (past_date, past_date))

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Find the moved file
            moved_file = None
            for root, dirs, files in os.walk(test_dir):
                if "test.jpg" in files:
                    moved_file = os.path.join(root, "test.jpg")
                    break

            assert moved_file is not None, "File should be moved to date folder"

            # Check content is preserved
            with open(moved_file, "rb") as f:
                moved_content = f.read()

            assert moved_content == test_content, "File content should be preserved"

    def test_organize_handles_empty_directory(self):
        """Test organizing empty directory."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Run organize on empty directory
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            # Should succeed (nothing to organize)
            assert result.returncode == 0, f"Organize empty dir failed: {result.stderr}"

            # Should indicate no files to process
            output = result.stdout.lower()
            assert "0" in output or "no files" in output or "empty" in output

    def test_organize_with_recursive_option(self):
        """Test organizing with recursive option."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create nested directory structure
            subdir = os.path.join(test_dir, "subfolder")
            os.makedirs(subdir)

            # Create files in both root and subdirectory
            root_file = os.path.join(test_dir, "root.jpg")
            sub_file = os.path.join(subdir, "nested.jpg")

            Path(root_file).touch()
            Path(sub_file).touch()

            # Set modification times
            past_date = datetime(2024, 2, 15).timestamp()
            os.utime(root_file, (past_date, past_date))
            os.utime(sub_file, (past_date, past_date))

            # Run organize with recursive option
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Recursive organize failed: {result.stderr}"

            # Both files should be processed
            # Find moved files
            moved_files = []
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.jpg'):
                        moved_files.append(os.path.join(root, file))

            # Should have moved both files to date folders
            assert len(moved_files) == 2, f"Should move 2 files, found: {moved_files}"

    def test_organize_specific_file_types(self):
        """Test organizing only specific file types."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create mixed file types
            jpg_file = os.path.join(test_dir, "image.jpg")
            png_file = os.path.join(test_dir, "image.png")
            txt_file = os.path.join(test_dir, "document.txt")

            Path(jpg_file).touch()
            Path(png_file).touch()
            Path(txt_file).touch()

            # Set modification times
            past_date = datetime(2024, 4, 15).timestamp()
            for file_path in [jpg_file, png_file, txt_file]:
                os.utime(file_path, (past_date, past_date))

            # Run organize with specific file types
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--file-types", ".jpg", ".png", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"File type organize failed: {result.stderr}"

            # JPG and PNG should be moved
            assert not os.path.exists(jpg_file), "JPG should be moved"
            assert not os.path.exists(png_file), "PNG should be moved"

            # TXT should remain
            assert os.path.exists(txt_file), "TXT should not be moved"

    def test_organize_shows_progress_info(self):
        """Test that organize shows progress information."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create some test files
            files = self.create_test_media_files(test_dir)

            # Run organize with verbose output
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--verbose", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Verbose organize failed: {result.stderr}"

            # Should show processing information
            output = result.stdout.lower()
            progress_terms = ["processing", "moving", "files", "complete", "processed"]
            assert any(term in output for term in progress_terms), f"Should show progress info: {result.stdout}"