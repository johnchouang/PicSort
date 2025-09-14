"""Unit tests for date extraction logic."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from PIL import Image
from PIL.ExifTags import TAGS

from src.lib.exif_reader import ExifReader
from src.lib.date_organizer import DateOrganizer
from src.models.media_file import MediaFile
from src.models.configuration import Configuration


class TestExifReader:
    """Test EXIF date extraction functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.exif_reader = ExifReader()

    def test_parse_exif_datetime_standard_format(self):
        """Test parsing standard EXIF datetime format."""
        test_cases = [
            ("2023:12:25 14:30:45", datetime(2023, 12, 25, 14, 30, 45)),
            ("2024:01:01 00:00:00", datetime(2024, 1, 1, 0, 0, 0)),
            ("2022:06:15 23:59:59", datetime(2022, 6, 15, 23, 59, 59)),
        ]

        for datetime_str, expected in test_cases:
            result = self.exif_reader._parse_exif_datetime(datetime_str)
            assert result == expected, f"Failed to parse '{datetime_str}'"

    def test_parse_exif_datetime_alternative_formats(self):
        """Test parsing alternative datetime formats."""
        test_cases = [
            ("2023-12-25 14:30:45", datetime(2023, 12, 25, 14, 30, 45)),
            ("2023:12:25", datetime(2023, 12, 25, 0, 0, 0)),
            ("2023-12-25", datetime(2023, 12, 25, 0, 0, 0)),
            ("2023/12/25 14:30:45", datetime(2023, 12, 25, 14, 30, 45)),
            ("2023/12/25", datetime(2023, 12, 25, 0, 0, 0)),
        ]

        for datetime_str, expected in test_cases:
            result = self.exif_reader._parse_exif_datetime(datetime_str)
            assert result == expected, f"Failed to parse '{datetime_str}'"

    def test_parse_exif_datetime_invalid_formats(self):
        """Test parsing invalid datetime strings."""
        invalid_cases = [
            "",
            None,
            "not a date",
            "2023:13:25 14:30:45",  # Invalid month
            "2023:12:32 14:30:45",  # Invalid day
            "2023:12:25 25:30:45",  # Invalid hour
            "2023/12/25T14:30:45Z",  # ISO format (not supported)
        ]

        for invalid_str in invalid_cases:
            result = self.exif_reader._parse_exif_datetime(invalid_str)
            assert result is None, f"Should not parse invalid datetime: '{invalid_str}'"

    def test_parse_exif_datetime_whitespace_handling(self):
        """Test parsing with whitespace."""
        test_cases = [
            ("  2023:12:25 14:30:45  ", datetime(2023, 12, 25, 14, 30, 45)),
            ("\t2023:12:25 14:30:45\n", datetime(2023, 12, 25, 14, 30, 45)),
            ("   ", None),
        ]

        for datetime_str, expected in test_cases:
            result = self.exif_reader._parse_exif_datetime(datetime_str)
            assert result == expected, f"Failed to handle whitespace in '{datetime_str}'"

    @patch('src.lib.exif_reader.Image.open')
    def test_extract_creation_date_with_datetime_original(self, mock_open):
        """Test extracting DateTimeOriginal from EXIF."""
        # Mock image with EXIF data
        mock_image = Mock()
        mock_exif = {}

        # Find DateTimeOriginal tag ID
        datetime_original_tag = None
        for tag_id, tag_name in TAGS.items():
            if tag_name == 'DateTimeOriginal':
                datetime_original_tag = tag_id
                break

        mock_exif[datetime_original_tag] = "2023:12:25 14:30:45"
        mock_image._getexif.return_value = mock_exif
        mock_open.return_value.__enter__.return_value = mock_image

        result = self.exif_reader.extract_creation_date("test.jpg")
        assert result == datetime(2023, 12, 25, 14, 30, 45)

    @patch('src.lib.exif_reader.Image.open')
    def test_extract_creation_date_fallback_to_datetime_digitized(self, mock_open):
        """Test falling back to DateTimeDigitized when DateTimeOriginal is not available."""
        mock_image = Mock()
        mock_exif = {}

        # Find DateTimeDigitized tag ID
        datetime_digitized_tag = None
        for tag_id, tag_name in TAGS.items():
            if tag_name == 'DateTimeDigitized':
                datetime_digitized_tag = tag_id
                break

        mock_exif[datetime_digitized_tag] = "2023:12:25 15:45:30"
        mock_image._getexif.return_value = mock_exif
        mock_open.return_value.__enter__.return_value = mock_image

        result = self.exif_reader.extract_creation_date("test.jpg")
        assert result == datetime(2023, 12, 25, 15, 45, 30)

    @patch('src.lib.exif_reader.Image.open')
    def test_extract_creation_date_fallback_to_datetime(self, mock_open):
        """Test falling back to DateTime when higher priority tags are not available."""
        mock_image = Mock()
        mock_exif = {}

        # Find DateTime tag ID
        datetime_tag = None
        for tag_id, tag_name in TAGS.items():
            if tag_name == 'DateTime':
                datetime_tag = tag_id
                break

        mock_exif[datetime_tag] = "2023:12:25 16:15:20"
        mock_image._getexif.return_value = mock_exif
        mock_open.return_value.__enter__.return_value = mock_image

        result = self.exif_reader.extract_creation_date("test.jpg")
        assert result == datetime(2023, 12, 25, 16, 15, 20)

    @patch('src.lib.exif_reader.Image.open')
    def test_extract_creation_date_no_exif(self, mock_open):
        """Test handling files with no EXIF data."""
        mock_image = Mock()
        mock_image._getexif.return_value = None
        mock_open.return_value.__enter__.return_value = mock_image

        result = self.exif_reader.extract_creation_date("test.jpg")
        assert result is None

    def test_extract_creation_date_unsupported_format(self):
        """Test handling unsupported file formats."""
        unsupported_files = [
            "test.txt",
            "test.pdf",
            "test.doc",
            "test.mp4",  # Video files not supported by EXIF reader
        ]

        for filename in unsupported_files:
            result = self.exif_reader.extract_creation_date(filename)
            assert result is None, f"Should not extract from unsupported format: {filename}"

    def test_extract_creation_date_non_exif_image_formats(self):
        """Test handling image formats that don't support EXIF."""
        with patch('src.lib.exif_reader.Image.open') as mock_open:
            mock_image = Mock()
            mock_open.return_value.__enter__.return_value = mock_image

            non_exif_formats = ["test.png", "test.gif", "test.bmp"]

            for filename in non_exif_formats:
                result = self.exif_reader.extract_creation_date(filename)
                assert result is None, f"Should not extract EXIF from format: {filename}"

    @patch('src.lib.exif_reader.Image.open')
    def test_extract_creation_date_corrupted_exif(self, mock_open):
        """Test handling corrupted EXIF data."""
        mock_image = Mock()
        mock_exif = {}

        # Find DateTime tag ID and set corrupted value
        datetime_tag = None
        for tag_id, tag_name in TAGS.items():
            if tag_name == 'DateTime':
                datetime_tag = tag_id
                break

        mock_exif[datetime_tag] = "corrupted:date:string"
        mock_image._getexif.return_value = mock_exif
        mock_open.return_value.__enter__.return_value = mock_image

        result = self.exif_reader.extract_creation_date("test.jpg")
        assert result is None

    @patch('src.lib.exif_reader.Image.open')
    def test_extract_creation_date_exception_handling(self, mock_open):
        """Test handling exceptions during EXIF extraction."""
        mock_open.side_effect = Exception("File not found")

        result = self.exif_reader.extract_creation_date("nonexistent.jpg")
        assert result is None

    def test_can_extract_metadata(self):
        """Test checking if metadata can be extracted from file types."""
        supported_cases = [
            ("test.jpg", True),
            ("test.jpeg", True),
            ("test.png", True),
            ("test.gif", True),
            ("test.bmp", True),
            ("test.tiff", True),
            ("test.tif", True),
            ("test.webp", True),
            ("TEST.JPG", True),  # Case insensitive
        ]

        unsupported_cases = [
            ("test.txt", False),
            ("test.pdf", False),
            ("test.mp4", False),
            ("test.avi", False),
            ("test.doc", False),
            ("test", False),  # No extension
        ]

        for filename, expected in supported_cases + unsupported_cases:
            result = self.exif_reader.can_extract_metadata(filename)
            assert result == expected, f"Metadata extraction check failed for {filename}"


