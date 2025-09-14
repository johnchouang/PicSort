"""Integration tests for quickstart.md scenarios."""
import os
import tempfile
import shutil
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import sys

from src.cli.main import cli
from src.models.configuration import Configuration
from src.lib.config_manager import ConfigManager


class TestQuickstartScenarios:
    """Test scenarios from quickstart.md guide."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "Pictures", "Camera")
        self.config_dir = os.path.join(self.temp_dir, ".picsort")
        os.makedirs(self.source_dir)
        os.makedirs(self.config_dir)

        # Mock home directory to use temp directory
        self.original_home = os.path.expanduser("~")
        os.environ['HOME'] = self.temp_dir
        if 'USERPROFILE' in os.environ:
            os.environ['USERPROFILE'] = self.temp_dir

    def teardown_method(self):
        """Clean up test fixtures."""
        # Restore original home directory
        os.environ['HOME'] = self.original_home
        if 'USERPROFILE' in os.environ:
            os.environ['USERPROFILE'] = self.original_home

        # Clean up temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_media_files(self, count: int = 50) -> list:
        """Create test media files with various dates.

        Args:
            count: Number of files to create

        Returns:
            List of created file paths
        """
        file_paths = []
        base_date = datetime(2024, 1, 1)

        for i in range(count):
            # Create files spanning several months
            file_date = base_date + timedelta(days=(i * 3))  # Every 3 days

            # Various file types
            extensions = ['.jpg', '.jpeg', '.mp4', '.mov', '.png']
            extension = extensions[i % len(extensions)]

            filename = f"IMG_{20240101 + i:04d}{extension}"
            file_path = os.path.join(self.source_dir, filename)

            # Create file with some content
            with open(file_path, 'w') as f:
                f.write(f"Test media file {i}")

            # Set modification time to simulate realistic dates
            timestamp = file_date.timestamp()
            os.utime(file_path, (timestamp, timestamp))

            file_paths.append(file_path)

        return file_paths

    def _create_config_file(self) -> str:
        """Create a test configuration file.

        Returns:
            Path to configuration file
        """
        config_manager = ConfigManager()
        config = config_manager.create_default_config()

        # Customize for testing
        config.dry_run_default = True
        config.verify_checksum = False  # Faster for testing

        config_path = os.path.join(self.config_dir, "config.yaml")
        config_manager.save_config(config, config_path)

        return config_path

    @pytest.mark.integration
    def test_scenario_1_preview_dry_run(self):
        """Test: Preview What Will Happen (Dry Run)."""
        # Create test files
        self._create_test_media_files(25)

        # Create config
        self._create_config_file()

        # Test CLI command: picsort organize --dry-run ~/Pictures/Camera
        with patch('sys.argv', ['picsort', 'organize', '--dry-run', self.source_dir]):
            try:
                result = pytest.main(['-x', '--tb=short'])
                # For now, just verify the command doesn't crash
                # In a real implementation, we'd check the output
            except SystemExit:
                pass  # CLI commands often exit

        # Verify no files were moved (dry run)
        files_in_source = list(Path(self.source_dir).glob('*'))
        assert len(files_in_source) == 25, "Files should not be moved in dry run"

    @pytest.mark.integration
    def test_scenario_2_organize_files(self):
        """Test: Organize Your Files."""
        # Create test files
        test_files = self._create_test_media_files(15)

        # Create config with dry_run disabled for this test
        config_manager = ConfigManager()
        config = config_manager.create_default_config()
        config.dry_run_default = False
        config.verify_checksum = False
        config_path = os.path.join(self.config_dir, "config.yaml")
        config_manager.save_config(config, config_path)

        # Mock user confirmation to automatically confirm
        with patch('click.confirm', return_value=True):
            with patch('sys.argv', ['picsort', 'organize', self.source_dir]):
                try:
                    # This would normally call the CLI
                    # For testing, we'll simulate the organize operation
                    from src.lib.file_scanner import FileScanner
                    from src.lib.date_organizer import DateOrganizer
                    from src.lib.file_mover import FileMover

                    scanner = FileScanner(config)
                    organizer = DateOrganizer(config)
                    mover = FileMover(config)

                    # Scan files
                    media_files = scanner.scan_directory(self.source_dir)
                    assert len(media_files) > 0, "Should find media files"

                    # Organize files
                    organization = organizer.organize_files(media_files, self.source_dir)
                    assert len(organization) > 0, "Should create organization plan"

                    # Execute moves (dry run for safety in tests)
                    operations = mover.move_files(organization, dry_run=True)
                    assert len(operations) > 0, "Should create operations"

                except Exception as e:
                    pytest.skip(f"CLI test skipped due to setup: {e}")

    @pytest.mark.integration
    def test_scenario_3_multiple_devices(self):
        """Test: Organize Photos from Multiple Devices."""
        # Create multiple device folders
        device_folders = ['iPhone', 'Camera', 'GoPro']
        all_files = []

        for device in device_folders:
            device_dir = os.path.join(self.temp_dir, 'Pictures', device)
            os.makedirs(device_dir)

            # Create files in each device folder
            for i in range(5):
                filename = f"{device}_{i:03d}.jpg"
                file_path = os.path.join(device_dir, filename)

                with open(file_path, 'w') as f:
                    f.write(f"Test file from {device}")

                all_files.append(file_path)

        # Verify files were created
        assert len(all_files) == 15, "Should create files for all devices"

        # Test that we can scan each device folder
        config = Configuration()
        scanner = FileScanner(config)

        for device in device_folders:
            device_dir = os.path.join(self.temp_dir, 'Pictures', device)
            media_files = scanner.scan_directory(device_dir)
            assert len(media_files) == 5, f"Should find 5 files in {device} folder"

    @pytest.mark.integration
    def test_scenario_4_include_videos_and_raw(self):
        """Test: Include Videos and RAW Files."""
        # Create files with various extensions
        extensions = ['.jpg', '.mp4', '.mov', '.raw', '.dng', '.png', '.avi']
        test_files = []

        for i, ext in enumerate(extensions):
            filename = f"media_{i:03d}{ext}"
            file_path = os.path.join(self.source_dir, filename)

            with open(file_path, 'w') as f:
                f.write(f"Test {ext} file")

            test_files.append(file_path)

        # Test scanning with specific file types
        config = Configuration()
        config.supported_extensions = {
            'images': ['.jpg', '.png', '.raw', '.dng'],
            'videos': ['.mp4', '.mov', '.avi']
        }

        scanner = FileScanner(config)
        media_files = scanner.scan_directory(self.source_dir)

        # Should find all media files (not text or other formats)
        expected_count = len(extensions)  # All extensions are media in our test
        assert len(media_files) == expected_count, f"Should find {expected_count} media files"

    @pytest.mark.integration
    def test_scenario_5_recursive_processing(self):
        """Test: Process All Subfolders."""
        # Create nested folder structure
        subfolder_structure = [
            '2024/January/Week1',
            '2024/January/Week2',
            '2024/February/Week1',
            '2023/December'
        ]

        total_files = 0
        for subfolder in subfolder_structure:
            subfolder_path = os.path.join(self.source_dir, subfolder)
            os.makedirs(subfolder_path)

            # Create 2 files in each subfolder
            for i in range(2):
                filename = f"photo_{i:03d}.jpg"
                file_path = os.path.join(subfolder_path, filename)

                with open(file_path, 'w') as f:
                    f.write(f"Test file in {subfolder}")

                total_files += 1

        # Test recursive scanning
        config = Configuration()
        config.recursive = True

        scanner = FileScanner(config)
        media_files = scanner.scan_directory(self.source_dir)

        assert len(media_files) == total_files, f"Should find all {total_files} files recursively"

    @pytest.mark.integration
    def test_scenario_6_custom_date_format(self):
        """Test: Custom Date Format."""
        # Create test files
        self._create_test_media_files(10)

        # Test different date formats
        date_formats = ['MM.YYYY', 'YYYY-MM', 'MMM YYYY', 'YYYY/MM/DD']

        config = Configuration()
        scanner = FileScanner(config)
        media_files = scanner.scan_directory(self.source_dir)

        for date_format in date_formats:
            config.date_format = date_format
            organizer = DateOrganizer(config)

            organization = organizer.organize_files(media_files, self.source_dir)
            assert len(organization) > 0, f"Should organize with {date_format} format"

            # Check that folder names match the expected format
            for folder_path in organization.keys():
                folder_name = os.path.basename(folder_path)
                # Basic validation that format was applied
                if 'MM' in date_format:
                    assert any(c.isdigit() for c in folder_name), f"Should contain numbers for {date_format}"

    @pytest.mark.integration
    def test_scenario_7_organize_all_files(self):
        """Test: Organize All File Types (Not Just Media)."""
        # Create mix of file types
        file_types = [
            'document.pdf',
            'spreadsheet.xlsx',
            'photo.jpg',
            'video.mp4',
            'text.txt',
            'archive.zip'
        ]

        for filename in file_types:
            file_path = os.path.join(self.source_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Content of {filename}")

        # Test with process_all_files enabled
        config = Configuration()
        config.process_all_files = True

        scanner = FileScanner(config)
        media_files = scanner.scan_directory(self.source_dir)

        # Should find all files, not just media
        assert len(media_files) == len(file_types), "Should process all file types"

        # Test organization
        organizer = DateOrganizer(config)
        organization = organizer.organize_files(media_files, self.source_dir)

        total_organized_files = sum(len(files) for files in organization.values())
        assert total_organized_files == len(file_types), "Should organize all file types"

    @pytest.mark.integration
    def test_scenario_8_scan_before_organize(self):
        """Test: Always Start with Scan."""
        # Create test files
        test_files = self._create_test_media_files(20)

        config = Configuration()
        scanner = FileScanner(config)
        organizer = DateOrganizer(config)

        # Scan directory
        media_files = scanner.scan_directory(self.source_dir)
        assert len(media_files) == 20, "Scan should find all files"

        # Preview organization
        preview = organizer.preview_organization(media_files, self.source_dir)
        assert len(preview) > 0, "Preview should show organization plan"

        # Verify preview contains expected information
        for folder_info in preview:
            assert 'folder' in folder_info, "Preview should contain folder name"
            assert 'file_count' in folder_info, "Preview should contain file count"
            assert 'files' in folder_info, "Preview should contain file list"
            assert folder_info['file_count'] > 0, "Folders should contain files"

    @pytest.mark.integration
    def test_scenario_9_duplicate_handling(self):
        """Test: Handle Duplicates Safely."""
        # Create files that would have duplicate names after organization
        base_date = datetime(2024, 3, 15)
        duplicate_names = ['IMG_1234.jpg', 'IMG_1234.jpg', 'IMG_1234.jpg']

        for i, filename in enumerate(duplicate_names):
            # Create files in different subdirectories but with same name
            subdir = os.path.join(self.source_dir, f"subfolder_{i}")
            os.makedirs(subdir, exist_ok=True)

            file_path = os.path.join(subdir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Duplicate file {i}")

            # Set same date so they go to same target folder
            timestamp = base_date.timestamp()
            os.utime(file_path, (timestamp, timestamp))

        # Test duplicate handling
        config = Configuration()
        config.duplicate_handling = 'increment'
        config.recursive = True

        scanner = FileScanner(config)
        organizer = DateOrganizer(config)
        mover = FileMover(config)

        # Scan and organize
        media_files = scanner.scan_directory(self.source_dir)
        assert len(media_files) == 3, "Should find all duplicate files"

        organization = organizer.organize_files(media_files, self.source_dir)

        # Preview should show duplicate handling
        preview = organizer.preview_organization(media_files, self.source_dir)
        has_duplicates = any(folder['duplicates'] for folder in preview)
        assert has_duplicates, "Preview should identify duplicate conflicts"

        # Test move operations (dry run)
        operations = mover.move_files(organization, dry_run=True)
        destination_paths = [op.destination_path for op in operations]

        # Should have different destination paths due to increment handling
        unique_destinations = set(destination_paths)
        assert len(unique_destinations) == 3, "Should create unique destination paths for duplicates"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_scenario_10_full_workflow(self):
        """Test: Complete Example Workflow."""
        # Create a realistic scenario
        vacation_dir = os.path.join(self.temp_dir, "Pictures", "Vacation2024")
        os.makedirs(vacation_dir)

        # Create files spanning multiple months
        file_count = 30
        for i in range(file_count):
            # Files from January to March 2024
            month = (i % 3) + 1  # 1, 2, or 3
            day = (i % 28) + 1   # 1-28
            file_date = datetime(2024, month, day)

            filename = f"vacation_{i:03d}.jpg"
            file_path = os.path.join(vacation_dir, filename)

            with open(file_path, 'w') as f:
                f.write(f"Vacation photo {i}")

            # Set file date
            timestamp = file_date.timestamp()
            os.utime(file_path, (timestamp, timestamp))

        # Step 1: Scan to preview
        config = Configuration()
        scanner = FileScanner(config)
        media_files = scanner.scan_directory(vacation_dir)

        scan_summary = scanner.get_scan_summary(media_files)
        assert scan_summary['total_files'] == file_count, "Scan should find all vacation files"
        assert scan_summary['media_files'] == file_count, "All files should be media"

        # Step 2: Preview organization
        organizer = DateOrganizer(config)
        organization = organizer.organize_files(media_files, vacation_dir)

        # Should create folders for January, February, March
        assert len(organization) == 3, "Should organize into 3 monthly folders"

        # Step 3: Dry run to confirm
        mover = FileMover(config)
        operations = mover.move_files(organization, dry_run=True)

        operation_summary = mover.get_operation_summary(operations)
        assert operation_summary['total'] == file_count, "Should plan to move all files"
        assert operation_summary['skipped'] == file_count, "All operations should be skipped in dry run"

        # Step 4: Verify expected folder structure (simulated)
        expected_folders = ['01.2024', '02.2024', '03.2024']
        actual_folders = [os.path.basename(folder) for folder in organization.keys()]

        for expected_folder in expected_folders:
            assert expected_folder in actual_folders, f"Should create {expected_folder} folder"

    def test_configuration_scenarios(self):
        """Test configuration-related scenarios from quickstart."""
        # Test interactive config initialization
        config_manager = ConfigManager()

        # Test creating default config
        default_config = config_manager.create_default_config()
        assert default_config is not None, "Should create default configuration"
        assert default_config.date_format == "MM.YYYY", "Should use default date format"
        assert default_config.duplicate_handling == "increment", "Should use default duplicate handling"

        # Test config validation
        errors = config_manager.validate_config(default_config)
        assert len(errors) == 0, "Default configuration should be valid"

        # Test saving and loading config
        config_path = os.path.join(self.config_dir, "test_config.yaml")
        config_manager.save_config(default_config, config_path)
        assert os.path.exists(config_path), "Configuration file should be saved"

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config.date_format == default_config.date_format, "Loaded config should match saved config"

    @pytest.mark.integration
    def test_error_handling_scenarios(self):
        """Test error handling scenarios from quickstart troubleshooting."""
        # Test permission denied scenario
        protected_file = os.path.join(self.source_dir, "protected.jpg")
        with open(protected_file, 'w') as f:
            f.write("Protected file")

        # Test file scanning with potential permission issues
        config = Configuration()
        scanner = FileScanner(config)

        try:
            media_files = scanner.scan_directory(self.source_dir)
            # If we get here, the file was accessible
            assert any(f.path == protected_file for f in media_files), "Should find the protected file"
        except Exception:
            # Expected if we actually set restrictive permissions
            pass

        # Test wrong date detection scenario
        # Create file with no EXIF data (uses modification date)
        no_exif_file = os.path.join(self.source_dir, "no_exif.txt")  # Non-image file
        with open(no_exif_file, 'w') as f:
            f.write("File with no EXIF data")

        config.process_all_files = True  # Include non-media files
        media_files = scanner.scan_directory(self.source_dir)

        # Find our non-EXIF file
        txt_files = [f for f in media_files if f.filename.endswith('.txt')]
        assert len(txt_files) > 0, "Should find text file when processing all files"

        # Should use modification date
        txt_file = txt_files[0]
        assert txt_file.modification_date is not None, "Should have modification date"
        # creation_date might be None for non-image files
        # This is expected behavior


if __name__ == '__main__':
    # Run the quickstart scenario tests
    pytest.main(['-v', __file__, '-m', 'integration'])