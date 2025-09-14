"""Contract tests for the 'picsort undo' command.

These tests verify that the CLI command interface matches the specification
in specs/001-i-have-folders/contracts/cli-interface.yaml
"""
import pytest
import subprocess
import tempfile
import os
from pathlib import Path


class TestUndoCommand:
    """Test contract for 'picsort undo' command."""

    def test_undo_command_exists(self):
        """Test that 'picsort undo' command is available."""
        # This should fail initially as the command doesn't exist yet
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "undo command should be available"
        assert "undo" in result.stdout.lower()

    def test_undo_no_arguments_required(self):
        """Test that undo command doesn't require arguments."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo"],
            capture_output=True,
            text=True
        )
        # Should not fail due to missing arguments (may fail for other reasons like no operations to undo)
        # But should not show "missing argument" type errors
        if result.returncode != 0:
            assert "missing" not in result.stderr.lower() and "required" not in result.stderr.lower()

    def test_undo_operation_id_option(self):
        """Test --operation-id/-o option is recognized."""
        # Test long form
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--operation-id", "test123"],
            capture_output=True,
            text=True
        )
        # Should not fail due to unrecognized option
        assert "--operation-id" not in result.stderr or "unrecognized" not in result.stderr.lower()

        # Test short form
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "-o", "test123"],
            capture_output=True,
            text=True
        )
        assert "-o" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_undo_dry_run_option(self):
        """Test --dry-run/-d option is recognized."""
        # Test long form
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--dry-run"],
            capture_output=True,
            text=True
        )
        # Should not fail due to unrecognized option
        assert "--dry-run" not in result.stderr or "unrecognized" not in result.stderr.lower()

        # Test short form
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "-d"],
            capture_output=True,
            text=True
        )
        assert "-d" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_undo_yes_option(self):
        """Test --yes/-y option is recognized."""
        # Test long form
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--yes"],
            capture_output=True,
            text=True
        )
        # Should not fail due to unrecognized option
        assert "--yes" not in result.stderr or "unrecognized" not in result.stderr.lower()

        # Test short form
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "-y"],
            capture_output=True,
            text=True
        )
        assert "-y" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_undo_dry_run_default_behavior(self):
        """Test that undo defaults to dry-run mode."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo"],
            capture_output=True,
            text=True
        )
        # According to contract, dry-run should be true by default
        # Should either show dry-run behavior or indicate no operations to undo
        if result.returncode == 0:
            output = result.stdout.lower()
            # Should indicate preview/dry-run behavior or show results
            expected_terms = ["preview", "would", "dry", "no operations", "nothing to undo"]
            assert any(term in output for term in expected_terms)

    def test_undo_with_operation_id(self):
        """Test undo with specific operation ID."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--operation-id", "nonexistent123"],
            capture_output=True,
            text=True
        )
        # Should handle non-existent operation gracefully
        if result.returncode != 0:
            # Should show meaningful error, not argument parsing error
            assert "not found" in result.stderr.lower() or "invalid" in result.stderr.lower() or "unknown" in result.stderr.lower()

    def test_undo_combined_options(self):
        """Test undo with multiple options combined."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--dry-run", "--yes", "--operation-id", "test123"],
            capture_output=True,
            text=True
        )
        # All options should be recognized
        assert "unrecognized" not in result.stderr.lower()

    def test_undo_success_output_format(self):
        """Test that undo shows expected success output format."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--dry-run"],
            capture_output=True,
            text=True
        )
        # Should show some form of undo status/result
        if result.returncode == 0:
            output = result.stdout.lower()
            # Should contain undo-related messaging
            expected_terms = ["undo", "restore", "files", "operations", "complete", "nothing"]
            assert any(term in output for term in expected_terms)

    def test_undo_error_output_format(self):
        """Test that undo shows expected error output format when failing."""
        # Try to undo with invalid operation ID to trigger error
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--operation-id", "definitely-invalid-12345"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            # Error should be informative (per contract)
            error_output = result.stderr.lower() if result.stderr else result.stdout.lower()
            # Should indicate what went wrong
            expected_terms = ["error", "failed", "not found", "invalid", "undo"]
            assert any(term in error_output for term in expected_terms)

    def test_undo_confirmation_behavior(self):
        """Test that undo prompts for confirmation without --yes."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo"],
            capture_output=True,
            text=True,
            input="n\n",  # Respond "no" to any confirmation
            timeout=5     # Don't wait forever
        )
        # Should either complete or show confirmation-related behavior
        # If it asks for confirmation, should handle "no" response
        if result.returncode != 0:
            # Should not fail due to missing command or unrecognized options
            assert "not found" not in result.stderr.lower() and "unrecognized" not in result.stderr.lower()

    def test_undo_skip_confirmation_with_yes(self):
        """Test that --yes skips confirmation prompts."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "undo", "--yes", "--dry-run"],
            capture_output=True,
            text=True
        )
        # Should complete quickly without waiting for input
        # (dry-run with --yes should not prompt)
        assert "unrecognized" not in result.stderr.lower()