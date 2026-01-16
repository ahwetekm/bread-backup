"""Backup metadata management."""

import hashlib
import json
import platform
import socket
import tarfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from bread_backup import __version__


@dataclass
class BackupMetadata:
    """Metadata for a backup."""

    backup_id: str
    backup_type: str  # "full" or "incremental"
    timestamp: str
    hostname: str
    kernel_version: str
    bread_version: str
    compression: str
    parent_backup_id: Optional[str] = None
    components: dict[str, dict[str, Any]] = field(default_factory=dict)
    exclude_patterns: list[str] = field(default_factory=list)
    checksums: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "backup_id": self.backup_id,
            "backup_type": self.backup_type,
            "parent_backup_id": self.parent_backup_id,
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "kernel_version": self.kernel_version,
            "bread_version": self.bread_version,
            "compression": self.compression,
            "components": self.components,
            "exclude_patterns": self.exclude_patterns,
            "checksums": self.checksums,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BackupMetadata":
        """Create from dictionary."""
        return cls(**data)


class MetadataManager:
    """Manages backup metadata."""

    MANIFEST_FILENAME = "manifest.json"

    def create_metadata(
        self,
        backup_type: str = "full",
        compression: str = "zstd",
        parent_backup_id: Optional[str] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> BackupMetadata:
        """Create new backup metadata.

        Args:
            backup_type: Type of backup ("full" or "incremental")
            compression: Compression algorithm used
            parent_backup_id: ID of parent backup (for incremental backups)
            exclude_patterns: List of exclude patterns

        Returns:
            BackupMetadata instance
        """
        return BackupMetadata(
            backup_id=str(uuid.uuid4()),
            backup_type=backup_type,
            parent_backup_id=parent_backup_id,
            timestamp=datetime.now().isoformat(),
            hostname=socket.gethostname(),
            kernel_version=platform.release(),
            bread_version=__version__,
            compression=compression,
            exclude_patterns=exclude_patterns or [],
            components={},
            checksums={},
        )

    def add_component(
        self,
        metadata: BackupMetadata,
        component_name: str,
        component_info: dict[str, Any],
    ) -> None:
        """Add component information to metadata.

        Args:
            metadata: BackupMetadata instance
            component_name: Name of component (e.g., "packages", "config")
            component_info: Dictionary with component details
        """
        metadata.components[component_name] = component_info

    def add_checksum(self, metadata: BackupMetadata, file_path: str, checksum: str) -> None:
        """Add file checksum to metadata.

        Args:
            metadata: BackupMetadata instance
            file_path: Path to file (relative to backup root)
            checksum: SHA256 checksum
        """
        metadata.checksums[file_path] = checksum

    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of SHA256 hash
        """
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def save_metadata(self, metadata: BackupMetadata, output_path: Path) -> None:
        """Save metadata to JSON file.

        Args:
            metadata: BackupMetadata instance
            output_path: Path to save manifest.json
        """
        manifest_path = output_path / self.MANIFEST_FILENAME

        with open(manifest_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)

    def load_metadata(self, manifest_path: Path) -> BackupMetadata:
        """Load metadata from JSON file.

        Args:
            manifest_path: Path to manifest.json

        Returns:
            BackupMetadata instance

        Raises:
            FileNotFoundError: If manifest file doesn't exist
            json.JSONDecodeError: If manifest is invalid JSON
        """
        with open(manifest_path, "r") as f:
            data = json.load(f)

        return BackupMetadata.from_dict(data)

    def read_from_backup(self, backup_file: Path) -> BackupMetadata:
        """Extract and read metadata from backup archive.

        Args:
            backup_file: Path to .bread backup file

        Returns:
            BackupMetadata instance

        Raises:
            FileNotFoundError: If backup file doesn't exist
            tarfile.TarError: If backup file is corrupted
            KeyError: If manifest.json not found in archive
        """
        with tarfile.open(backup_file, "r:*") as tar:
            # Find manifest.json in archive
            try:
                manifest_member = tar.getmember(self.MANIFEST_FILENAME)
            except KeyError:
                raise KeyError(f"No {self.MANIFEST_FILENAME} found in backup archive")

            # Extract and parse manifest
            manifest_file = tar.extractfile(manifest_member)
            if manifest_file is None:
                raise ValueError(f"Cannot read {self.MANIFEST_FILENAME} from archive")

            data = json.load(manifest_file)

        return BackupMetadata.from_dict(data)

    def verify_checksums(self, backup_root: Path, metadata: BackupMetadata) -> bool:
        """Verify all checksums in metadata.

        Args:
            backup_root: Root directory of extracted backup
            metadata: BackupMetadata with checksums

        Returns:
            True if all checksums match, False otherwise
        """
        for file_path, expected_checksum in metadata.checksums.items():
            full_path = backup_root / file_path

            if not full_path.exists():
                print(f"Warning: File {file_path} missing from backup")
                return False

            actual_checksum = self.calculate_file_checksum(full_path)

            if actual_checksum != expected_checksum:
                print(f"Checksum mismatch for {file_path}")
                print(f"  Expected: {expected_checksum}")
                print(f"  Actual:   {actual_checksum}")
                return False

        return True

    @staticmethod
    def get_system_info() -> dict[str, str]:
        """Get current system information.

        Returns:
            Dictionary with system information
        """
        return {
            "hostname": socket.gethostname(),
            "kernel": platform.release(),
            "system": platform.system(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }
