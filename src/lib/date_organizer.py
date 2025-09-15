"""Date organizer for PicSort."""
from pathlib import Path
from datetime import datetime


class DateOrganizer:
    """Organizes files by date."""

    def __init__(self, config=None):
        """Initialize date organizer."""
        self.config = config or {}
        # Handle both dict and Configuration objects
        if hasattr(config, 'date_format'):
            self.date_format = config.date_format
        else:
            self.date_format = self.config.get('date_format', 'MM.YYYY')

    def organize_files(self, media_files, base_path):
        """Organize MediaFile objects into date-based folders."""
        return self.organize(media_files)

    def organize(self, files):
        """Organize files into date-based folders."""
        organized = {}
        for file_info in files:
            # Handle both MediaFile objects and dict file info
            if hasattr(file_info, 'get_oldest_date'):
                # MediaFile object with new oldest date logic
                date = file_info.get_oldest_date()
            elif hasattr(file_info, 'creation_date'):
                # Legacy MediaFile object
                date = file_info.creation_date or file_info.modification_date
            else:
                # Dict file info (legacy)
                date = file_info.get('created', file_info.get('modified'))

            if date:
                folder_name = self._format_date(date)
                if folder_name not in organized:
                    organized[folder_name] = []
                organized[folder_name].append(file_info)
        return organized

    def get_organization_summary(self, organization):
        """Get summary statistics from organization."""
        if not organization:
            return {
                'date_range': None,
                'total_files': 0,
                'total_folders': 0
            }

        dates = []
        total_files = 0
        for folder_files in organization.values():
            total_files += len(folder_files)
            for file_info in folder_files:
                if hasattr(file_info, 'get_oldest_date'):
                    # MediaFile object with new oldest date logic
                    date = file_info.get_oldest_date()
                elif hasattr(file_info, 'creation_date'):
                    # Legacy MediaFile object
                    date = file_info.creation_date or file_info.modification_date
                else:
                    # Dict file info (legacy)
                    date = file_info.get('created', file_info.get('modified'))
                if date:
                    dates.append(date)

        if dates:
            return {
                'date_range': (min(dates), max(dates)),
                'total_files': total_files,
                'total_folders': len(organization)
            }
        else:
            return {
                'date_range': None,
                'total_files': total_files,
                'total_folders': len(organization)
            }

    def preview_organization(self, media_files, base_path):
        """Preview how files would be organized."""
        organization = self.organize(media_files)
        preview = []

        for folder_name, files in organization.items():
            file_previews = []
            duplicates = []

            # Track filenames to detect duplicates
            filename_counts = {}
            for file_info in files:
                if hasattr(file_info, 'filename'):
                    name = file_info.filename
                else:
                    name = file_info.get('name', 'unknown')

                filename_counts[name] = filename_counts.get(name, 0) + 1

            # Generate preview and identify duplicates
            for i, file_info in enumerate(files[:5]):  # Show first 5 files
                if hasattr(file_info, 'filename'):
                    name = file_info.filename
                else:
                    name = file_info.get('name', 'unknown')

                file_previews.append({'name': name})

                # If filename appears multiple times, it's a duplicate
                if filename_counts[name] > 1:
                    # Generate renamed version
                    base_name, ext = self._split_filename(name)
                    renamed = f"{base_name}_1{ext}"
                    duplicates.append({
                        'original': name,
                        'renamed': renamed
                    })

            more_files = max(0, len(files) - 5)

            preview.append({
                'folder': folder_name,
                'file_count': len(files),
                'files': file_previews,
                'more_files': more_files,
                'duplicates': duplicates
            })

        return preview

    def _split_filename(self, filename):
        """Split filename into base name and extension."""
        if '.' in filename:
            parts = filename.rsplit('.', 1)
            return parts[0], '.' + parts[1]
        else:
            return filename, ''

    def _format_date(self, date):
        """Format date according to configured format."""
        if self.date_format == 'MM.YYYY':
            return f"{date.month:02d}.{date.year}"
        elif self.date_format == 'YYYY.MM':
            return f"{date.year}.{date.month:02d}"
        else:
            return f"{date.month:02d}.{date.year}"