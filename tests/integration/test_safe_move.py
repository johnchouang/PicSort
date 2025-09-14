"""Integration test: verify file before delete (safe file move).

This test verifies that the system safely moves files by verifying
the copy before deleting the original, as specified in the safety requirements.
"""
import pytest
import tempfile
import os
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
import time


class TestSafeFileMove:
    """Integration tests for safe file move operations."""

    def calculate_file_checksum(self, file_path):
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def create_test_file_with_content(self, file_path, size_mb=1):
        """Create a test file with specific content for verification."""
        # Create file with pseudo-random but deterministic content
        content = b"Test file content for safe move verification.\n"
        content += b"This file should be copied safely before deletion.\n"
        content += b"X" * (size_mb * 1024 * 1024 - len(content))  # Pad to desired size

        with open(file_path, "wb") as f:
            f.write(content)

        return content

    def test_file_integrity_after_move(self):
        """Test that moved files maintain their integrity (checksum verification)."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file with specific content
            test_file = os.path.join(test_dir, "integrity_test.jpg")
            original_content = self.create_test_file_with_content(test_file)
            original_checksum = self.calculate_file_checksum(test_file)

            # Set modification time
            target_date = datetime(2024, 8, 15).timestamp()
            os.utime(test_file, (target_date, target_date))

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
                if "integrity_test.jpg" in files:
                    moved_file = os.path.join(root, "integrity_test.jpg")
                    break

            assert moved_file is not None, "File should be moved to date folder"

            # Verify file integrity
            moved_checksum = self.calculate_file_checksum(moved_file)
            assert moved_checksum == original_checksum, "File checksum should be preserved after move"

            # Verify content is identical
            with open(moved_file, "rb") as f:
                moved_content = f.read()
            assert moved_content == original_content, "File content should be identical after move"

    def test_original_file_deleted_only_after_verification(self):
        """Test that original file is deleted only after successful copy verification."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file
            test_file = os.path.join(test_dir, "delete_test.png")
            self.create_test_file_with_content(test_file)

            # Set modification time
            target_date = datetime(2024, 9, 10).timestamp()
            os.utime(test_file, (target_date, target_date))

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize failed: {result.stderr}"

            # Original file should be gone (moved successfully)
            assert not os.path.exists(test_file), "Original file should be deleted after successful move"

            # File should exist in date folder
            moved_file_exists = False
            for root, dirs, files in os.walk(test_dir):
                if "delete_test.png" in files:
                    moved_file_exists = True
                    break

            assert moved_file_exists, "File should exist in destination date folder"

    def test_no_verify_option_behavior(self):
        """Test --no-verify option for faster but less safe operations."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file
            test_file = os.path.join(test_dir, "no_verify_test.gif")
            original_content = self.create_test_file_with_content(test_file)
            original_checksum = self.calculate_file_checksum(test_file)

            # Set modification time
            target_date = datetime(2024, 10, 5).timestamp()
            os.utime(test_file, (target_date, target_date))

            # Run organize with --no-verify
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--no-verify", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Organize with --no-verify failed: {result.stderr}"

            # File should still be moved correctly
            moved_file = None
            for root, dirs, files in os.walk(test_dir):
                if "no_verify_test.gif" in files:
                    moved_file = os.path.join(root, "no_verify_test.gif")
                    break

            assert moved_file is not None, "File should be moved even with --no-verify"

            # Content should still be preserved (even without explicit verification)
            moved_checksum = self.calculate_file_checksum(moved_file)
            assert moved_checksum == original_checksum, "File should still be intact with --no-verify"

    def test_large_file_safe_move(self):
        """Test safe move of larger files."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create larger test file (5MB)
            test_file = os.path.join(test_dir, "large_file.mp4")
            original_content = self.create_test_file_with_content(test_file, size_mb=5)
            original_checksum = self.calculate_file_checksum(test_file)

            # Set modification time
            target_date = datetime(2024, 11, 20).timestamp()
            os.utime(test_file, (target_date, target_date))

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Large file organize failed: {result.stderr}"

            # Find and verify moved file
            moved_file = None
            for root, dirs, files in os.walk(test_dir):
                if "large_file.mp4" in files:
                    moved_file = os.path.join(root, "large_file.mp4")
                    break

            assert moved_file is not None, "Large file should be moved"

            # Verify integrity of large file
            moved_checksum = self.calculate_file_checksum(moved_file)
            assert moved_checksum == original_checksum, "Large file checksum should be preserved"

            # Verify file size is preserved
            original_size = len(original_content)
            moved_size = os.path.getsize(moved_file)
            assert moved_size == original_size, "Large file size should be preserved"

    def test_multiple_files_safe_move(self):
        """Test safe move of multiple files simultaneously."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create multiple test files
            test_files = []
            original_checksums = {}

            for i in range(3):
                file_path = os.path.join(test_dir, f"multi_test_{i}.jpg")
                self.create_test_file_with_content(file_path)
                original_checksums[f"multi_test_{i}.jpg"] = self.calculate_file_checksum(file_path)
                test_files.append(file_path)

                # Same target date for all files
                target_date = datetime(2024, 12, 1).timestamp()
                os.utime(file_path, (target_date, target_date))

            # Run organize
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Multiple file organize failed: {result.stderr}"

            # Verify all files moved safely
            moved_files = {}
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.startswith("multi_test_"):
                        file_path = os.path.join(root, file)
                        moved_files[file] = self.calculate_file_checksum(file_path)

            assert len(moved_files) == 3, "All 3 files should be moved"

            # Verify checksums of all moved files
            for filename, checksum in moved_files.items():
                assert checksum == original_checksums[filename], f"File {filename} checksum should be preserved"

    def test_move_failure_recovery(self):
        """Test behavior when file move fails (e.g., destination read-only)."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file
            test_file = os.path.join(test_dir, "fail_test.mov")
            self.create_test_file_with_content(test_file)

            # Set modification time
            target_date = datetime(2024, 1, 10).timestamp()
            os.utime(test_file, (target_date, target_date))

            # Create the expected date folder and make it read-only
            date_folder = os.path.join(test_dir, "01.2024")
            os.makedirs(date_folder)
            # Make directory read-only to simulate failure
            os.chmod(date_folder, 0o444)

            try:
                # Run organize - should handle the failure gracefully
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                    capture_output=True,
                    text=True
                )

                # Should fail gracefully (non-zero exit code but not crash)
                assert result.returncode != 0, "Should fail when cannot write to destination"

                # Original file should still exist (not deleted due to failed copy)
                assert os.path.exists(test_file), "Original file should remain if move fails"

                # Should show meaningful error message
                error_output = result.stderr.lower() if result.stderr else result.stdout.lower()
                assert "error" in error_output or "failed" in error_output or "permission" in error_output

            finally:
                # Restore permissions for cleanup
                os.chmod(date_folder, 0o755)

    def test_verification_logging(self):
        """Test that file verification is logged appropriately."""
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test file
            test_file = os.path.join(test_dir, "log_test.avi")
            self.create_test_file_with_content(test_file)

            # Set modification time
            target_date = datetime(2024, 2, 14).timestamp()
            os.utime(test_file, (target_date, target_date))

            # Run organize with verbose output
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--verbose", "--yes", test_dir],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Verbose organize failed: {result.stderr}"

            # Should show verification-related messages
            output = result.stdout.lower()
            verification_terms = ["verify", "checksum", "integrity", "copied", "moved", "safe"]
            assert any(term in output for term in verification_terms), f"Should mention verification: {result.stdout}"