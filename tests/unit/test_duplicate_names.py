"""Unit tests for duplicate filename handling."""
import pytest
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from src.lib.file_mover import FileMover
from src.models.media_file import MediaFile
from src.models.configuration import Configuration
from src.models.file_operation import FileOperation


class TestDuplicateHandling:
    """Test duplicate filename handling functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(self.source_dir)
        os.makedirs(self.target_dir)

        # Default configuration
        self.config = Configuration()
        self.config.verify_checksum = False  # Disable for faster testing
        self.config.duplicate_handling = 'increment'  # Default to increment

        self.file_mover = FileMover(self.config)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_destination_path_no_duplicate(self):
        """Test getting destination path when no duplicate exists."""
        media_file = MediaFile(os.path.join(self.source_dir, "test.jpg"))
        media_file.filename = "test.jpg"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        expected = os.path.join(self.target_dir, "test.jpg")

        assert result == expected

    def test_get_destination_path_dry_run_with_existing(self):
        """Test getting destination path in dry run mode (should use original name)."""
        # Create existing file
        existing_file = os.path.join(self.target_dir, "test.jpg")
        with open(existing_file, 'w') as f:
            f.write("existing content")

        media_file = MediaFile(os.path.join(self.source_dir, "test.jpg"))
        media_file.filename = "test.jpg"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=True)
        expected = os.path.join(self.target_dir, "test.jpg")

        assert result == expected  # Should use original name in dry run

    def test_get_destination_path_increment_single_duplicate(self):
        """Test incrementing filename when single duplicate exists."""
        # Create existing file
        existing_file = os.path.join(self.target_dir, "test.jpg")
        with open(existing_file, 'w') as f:
            f.write("existing content")

        media_file = MediaFile(os.path.join(self.source_dir, "test.jpg"))
        media_file.filename = "test.jpg"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        expected = os.path.join(self.target_dir, "test_1.jpg")

        assert result == expected

    def test_get_destination_path_increment_multiple_duplicates(self):
        """Test incrementing filename when multiple duplicates exist."""
        # Create existing files
        for i in range(3):
            suffix = f"_{i}" if i > 0 else ""
            existing_file = os.path.join(self.target_dir, f"test{suffix}.jpg")
            with open(existing_file, 'w') as f:
                f.write(f"existing content {i}")

        media_file = MediaFile(os.path.join(self.source_dir, "test.jpg"))
        media_file.filename = "test.jpg"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        expected = os.path.join(self.target_dir, "test_3.jpg")

        assert result == expected

    def test_get_destination_path_increment_complex_filename(self):
        """Test incrementing complex filenames with multiple dots."""
        # Create existing file
        existing_file = os.path.join(self.target_dir, "IMG_20231225_143000.DSC_1234.jpg")
        with open(existing_file, 'w') as f:
            f.write("existing content")

        media_file = MediaFile(os.path.join(self.source_dir, "IMG_20231225_143000.DSC_1234.jpg"))
        media_file.filename = "IMG_20231225_143000.DSC_1234.jpg"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        expected = os.path.join(self.target_dir, "IMG_20231225_143000.DSC_1234_1.jpg")

        assert result == expected

    def test_get_destination_path_increment_no_extension(self):
        """Test incrementing filenames with no extension."""
        # Create existing file
        existing_file = os.path.join(self.target_dir, "README")
        with open(existing_file, 'w') as f:
            f.write("existing content")

        media_file = MediaFile(os.path.join(self.source_dir, "README"))
        media_file.filename = "README"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        expected = os.path.join(self.target_dir, "README_1")

        assert result == expected

    def test_get_destination_path_skip_mode(self):
        """Test skip mode returns original path even with duplicates."""
        self.config.duplicate_handling = 'skip'

        # Create existing file
        existing_file = os.path.join(self.target_dir, "test.jpg")
        with open(existing_file, 'w') as f:
            f.write("existing content")

        media_file = MediaFile(os.path.join(self.source_dir, "test.jpg"))
        media_file.filename = "test.jpg"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        expected = os.path.join(self.target_dir, "test.jpg")

        assert result == expected  # Should return original path in skip mode

    def test_get_destination_path_overwrite_mode(self):
        """Test overwrite mode returns original path even with duplicates."""
        self.config.duplicate_handling = 'overwrite'

        # Create existing file
        existing_file = os.path.join(self.target_dir, "test.jpg")
        with open(existing_file, 'w') as f:
            f.write("existing content")

        media_file = MediaFile(os.path.join(self.source_dir, "test.jpg"))
        media_file.filename = "test.jpg"

        result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        expected = os.path.join(self.target_dir, "test.jpg")

        assert result == expected  # Should return original path in overwrite mode

    def test_get_destination_path_increment_safety_limit(self):
        """Test safety limit prevents infinite loop with too many duplicates."""
        self.config.duplicate_handling = 'increment'

        media_file = MediaFile(os.path.join(self.source_dir, "test.jpg"))
        media_file.filename = "test.jpg"

        # Mock os.path.exists to always return True (simulate infinite duplicates)
        original_exists = os.path.exists
        def mock_exists(path):
            return True  # Always report file exists

        import src.lib.file_mover
        src.lib.file_mover.os.path.exists = mock_exists

        try:
            with pytest.raises(ValueError, match="Too many duplicates"):
                self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
        finally:
            # Restore original function
            src.lib.file_mover.os.path.exists = original_exists

    def test_move_single_file_with_increment_duplicate(self):
        """Test moving a single file with duplicate handling via increment."""
        # Create source file
        source_file = os.path.join(self.source_dir, "photo.jpg")
        with open(source_file, 'w') as f:
            f.write("source content")

        # Create existing target file
        existing_target = os.path.join(self.target_dir, "photo.jpg")
        with open(existing_target, 'w') as f:
            f.write("existing target content")

        media_file = MediaFile(source_file)
        media_file.filename = "photo.jpg"
        media_file.size = len("source content")

        operation = self.file_mover._move_single_file(media_file, self.target_dir, dry_run=False)

        # Should have incremented the filename
        expected_dest = os.path.join(self.target_dir, "photo_1.jpg")
        assert operation.destination_path == expected_dest
        assert operation.status == 'completed'

        # Check files exist correctly
        assert os.path.exists(expected_dest)
        assert not os.path.exists(source_file)  # Source should be removed
        assert os.path.exists(existing_target)  # Original target should remain

        # Check content
        with open(expected_dest, 'r') as f:
            assert f.read() == "source content"
        with open(existing_target, 'r') as f:
            assert f.read() == "existing target content"

    def test_move_single_file_overwrite_mode(self):
        """Test moving a single file with overwrite duplicate handling."""
        self.config.duplicate_handling = 'overwrite'

        # Create source file
        source_file = os.path.join(self.source_dir, "photo.jpg")
        with open(source_file, 'w') as f:
            f.write("new content")

        # Create existing target file
        existing_target = os.path.join(self.target_dir, "photo.jpg")
        with open(existing_target, 'w') as f:
            f.write("old content")

        media_file = MediaFile(source_file)
        media_file.filename = "photo.jpg"
        media_file.size = len("new content")

        operation = self.file_mover._move_single_file(media_file, self.target_dir, dry_run=False)

        assert operation.destination_path == existing_target
        assert operation.status == 'completed'

        # Check source is removed
        assert not os.path.exists(source_file)

        # Check target was overwritten
        assert os.path.exists(existing_target)
        with open(existing_target, 'r') as f:
            assert f.read() == "new content"

    def test_move_files_multiple_duplicates_same_folder(self):
        """Test moving multiple files with same name to same folder."""
        # Create multiple source files with same name
        source_files = []
        media_files = []

        for i in range(3):
            source_file = os.path.join(self.source_dir, f"source{i}", "photo.jpg")
            os.makedirs(os.path.dirname(source_file), exist_ok=True)

            with open(source_file, 'w') as f:
                f.write(f"content {i}")

            media_file = MediaFile(source_file)
            media_file.filename = "photo.jpg"
            media_file.size = len(f"content {i}")

            source_files.append(source_file)
            media_files.append(media_file)

        # Create organization with all files going to same folder
        organization = {self.target_dir: media_files}

        operations = self.file_mover.move_files(organization, dry_run=False)

        assert len(operations) == 3
        assert all(op.status == 'completed' for op in operations)

        # Check destination paths are incremented
        expected_destinations = [
            os.path.join(self.target_dir, "photo.jpg"),
            os.path.join(self.target_dir, "photo_1.jpg"),
            os.path.join(self.target_dir, "photo_2.jpg"),
        ]

        actual_destinations = [op.destination_path for op in operations]
        assert set(actual_destinations) == set(expected_destinations)

        # Check all destination files exist with correct content
        for i, dest in enumerate(expected_destinations):
            assert os.path.exists(dest)
            with open(dest, 'r') as f:
                content = f.read()
                assert content in [f"content {j}" for j in range(3)]

        # Check all source files are removed
        for source_file in source_files:
            assert not os.path.exists(source_file)

    def test_duplicate_name_pattern_matching(self):
        """Test that duplicate patterns are correctly identified."""
        # Test various filename patterns and their incremented versions
        test_cases = [
            ("photo.jpg", "photo_1.jpg"),
            ("IMG_1234.JPG", "IMG_1234_1.JPG"),
            ("document.pdf", "document_1.pdf"),
            ("file", "file_1"),
            ("my.file.txt", "my.file_1.txt"),
            ("file.with.many.dots.ext", "file.with.many.dots_1.ext"),
        ]

        for original_name, expected_incremented in test_cases:
            # Create existing file
            existing_file = os.path.join(self.target_dir, original_name)
            with open(existing_file, 'w') as f:
                f.write("existing")

            media_file = MediaFile(os.path.join(self.source_dir, original_name))
            media_file.filename = original_name

            result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
            expected_path = os.path.join(self.target_dir, expected_incremented)

            assert result == expected_path, f"Failed for filename: {original_name}"

            # Clean up for next test
            os.remove(existing_file)

    def test_duplicate_handling_edge_cases(self):
        """Test edge cases in duplicate handling."""
        # Test with various special characters and Unicode
        special_names = [
            "файл.jpg",  # Cyrillic
            "café.jpg",   # Accented characters
            "file with spaces.jpg",
            "file-with-dashes.jpg",
            "file_with_underscores.jpg",
            "(parentheses).jpg",
            "[brackets].jpg",
            "file&symbols!.jpg",
        ]

        for name in special_names:
            # Clean target directory
            for f in os.listdir(self.target_dir):
                os.remove(os.path.join(self.target_dir, f))

            # Create existing file
            try:
                existing_file = os.path.join(self.target_dir, name)
                with open(existing_file, 'w', encoding='utf-8') as f:
                    f.write("existing")

                media_file = MediaFile(os.path.join(self.source_dir, name))
                media_file.filename = name

                # This should not raise an exception
                result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
                assert result is not None
                assert result != existing_file  # Should be different due to increment

            except (OSError, UnicodeError):
                # Skip files that can't be created on this filesystem
                continue

    def test_duplicate_detection_case_sensitivity(self):
        """Test duplicate detection with different case (platform dependent)."""
        # This test behavior depends on filesystem case sensitivity
        # On Windows: photo.jpg and Photo.jpg are the same
        # On Linux: they are different files

        media_file1 = MediaFile(os.path.join(self.source_dir, "photo.jpg"))
        media_file1.filename = "photo.jpg"

        media_file2 = MediaFile(os.path.join(self.source_dir, "Photo.jpg"))
        media_file2.filename = "Photo.jpg"

        # Create first file
        path1 = self.file_mover._get_destination_path(media_file1, self.target_dir, dry_run=True)

        # Now create the first file physically
        with open(path1, 'w') as f:
            f.write("first")

        # Try second file with different case
        path2 = self.file_mover._get_destination_path(media_file2, self.target_dir, dry_run=False)

        # The behavior here is platform-dependent, but the function should not crash
        assert path2 is not None

        # On case-insensitive systems, should get increment
        # On case-sensitive systems, should get original name
        is_case_sensitive = (path1.lower() != path2.lower() if path1 != path2 else False)

        if not is_case_sensitive and path1.lower() == path2.lower():
            # Case-insensitive filesystem - should increment
            expected_base = Path(media_file2.filename).stem
            expected_ext = Path(media_file2.filename).suffix
            assert f"_{1}" in Path(path2).stem or path2 == path1

    def test_get_destination_path_preserves_extensions(self):
        """Test that file extensions are preserved during duplicate handling."""
        extensions_to_test = [
            ".jpg", ".JPG", ".jpeg", ".JPEG",
            ".png", ".PNG", ".gif", ".GIF",
            ".pdf", ".txt", ".doc", ".docx",
            "", ".tar.gz", ".backup"
        ]

        for ext in extensions_to_test:
            # Clean target directory
            for f in os.listdir(self.target_dir):
                os.remove(os.path.join(self.target_dir, f))

            filename = f"test{ext}"

            # Create existing file
            existing_file = os.path.join(self.target_dir, filename)
            with open(existing_file, 'w') as f:
                f.write("existing")

            media_file = MediaFile(os.path.join(self.source_dir, filename))
            media_file.filename = filename

            result = self.file_mover._get_destination_path(media_file, self.target_dir, dry_run=False)
            result_path = Path(result)

            # Check that extension is preserved
            if ext:
                assert result_path.suffix == Path(filename).suffix, f"Extension not preserved for {filename}"

            # Check that incremented name follows pattern
            if ext:
                expected_name = f"test_1{ext}"
            else:
                expected_name = "test_1"

            assert result_path.name == expected_name, f"Increment pattern wrong for {filename}"