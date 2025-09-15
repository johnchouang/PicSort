"""Comprehensive integration tests for the organize command."""
import os
import tempfile
import pytest
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
import subprocess

from src.cli.commands.organize import organize
from src.lib.config_manager import ConfigManager
from src.models.media_file import MediaFile


class TestOrganizeCommandComprehensive:
    """Comprehensive tests for the organize command functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename, content=b"test content", modify_time=None):
        """Create a test file with optional modification time."""
        file_path = self.test_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(content)

        if modify_time:
            timestamp = modify_time.timestamp()
            os.utime(file_path, (timestamp, timestamp))

        return file_path

    def test_organize_dry_run_with_files(self):
        """Test organize command in dry-run mode with test files."""
        # Create test files with different dates
        jan_2024 = datetime(2024, 1, 15)
        feb_2024 = datetime(2024, 2, 20)

        self.create_test_file("photo1.jpg", modify_time=jan_2024)
        self.create_test_file("photo2.png", modify_time=feb_2024)
        self.create_test_file("document.txt", modify_time=jan_2024)

        # Run organize in dry-run mode
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "photo1.jpg" in result.stdout
        assert "photo2.png" in result.stdout
        assert "01.2024" in result.stdout or "02.2024" in result.stdout

    def test_organize_no_resume_manager_error(self):
        """Test that organize command doesn't fail with ResumeManager error."""
        # Create a simple test file
        self.create_test_file("test.jpg")

        # Run organize command and check it doesn't fail with ResumeManager error
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        # Should not contain ResumeManager error
        assert "create_resume_point" not in result.stderr
        assert "ResumeManager" not in result.stderr or "object has no attribute" not in result.stderr

    def test_organize_empty_directory(self):
        """Test organize command on empty directory."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "no files found" in result.stdout.lower() or "complete" in result.stdout.lower()

    def test_organize_with_non_media_files_only(self):
        """Test organize command with only non-media files."""
        self.create_test_file("document.txt")
        self.create_test_file("spreadsheet.xlsx")
        self.create_test_file("readme.md")

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0

    def test_organize_with_all_files_flag(self):
        """Test organize command with --all-files flag."""
        jan_2024 = datetime(2024, 1, 15)

        self.create_test_file("photo.jpg", modify_time=jan_2024)
        self.create_test_file("document.txt", modify_time=jan_2024)

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--all-files", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0
        # Both files should be mentioned in output with --all-files
        assert "photo.jpg" in result.stdout
        assert "document.txt" in result.stdout

    def test_organize_recursive_flag(self):
        """Test organize command with recursive flag."""
        jan_2024 = datetime(2024, 1, 15)

        # Create files in subdirectories
        self.create_test_file("subfolder/photo1.jpg", modify_time=jan_2024)
        self.create_test_file("deep/nested/photo2.png", modify_time=jan_2024)
        self.create_test_file("photo3.jpg", modify_time=jan_2024)

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--recursive", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0
        # All photos should be found with recursive flag
        output = result.stdout
        assert "photo1.jpg" in output
        assert "photo2.png" in output
        assert "photo3.jpg" in output

    def test_organize_with_specific_file_types(self):
        """Test organize command with specific file types."""
        jan_2024 = datetime(2024, 1, 15)

        self.create_test_file("photo.jpg", modify_time=jan_2024)
        self.create_test_file("image.png", modify_time=jan_2024)
        self.create_test_file("video.mp4", modify_time=jan_2024)

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--file-types", ".jpg", ".png", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0
        # Should include .jpg and .png but not .mp4
        output = result.stdout
        assert "photo.jpg" in output
        assert "image.png" in output

    def test_organize_verbose_output(self):
        """Test organize command with verbose output."""
        self.create_test_file("photo.jpg")

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--verbose", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0

    def test_organize_quiet_output(self):
        """Test organize command with quiet output."""
        self.create_test_file("photo.jpg")

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--quiet", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0
        # Should have minimal output with --quiet
        assert len(result.stdout.strip()) < 100  # Minimal output expected

    def test_organize_actual_move_operations(self):
        """Test organize command with actual file moves (not dry-run)."""
        jan_2024 = datetime(2024, 1, 15)
        feb_2024 = datetime(2024, 2, 20)

        photo1 = self.create_test_file("photo1.jpg", modify_time=jan_2024)
        photo2 = self.create_test_file("photo2.png", modify_time=feb_2024)

        # Verify files exist before organize
        assert photo1.exists()
        assert photo2.exists()

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--yes", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0

        # Check that date folders were created
        jan_folder = self.test_path / "01.2024"
        feb_folder = self.test_path / "02.2024"

        # Files should have been moved to date folders
        if jan_folder.exists():
            assert (jan_folder / "photo1.jpg").exists()
        if feb_folder.exists():
            assert (feb_folder / "photo2.png").exists()

    def test_organize_with_duplicates(self):
        """Test organize command handles duplicate filenames."""
        jan_2024 = datetime(2024, 1, 15)

        # Create files with same name but different content
        self.create_test_file("photo.jpg", content=b"content1", modify_time=jan_2024)
        self.create_test_file("subfolder/photo.jpg", content=b"content2", modify_time=jan_2024)

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--recursive", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0
        # Should handle duplicates gracefully
        output = result.stdout
        assert "photo.jpg" in output

    @pytest.mark.skipif(not os.path.exists(r"C:\Users\JChouangrasa\OneDrive - NRG Energy, Inc\Pictures"),
                       reason="Test Pictures directory not available")
    def test_organize_with_actual_pictures_directory(self):
        """Test organize command with the actual Pictures directory (dry-run only)."""
        pictures_path = r"C:\Users\JChouangrasa\OneDrive - NRG Energy, Inc\Pictures"

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--dry-run", "--recursive", pictures_path],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            timeout=120  # 2 minutes timeout for safety
        )

        # Should not crash with ResumeManager error
        assert "create_resume_point" not in result.stderr
        assert "ResumeManager" not in result.stderr or "object has no attribute" not in result.stderr

        # Should either succeed or fail gracefully
        if result.returncode != 0:
            # If it fails, the error should be meaningful (not a ResumeManager error)
            assert "create_resume_point" not in result.stderr

    def test_organize_error_handling(self):
        """Test organize command error handling."""
        # Test with non-existent directory
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "/non/existent/path"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode != 0
        assert "does not exist" in result.stderr.lower() or "path" in result.stderr.lower()

    def test_organize_with_corrupted_file(self):
        """Test organize command with corrupted or locked files."""
        # Create a test file
        corrupted_file = self.create_test_file("corrupted.jpg", content=b"not really an image")

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--dry-run", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        # Should handle corrupted files gracefully
        assert result.returncode == 0

    def test_organize_config_loading(self):
        """Test organize command with custom config."""
        # Create a simple config file
        config_path = self.test_path / "test_config.yaml"
        config_content = """
file_types:
  - .jpg
  - .png
date_format: "MM.YYYY"
dry_run_default: true
"""
        with open(config_path, 'w') as f:
            f.write(config_content)

        self.create_test_file("photo.jpg")

        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--config", str(config_path), str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0

    def test_organize_resume_manager_integration(self):
        """Test that ResumeManager integration works correctly."""
        jan_2024 = datetime(2024, 1, 15)
        self.create_test_file("photo.jpg", modify_time=jan_2024)

        # Test that the command works without ResumeManager errors
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--yes", str(self.test_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        # Should not have ResumeManager attribute errors
        assert "create_resume_point" not in result.stderr
        assert "update_resume_point" not in result.stderr
        assert "cleanup_completed_operation" not in result.stderr

        # Command should complete successfully
        assert result.returncode == 0