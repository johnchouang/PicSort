"""Contract tests for the 'picsort config' commands.

These tests verify that the CLI command interface matches the specification
in specs/001-i-have-folders/contracts/cli-interface.yaml
"""
import pytest
import subprocess
import tempfile
import os
from pathlib import Path


class TestConfigCommand:
    """Test contract for 'picsort config' commands."""

    def test_config_command_exists(self):
        """Test that 'picsort config' command is available."""
        # This should fail initially as the command doesn't exist yet
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "config command should be available"
        assert "config" in result.stdout.lower()

    def test_config_init_subcommand_exists(self):
        """Test that 'picsort config init' subcommand is available."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "init", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "config init subcommand should be available"
        assert "init" in result.stdout.lower()

    def test_config_show_subcommand_exists(self):
        """Test that 'picsort config show' subcommand is available."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "show", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "config show subcommand should be available"
        assert "show" in result.stdout.lower()

    def test_config_set_subcommand_exists(self):
        """Test that 'picsort config set' subcommand is available."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "set", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "config set subcommand should be available"
        assert "set" in result.stdout.lower()

    def test_config_reset_subcommand_exists(self):
        """Test that 'picsort config reset' subcommand is available."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "reset", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "config reset subcommand should be available"
        assert "reset" in result.stdout.lower()

    def test_config_init_success(self):
        """Test that 'picsort config init' runs successfully."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "init"],
            capture_output=True,
            text=True,
            input="\n" * 10  # Provide default answers to any interactive prompts
        )
        # Should complete successfully and create config
        assert result.returncode == 0, f"config init should succeed, got exit code {result.returncode}"

    def test_config_init_output_format(self):
        """Test that 'picsort config init' shows expected output format."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "init"],
            capture_output=True,
            text=True,
            input="\n" * 10  # Provide default answers to any interactive prompts
        )
        if result.returncode == 0:
            # Should show success message with path
            output = result.stdout.lower()
            assert "configuration" in output and ("saved" in output or "created" in output)

    def test_config_show_success(self):
        """Test that 'picsort config show' runs successfully."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "show"],
            capture_output=True,
            text=True
        )
        # Should either show config or indicate no config found
        assert result.returncode == 0 or "not found" in result.stderr.lower()

    def test_config_show_json_option(self):
        """Test that 'picsort config show --json' option is recognized."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "show", "--json"],
            capture_output=True,
            text=True
        )
        # Should not fail due to unrecognized option
        assert "--json" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_config_set_requires_key_value(self):
        """Test that 'picsort config set' requires KEY VALUE arguments."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "set"],
            capture_output=True,
            text=True
        )
        # Should fail with error about missing arguments
        assert result.returncode != 0, "Should fail when no key/value provided"

    def test_config_set_with_valid_arguments(self):
        """Test that 'picsort config set' accepts KEY VALUE arguments."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "set", "recursive", "true"],
            capture_output=True,
            text=True
        )
        # Should not fail due to argument parsing (may fail for other reasons like no config file)
        # But should recognize the arguments
        assert "unrecognized" not in result.stderr.lower() or "usage" not in result.stderr.lower()

    def test_config_set_date_format_example(self):
        """Test that 'picsort config set' works with date_format example."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "set", "date_format", "YYYY-MM"],
            capture_output=True,
            text=True
        )
        # Should recognize the arguments (contract example)
        assert "unrecognized" not in result.stderr.lower() or "usage" not in result.stderr.lower()

    def test_config_reset_requires_yes_option(self):
        """Test that 'picsort config reset' requires --yes option."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "reset"],
            capture_output=True,
            text=True
        )
        # Should fail or prompt for confirmation without --yes
        assert result.returncode != 0 or "yes" in result.stdout.lower() or "confirm" in result.stdout.lower()

    def test_config_reset_with_yes_option(self):
        """Test that 'picsort config reset --yes' option is recognized."""
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "reset", "--yes"],
            capture_output=True,
            text=True
        )
        # Should not fail due to unrecognized option
        assert "--yes" not in result.stderr or "unrecognized" not in result.stderr.lower()

    def test_config_commands_help_available(self):
        """Test that all config subcommands have help available."""
        subcommands = ["init", "show", "set", "reset"]
        for subcmd in subcommands:
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "config", subcmd, "--help"],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"config {subcmd} --help should work"
            assert subcmd in result.stdout.lower(), f"Help should mention {subcmd}"

    def test_config_interactive_behavior(self):
        """Test that config init has interactive behavior."""
        # Test with minimal input to see if it's interactive
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "config", "init"],
            capture_output=True,
            text=True,
            input="",  # No input to test if it prompts
            timeout=5   # Don't wait forever
        )
        # Should either complete quickly or show prompts/questions
        # Interactive prompts would typically cause a timeout or show question text
        if result.returncode != 0:
            # May timeout or fail, but shouldn't be due to missing command
            assert "not found" not in result.stderr.lower() and "unrecognized" not in result.stderr.lower()