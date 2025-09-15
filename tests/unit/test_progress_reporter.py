"""Unit tests for the ProgressReporter class."""
import pytest
from io import StringIO
import sys
from unittest.mock import patch, MagicMock

try:
    from src.lib.progress_reporter import ProgressReporter
except ImportError:
    from lib.progress_reporter import ProgressReporter


class TestProgressReporter:
    """Test the ProgressReporter class functionality."""

    def test_init_default_values(self):
        """Test ProgressReporter initialization with default values."""
        reporter = ProgressReporter()
        assert not reporter.verbose
        assert not reporter.quiet
        assert reporter.total is None
        assert reporter.desc is None
        assert reporter.progress is None
        assert reporter.current_status is None
        assert reporter.current_phase is None

    def test_init_with_values(self):
        """Test ProgressReporter initialization with custom values."""
        reporter = ProgressReporter(verbose=True, quiet=False, total=100, desc="Test operation")
        assert reporter.verbose
        assert not reporter.quiet
        assert reporter.total == 100
        assert reporter.desc == "Test operation"

    def test_start_operation_with_total(self):
        """Test starting an operation with a total count."""
        reporter = ProgressReporter(quiet=False)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm:
            mock_progress = MagicMock()
            mock_tqdm.return_value = mock_progress

            reporter.start_operation("Test operation", 50)

            mock_tqdm.assert_called_once()
            assert reporter.progress == mock_progress
            assert reporter.total == 50
            assert reporter.desc == "Test operation"

    def test_start_operation_without_total_verbose(self):
        """Test starting an operation without total in verbose mode."""
        reporter = ProgressReporter(verbose=True, quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.start_operation("Test operation")
            mock_print.assert_called_once_with("🔄 Test operation")

    def test_start_operation_quiet_mode(self):
        """Test starting an operation in quiet mode."""
        reporter = ProgressReporter(quiet=True)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm, \
             patch('builtins.print') as mock_print:

            reporter.start_operation("Test operation", 50)

            mock_tqdm.assert_not_called()
            mock_print.assert_not_called()

    def test_phase_context_manager(self):
        """Test the phase context manager."""
        reporter = ProgressReporter(quiet=False)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm:
            mock_progress = MagicMock()
            mock_tqdm.return_value = mock_progress

            with reporter.phase("Test phase", 10) as phase:
                assert phase == reporter
                assert reporter.current_phase == "Test phase"
                mock_tqdm.assert_called_once()

            # Should close progress after exiting context
            assert reporter.current_phase is None
            mock_progress.close.assert_called_once()

    def test_start_phase_with_total(self):
        """Test starting a phase with a total count."""
        reporter = ProgressReporter(quiet=False)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm:
            mock_progress = MagicMock()
            mock_tqdm.return_value = mock_progress

            reporter.start_phase("Test phase", 25)

            assert reporter.current_phase == "Test phase"
            mock_tqdm.assert_called_once()
            # Check that the progress bar was configured with folder icon
            call_args = mock_tqdm.call_args
            assert "📂 Test phase" in str(call_args)

    def test_start_indeterminate_phase_verbose(self):
        """Test starting an indeterminate phase in verbose mode."""
        reporter = ProgressReporter(verbose=True, quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.start_indeterminate_phase("Loading phase")

            assert reporter.current_phase == "Loading phase"
            mock_print.assert_called_once_with("⏳ Loading phase...")

    def test_set_status(self):
        """Test setting status message."""
        reporter = ProgressReporter(quiet=False)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm:
            mock_progress = MagicMock()
            mock_progress.desc = "Test operation"
            mock_tqdm.return_value = mock_progress
            reporter.progress = mock_progress

            reporter.set_status("Processing files")

            assert reporter.current_status == "Processing files"
            mock_progress.set_description.assert_called_once()

    def test_set_status_verbose_no_progress(self):
        """Test setting status in verbose mode without active progress bar."""
        reporter = ProgressReporter(verbose=True, quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.set_status("Processing files")

            assert reporter.current_status == "Processing files"
            mock_print.assert_called_once_with("  Processing files")

    def test_update_with_status(self):
        """Test updating progress with status message."""
        reporter = ProgressReporter(quiet=False)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm:
            mock_progress = MagicMock()
            mock_progress.desc = "Test operation"
            mock_tqdm.return_value = mock_progress
            reporter.progress = mock_progress

            reporter.update_with_status(2, "Updated status")

            mock_progress.update.assert_called_once_with(2)
            mock_progress.set_description.assert_called_once()

    def test_finish_operation_success(self):
        """Test finishing an operation successfully."""
        reporter = ProgressReporter(verbose=True, quiet=False)
        reporter.desc = "Test operation"

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm, \
             patch('builtins.print') as mock_print:

            mock_progress = MagicMock()
            mock_tqdm.return_value = mock_progress
            reporter.progress = mock_progress

            reporter.finish_operation(success=True)

            mock_progress.close.assert_called_once()
            assert reporter.progress is None
            mock_print.assert_called_once_with("✅ Test operation completed successfully")

    def test_finish_operation_failure(self):
        """Test finishing an operation with failure."""
        reporter = ProgressReporter(quiet=False)
        reporter.desc = "Test operation"

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm, \
             patch('builtins.print') as mock_print:

            mock_progress = MagicMock()
            mock_tqdm.return_value = mock_progress
            reporter.progress = mock_progress

            reporter.finish_operation(success=False)

            mock_progress.close.assert_called_once()
            assert reporter.progress is None
            mock_print.assert_called_once_with("❌ Test operation failed")

    def test_report_error(self):
        """Test reporting an error."""
        reporter = ProgressReporter(quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.report_error("Something went wrong")
            mock_print.assert_called_once_with("❌ Error: Something went wrong")

    def test_report_error_quiet_mode(self):
        """Test reporting an error in quiet mode."""
        reporter = ProgressReporter(quiet=True)

        with patch('builtins.print') as mock_print:
            reporter.report_error("Something went wrong")
            mock_print.assert_not_called()

    def test_message_with_progress(self):
        """Test displaying a message with active progress bar."""
        reporter = ProgressReporter(quiet=False)

        mock_progress = MagicMock()
        reporter.progress = mock_progress

        reporter.message("Test message")

        mock_progress.write.assert_called_once_with("💬 Test message")

    def test_message_without_progress(self):
        """Test displaying a message without active progress bar."""
        reporter = ProgressReporter(quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.message("Test message")
            mock_print.assert_called_once_with("💬 Test message")

    def test_info_verbose(self):
        """Test displaying an info message in verbose mode."""
        reporter = ProgressReporter(verbose=True, quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.info("Info message")
            mock_print.assert_called_once_with("ℹ️  Info message")

    def test_info_not_verbose(self):
        """Test that info messages are not displayed when not verbose."""
        reporter = ProgressReporter(verbose=False, quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.info("Info message")
            mock_print.assert_not_called()

    def test_warning(self):
        """Test displaying a warning message."""
        reporter = ProgressReporter(quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.warning("Warning message")
            mock_print.assert_called_once_with("⚠️  Warning message")

    def test_success(self):
        """Test displaying a success message."""
        reporter = ProgressReporter(quiet=False)

        with patch('builtins.print') as mock_print:
            reporter.success("Success message")
            mock_print.assert_called_once_with("✅ Success message")

    def test_end_phase(self):
        """Test ending a phase."""
        reporter = ProgressReporter(quiet=False)

        mock_progress = MagicMock()
        reporter.progress = mock_progress
        reporter.current_phase = "Test phase"

        reporter.end_phase()

        mock_progress.close.assert_called_once()
        assert reporter.progress is None
        assert reporter.current_phase is None

    def test_multiple_phases(self):
        """Test multiple sequential phases."""
        reporter = ProgressReporter(quiet=False)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm:
            mock_progress_1 = MagicMock()
            mock_progress_2 = MagicMock()
            mock_tqdm.side_effect = [mock_progress_1, mock_progress_2]

            # First phase
            with reporter.phase("Phase 1", 10):
                assert reporter.current_phase == "Phase 1"

            # Second phase
            with reporter.phase("Phase 2", 20):
                assert reporter.current_phase == "Phase 2"

            # Both progress bars should have been closed
            mock_progress_1.close.assert_called_once()
            mock_progress_2.close.assert_called_once()
            assert reporter.current_phase is None

    def test_nested_phases_not_supported(self):
        """Test that nested phases work by replacing the current phase."""
        reporter = ProgressReporter(quiet=False)

        with patch('src.lib.progress_reporter.tqdm') as mock_tqdm:
            mock_progress_1 = MagicMock()
            mock_progress_2 = MagicMock()
            mock_tqdm.side_effect = [mock_progress_1, mock_progress_2]

            with reporter.phase("Outer phase", 10):
                assert reporter.current_phase == "Outer phase"

                with reporter.phase("Inner phase", 5):
                    assert reporter.current_phase == "Inner phase"
                    # Outer phase progress should be closed
                    mock_progress_1.close.assert_called_once()

                # After inner phase ends
                assert reporter.current_phase is None
                mock_progress_2.close.assert_called_once()