"""Unit tests for oldest date logic in MediaFile."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.models.media_file import MediaFile


class TestOldestDateLogic:
    """Test the oldest date logic functionality."""

    def test_get_oldest_date_with_all_dates(self):
        """Test getting oldest date when all dates are available."""
        # EXIF date is oldest (2023-01-01)
        # Creation date is middle (2023-06-15)
        # Modification date is newest (2023-12-25)
        media_file = self._create_test_media_file()
        media_file.exif_date = datetime(2023, 1, 1, 10, 0, 0)
        media_file.creation_date = datetime(2023, 6, 15, 14, 30, 0)
        media_file.modification_date = datetime(2023, 12, 25, 20, 45, 0)

        oldest = media_file.get_oldest_date()
        assert oldest == datetime(2023, 1, 1, 10, 0, 0)

    def test_get_oldest_date_exif_is_newest(self):
        """Test when EXIF date is actually newer than filesystem dates."""
        # Creation date is oldest (2022-01-01)
        # Modification date is middle (2023-06-15)
        # EXIF date is newest (2023-12-25)
        media_file = self._create_test_media_file()
        media_file.exif_date = datetime(2023, 12, 25, 20, 45, 0)
        media_file.creation_date = datetime(2022, 1, 1, 10, 0, 0)
        media_file.modification_date = datetime(2023, 6, 15, 14, 30, 0)

        oldest = media_file.get_oldest_date()
        assert oldest == datetime(2022, 1, 1, 10, 0, 0)

    def test_get_oldest_date_modification_is_oldest(self):
        """Test when modification date is oldest."""
        # Modification date is oldest (2020-01-01)
        # Creation date is middle (2022-06-15)
        # EXIF date is newest (2023-12-25)
        media_file = self._create_test_media_file()
        media_file.exif_date = datetime(2023, 12, 25, 20, 45, 0)
        media_file.creation_date = datetime(2022, 6, 15, 14, 30, 0)
        media_file.modification_date = datetime(2020, 1, 1, 10, 0, 0)

        oldest = media_file.get_oldest_date()
        assert oldest == datetime(2020, 1, 1, 10, 0, 0)

    def test_get_oldest_date_no_exif_date(self):
        """Test getting oldest date when EXIF date is None."""
        # Only creation and modification dates available
        # Creation date is older
        media_file = self._create_test_media_file()
        media_file.exif_date = None
        media_file.creation_date = datetime(2022, 6, 15, 14, 30, 0)
        media_file.modification_date = datetime(2023, 12, 25, 20, 45, 0)

        oldest = media_file.get_oldest_date()
        assert oldest == datetime(2022, 6, 15, 14, 30, 0)

    def test_get_oldest_date_no_creation_date(self):
        """Test getting oldest date when creation date is None."""
        # Only EXIF and modification dates available
        # EXIF date is older
        media_file = self._create_test_media_file()
        media_file.exif_date = datetime(2021, 1, 1, 10, 0, 0)
        media_file.creation_date = None
        media_file.modification_date = datetime(2023, 12, 25, 20, 45, 0)

        oldest = media_file.get_oldest_date()
        assert oldest == datetime(2021, 1, 1, 10, 0, 0)

    def test_get_oldest_date_only_modification_date(self):
        """Test fallback to modification date when others are None."""
        # Only modification date available
        media_file = self._create_test_media_file()
        media_file.exif_date = None
        media_file.creation_date = None
        media_file.modification_date = datetime(2023, 12, 25, 20, 45, 0)

        oldest = media_file.get_oldest_date()
        assert oldest == datetime(2023, 12, 25, 20, 45, 0)

    def test_get_target_folder_uses_oldest_date(self):
        """Test that get_target_folder uses the oldest date."""
        # EXIF date is oldest (January 2023)
        # Creation date is newer (June 2023)
        # Modification date is newest (December 2023)
        media_file = self._create_test_media_file()
        media_file.exif_date = datetime(2023, 1, 15, 10, 0, 0)
        media_file.creation_date = datetime(2023, 6, 15, 14, 30, 0)
        media_file.modification_date = datetime(2023, 12, 25, 20, 45, 0)

        target_folder = media_file.get_target_folder()
        # Should use January (01) from EXIF date, not June (06) from creation
        assert target_folder == "01.2023"

    def test_get_target_folder_complex_oldest_date_scenario(self):
        """Test complex scenario where creation date is oldest."""
        # Creation date is oldest (March 2022)
        # EXIF date is newer (January 2023)
        # Modification date is newest (December 2023)
        media_file = self._create_test_media_file()
        media_file.exif_date = datetime(2023, 1, 15, 10, 0, 0)
        media_file.creation_date = datetime(2022, 3, 10, 9, 15, 0)
        media_file.modification_date = datetime(2023, 12, 25, 20, 45, 0)

        target_folder = media_file.get_target_folder()
        # Should use March 2022 from creation date
        assert target_folder == "03.2022"

    def test_get_oldest_date_identical_dates(self):
        """Test behavior when all dates are identical."""
        same_date = datetime(2023, 6, 15, 14, 30, 0)
        media_file = self._create_test_media_file()
        media_file.exif_date = same_date
        media_file.creation_date = same_date
        media_file.modification_date = same_date

        oldest = media_file.get_oldest_date()
        assert oldest == same_date

    def test_get_oldest_date_microsecond_precision(self):
        """Test oldest date logic with microsecond precision."""
        # Dates very close together, differing by microseconds
        base_time = datetime(2023, 6, 15, 14, 30, 0)
        media_file = self._create_test_media_file()
        media_file.exif_date = base_time.replace(microsecond=1000)     # Oldest
        media_file.creation_date = base_time.replace(microsecond=2000)  # Middle
        media_file.modification_date = base_time.replace(microsecond=3000)  # Newest

        oldest = media_file.get_oldest_date()
        assert oldest == base_time.replace(microsecond=1000)

    def test_get_oldest_date_year_boundary(self):
        """Test oldest date logic across year boundaries."""
        # EXIF date from previous year
        # Creation and modification dates from current year
        media_file = self._create_test_media_file()
        media_file.exif_date = datetime(2022, 12, 31, 23, 59, 59)      # Previous year
        media_file.creation_date = datetime(2023, 1, 1, 0, 0, 1)      # New year
        media_file.modification_date = datetime(2023, 6, 15, 14, 30, 0)

        oldest = media_file.get_oldest_date()
        assert oldest == datetime(2022, 12, 31, 23, 59, 59)

        target_folder = media_file.get_target_folder()
        assert target_folder == "12.2022"  # Should use December 2022

    def _create_test_media_file(self):
        """Helper to create a basic MediaFile for testing."""
        # Create a temporary file for validation
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_path = tmp_file.name

        try:
            # Create MediaFile with basic required fields
            media_file = MediaFile(
                path=tmp_path,
                filename="test.jpg",
                size=100,
                creation_date=datetime.now(),
                modification_date=datetime.now(),
                file_type=".jpg",
                is_media=True,
                metadata_source="test",
                error=None,
                exif_date=None
            )
            return media_file
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


class TestDateOrganizerOldestDateIntegration:
    """Test DateOrganizer integration with oldest date logic."""

    def test_organize_uses_oldest_dates(self):
        """Test that DateOrganizer uses oldest dates for organization."""
        from src.lib.date_organizer import DateOrganizer
        from src.models.configuration import Configuration

        config = Configuration.create_default()
        organizer = DateOrganizer(config)

        # Create test files with different oldest dates
        files = [
            self._create_test_media_file_with_dates(
                "photo1.jpg",
                exif_date=datetime(2023, 1, 15),      # Oldest - should use Jan 2023
                creation_date=datetime(2023, 6, 15),
                modification_date=datetime(2023, 12, 25)
            ),
            self._create_test_media_file_with_dates(
                "photo2.jpg",
                exif_date=datetime(2023, 8, 10),      # Newest
                creation_date=datetime(2023, 3, 20),  # Oldest - should use Mar 2023
                modification_date=datetime(2023, 7, 5)
            ),
            self._create_test_media_file_with_dates(
                "photo3.jpg",
                exif_date=None,
                creation_date=None,
                modification_date=datetime(2023, 2, 28)  # Only date - should use Feb 2023
            )
        ]

        organization = organizer.organize(files)

        # Should have 3 folders: 01.2023, 02.2023, 03.2023
        assert len(organization) == 3
        assert "01.2023" in organization  # photo1 uses EXIF date (January)
        assert "02.2023" in organization  # photo3 uses modification date (February)
        assert "03.2023" in organization  # photo2 uses creation date (March)

        # Each folder should have one file
        assert len(organization["01.2023"]) == 1
        assert len(organization["02.2023"]) == 1
        assert len(organization["03.2023"]) == 1

        # Verify correct files are in correct folders
        assert organization["01.2023"][0].filename == "photo1.jpg"
        assert organization["02.2023"][0].filename == "photo3.jpg"
        assert organization["03.2023"][0].filename == "photo2.jpg"

    def _create_test_media_file_with_dates(self, filename, exif_date=None, creation_date=None, modification_date=None):
        """Helper to create MediaFile with specific dates."""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_path = tmp_file.name

        try:
            media_file = MediaFile(
                path=tmp_path,
                filename=filename,
                size=100,
                creation_date=creation_date,
                modification_date=modification_date or datetime.now(),
                file_type=".jpg",
                is_media=True,
                metadata_source="test",
                error=None,
                exif_date=exif_date
            )
            return media_file
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass