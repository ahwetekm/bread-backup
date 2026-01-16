"""Local filesystem storage backend."""

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class BackupInfo:
    """Information about a backup file."""

    filename: str
    path: Path
    size: int
    date: datetime
    backup_type: str = "unknown"

    @property
    def size_human(self) -> str:
        """Get human-readable size."""
        size = self.size
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "filename": self.filename,
            "path": str(self.path),
            "size": self.size,
            "size_human": self.size_human,
            "date": self.date.isoformat(),
            "backup_type": self.backup_type,
        }


class LocalStorage:
    """Local filesystem storage backend."""

    def __init__(self, destination: Path):
        """Initialize local storage.

        Args:
            destination: Directory to store backups
        """
        self.destination = Path(destination)

    def ensure_destination_exists(self) -> None:
        """Ensure destination directory exists.

        Raises:
            OSError: If directory cannot be created
        """
        self.destination.mkdir(parents=True, exist_ok=True)

    def check_disk_space(self, required_bytes: int) -> bool:
        """Check if there's enough disk space.

        Args:
            required_bytes: Required space in bytes

        Returns:
            True if enough space available
        """
        try:
            stat = shutil.disk_usage(self.destination)
            return stat.free >= required_bytes
        except OSError:
            return False

    def get_available_space(self) -> int:
        """Get available disk space in bytes.

        Returns:
            Available space in bytes
        """
        try:
            stat = shutil.disk_usage(self.destination)
            return stat.free
        except OSError:
            return 0

    def save_backup(self, source: Path, filename: Optional[str] = None) -> Path:
        """Save backup file to storage.

        Args:
            source: Source backup file
            filename: Optional custom filename (default: use source filename)

        Returns:
            Path to saved backup

        Raises:
            FileNotFoundError: If source file doesn't exist
            OSError: If file cannot be copied
        """
        self.ensure_destination_exists()

        dest_filename = filename or source.name
        dest_path = self.destination / dest_filename

        # Copy file
        shutil.copy2(source, dest_path)

        return dest_path

    def list_backups(self, sort_by: str = "date") -> list[BackupInfo]:
        """List all backup files in destination.

        Args:
            sort_by: Sort order ("date", "size", or "name")

        Returns:
            List of BackupInfo objects
        """
        if not self.destination.exists():
            return []

        backups = []

        for file_path in self.destination.glob("*.bread"):
            try:
                stat = file_path.stat()
                backups.append(
                    BackupInfo(
                        filename=file_path.name,
                        path=file_path,
                        size=stat.st_size,
                        date=datetime.fromtimestamp(stat.st_mtime),
                    )
                )
            except OSError:
                continue

        # Sort backups
        if sort_by == "date":
            backups.sort(key=lambda b: b.date, reverse=True)
        elif sort_by == "size":
            backups.sort(key=lambda b: b.size, reverse=True)
        elif sort_by == "name":
            backups.sort(key=lambda b: b.filename)

        return backups

    def delete_backup(self, backup_path: Path) -> None:
        """Delete a backup file.

        Args:
            backup_path: Path to backup file

        Raises:
            FileNotFoundError: If backup doesn't exist
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        backup_path.unlink()

    def get_backup_info(self, backup_path: Path) -> BackupInfo:
        """Get information about a specific backup.

        Args:
            backup_path: Path to backup file

        Returns:
            BackupInfo object

        Raises:
            FileNotFoundError: If backup doesn't exist
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        stat = backup_path.stat()

        return BackupInfo(
            filename=backup_path.name,
            path=backup_path,
            size=stat.st_size,
            date=datetime.fromtimestamp(stat.st_mtime),
        )

    def cleanup_old_backups(self, keep_count: int) -> list[Path]:
        """Delete old backups keeping only the most recent ones.

        Args:
            keep_count: Number of backups to keep

        Returns:
            List of deleted backup paths
        """
        backups = self.list_backups(sort_by="date")

        deleted = []
        for backup in backups[keep_count:]:
            try:
                self.delete_backup(backup.path)
                deleted.append(backup.path)
            except OSError:
                pass

        return deleted

    @staticmethod
    def validate_backup_filename(filename: str) -> bool:
        """Validate backup filename format.

        Args:
            filename: Filename to validate

        Returns:
            True if valid
        """
        return filename.endswith(".bread")

    @staticmethod
    def generate_backup_filename(hostname: str, timestamp: Optional[datetime] = None) -> str:
        """Generate standard backup filename.

        Args:
            hostname: System hostname
            timestamp: Backup timestamp (default: now)

        Returns:
            Filename in format: backup-hostname-YYYY-MM-DD-HHMMSS.bread
        """
        if timestamp is None:
            timestamp = datetime.now()

        date_str = timestamp.strftime("%Y-%m-%d-%H%M%S")
        return f"backup-{hostname}-{date_str}.bread"
