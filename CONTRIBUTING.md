# Contributing to PicSort

Thank you for your interest in contributing to PicSort! This guide will help you get started with contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Workflow](#contributing-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Release Process](#release-process)

## Code of Conduct

This project follows a simple code of conduct:

- **Be respectful**: Treat all contributors and users with respect
- **Be constructive**: Provide helpful feedback and suggestions
- **Be collaborative**: Work together to make PicSort better
- **Be inclusive**: Welcome contributors from all backgrounds

## Getting Started

### Types of Contributions

We welcome several types of contributions:

- **Bug reports**: Help us identify and fix issues
- **Feature requests**: Suggest new functionality
- **Code contributions**: Bug fixes, new features, improvements
- **Documentation**: Improve guides, API docs, examples
- **Testing**: Add test cases, improve test coverage
- **Design**: UI/UX improvements for CLI output

### Good First Issues

Look for issues labeled with:
- `good first issue`: Perfect for newcomers
- `help wanted`: We need community help
- `documentation`: Documentation improvements
- `bug`: Bug fixes needed

## Development Setup

### Prerequisites

- **Python 3.11+** (3.11 or 3.12 recommended)
- **Git** for version control
- **pip** for package management

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/PicSort.git
   cd PicSort
   ```

3. **Set up remote upstream**:
   ```bash
   git remote add upstream https://github.com/johnchouang/PicSort.git
   ```

4. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # Activate on Linux/macOS
   source venv/bin/activate

   # Activate on Windows
   venv\Scripts\activate
   ```

5. **Install in development mode**:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   pip install -r requirements-build.txt
   ```

6. **Verify installation**:
   ```bash
   picsort --version
   pytest --version
   ```

### Project Structure

Understanding the codebase structure:

```
PicSort/
├── src/                    # Source code
│   ├── cli/               # Command-line interface
│   │   ├── commands/      # Individual CLI commands
│   │   │   ├── organize.py
│   │   │   ├── scan.py
│   │   │   ├── config.py
│   │   │   └── undo.py
│   │   ├── main.py        # Main CLI entry point
│   │   └── helpers.py     # CLI utility functions
│   ├── lib/               # Core libraries
│   │   ├── file_scanner.py      # File discovery and metadata
│   │   ├── date_organizer.py    # Organization logic
│   │   ├── file_mover.py        # Safe file operations
│   │   ├── config_manager.py    # Configuration handling
│   │   ├── exif_reader.py       # EXIF metadata extraction
│   │   ├── progress_reporter.py # Progress display
│   │   ├── operation_logger.py  # Operation logging
│   │   └── resume_manager.py    # Resume functionality
│   ├── models/            # Data models
│   │   ├── media_file.py        # Media file representation
│   │   ├── configuration.py     # Configuration model
│   │   ├── file_operation.py    # File operation model
│   │   └── operation_log.py     # Operation log model
│   └── services/          # Business logic services
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── contract/         # API contract tests
│   └── performance/      # Performance tests
├── docs/                 # Documentation
├── build_executable.py  # Standalone executable builder
├── setup.py             # Package setup
└── requirements*.txt    # Dependencies
```

### Key Components

- **CLI Commands**: User-facing command implementations
- **Core Libraries**: Business logic and file operations
- **Models**: Data structures and validation
- **Tests**: Comprehensive test suite

## Contributing Workflow

### 1. Choose or Create an Issue

- Browse [existing issues](https://github.com/johnchouang/PicSort/issues)
- Comment on issues you want to work on
- Create new issues for bugs or features

### 2. Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description
```

### 3. Make Your Changes

- Write code following our [coding standards](#coding-standards)
- Add or update tests as needed
- Update documentation if required
- Ensure all tests pass

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add support for HEIC image format

- Add HEIC to default file types
- Update EXIF reader to handle HEIC metadata
- Add tests for HEIC file processing
- Update documentation with HEIC examples"
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Coding Standards

### Python Style

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized with `isort`
- **Formatting**: Use `black` for automatic formatting

### Code Organization

#### Imports

Organize imports in this order:

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict

# Third-party imports
import click
import yaml
from PIL import Image

# Local imports
from ..models.media_file import MediaFile
from ..lib.config_manager import ConfigManager
```

#### Type Hints

Use type hints for all functions:

```python
def organize_files(
    files: List[MediaFile],
    base_path: str,
    config: Optional[Configuration] = None
) -> Dict[str, List[MediaFile]]:
    """Organize files into date-based groups.

    Args:
        files: List of media files to organize
        base_path: Base directory path
        config: Optional configuration override

    Returns:
        Dictionary mapping folder names to file lists
    """
```

#### Error Handling

Use specific exception types and provide helpful messages:

```python
# Good
try:
    config = load_config(config_path)
except FileNotFoundError:
    raise ConfigError(f"Configuration file not found: {config_path}")
except yaml.YAMLError as e:
    raise ConfigError(f"Invalid YAML syntax in {config_path}: {e}")

# Avoid bare except clauses
try:
    risky_operation()
except Exception:  # Too broad
    pass
```

#### Logging

Use structured logging with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

def process_file(file_path: str) -> None:
    logger.info("Processing file", extra={"file_path": file_path})

    try:
        # Process file
        result = do_processing(file_path)
        logger.debug("File processed successfully", extra={
            "file_path": file_path,
            "result_size": len(result)
        })
    except ProcessingError as e:
        logger.error("File processing failed", extra={
            "file_path": file_path,
            "error": str(e)
        })
        raise
```

### Code Quality Tools

Run these tools before submitting:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
python -m pytest --flake8 --mypy
```

## Testing

### Test Structure

We use **pytest** with multiple test categories:

- **Unit tests** (`tests/unit/`): Test individual functions/classes
- **Integration tests** (`tests/integration/`): Test component interactions
- **Contract tests** (`tests/contract/`): Test CLI interface contracts
- **Performance tests** (`tests/performance/`): Test performance requirements

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m contract
pytest -m performance

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_file_scanner.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_organize"
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/test_date_extraction.py
import pytest
from datetime import datetime
from pathlib import Path

from picsort.lib.exif_reader import ExifReader
from picsort.models.media_file import MediaFile


class TestDateExtraction:
    """Test date extraction from various file types."""

    def test_extract_date_from_jpeg_exif(self):
        """Test extracting date from JPEG EXIF data."""
        # Arrange
        reader = ExifReader()
        test_file = Path("tests/fixtures/photo_with_exif.jpg")

        # Act
        date = reader.extract_creation_date(test_file)

        # Assert
        assert date == datetime(2023, 6, 15, 14, 30, 0)

    def test_fallback_to_file_date(self):
        """Test fallback to file modification date when no EXIF."""
        # Arrange
        reader = ExifReader()
        test_file = Path("tests/fixtures/photo_no_exif.jpg")

        # Act
        date = reader.extract_creation_date(test_file)

        # Assert
        assert date is not None
        assert isinstance(date, datetime)

    @pytest.mark.parametrize("file_extension,expected_result", [
        (".jpg", True),
        (".jpeg", True),
        (".png", False),
        (".txt", False),
    ])
    def test_supports_file_type(self, file_extension, expected_result):
        """Test file type support detection."""
        reader = ExifReader()
        assert reader.supports_exif(file_extension) == expected_result
```

#### Integration Test Example

```python
# tests/integration/test_organize_media.py
import pytest
import tempfile
from pathlib import Path

from picsort.lib.file_scanner import FileScanner
from picsort.lib.date_organizer import DateOrganizer
from picsort.models.configuration import Configuration


class TestOrganizeMedia:
    """Integration tests for media organization workflow."""

    def test_full_organization_workflow(self, tmp_path):
        """Test complete workflow from scanning to organization."""
        # Arrange
        config = Configuration.create_default()

        # Create test files
        test_photos = tmp_path / "photos"
        test_photos.mkdir()

        # Copy test files with different dates
        (test_photos / "photo1.jpg").write_bytes(b"fake jpg data")
        (test_photos / "photo2.jpg").write_bytes(b"fake jpg data")

        scanner = FileScanner(config)
        organizer = DateOrganizer(config)

        # Act
        files = scanner.scan_directory(str(test_photos))
        organization = organizer.organize_files(files, str(test_photos))

        # Assert
        assert len(files) == 2
        assert len(organization) > 0

        # Check folder structure
        for folder_name in organization.keys():
            assert "." in folder_name  # Should be MM.YYYY format
```

### Test Fixtures

Use fixtures for common test data:

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_photo_dir():
    """Create temporary directory with test photos."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        photo_dir = Path(tmp_dir) / "photos"
        photo_dir.mkdir()

        # Create test files
        (photo_dir / "photo1.jpg").write_bytes(b"fake jpg")
        (photo_dir / "photo2.png").write_bytes(b"fake png")
        (photo_dir / "video1.mp4").write_bytes(b"fake mp4")

        yield photo_dir

@pytest.fixture
def default_config():
    """Create default configuration for tests."""
    return Configuration.create_default()
```

### Test Coverage

Maintain high test coverage:

- **Minimum**: 80% overall coverage
- **Target**: 90%+ for core functionality
- **Critical paths**: 100% coverage for file operations

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings, comments
2. **User Documentation**: User guide, API reference
3. **Developer Documentation**: Contributing guide, architecture
4. **Examples**: Usage examples, tutorials

### Docstring Style

Use **Google style** docstrings:

```python
def organize_files(files: List[MediaFile], base_path: str) -> Dict[str, List[MediaFile]]:
    """Organize media files into date-based groups.

    Takes a list of media files and organizes them into groups based on their
    creation dates. Files without valid dates are grouped separately.

    Args:
        files: List of MediaFile objects to organize
        base_path: Base directory path for relative path calculations

    Returns:
        Dictionary mapping folder names (MM.YYYY format) to lists of MediaFile
        objects that should be placed in those folders.

    Raises:
        ValueError: If base_path doesn't exist or files list is empty
        PermissionError: If base_path is not readable

    Example:
        >>> files = [MediaFile("/path/photo1.jpg"), MediaFile("/path/photo2.jpg")]
        >>> result = organize_files(files, "/path")
        >>> print(result)
        {"01.2023": [MediaFile(...)], "02.2023": [MediaFile(...)]}
    """
```

### Updating Documentation

When making changes that affect users:

1. **Update README.md** if changing core functionality
2. **Update User Guide** for new features or workflows
3. **Update API Reference** for CLI changes
4. **Add examples** for new functionality

## Pull Request Process

### Before Submitting

Ensure your PR:

- [ ] Follows coding standards
- [ ] Includes tests for new functionality
- [ ] Updates documentation as needed
- [ ] Passes all existing tests
- [ ] Has a clear description

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainer(s)
3. **Testing** in different environments
4. **Documentation review** if applicable
5. **Approval** and merge

### After Merge

- Update your local repository
- Delete feature branch
- Close related issues

## Release Process

### Version Numbers

We use **Semantic Versioning** (SemVer):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

For maintainers releasing new versions:

1. **Update version numbers** in relevant files
2. **Update CHANGELOG.md** with new features/fixes
3. **Run full test suite**
4. **Build and test executables**
5. **Create release tag**
6. **Publish release** with release notes

### Pre-release Testing

Test on multiple platforms:

- **Windows**: 10, 11
- **macOS**: Latest 2 versions
- **Linux**: Ubuntu, CentOS

## Getting Help

### For Contributors

- **GitHub Issues**: Ask questions, report problems
- **Discussions**: General development discussion
- **Code Review**: Request feedback on approaches

### For Maintainers

- **Security Issues**: Report privately via email
- **Performance Issues**: Include benchmarks
- **Breaking Changes**: Discuss in issues first

---

Thank you for contributing to PicSort! Your contributions help make file organization easier for everyone.