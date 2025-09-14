"""Comprehensive error handling with recovery suggestions."""
import os
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class ErrorCategory:
    """Error categories for classification."""
    PERMISSION = "permission"
    STORAGE = "storage"
    CORRUPTION = "corruption"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    SYSTEM = "system"
    USER = "user"
    TEMPORARY = "temporary"


class RecoveryAction:
    """Recovery action types."""
    RETRY = "retry"
    SKIP = "skip"
    MANUAL = "manual"
    CONFIGURE = "configure"
    WAIT = "wait"
    ABORT = "abort"


class PicSortError:
    """Enhanced error information with recovery suggestions."""

    def __init__(self,
                 error_type: str,
                 message: str,
                 category: str = ErrorCategory.SYSTEM,
                 file_path: Optional[str] = None,
                 details: Optional[Dict] = None,
                 recovery_actions: Optional[List[Dict]] = None):
        """Initialize error with comprehensive information.

        Args:
            error_type: Type of error (e.g., 'permission_denied', 'disk_full')
            message: Human-readable error message
            category: Error category for classification
            file_path: File path related to error (if applicable)
            details: Additional error details
            recovery_actions: List of suggested recovery actions
        """
        self.error_type = error_type
        self.message = message
        self.category = category
        self.file_path = file_path
        self.details = details or {}
        self.recovery_actions = recovery_actions or []
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        """String representation of the error."""
        return f"{self.error_type}: {self.message}"


