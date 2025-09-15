"""Integration tests for progress indicators in scan and organize commands."""
import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import sys

try:
    from src.cli.commands.scan import scan
    from src.cli.commands.organize import organize
    from src.lib.progress_reporter import ProgressReporter
    from src.lib.config_manager import ConfigManager
except ImportError:
    from cli.commands.scan import scan
    from cli.commands.organize import organize
    from lib.progress_reporter import ProgressReporter
    from lib.config_manager import ConfigManager


class TestProgressIntegration:
    """Test progress indicators in real command scenarios."""

    @pytest.fixture
    def temp_dir_with_files(self):
        """Create a temporary directory with test files."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create test image files
            for i in range(5):
                test_file = Path(temp_dir) / f"image_{i}.jpg"
                test_file.touch()
                # Set modification time to different dates
                import time
                timestamp = time.time() - (i * 86400)  # Different days
                os.utime(test_file, (timestamp, timestamp))

            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def empty_temp_dir(self):
        """Create an empty temporary directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_scan_command_progress_verbose(self, temp_dir_with_files):
        """Test that scan command shows progress in verbose mode."""
        from click.testing import CliRunner

        runner = CliRunner()

        # Test with verbose flag
        result = runner.invoke(scan, [
            '--verbose',
            '--format', 'table',
            temp_dir_with_files
        ])

        # Should succeed
        assert result.exit_code == 0

        # Output should contain progress indicators (emojis and status messages)
        output = result.output.lower()

        # Check for progress-related content
        # Note: In testing, tqdm might not display progress bars, but we should see status messages
        assert 'scan results' in output or 'total files' in output

    def test_scan_command_progress_quiet(self, temp_dir_with_files):
        """Test that scan command respects quiet mode."""
        from click.testing import CliRunner

        runner = CliRunner()

        # Test with quiet flag
        result = runner.invoke(scan, [
            '--quiet',
            '--format', 'table',
            temp_dir_with_files
        ])

        # Should succeed
        assert result.exit_code == 0

        # Output should be minimal in quiet mode
        assert result.output.strip() == '' or len(result.output.strip()) < 50

    def test_scan_command_progress_json_format(self, temp_dir_with_files):
        """Test that scan command doesn't show progress bars for JSON format."""
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(scan, [
            '--format', 'json',
            temp_dir_with_files
        ])

        # Should succeed
        assert result.exit_code == 0

        # Output should be valid JSON without progress messages
        import json
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            pytest.fail("Output should be valid JSON")

    def test_organize_command_dry_run_progress(self, temp_dir_with_files):
        """Test that organize command shows progress in dry run mode."""
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(organize, [
            '--dry-run',
            '--verbose',
            temp_dir_with_files
        ])

        # Should succeed
        assert result.exit_code == 0

        # Should contain dry run results
        output = result.output.lower()
        assert 'dry run' in output or 'would be' in output

    def test_organize_command_progress_phases(self, temp_dir_with_files):
        """Test that organize command shows different phases."""
        from click.testing import CliRunner

        runner = CliRunner()

        # Create a copy for actual organization to avoid modifying the fixture
        test_dir = tempfile.mkdtemp()
        try:
            # Copy files to test directory
            for file in Path(temp_dir_with_files).iterdir():
                if file.is_file():
                    shutil.copy2(file, test_dir)

            result = runner.invoke(organize, [
                '--verbose',
                '--yes',  # Skip confirmation
                test_dir
            ])

            # Should succeed
            assert result.exit_code == 0

            # Output should indicate completion
            output = result.output.lower()
            assert 'operation complete' in output or 'successfully processed' in output or 'completed' in output

        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_progress_reporter_with_real_tqdm(self):
        """Test ProgressReporter with actual tqdm (not mocked)."""
        reporter = ProgressReporter(verbose=True, quiet=False)

        # Test phase context manager
        with reporter.phase("Test phase", 10) as phase:
            for i in range(10):
                phase.update(1)
                if i == 5:
                    phase.set_status("Halfway done")

        # Test should complete without errors
        assert reporter.current_phase is None

    def test_progress_reporter_indeterminate_phase(self):
        """Test indeterminate progress phase."""
        reporter = ProgressReporter(verbose=True, quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.start_indeterminate_phase("Loading")
            assert reporter.current_phase == "Loading"
            mock_print.assert_called_with("⏳ Loading...")

    def test_progress_reporter_error_handling(self):
        """Test progress reporter error handling."""
        reporter = ProgressReporter(quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.report_error("Test error")
            mock_print.assert_called_with("❌ Error: Test error")

    def test_scan_empty_directory_progress(self, empty_temp_dir):
        """Test scan command progress with empty directory."""
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(scan, [
            '--verbose',
            empty_temp_dir
        ])

        # Should succeed
        assert result.exit_code == 0

        # Should indicate no files found
        output = result.output.lower()
        assert 'total files: 0' in output or 'no files' in output

    def test_organize_empty_directory_progress(self, empty_temp_dir):
        """Test organize command progress with empty directory."""
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(organize, [
            '--verbose',
            empty_temp_dir
        ])

        # Should succeed
        assert result.exit_code == 0

        # Should indicate no files found
        output = result.output.lower()
        assert 'no files found' in output or 'organization complete' in output

    def test_progress_messages_threading_safe(self):
        """Test that progress messages are thread-safe."""
        import threading
        import time

        reporter = ProgressReporter(verbose=True, quiet=False)
        errors = []

        def worker(worker_id):
            try:
                with reporter.phase(f"Worker {worker_id}", 5):
                    for i in range(5):
                        reporter.update(1)
                        time.sleep(0.01)  # Small delay
            except Exception as e:
                errors.append(e)

        # Create multiple worker threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Should complete without errors
        assert len(errors) == 0

    def test_cli_progress_with_actual_subprocess(self, temp_dir_with_files):
        """Test progress indicators via actual subprocess calls."""
        # Test scan command
        result = subprocess.run([
            sys.executable, "-m", "src.cli.main", "scan",
            "--verbose", temp_dir_with_files
        ], capture_output=True, text=True, cwd=os.getcwd())

        # Should succeed
        assert result.returncode == 0

        # Should have some output (not testing exact content due to tqdm behavior in subprocess)
        assert len(result.stdout) > 0

    def test_organize_keyboard_interrupt_handling(self, temp_dir_with_files):
        """Test that organize command handles keyboard interrupts gracefully."""
        from click.testing import CliRunner

        runner = CliRunner()

        # Create a copy for testing
        test_dir = tempfile.mkdtemp()
        try:
            # Copy files to test directory
            for file in Path(temp_dir_with_files).iterdir():
                if file.is_file():
                    shutil.copy2(file, test_dir)

            # Simulate keyboard interrupt during processing
            with patch('src.lib.file_mover.FileMover.move_file') as mock_move:
                mock_move.side_effect = KeyboardInterrupt()

                result = runner.invoke(organize, [
                    '--verbose',
                    '--yes',
                    test_dir
                ])

                # Should exit with keyboard interrupt code
                assert result.exit_code == 130

        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_progress_compatibility_with_existing_methods(self):
        """Test that new progress methods are compatible with existing code."""
        reporter = ProgressReporter(verbose=True, quiet=False)

        # Test backward compatibility with existing methods
        with patch('builtins.print') as mock_print:
            reporter.start_operation("Test", 100)
            reporter.set_status("Processing")
            reporter.update(50)
            reporter.finish_operation(success=True)

            # Should not raise any errors
            assert mock_print.call_count >= 1  # At least one print call