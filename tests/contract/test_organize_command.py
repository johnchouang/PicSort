"""Contract tests for the 'picsort organize' command.

These tests verify that the CLI command interface matches the specification
in specs/001-i-have-folders/contracts/cli-interface.yaml
"""
import pytest
import subprocess
import tempfile
import os
from pathlib import Path


class TestOrganizeCommand:
    """Test contract for 'picsort organize' command."""

    def test_organize_command_exists(self):
        """Test that 'picsort organize' command is available."""
        # This should fail initially as the command doesn't exist yet
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "organize command should be available"
        assert "organize" in result.stdout.lower()

    def test_organize_requires_path_argument(self):
        """Test that organize command requires a PATH argument."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize"],
            capture_output=True,
            text=True
        )
        # Should fail with error about missing path
        assert result.returncode != 0, "Should fail when no path provided"
        assert "path" in result.stderr.lower() or "missing" in result.stderr.lower()

    def test_organize_validates_path_exists(self):
        """Test that organize validates path exists."""
        fake_path = "/non/existent/path/12345"
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "organize", fake_path],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, "Should fail for non-existent path"

    def test_organize_validates_path_is_directory(self):
        """Test that organize validates path is a directory."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", tmp_file.name],
                capture_output=True,
                text=True
            )
            assert result.returncode != 0, "Should fail for file path (not directory)"

    def test_organize_recursive_option(self):
        """Test --recursive/-r option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test long form
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--recursive", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            # Should not fail due to unrecognized option
            assert "--recursive" not in result.stderr or "unrecognized" not in result.stderr.lower()

            # Test short form
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "-r", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "-r" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_dry_run_option(self):
        """Test --dry-run/-d option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test long form
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--dry-run" not in result.stderr or "unrecognized" not in result.stderr.lower()

            # Test short form
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "-d", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "-d" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_file_types_option(self):
        """Test --file-types/-t option accepts list."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--file-types", ".jpg", ".png", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--file-types" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_all_files_option(self):
        """Test --all-files/-a option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--all-files", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--all-files" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_date_format_option(self):
        """Test --date-format/-f option accepts valid formats."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            valid_formats = ["MM.YYYY", "YYYY.MM", "YYYY-MM", "MMM_YYYY"]
            for date_format in valid_formats:
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", "organize", "--date-format", date_format, "--dry-run", tmp_dir],
                    capture_output=True,
                    text=True
                )
                assert "--date-format" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_verbose_option(self):
        """Test --verbose/-v option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--verbose", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--verbose" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_quiet_option(self):
        """Test --quiet/-q option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--quiet", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--quiet" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_yes_option(self):
        """Test --yes/-y option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--yes", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--yes" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_no_verify_option(self):
        """Test --no-verify option is recognized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--no-verify", "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--no-verify" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_log_file_option(self):
        """Test --log-file/-l option accepts file path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = os.path.join(tmp_dir, "test.log")
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--log-file", log_file, "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--log-file" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_config_option(self):
        """Test --config/-c option accepts file path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = os.path.join(tmp_dir, "config.yaml")
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--config", config_file, "--dry-run", tmp_dir],
                capture_output=True,
                text=True
            )
            assert "--config" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_organize_success_exit_code(self):
        """Test that successful organize returns exit code 0."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a simple test scenario that should succeed
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", tmp_dir],
                capture_output=True,
                text=True
            )
            # For successful dry-run on empty directory, should return 0
            assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

    def test_organize_output_format(self):
        """Test that organize command outputs expected success format."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", tmp_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Should contain success indicators from contract
                output = result.stdout.lower()
                assert "organization" in output or "complete" in output or "processed" in output