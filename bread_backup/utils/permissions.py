"""File permission and metadata handling utilities."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FileMetadata:
    """Stores file metadata including permissions, ownership, and timestamps."""

    path: str
    mode: int  # File permissions (e.g., 0o644)
    uid: int  # Owner user ID
    gid: int  # Owner group ID
    atime: float  # Access time
    mtime: float  # Modification time
    size: int  # File size in bytes
    is_symlink: bool = False
    symlink_target: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert metadata to dictionary."""
        return {
            "path": self.path,
            "mode": oct(self.mode),  # Store as octal string for readability
            "uid": self.uid,
            "gid": self.gid,
            "atime": self.atime,
            "mtime": self.mtime,
            "size": self.size,
            "is_symlink": self.is_symlink,
            "symlink_target": self.symlink_target,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FileMetadata":
        """Create FileMetadata from dictionary."""
        data = data.copy()
        # Convert octal string back to int
        if isinstance(data["mode"], str):
            data["mode"] = int(data["mode"], 8)
        return cls(**data)


class FilePermissionManager:
    """Manages file permissions and ownership."""

    def capture_permissions(self, file_path: Path) -> FileMetadata:
        """Capture file metadata including permissions, ownership, timestamps.

        Args:
            file_path: Path to the file

        Returns:
            FileMetadata object with all metadata

        Raises:
            OSError: If file cannot be accessed
        """
        # Use follow_symlinks=False to get symlink metadata, not target
        stat_info = os.stat(file_path, follow_symlinks=False)

        is_symlink = os.path.islink(file_path)
        symlink_target = None
        if is_symlink:
            try:
                symlink_target = os.readlink(file_path)
            except OSError:
                # If we can't read the symlink, treat it as a regular file
                is_symlink = False

        return FileMetadata(
            path=str(file_path),
            mode=stat_info.st_mode,
            uid=stat_info.st_uid,
            gid=stat_info.st_gid,
            atime=stat_info.st_atime,
            mtime=stat_info.st_mtime,
            size=stat_info.st_size,
            is_symlink=is_symlink,
            symlink_target=symlink_target,
        )

    def restore_permissions(self, file_path: Path, metadata: FileMetadata) -> None:
        """Restore file metadata from FileMetadata object.

        Args:
            file_path: Path to the file
            metadata: FileMetadata with permissions to restore

        Raises:
            OSError: If permissions cannot be set
            PermissionError: If insufficient privileges
        """
        # Restore ownership (requires root privileges)
        try:
            os.chown(file_path, metadata.uid, metadata.gid, follow_symlinks=False)
        except PermissionError:
            # If we don't have permission, try to continue
            # This might happen if not running as root
            pass

        # Restore permissions (only if not symlink)
        # Symlinks don't have their own permissions
        if not metadata.is_symlink:
            try:
                os.chmod(file_path, metadata.mode)
            except PermissionError:
                pass

        # Restore timestamps
        try:
            os.utime(file_path, (metadata.atime, metadata.mtime), follow_symlinks=False)
        except (PermissionError, OSError):
            # Some filesystems don't support setting times on symlinks
            pass

    def capture_directory_permissions(
        self, directory: Path, relative_to: Optional[Path] = None
    ) -> dict[str, FileMetadata]:
        """Capture permissions for all files in a directory recursively.

        Args:
            directory: Root directory to scan
            relative_to: Make paths relative to this directory (optional)

        Returns:
            Dictionary mapping relative paths to FileMetadata objects
        """
        permissions = {}

        for root, dirs, files in os.walk(directory, followlinks=False):
            root_path = Path(root)

            # Process files
            for filename in files:
                file_path = root_path / filename
                try:
                    metadata = self.capture_permissions(file_path)

                    # Make path relative if requested
                    if relative_to:
                        rel_path = file_path.relative_to(relative_to)
                        metadata.path = str(rel_path)

                    permissions[metadata.path] = metadata
                except (OSError, PermissionError) as e:
                    # Skip files we can't access
                    print(f"Warning: Could not capture permissions for {file_path}: {e}")
                    continue

            # Also process directories themselves
            for dirname in dirs:
                dir_path = root_path / dirname
                try:
                    metadata = self.capture_permissions(dir_path)

                    if relative_to:
                        rel_path = dir_path.relative_to(relative_to)
                        metadata.path = str(rel_path)

                    permissions[metadata.path] = metadata
                except (OSError, PermissionError) as e:
                    print(f"Warning: Could not capture permissions for {dir_path}: {e}")
                    continue

        return permissions

    def restore_directory_permissions(
        self, base_path: Path, permissions: dict[str, FileMetadata]
    ) -> None:
        """Restore permissions for all files in a directory.

        Args:
            base_path: Base directory where files are located
            permissions: Dictionary mapping paths to FileMetadata objects
        """
        for rel_path, metadata in permissions.items():
            full_path = base_path / rel_path

            if not full_path.exists():
                print(f"Warning: File {full_path} does not exist, skipping permission restore")
                continue

            try:
                self.restore_permissions(full_path, metadata)
            except Exception as e:
                print(f"Warning: Could not restore permissions for {full_path}: {e}")
                continue

    @staticmethod
    def is_root() -> bool:
        """Check if running with root privileges."""
        return os.geteuid() == 0

    @staticmethod
    def get_username_from_uid(uid: int) -> Optional[str]:
        """Get username from UID.

        Args:
            uid: User ID

        Returns:
            Username or None if not found
        """
        try:
            import pwd

            return pwd.getpwuid(uid).pw_name
        except (KeyError, ImportError):
            return None

    @staticmethod
    def get_groupname_from_gid(gid: int) -> Optional[str]:
        """Get group name from GID.

        Args:
            gid: Group ID

        Returns:
            Group name or None if not found
        """
        try:
            import grp

            return grp.getgrgid(gid).gr_name
        except (KeyError, ImportError):
            return None