class TestDateOrganizer:
    """Test date organization functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Configuration()
        self.config.date_format = "MM.YYYY"
        self.config.process_all_files = False
        self.organizer = DateOrganizer(self.config)

    def test_format_date_folder_mm_yyyy(self):
        """Test formatting dates into MM.YYYY format."""
        test_cases = [
            (datetime(2023, 1, 15), "01.2023"),
            (datetime(2023, 12, 31), "12.2023"),
            (datetime(2024, 6, 1), "06.2024"),
        ]

        for date, expected in test_cases:
            result = self.organizer._format_date_folder(date)
            assert result == expected, f"Failed to format {date}"

    def test_format_date_folder_yyyy_mm(self):
        """Test formatting dates into YYYY-MM format."""
        self.config.date_format = "YYYY-MM"

        test_cases = [
            (datetime(2023, 1, 15), "2023-01"),
            (datetime(2023, 12, 31), "2023-12"),
            (datetime(2024, 6, 1), "2024-06"),
        ]

        for date, expected in test_cases:
            result = self.organizer._format_date_folder(date)
            assert result == expected, f"Failed to format {date}"

    def test_format_date_folder_mmm_yyyy(self):
        """Test formatting dates with month names."""
        self.config.date_format = "MMM YYYY"

        test_cases = [
            (datetime(2023, 1, 15), "Jan 2023"),
            (datetime(2023, 12, 31), "Dec 2023"),
            (datetime(2024, 6, 1), "Jun 2024"),
        ]

        for date, expected in test_cases:
            result = self.organizer._format_date_folder(date)
            assert result == expected, f"Failed to format {date}"

    def test_format_date_folder_complex_format(self):
        """Test complex date formatting with multiple placeholders."""
        self.config.date_format = "YYYY-MM-DD (MMM)"

        test_cases = [
            (datetime(2023, 1, 15), "2023-01-15 (Jan)"),
            (datetime(2023, 12, 31), "2023-12-31 (Dec)"),
            (datetime(2024, 6, 1), "2024-06-01 (Jun)"),
        ]

        for date, expected in test_cases:
            result = self.organizer._format_date_folder(date)
            assert result == expected, f"Failed to format {date}"

    def test_get_target_folder_with_creation_date(self):
        """Test getting target folder using creation date."""
        media_file = MediaFile("test.jpg")
        media_file.creation_date = datetime(2023, 6, 15, 14, 30, 0)
        media_file.modification_date = datetime(2023, 7, 20, 10, 0, 0)

        result = self.organizer._get_target_folder(media_file, "/base")
        expected = "/base/06.2023"  # Should use creation date, not modification
        assert result == expected

    def test_get_target_folder_fallback_to_modification_date(self):
        """Test falling back to modification date when creation date is None."""
        media_file = MediaFile("test.jpg")
        media_file.creation_date = None
        media_file.modification_date = datetime(2023, 7, 20, 10, 0, 0)

        result = self.organizer._get_target_folder(media_file, "/base")
        expected = "/base/07.2023"  # Should use modification date
        assert result == expected

    def test_should_organize_file_media_files_only(self):
        """Test organizing only media files when process_all_files is False."""
        self.config.process_all_files = False

        # Media file should be organized
        media_file = MediaFile("photo.jpg")
        media_file.is_media = True
        media_file.error = None
        assert self.organizer._should_organize_file(media_file) is True

        # Non-media file should not be organized
        text_file = MediaFile("document.txt")
        text_file.is_media = False
        text_file.error = None
        assert self.organizer._should_organize_file(text_file) is False

    def test_should_organize_file_all_files(self):
        """Test organizing all files when process_all_files is True."""
        self.config.process_all_files = True

        # Both media and non-media files should be organized
        media_file = MediaFile("photo.jpg")
        media_file.is_media = True
        media_file.error = None
        assert self.organizer._should_organize_file(media_file) is True

        text_file = MediaFile("document.txt")
        text_file.is_media = False
        text_file.error = None
        assert self.organizer._should_organize_file(text_file) is True

    def test_should_organize_file_with_errors(self):
        """Test not organizing files with errors."""
        # File with error should not be organized regardless of settings
        error_file = MediaFile("corrupted.jpg")
        error_file.is_media = True
        error_file.error = "File corrupted"

        self.config.process_all_files = False
        assert self.organizer._should_organize_file(error_file) is False

        self.config.process_all_files = True
        assert self.organizer._should_organize_file(error_file) is False

    def test_organize_files_basic_grouping(self):
        """Test basic file organization and grouping."""
        files = [
            self._create_test_file("photo1.jpg", datetime(2023, 6, 15), is_media=True),
            self._create_test_file("photo2.jpg", datetime(2023, 6, 20), is_media=True),
            self._create_test_file("photo3.jpg", datetime(2023, 7, 5), is_media=True),
        ]

        result = self.organizer.organize_files(files, "/base")

        assert len(result) == 2  # Two months: June and July
        assert "/base/06.2023" in result
        assert "/base/07.2023" in result
        assert len(result["/base/06.2023"]) == 2  # Two June photos
        assert len(result["/base/07.2023"]) == 1   # One July photo

    def test_organize_files_skip_non_media(self):
        """Test skipping non-media files when process_all_files is False."""
        files = [
            self._create_test_file("photo.jpg", datetime(2023, 6, 15), is_media=True),
            self._create_test_file("document.txt", datetime(2023, 6, 15), is_media=False),
        ]

        result = self.organizer.organize_files(files, "/base")

        assert len(result) == 1
        assert "/base/06.2023" in result
        assert len(result["/base/06.2023"]) == 1  # Only the photo
        assert result["/base/06.2023"][0].filename == "photo.jpg"

    def test_organize_files_include_all_files(self):
        """Test including all files when process_all_files is True."""
        self.config.process_all_files = True

        files = [
            self._create_test_file("photo.jpg", datetime(2023, 6, 15), is_media=True),
            self._create_test_file("document.txt", datetime(2023, 6, 15), is_media=False),
        ]

        result = self.organizer.organize_files(files, "/base")

        assert len(result) == 1
        assert "/base/06.2023" in result
        assert len(result["/base/06.2023"]) == 2  # Both files

    def test_organize_files_skip_error_files(self):
        """Test skipping files with errors."""
        files = [
            self._create_test_file("good.jpg", datetime(2023, 6, 15), is_media=True),
            self._create_test_file("bad.jpg", datetime(2023, 6, 15), is_media=True, error="Corrupted"),
        ]

        result = self.organizer.organize_files(files, "/base")

        assert len(result) == 1
        assert "/base/06.2023" in result
        assert len(result["/base/06.2023"]) == 1  # Only the good file
        assert result["/base/06.2023"][0].filename == "good.jpg"

    def test_get_required_folders(self):
        """Test getting required folders from organization."""
        files = [
            self._create_test_file("photo1.jpg", datetime(2023, 6, 15), is_media=True),
            self._create_test_file("photo2.jpg", datetime(2023, 7, 5), is_media=True),
            self._create_test_file("photo3.jpg", datetime(2023, 8, 10), is_media=True),
        ]

        organization = self.organizer.organize_files(files, "/base")
        required_folders = self.organizer.get_required_folders(organization)

        expected_folders = {"/base/06.2023", "/base/07.2023", "/base/08.2023"}
        assert required_folders == expected_folders

    def test_get_organization_summary(self):
        """Test getting organization summary statistics."""
        files = [
            self._create_test_file("photo1.jpg", datetime(2023, 6, 15), is_media=True, size=1000),
            self._create_test_file("photo2.jpg", datetime(2023, 7, 5), is_media=True, size=2000),
            self._create_test_file("photo3.jpg", datetime(2023, 8, 10), is_media=True, size=1500),
        ]

        organization = self.organizer.organize_files(files, "/base")
        summary = self.organizer.get_organization_summary(organization)

        assert summary['total_files'] == 3
        assert summary['total_folders'] == 3
        assert summary['total_size_bytes'] == 4500
        assert summary['date_range'] == (datetime(2023, 6, 15), datetime(2023, 8, 10))
        assert len(summary['folders']) == 3

    def _create_test_file(self, filename, date, is_media=True, error=None, size=1000):
        """Helper to create test MediaFile objects."""
        file = MediaFile(filename)
        file.filename = filename
        file.creation_date = date
        file.modification_date = date
        file.is_media = is_media
        file.error = error
        file.size = size
        return file