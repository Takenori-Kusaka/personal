"""
File Handler Utility
Handles file operations for the Digital Garden automation system

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import json

from automation.utils.logging_setup import StructuredLogger

class FileHandler:
    """
    Utility class for safe file operations with backup and validation
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize file handler with configuration"""
        self.config = config or {}
        self.logger = StructuredLogger('file_handler')

        self.create_backups = self.config.get('create_backups', True)
        self.backup_retention_days = self.config.get('backup_retention_days', 30)
        self.compress_archives = self.config.get('compress_archives', True)
        self.preserve_metadata = self.config.get('preserve_metadata', True)

        # Initialize MIME types
        mimetypes.init()

    def validate_file(self, file_path: Union[str, Path], allowed_types: List[str] = None, max_size_mb: int = None) -> Dict[str, Any]:
        """
        Validate file before processing

        Args:
            file_path: Path to file
            allowed_types: List of allowed file extensions
            max_size_mb: Maximum file size in MB

        Returns:
            Dict with validation results
        """
        file_path = Path(file_path)

        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }

        try:
            if not file_path.exists():
                validation['valid'] = False
                validation['errors'].append(f"File does not exist: {file_path}")
                return validation

            # Get file stats
            stats = file_path.stat()
            validation['metadata'] = {
                'size_bytes': stats.st_size,
                'size_mb': stats.st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(stats.st_mtime),
                'created': datetime.fromtimestamp(stats.st_ctime),
                'extension': file_path.suffix.lower().lstrip('.'),
                'mime_type': mimetypes.guess_type(str(file_path))[0]
            }

            # Check file extension
            if allowed_types:
                if validation['metadata']['extension'] not in allowed_types:
                    validation['valid'] = False
                    validation['errors'].append(
                        f"File type '{validation['metadata']['extension']}' not allowed. "
                        f"Allowed types: {', '.join(allowed_types)}"
                    )

            # Check file size
            if max_size_mb and validation['metadata']['size_mb'] > max_size_mb:
                validation['valid'] = False
                validation['errors'].append(
                    f"File size ({validation['metadata']['size_mb']:.1f}MB) exceeds limit ({max_size_mb}MB)"
                )

            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                validation['valid'] = False
                validation['errors'].append(f"File is not readable: {file_path}")

            # Warn about large files
            if validation['metadata']['size_mb'] > 100:
                validation['warnings'].append(f"Large file ({validation['metadata']['size_mb']:.1f}MB) may take time to process")

            # Calculate file hash for integrity
            if validation['valid']:
                validation['metadata']['hash'] = self._calculate_file_hash(file_path)

        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Error validating file: {str(e)}")
            self.logger.error("File validation failed", error=e, file_path=str(file_path))

        return validation

    def create_backup(self, file_path: Union[str, Path], backup_dir: Union[str, Path] = None) -> Optional[Path]:
        """
        Create backup of file before processing

        Args:
            file_path: Path to file to backup
            backup_dir: Directory for backups (default: file_path.parent / 'backups')

        Returns:
            Path to backup file or None if failed
        """
        if not self.create_backups:
            return None

        try:
            file_path = Path(file_path)

            if not file_path.exists():
                self.logger.warning("Cannot backup non-existent file", file_path=str(file_path))
                return None

            # Set backup directory
            if backup_dir:
                backup_dir = Path(backup_dir)
            else:
                backup_dir = file_path.parent / 'backups'

            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name

            # Copy file
            shutil.copy2(file_path, backup_path)

            # Preserve extended attributes if requested
            if self.preserve_metadata:
                try:
                    shutil.copystat(file_path, backup_path)
                except Exception as e:
                    self.logger.warning("Could not preserve metadata", error=e)

            self.logger.debug("File backed up",
                            original=str(file_path),
                            backup=str(backup_path))

            return backup_path

        except Exception as e:
            self.logger.error("Backup creation failed", error=e, file_path=str(file_path))
            return None

    def safe_move(self, source: Union[str, Path], destination: Union[str, Path], create_backup: bool = True) -> bool:
        """
        Safely move file with backup and validation

        Args:
            source: Source file path
            destination: Destination file path
            create_backup: Create backup before moving

        Returns:
            True if successful, False otherwise
        """
        try:
            source = Path(source)
            destination = Path(destination)

            if not source.exists():
                self.logger.error("Source file does not exist", source=str(source))
                return False

            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if requested and destination exists
            if create_backup and destination.exists():
                backup_path = self.create_backup(destination)
                if backup_path:
                    self.logger.info("Backup created before move", backup=str(backup_path))

            # Move file
            shutil.move(str(source), str(destination))

            self.logger.info("File moved successfully",
                           source=str(source),
                           destination=str(destination))
            return True

        except Exception as e:
            self.logger.error("File move failed", error=e,
                            source=str(source),
                            destination=str(destination))
            return False

    def safe_delete(self, file_path: Union[str, Path], create_backup: bool = True) -> bool:
        """
        Safely delete file with optional backup

        Args:
            file_path: Path to file to delete
            create_backup: Create backup before deletion

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                self.logger.warning("File does not exist for deletion", file_path=str(file_path))
                return True  # Consider it successful if file doesn't exist

            # Create backup if requested
            if create_backup:
                backup_path = self.create_backup(file_path)
                if backup_path:
                    self.logger.info("Backup created before deletion", backup=str(backup_path))

            # Delete file
            file_path.unlink()

            self.logger.info("File deleted successfully", file_path=str(file_path))
            return True

        except Exception as e:
            self.logger.error("File deletion failed", error=e, file_path=str(file_path))
            return False

    def cleanup_old_backups(self, backup_dir: Union[str, Path], retention_days: int = None) -> int:
        """
        Clean up old backup files

        Args:
            backup_dir: Directory containing backups
            retention_days: Days to retain backups (default: from config)

        Returns:
            Number of files cleaned up
        """
        retention_days = retention_days or self.backup_retention_days
        backup_dir = Path(backup_dir)

        if not backup_dir.exists():
            return 0

        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)

        try:
            for backup_file in backup_dir.iterdir():
                if backup_file.is_file():
                    if backup_file.stat().st_mtime < cutoff_time:
                        backup_file.unlink()
                        cleaned_count += 1
                        self.logger.debug("Cleaned up old backup", file=str(backup_file))

            if cleaned_count > 0:
                self.logger.info("Backup cleanup completed", files_cleaned=cleaned_count)

        except Exception as e:
            self.logger.error("Backup cleanup failed", error=e)

        return cleaned_count

    def get_directory_info(self, directory: Union[str, Path]) -> Dict[str, Any]:
        """
        Get detailed information about directory contents

        Args:
            directory: Directory to analyze

        Returns:
            Dict with directory information
        """
        directory = Path(directory)

        info = {
            'path': str(directory),
            'exists': directory.exists(),
            'file_count': 0,
            'total_size_bytes': 0,
            'total_size_mb': 0,
            'file_types': {},
            'largest_file': None,
            'newest_file': None,
            'oldest_file': None,
            'files': []
        }

        if not directory.exists():
            return info

        try:
            newest_time = 0
            oldest_time = float('inf')
            largest_size = 0

            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    stats = file_path.stat()

                    file_info = {
                        'name': file_path.name,
                        'path': str(file_path),
                        'size_bytes': stats.st_size,
                        'size_mb': stats.st_size / (1024 * 1024),
                        'modified': datetime.fromtimestamp(stats.st_mtime),
                        'extension': file_path.suffix.lower().lstrip('.')
                    }

                    info['files'].append(file_info)
                    info['file_count'] += 1
                    info['total_size_bytes'] += stats.st_size

                    # Track file types
                    ext = file_info['extension']
                    if ext:
                        info['file_types'][ext] = info['file_types'].get(ext, 0) + 1

                    # Track largest file
                    if stats.st_size > largest_size:
                        largest_size = stats.st_size
                        info['largest_file'] = file_info

                    # Track newest file
                    if stats.st_mtime > newest_time:
                        newest_time = stats.st_mtime
                        info['newest_file'] = file_info

                    # Track oldest file
                    if stats.st_mtime < oldest_time:
                        oldest_time = stats.st_mtime
                        info['oldest_file'] = file_info

            info['total_size_mb'] = info['total_size_bytes'] / (1024 * 1024)

        except Exception as e:
            self.logger.error("Error analyzing directory", error=e, directory=str(directory))

        return info

    def _calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """Calculate file hash for integrity checking"""
        hash_func = hashlib.new(algorithm)

        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.logger.error("Hash calculation failed", error=e, file_path=str(file_path))
            return ""

    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """
        Ensure directory exists, create if necessary

        Args:
            directory: Directory path

        Returns:
            Path object for the directory
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def write_json(self, data: Any, file_path: Union[str, Path], create_backup: bool = True) -> bool:
        """
        Write data to JSON file with backup

        Args:
            data: Data to write
            file_path: Target file path
            create_backup: Create backup if file exists

        Returns:
            True if successful
        """
        try:
            file_path = Path(file_path)

            # Create backup if file exists
            if create_backup and file_path.exists():
                self.create_backup(file_path)

            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            self.logger.debug("JSON file written", file_path=str(file_path))
            return True

        except Exception as e:
            self.logger.error("JSON write failed", error=e, file_path=str(file_path))
            return False

    def read_json(self, file_path: Union[str, Path]) -> Optional[Any]:
        """
        Read data from JSON file

        Args:
            file_path: Source file path

        Returns:
            Parsed JSON data or None if failed
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                self.logger.warning("JSON file does not exist", file_path=str(file_path))
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.logger.debug("JSON file read", file_path=str(file_path))
            return data

        except Exception as e:
            self.logger.error("JSON read failed", error=e, file_path=str(file_path))
            return None