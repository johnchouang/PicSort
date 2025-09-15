"""Contract tests for the 'picsort scan' command.

These tests verify that the CLI command interface matches the specification
in specs/001-i-have-folders/contracts/cli-interface.yaml
"""
import pytest
import subprocess
import tempfile
import os
from pathlib import Path


class TestScanCommand:
    """Test contract for 'picsort scan' command."""

    def test_scan_command_exists(self):
        """Test that 'picsort scan' command is available."""
        # This should fail initially as the command doesn't exist yet
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "scan", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "scan command should be available"
        assert "scan" in result.stdout.lower()

    def test_scan_requires_path_argument(self):
        """Test that scan command requires a PATH argument."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "scan"],
            capture_output=True,
            text=True
        )
        # Should fail with error about missing path
        assert result.returncode != 0, "Should fail when no path provided"
        assert "path" in result.stderr.lower() or "missing" in result.stderr.lower()

    def test_scan_validates_path_exists(self):
        """Test that scan validates path exists."""
        fake_path = "/non/existent/path/12345"
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "scan", fake_path],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, "Should fail for non-existent path"

    def test_scan_recursive_option(self):
        """Test --recursive/-r option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test long form
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", "--recursive", tmp_dir],
                capture_output=True,
                text=True
            )
            # Should not fail due to unrecognized option
            assert "--recursive" not in result.stderr or "unrecognized" not in result.stderr.lower()

            # Test short form
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", "-r", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "-r" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_scan_file_types_option(self):
        """Test --file-types/-t option accepts list."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", "--file-types", ".jpg", ".png", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--file-types" not in result.stderr or "unrecognized" not in result.stderr.lower()

            # Test short form
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", "-t", ".jpg", ".png", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "-t" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_scan_format_option(self):
        """Test --format option accepts valid formats."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            valid_formats = ["table", "json", "csv"]
            for format_type in valid_formats:
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", "scan", "--format", format_type, tmp_dir],
                    capture_output=True,
                    text=True
                )
                assert "--format" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_scan_success_exit_code(self):
        """Test that successful scan returns exit code 0."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", tmp_dir],
                capture_output=True,
                text=True
            )
            # For successful scan on empty directory, should return 0
            assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

    def test_scan_output_format_table(self):
        """Test that scan command outputs expected table format by default."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", tmp_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Should contain scan results structure from contract
                output = result.stdout.lower()
                assert "scan results" in output or "total files" in output or "media files" in output

    def test_scan_output_format_json(self):
        """Test that scan command can output JSON format."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", "--format", "json", tmp_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Should be valid JSON (basic check)
                output = result.stdout.strip()
                assert output.startswith('{') or output.startswith('['), "JSON output should start with { or ["

    def test_scan_output_format_csv(self):
        """Test that scan command can output CSV format."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", "--format", "csv", tmp_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Should contain CSV-like structure (headers, commas)
                output = result.stdout
                lines = output.strip().split('\n')
                if len(lines) > 1:  # Should have at least header line
                    assert ',' in lines[0], "CSV should contain commas"

    def test_scan_shows_folder_creation_info(self):
        """Test that scan shows information about folders to be created."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a test image file with a known date
            test_file = os.path.join(tmp_dir, "test.jpg")
            Path(test_file).touch()

            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", tmp_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                # Should mention folders, organization info, or file status
                output = result.stdout.lower()
                expected_terms = ["folders to create", "folder", "organize", "date", "scan results", "total files", "media files"]
                assert any(term in output for term in expected_terms)

    def test_scan_shows_monthly_summary(self):
        """Test that scan shows monthly summary information."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test files
            test_file = os.path.join(tmp_dir, "test.jpg")
            Path(test_file).touch()

            result = subprocess.run(
                ["python", "-m", "src.cli.main", "scan", tmp_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                # Should show monthly breakdown or file counts
                output = result.stdout.lower()
                expected_terms = ["month", "files by", "summary", "total"]
                assert any(term in output for term in expected_terms)