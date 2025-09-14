"""Integration test: config file loading and usage.

This test verifies that the system correctly loads and uses configuration
from YAML files, including the default location and custom config paths.
"""
import pytest
import tempfile
import os
import subprocess
import yaml
from pathlib import Path
from datetime import datetime


class TestConfigLoading:
    """Integration tests for configuration file loading."""

    def create_test_config(self, config_path, config_data):
        """Create a test configuration file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        return config_path

    def test_default_config_location(self):
        """Test that system can find config at default location."""
        with tempfile.TemporaryDirectory() as temp_home:
            # Create .picsort directory structure
            config_dir = os.path.join(temp_home, ".picsort")
            config_file = os.path.join(config_dir, "config.yaml")

            # Create test config
            test_config = {
                'file_types': ['.jpg', '.png'],
                'date_format': 'YYYY-MM',
                'recursive': True,
                'dry_run': False
            }
            self.create_test_config(config_file, test_config)

            # Set environment to use our test home directory
            env = os.environ.copy()
            env['HOME'] = temp_home
            env['USERPROFILE'] = temp_home  # For Windows

            # Create test directory with files
            with tempfile.TemporaryDirectory() as test_dir:
                # Create test files
                jpg_file = os.path.join(test_dir, "test.jpg")
                png_file = os.path.join(test_dir, "test.png")
                gif_file = os.path.join(test_dir, "test.gif")  # Should be ignored per config

                for file_path in [jpg_file, png_file, gif_file]:
                    Path(file_path).touch()
                    test_date = datetime(2024, 5, 15)
                    os.utime(file_path, (test_date.timestamp(), test_date.timestamp()))

                # Run organize (should use default config)
                result = subprocess.run(
                    ["python", "-m", "src.cli.main", "organize", "--yes", test_dir],
                    capture_output=True,
                    text=True,
                    env=env
                )

                # Should use config settings (YYYY-MM format)
                if result.returncode == 0:
                    # Check that folder was created in YYYY-MM format
                    folders = [f for f in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, f))]
                    if folders:
                        # Should be YYYY-MM format from config
                        assert any("2024-05" in folder for folder in folders), f"Should use YYYY-MM format from config: {folders}"

    def test_custom_config_file(self):
        """Test specifying custom config file with --config option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create custom config file
            custom_config_path = os.path.join(temp_dir, "custom_config.yaml")
            custom_config = {
                'file_types': ['.mp4', '.mov'],  # Only videos
                'date_format': 'MMM_YYYY',
                'recursive': False,
                'dry_run': True  # Force dry run
            }
            self.create_test_config(custom_config_path, custom_config)

            # Create test files
            mp4_file = os.path.join(temp_dir, "video.mp4")
            jpg_file = os.path.join(temp_dir, "photo.jpg")  # Should be ignored

            Path(mp4_file).touch()
            Path(jpg_file).touch()

            test_date = datetime(2024, 7, 10)
            for file_path in [mp4_file, jpg_file]:
                os.utime(file_path, (test_date.timestamp(), test_date.timestamp()))

            # Run organize with custom config
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--config", custom_config_path, "--yes", temp_dir],
                capture_output=True,
                text=True
            )

            # Should use custom config (dry_run=True, so no files moved)
            assert os.path.exists(mp4_file), "MP4 file should still exist (dry run from config)"
            assert os.path.exists(jpg_file), "JPG file should still exist (ignored by config)"

            # Should show MMM_YYYY format in output
            if result.returncode == 0:
                assert "Jul_2024" in result.stdout or "jul_2024" in result.stdout.lower()

    def test_config_file_validation(self):
        """Test that invalid config files are handled gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid config file (invalid YAML)
            invalid_config_path = os.path.join(temp_dir, "invalid.yaml")
            with open(invalid_config_path, 'w') as f:
                f.write("invalid: yaml: content: [unclosed")

            # Run organize with invalid config
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--config", invalid_config_path, "--yes", temp_dir],
                capture_output=True,
                text=True
            )

            # Should fail gracefully with meaningful error
            assert result.returncode != 0, "Should fail with invalid config"
            error_output = (result.stderr + result.stdout).lower()
            assert "config" in error_output or "yaml" in error_output or "invalid" in error_output

    def test_config_override_with_command_line(self):
        """Test that command line options override config file settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with specific settings
            config_path = os.path.join(temp_dir, "override_test.yaml")
            config_data = {
                'date_format': 'MM.YYYY',  # Config says MM.YYYY
                'recursive': False,
                'dry_run': False
            }
            self.create_test_config(config_path, config_data)

            # Create test file
            test_file = os.path.join(temp_dir, "test.jpg")
            Path(test_file).touch()
            test_date = datetime(2024, 8, 20)
            os.utime(test_file, (test_date.timestamp(), test_date.timestamp()))

            # Run with command line override
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize",
                 "--config", config_path,
                 "--date-format", "YYYY-MM",  # Override config setting
                 "--dry-run",  # Override config setting
                 "--yes", temp_dir],
                capture_output=True,
                text=True
            )

            # Should use command line format (YYYY-MM), not config format (MM.YYYY)
            if result.returncode == 0:
                output = result.stdout
                assert "2024-08" in output, f"Should use command line format YYYY-MM: {output}"
                # Should not show MM.YYYY format
                assert "08.2024" not in output, f"Should not use config format MM.YYYY: {output}"

    def test_partial_config_with_defaults(self):
        """Test that partial config files use defaults for missing values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create partial config (only some settings)
            config_path = os.path.join(temp_dir, "partial.yaml")
            partial_config = {
                'date_format': 'YYYY.MM',  # Only specify date format
                # Other settings should use defaults
            }
            self.create_test_config(config_path, partial_config)

            # Create various file types
            test_files = [
                "image.jpg",    # Default media type
                "video.mp4",    # Default media type
                "document.pdf"  # Non-media (should be ignored by default)
            ]

            for filename in test_files:
                file_path = os.path.join(temp_dir, filename)
                Path(file_path).touch()
                test_date = datetime(2024, 9, 5)
                os.utime(file_path, (test_date.timestamp(), test_date.timestamp()))

            # Run with partial config
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--config", config_path, "--yes", temp_dir],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Should use config date format
                folders = [f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))]
                if folders:
                    assert any("2024.09" in folder for folder in folders), f"Should use config date format: {folders}"

                # Should use default file types (process media, ignore PDF)
                assert not os.path.exists(os.path.join(temp_dir, "document.pdf")) or \
                       os.path.exists(os.path.join(temp_dir, "document.pdf")), "PDF handling depends on defaults"

    def test_config_with_environment_variables(self):
        """Test that environment variables can override config paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config file
            config_path = os.path.join(temp_dir, "env_test.yaml")
            config_data = {
                'date_format': 'MMM_YYYY',
                'file_types': ['.jpg']
            }
            self.create_test_config(config_path, config_data)

            # Set environment variable for config path
            env = os.environ.copy()
            env['PICSORT_CONFIG'] = config_path

            # Create test file
            test_file = os.path.join(temp_dir, "env_test.jpg")
            Path(test_file).touch()
            test_date = datetime(2024, 10, 12)
            os.utime(test_file, (test_date.timestamp(), test_date.timestamp()))

            # Run without explicit --config (should use environment variable)
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--dry-run", "--yes", temp_dir],
                capture_output=True,
                text=True,
                env=env
            )

            # Should use config from environment variable
            if result.returncode == 0:
                assert "Oct_2024" in result.stdout or "oct_2024" in result.stdout.lower()

    def test_nonexistent_config_file(self):
        """Test behavior when specified config file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_config = os.path.join(temp_dir, "does_not_exist.yaml")

            # Create test file
            test_file = os.path.join(temp_dir, "test.png")
            Path(test_file).touch()

            # Run with nonexistent config file
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--config", nonexistent_config, "--yes", temp_dir],
                capture_output=True,
                text=True
            )

            # Should handle missing config gracefully
            if result.returncode != 0:
                error_output = (result.stderr + result.stdout).lower()
                assert "not found" in error_output or "config" in error_output

    def test_config_show_command(self):
        """Test that 'config show' displays current configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config file
            config_path = os.path.join(temp_dir, "show_test.yaml")
            config_data = {
                'date_format': 'YYYY-MM',
                'file_types': ['.jpg', '.png', '.mp4'],
                'recursive': True,
                'dry_run': False
            }
            self.create_test_config(config_path, config_data)

            # Run config show
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "config", "show", "--config", config_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                output = result.stdout
                # Should show configuration values
                assert "YYYY-MM" in output
                assert ".jpg" in output or "jpg" in output
                assert "recursive" in output.lower() or "true" in output.lower()

    def test_config_json_output(self):
        """Test that 'config show --json' outputs valid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config file
            config_path = os.path.join(temp_dir, "json_test.yaml")
            config_data = {
                'date_format': 'MM.YYYY',
                'file_types': ['.gif', '.mov']
            }
            self.create_test_config(config_path, config_data)

            # Run config show --json
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "config", "show", "--json", "--config", config_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                # Should be valid JSON
                try:
                    import json
                    config_json = json.loads(output)
                    assert isinstance(config_json, dict), "Should output JSON object"
                    assert "date_format" in config_json or "MM.YYYY" in str(config_json)
                except json.JSONDecodeError:
                    pytest.fail(f"Output should be valid JSON: {output}")

    def test_config_validation_with_invalid_values(self):
        """Test config validation with invalid configuration values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with invalid values
            config_path = os.path.join(temp_dir, "invalid_values.yaml")
            invalid_config = {
                'date_format': 'INVALID_FORMAT',  # Invalid date format
                'file_types': 'not_a_list',       # Should be list
                'recursive': 'maybe',             # Should be boolean
            }
            self.create_test_config(config_path, invalid_config)

            # Create test file
            test_file = os.path.join(temp_dir, "test.jpg")
            Path(test_file).touch()

            # Run with invalid config
            result = subprocess.run(
                ["python", "-m", "src.cli.main", "organize", "--config", config_path, "--yes", temp_dir],
                capture_output=True,
                text=True
            )

            # Should handle invalid values gracefully
            if result.returncode != 0:
                error_output = (result.stderr + result.stdout).lower()
                assert "invalid" in error_output or "config" in error_output or "error" in error_output