"""EXIF reader for PicSort."""
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from pathlib import Path


class ExifReader:
    """Reads EXIF data from image files."""

    def __init__(self):
        """Initialize EXIF reader."""
        pass

    def read_date(self, file_path):
        """Read creation date from EXIF data."""
        return self.extract_creation_date(file_path)

    def extract_creation_date(self, file_path):
        """Extract creation date from EXIF data with priority order."""
        file_path = Path(file_path)

        if not self.can_extract_metadata(str(file_path)):
            return None

        try:
            with Image.open(file_path) as img:
                exifdata = img.getexif()

                if exifdata:
                    # Priority order: DateTimeOriginal -> DateTimeDigitized -> DateTime
                    for tag_name in ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']:
                        for tag_id, value in exifdata.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag == tag_name:
                                parsed_date = self._parse_exif_datetime(value)
                                if parsed_date:
                                    return parsed_date
        except Exception:
            pass

        return None

    def can_extract_metadata(self, filename):
        """Check if metadata can be extracted from the file type."""
        if isinstance(filename, Path):
            filename = str(filename)

        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
        file_ext = Path(filename).suffix.lower()
        return file_ext in supported_extensions

    def _parse_exif_datetime(self, datetime_str):
        """Parse EXIF datetime string into datetime object."""
        if not datetime_str or not isinstance(datetime_str, str):
            return None

        # Clean whitespace
        datetime_str = datetime_str.strip()
        if not datetime_str:
            return None

        # Try different datetime formats
        formats = [
            '%Y:%m:%d %H:%M:%S',  # Standard EXIF format
            '%Y-%m-%d %H:%M:%S',  # Alternative format
            '%Y:%m:%d',           # Date only
            '%Y-%m-%d',           # Date only alternative
            '%Y/%m/%d %H:%M:%S',  # Another alternative
            '%Y/%m/%d',           # Date only slash format
        ]

        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue

        return None

    def read_all(self, file_path):
        """Read all EXIF data from file."""
        file_path = Path(file_path)
        exif_data = {}

        try:
            with Image.open(file_path) as img:
                exifdata = img.getexif()

                if exifdata:
                    for tag_id, value in exifdata.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
        except Exception:
            pass

        return exif_data