class ErrorHandler:
    """Comprehensive error handler with recovery suggestions."""

    def __init__(self):
        """Initialize error handler."""
        self.error_patterns = self._initialize_error_patterns()

    def _initialize_error_patterns(self) -> Dict:
        """Initialize error pattern database."""
        return {
            # Permission errors
            'permission_denied': {
                'category': ErrorCategory.PERMISSION,
                'patterns': ['permission denied', 'access denied', 'not permitted', 'operation not permitted'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Check file and directory permissions',
                        'details': 'Run as administrator/root or change file ownership',
                        'commands': {
                            'windows': 'Right-click → Properties → Security → Edit permissions',
                            'linux': 'chmod 755 <directory> or sudo chown $USER <file>',
                            'darwin': 'chmod 755 <directory> or sudo chown $USER <file>'
                        }
                    },
                    {
                        'action': RecoveryAction.SKIP,
                        'description': 'Skip files with permission issues',
                        'details': 'Continue processing other files'
                    }
                ]
            },

            # Storage errors
            'disk_full': {
                'category': ErrorCategory.STORAGE,
                'patterns': ['no space left', 'disk full', 'insufficient disk space', 'not enough space'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Free up disk space',
                        'details': 'Delete unnecessary files or move files to different drive',
                        'commands': {
                            'windows': 'Run Disk Cleanup or check Drive Properties',
                            'linux': 'df -h to check space, du -sh * to find large directories',
                            'darwin': 'About This Mac → Storage → Manage'
                        }
                    },
                    {
                        'action': RecoveryAction.CONFIGURE,
                        'description': 'Change target directory to different drive',
                        'details': 'Specify a target location with more available space'
                    }
                ]
            },

            'path_too_long': {
                'category': ErrorCategory.SYSTEM,
                'patterns': ['path too long', 'filename too long', 'name too long'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.CONFIGURE,
                        'description': 'Use shorter date format',
                        'details': 'Change from "Month Year" to "MM.YYYY" format',
                        'example': 'picsort config set date_format "MM.YYYY"'
                    },
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Move source files closer to root directory',
                        'details': 'Reduce overall path length by organizing source location'
                    }
                ]
            },

            # File corruption errors
            'checksum_mismatch': {
                'category': ErrorCategory.CORRUPTION,
                'patterns': ['checksum mismatch', 'verification failed', 'integrity check failed'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.RETRY,
                        'description': 'Retry operation',
                        'details': 'Temporary I/O error may resolve on retry'
                    },
                    {
                        'action': RecoveryAction.CONFIGURE,
                        'description': 'Disable checksum verification',
                        'details': 'Trade security for speed if files are trusted',
                        'example': 'picsort config set verify_checksum false'
                    },
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Check storage device health',
                        'details': 'Run disk check utilities to verify hardware integrity'
                    }
                ]
            },

            'file_corrupted': {
                'category': ErrorCategory.CORRUPTION,
                'patterns': ['corrupted', 'invalid file', 'cannot read', 'bad file format'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.SKIP,
                        'description': 'Skip corrupted file',
                        'details': 'Continue with other files, manually review later'
                    },
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Attempt file recovery',
                        'details': 'Use file recovery tools or restore from backup'
                    }
                ]
            },

            # Network errors
            'network_error': {
                'category': ErrorCategory.NETWORK,
                'patterns': ['network', 'connection', 'timeout', 'unreachable', 'offline'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.WAIT,
                        'description': 'Wait and retry',
                        'details': 'Network issues are often temporary',
                        'wait_seconds': 30
                    },
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Check network connection',
                        'details': 'Verify network drive is accessible and connected'
                    },
                    {
                        'action': RecoveryAction.CONFIGURE,
                        'description': 'Use local storage',
                        'details': 'Copy files locally first, then organize'
                    }
                ]
            },

            # Configuration errors
            'config_invalid': {
                'category': ErrorCategory.CONFIGURATION,
                'patterns': ['invalid configuration', 'config error', 'bad setting'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.CONFIGURE,
                        'description': 'Run interactive configuration',
                        'details': 'Reset configuration to working defaults',
                        'example': 'picsort config init'
                    },
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Edit configuration file',
                        'details': 'Manually fix configuration settings'
                    }
                ]
            },

            # File in use errors
            'file_in_use': {
                'category': ErrorCategory.TEMPORARY,
                'patterns': ['file in use', 'being used by another process', 'resource busy', 'sharing violation'],
                'recovery_actions': [
                    {
                        'action': RecoveryAction.WAIT,
                        'description': 'Wait and retry',
                        'details': 'File may be temporarily locked',
                        'wait_seconds': 5
                    },
                    {
                        'action': RecoveryAction.MANUAL,
                        'description': 'Close applications using the file',
                        'details': 'Check for photo viewers, editors, or antivirus scans'
                    },
                    {
                        'action': RecoveryAction.SKIP,
                        'description': 'Skip locked files',
                        'details': 'Continue with other files, retry locked files later'
                    }
                ]
            }
        }

    def analyze_error(self, exception: Exception, context: Optional[Dict] = None) -> PicSortError:
        """Analyze exception and create enhanced error information.

        Args:
            exception: The exception that occurred
            context: Additional context about the error

        Returns:
            Enhanced error information with recovery suggestions
        """
        context = context or {}
        error_message = str(exception).lower()
        file_path = context.get('file_path')

        # Analyze error type and category
        error_type = 'unknown_error'
        category = ErrorCategory.SYSTEM
        recovery_actions = []

        for error_pattern, pattern_info in self.error_patterns.items():
            for pattern in pattern_info['patterns']:
                if pattern in error_message:
                    error_type = error_pattern
                    category = pattern_info['category']
                    recovery_actions = pattern_info['recovery_actions']
                    break
            if error_type != 'unknown_error':
                break

        # Add context-specific details
        details = {
            'exception_type': type(exception).__name__,
            'original_message': str(exception),
            'platform': platform.system(),
            'context': context
        }

        # Add file-specific information if available
        if file_path:
            details.update(self._get_file_context(file_path))

        # Add system-specific information
        details.update(self._get_system_context())

        return PicSortError(
            error_type=error_type,
            message=self._create_user_friendly_message(error_type, exception, context),
            category=category,
            file_path=file_path,
            details=details,
            recovery_actions=recovery_actions
        )

    def _get_file_context(self, file_path: str) -> Dict:
        """Get context information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file context information
        """
        context = {'file_exists': False}

        try:
            path = Path(file_path)
            if path.exists():
                context.update({
                    'file_exists': True,
                    'file_size': path.stat().st_size,
                    'is_directory': path.is_dir(),
                    'parent_exists': path.parent.exists(),
                    'parent_writable': os.access(path.parent, os.W_OK) if path.parent.exists() else False
                })
        except Exception as e:
            context['context_error'] = str(e)

        return context

    def _get_system_context(self) -> Dict:
        """Get system context information.

        Returns:
            Dictionary with system context
        """
        context = {}

        try:
            # Disk space information
            statvfs = shutil.disk_usage('.')
            context.update({
                'disk_total_gb': statvfs.total / (1024**3),
                'disk_free_gb': statvfs.free / (1024**3),
                'disk_used_percent': ((statvfs.total - statvfs.free) / statvfs.total) * 100
            })
        except Exception:
            pass

        try:
            # System information
            context.update({
                'platform_system': platform.system(),
                'platform_release': platform.release(),
                'python_version': platform.python_version()
            })
        except Exception:
            pass

        return context

    def _create_user_friendly_message(self, error_type: str, exception: Exception, context: Dict) -> str:
        """Create user-friendly error message.

        Args:
            error_type: Type of error identified
            exception: Original exception
            context: Error context

        Returns:
            User-friendly error message
        """
        file_path = context.get('file_path', '')
        filename = Path(file_path).name if file_path else ''

        messages = {
            'permission_denied': f"Access denied to file '{filename}'. You don't have permission to read or modify this file.",
            'disk_full': f"Not enough disk space to complete the operation. Need additional space to process '{filename}'.",
            'path_too_long': f"File path is too long for the filesystem. Cannot process '{filename}' due to path length limits.",
            'checksum_mismatch': f"File integrity check failed for '{filename}'. The file may be corrupted or modified during transfer.",
            'file_corrupted': f"File '{filename}' appears to be corrupted or in an unsupported format.",
            'network_error': f"Network connection issue while accessing '{filename}'. The file may be on an unreachable network drive.",
            'config_invalid': f"Configuration error detected. Current settings are invalid or incompatible.",
            'file_in_use': f"File '{filename}' is currently being used by another application and cannot be moved.",
            'unknown_error': f"An unexpected error occurred while processing '{filename}': {str(exception)}"
        }

        return messages.get(error_type, f"Error processing '{filename}': {str(exception)}")

    def format_error_report(self, error: PicSortError, show_details: bool = False) -> str:
        """Format error for display to user.

        Args:
            error: Enhanced error information
            show_details: Whether to include technical details

        Returns:
            Formatted error report
        """
        lines = []

        # Main error message
        lines.append(f"❌ {error.message}")
        lines.append("")

        # Recovery suggestions
        if error.recovery_actions:
            lines.append("💡 Suggested solutions:")
            for i, action in enumerate(error.recovery_actions, 1):
                lines.append(f"  {i}. {action['description']}")
                if 'details' in action:
                    lines.append(f"     {action['details']}")

                # Platform-specific commands
                if 'commands' in action:
                    current_platform = platform.system().lower()
                    if current_platform == 'darwin':
                        current_platform = 'darwin'
                    elif current_platform == 'windows':
                        current_platform = 'windows'
                    else:
                        current_platform = 'linux'

                    if current_platform in action['commands']:
                        lines.append(f"     Command: {action['commands'][current_platform]}")

                # Example commands
                if 'example' in action:
                    lines.append(f"     Example: {action['example']}")

                lines.append("")

        # Technical details (if requested)
        if show_details and error.details:
            lines.append("🔍 Technical details:")
            for key, value in error.details.items():
                if key != 'context':  # Skip nested context
                    lines.append(f"  {key}: {value}")
            lines.append("")

        # File information
        if error.file_path:
            lines.append(f"📁 Affected file: {error.file_path}")
            lines.append("")

        return "\n".join(lines)

    def get_recovery_actions(self, error: PicSortError) -> List[Dict]:
        """Get available recovery actions for an error.

        Args:
            error: Enhanced error information

        Returns:
            List of recovery actions
        """
        return error.recovery_actions

    def suggest_next_steps(self, errors: List[PicSortError]) -> List[str]:
        """Suggest next steps based on multiple errors.

        Args:
            errors: List of errors encountered

        Returns:
            List of suggested next steps
        """
        suggestions = []
        error_categories = {}

        # Group errors by category
        for error in errors:
            category = error.category
            if category not in error_categories:
                error_categories[category] = []
            error_categories[category].append(error)

        # Generate category-specific suggestions
        if ErrorCategory.PERMISSION in error_categories:
            count = len(error_categories[ErrorCategory.PERMISSION])
            suggestions.append(f"Fix permission issues for {count} files - run with administrator privileges or check file ownership")

        if ErrorCategory.STORAGE in error_categories:
            suggestions.append("Free up disk space or choose a different target location with more available space")

        if ErrorCategory.CORRUPTION in error_categories:
            count = len(error_categories[ErrorCategory.CORRUPTION])
            suggestions.append(f"Check storage device health - found {count} corrupted files which may indicate hardware issues")

        if ErrorCategory.NETWORK in error_categories:
            suggestions.append("Check network connectivity and ensure network drives are properly connected")

        if ErrorCategory.TEMPORARY in error_categories:
            suggestions.append("Retry the operation - some errors may be temporary")

        # General suggestions
        if len(errors) > 10:
            suggestions.append("Consider using dry-run mode first to identify issues before making changes")

        if not suggestions:
            suggestions.append("Review individual error messages above for specific guidance")

        return suggestions

    def create_error_summary(self, errors: List[PicSortError]) -> Dict:
        """Create summary of errors for reporting.

        Args:
            errors: List of errors

        Returns:
            Error summary dictionary
        """
        if not errors:
            return {'total': 0, 'categories': {}, 'suggestions': []}

        categories = {}
        for error in errors:
            category = error.category
            if category not in categories:
                categories[category] = {'count': 0, 'errors': []}
            categories[category]['count'] += 1
            categories[category]['errors'].append(error.error_type)

        return {
            'total': len(errors),
            'categories': categories,
            'suggestions': self.suggest_next_steps(errors),
            'most_common': max(categories.keys(), key=lambda k: categories[k]['count']) if categories else None
        }


def handle_operation_errors(func):
    """Decorator to handle operation errors with recovery suggestions.

    Args:
        func: Function to wrap with error handling

    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        error_handler = ErrorHandler()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            }
            error = error_handler.analyze_error(e, context)
            logger.error(f"Operation failed: {error}")
            raise error
    return wrapper