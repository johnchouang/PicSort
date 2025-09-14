"""Integration test: handle duplicate filenames.

This test verifies that the system correctly handles duplicate filenames
when organizing files into date folders, using the numbering strategy
defined in the specification (file_1.jpg, file_2.jpg, etc.).
"""
import pytest
import tempfile
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import time


class TestDuplicateFilenames:
    """Integration tests for handling duplicate filenames."""

    def create_files_with_same_names(self, test_dir):
        """Create files with identical names but in different subdirs."""
        # Create subdirectories
        subdir1 = os.path.join(test_dir, "folder1")
        subdir2 = os.path.join(test_dir, "folder2")
        os.makedirs(subdir1)
        os.makedirs(subdir2)

        # Create files with same name in different locations
        file1_path = os.path.join(subdir1, "photo.jpg")
        file2_path = os.path.join(subdir2, "photo.jpg")
        root_file_path = os.path.join(test_dir, "photo.jpg")

        # Create files with different content
        with open(file1_path, "w") as f:
            f.write("content from folder1")
        with open(file2_path, "w") as f:
            f.write("content from folder2")
        with open(root_file_path, "w") as f:
            f.write("content from root")

        # Set same modification time (same target date folder)
        target_date = datetime(2024, 3, 15).timestamp()
        os.utime(file1_path, (target_date, target_date))
        os.utime(file2_path, (target_date, target_date))
        os.utime(root_file_path, (target_date, target_date))

        return [file1_path, file2_path, root_file_path]

    def test_duplicate_filenames_get_numbered(self):
        """Test that duplicate filenames get numbered when moved to same date folder."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create files with duplicate names
            duplicate_files = self.create_files_with_same_names(test_dir)

            # Run organize with recursive option to process all files
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize with duplicates failed: {result.stderr}"

            # Find the date folder that was created
            date_folders = []
            for item in os.listdir(test_dir):
                item_path = os.path.join(test_dir, item)
                if os.path.isdir(item_path) and "." in item:  # MM.YYYY format
                    date_folders.append(item_path)

            assert len(date_folders) == 1, "Should create exactly one date folder"
            date_folder = date_folders[0]

            # Check files in the date folder
            moved_files = os.listdir(date_folder)
            jpg_files = [f for f in moved_files if f.endswith('.jpg')]

            assert len(jpg_files) == 3, f"Should have 3 JPG files, found: {jpg_files}"

            # Should have photo.jpg, photo_1.jpg, photo_2.jpg (or similar numbering)
            expected_patterns = ["photo.jpg", "photo_1.jpg", "photo_2.jpg"]

            # Check that files are properly renamed to avoid conflicts
            assert "photo.jpg" in jpg_files, "Should have original photo.jpg"

            # Check that other files are numbered (could be _1, _2 or similar pattern)
            numbered_files = [f for f in jpg_files if f != "photo.jpg"]
            assert len(numbered_files) == 2, "Should have 2 numbered duplicate files"

    def test_duplicate_content_preservation(self):
        """Test that duplicate files preserve their original content."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create files with duplicate names but different content
            duplicate_files = self.create_files_with_same_names(test_dir)

            # Store original content for verification
            original_content = {}
            for file_path in duplicate_files:
                with open(file_path, "r") as f:
                    original_content[file_path] = f.read()

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Find all moved JPG files
            moved_files = []
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.jpg'):
                        moved_files.append(os.path.join(root, file))

            assert len(moved_files) == 3, "Should have moved 3 files"

            # Read content of moved files
            moved_content = {}
            for file_path in moved_files:
                with open(file_path, "r") as f:
                    moved_content[file_path] = f.read()

            # Verify all original content is preserved (order might be different)
            original_values = set(original_content.values())
            moved_values = set(moved_content.values())
            assert original_values == moved_values, "All original content should be preserved"

    def test_no_duplicates_no_numbering(self):
        """Test that files with unique names don't get numbered."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create files with unique names
            unique_files = [
                os.path.join(test_dir, "photo1.jpg"),
                os.path.join(test_dir, "photo2.jpg"),
                os.path.join(test_dir, "photo3.jpg")
            ]

            for file_path in unique_files:
                Path(file_path).touch()
                # Set same date so they go to same folder
                target_date = datetime(2024, 5, 10).timestamp()
                os.utime(file_path, (target_date, target_date))

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Find moved files
            moved_files = []
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.jpg'):
                        moved_files.append(file)

            # Should keep original names (no numbering needed)
            expected_names = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
            assert set(moved_files) == set(expected_names), f"Should keep original names: {moved_files}"

    def test_many_duplicates_numbering(self):
        """Test numbering with many duplicate files."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create many files with same name
            num_duplicates = 5
            duplicate_files = []

            for i in range(num_duplicates):
                subdir = os.path.join(test_dir, f"dir{i}")
                os.makedirs(subdir)
                file_path = os.path.join(subdir, "image.png")

                with open(file_path, "w") as f:
                    f.write(f"content from dir{i}")

                # Same modification time
                target_date = datetime(2024, 6, 20).timestamp()
                os.utime(file_path, (target_date, target_date))
                duplicate_files.append(file_path)

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Find moved PNG files
            moved_files = []
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.png'):
                        moved_files.append(file)

            assert len(moved_files) == num_duplicates, f"Should have {num_duplicates} files"

            # Should have image.png and numbered variants
            assert "image.png" in moved_files, "Should have original image.png"
            numbered_files = [f for f in moved_files if f != "image.png"]
            assert len(numbered_files) == num_duplicates - 1, "Should have numbered variants"

    def test_duplicate_handling_in_dry_run(self):
        """Test that dry-run mode shows duplicate handling behavior."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create duplicate files
            duplicate_files = self.create_files_with_same_names(test_dir)

            # Run organize in dry-run mode
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--dry-run", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dry-run organize failed: {result.stderr}"

            # Original files should still exist
            for file_path in duplicate_files:
                assert os.path.exists(file_path), f"File {file_path} should still exist in dry-run"

            # Should indicate duplicate handling in output
            output = result.stdout.lower()
            duplicate_terms = ["duplicate", "rename", "number", "conflict", "_1", "_2"]
            assert any(term in output for term in duplicate_terms), f"Should mention duplicate handling: {result.stdout}"

    def test_mixed_extensions_no_false_duplicates(self):
        """Test that files with same base name but different extensions aren't treated as duplicates."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create files with same base name but different extensions
            files = [
                os.path.join(test_dir, "image.jpg"),
                os.path.join(test_dir, "image.png"),
                os.path.join(test_dir, "image.gif")
            ]

            for file_path in files:
                Path(file_path).touch()
                # Same date
                target_date = datetime(2024, 7, 15).timestamp()
                os.utime(file_path, (target_date, target_date))

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Find moved files
            moved_files = []
            for root, dirs, files in os.walk(test_dir):
                moved_files.extend(files)

            # Should keep original names (different extensions = no duplicates)
            expected_names = ["image.jpg", "image.png", "image.gif"]
            assert set(moved_files) == set(expected_names), f"Should keep original names: {moved_files}"

            # None should be numbered
            numbered_files = [f for f in moved_files if "_1" in f or "_2" in f]
            assert len(numbered_files) == 0, "Should not number files with different extensions"