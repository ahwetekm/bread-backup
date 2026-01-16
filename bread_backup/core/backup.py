"""Backup orchestration - coordinates all backup operations."""

import hashlib
import shutil
import socket
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from bread_backup.collectors.config_files import ConfigCollector
from bread_backup.collectors.packages import PackageCollector
from bread_backup.core.metadata import BackupMetadata, MetadataManager
from bread_backup.storage.local import LocalStorage
from bread_backup.utils.exclude import ExcludePatternMatcher

console = Console()


class BackupOrchestrator:
    """Orchestrates the entire backup process."""

    def __init__(
        self,
        destination: Path,
        compression: str = "zstd",
        exclude_file: Optional[Path] = None,
        include_packages: bool = True,
        include_config: bool = True,
        include_user_data: bool = False,  # Not implemented yet
        incremental: bool = False,  # Not implemented yet
        verbose: bool = False,
    ):
        """Initialize backup orchestrator.

        Args:
            destination: Destination directory for backup
            compression: Compression algorithm (gzip, zstd, xz, lz4)
            exclude_file: File containing exclude patterns
            include_packages: Include package backup
            include_config: Include config backup
            include_user_data: Include user data backup
            incremental: Create incremental backup
            verbose: Enable verbose output
        """
        self.destination = destination
        self.compression = compression
        self.include_packages = include_packages
        self.include_config = include_config
        self.include_user_data = include_user_data
        self.incremental = incremental
        self.verbose = verbose

        # Load exclude patterns
        self.exclude_patterns = []
        if exclude_file and exclude_file.exists():
            self.exclude_matcher = ExcludePatternMatcher.from_file(exclude_file)
            self.exclude_patterns = self.exclude_matcher.get_patterns()

        # Initialize components
        self.storage = LocalStorage(destination)
        self.metadata_manager = MetadataManager()

    def execute(self) -> Path:
        """Execute the backup process.

        Returns:
            Path to created backup file

        Raises:
            RuntimeError: If backup fails
        """
        console.print(Panel.fit("Starting Backup Process", style="bold cyan"))

        # Check if pacman is available
        if self.include_packages and not PackageCollector.check_pacman_available():
            raise RuntimeError("pacman not found. Is this an Arch Linux system?")

        # Create temporary working directory
        with tempfile.TemporaryDirectory(prefix="bread-backup-") as temp_dir:
            temp_path = Path(temp_dir)

            if self.verbose:
                console.print(f"Working directory: [cyan]{temp_path}[/cyan]")

            # Create metadata
            metadata = self.metadata_manager.create_metadata(
                backup_type="incremental" if self.incremental else "full",
                compression=self.compression,
                exclude_patterns=self.exclude_patterns,
            )

            # Execute collection phases
            self._collect_packages(temp_path, metadata)
            self._collect_config(temp_path, metadata)

            if self.include_user_data:
                console.print("[yellow]User data backup not yet implemented[/yellow]")

            # Save metadata
            console.print("\n[bold]Finalizing backup...[/bold]")
            self.metadata_manager.save_metadata(metadata, temp_path)

            # Create archive
            backup_file = self._create_archive(temp_path, metadata)

            # Save to destination
            final_path = self._save_to_destination(backup_file)

        console.print("\n[bold green]✓ Backup completed successfully![/bold green]")
        return final_path

    def _collect_packages(self, temp_path: Path, metadata: BackupMetadata) -> None:
        """Collect package information.

        Args:
            temp_path: Temporary working directory
            metadata: Backup metadata to update
        """
        if not self.include_packages:
            return

        console.print("\n[bold]Collecting packages...[/bold]")

        packages_dir = temp_path / "packages"
        collector = PackageCollector(verbose=self.verbose)

        try:
            component_info = collector.collect(packages_dir)
            self.metadata_manager.add_component(metadata, "packages", component_info)
        except Exception as e:
            console.print(f"[bold red]✗ Package collection failed:[/bold red] {e}")
            raise

    def _collect_config(self, temp_path: Path, metadata: BackupMetadata) -> None:
        """Collect configuration files.

        Args:
            temp_path: Temporary working directory
            metadata: Backup metadata to update
        """
        if not self.include_config:
            return

        console.print("\n[bold]Collecting configuration files...[/bold]")

        config_dir = temp_path / "user-config"
        collector = ConfigCollector(
            verbose=self.verbose, exclude_patterns=self.exclude_patterns
        )

        try:
            component_info = collector.collect(config_dir)
            self.metadata_manager.add_component(metadata, "user_config", component_info)
        except Exception as e:
            console.print(f"[bold red]✗ Config collection failed:[/bold red] {e}")
            raise

    def _create_archive(self, temp_path: Path, metadata: BackupMetadata) -> Path:
        """Create compressed archive from collected data.

        Args:
            temp_path: Directory containing collected data
            metadata: Backup metadata

        Returns:
            Path to created archive
        """
        hostname = socket.gethostname()
        archive_name = self.storage.generate_backup_filename(hostname)
        archive_path = temp_path.parent / archive_name

        # Determine compression mode
        compression_map = {
            "gzip": "gz",
            "zstd": "zst" if self._check_zstd_support() else "gz",
            "xz": "xz",
            "lz4": "lz4" if self._check_lz4_support() else "gz",
        }

        compression_suffix = compression_map.get(self.compression, "gz")
        tar_mode = f"w:{compression_suffix}"

        console.print(f"Creating archive with {self.compression} compression...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Compressing backup...", total=None)

            try:
                with tarfile.open(archive_path, tar_mode) as tar:
                    # Add all files from temp directory
                    for item in temp_path.iterdir():
                        tar.add(item, arcname=item.name, recursive=True)

                progress.update(task, description="[green]✓ Archive created")

            except Exception as e:
                raise RuntimeError(f"Failed to create archive: {e}")

        # Calculate checksum
        console.print("Calculating checksum...")
        checksum = self.metadata_manager.calculate_file_checksum(archive_path)
        metadata.checksums["backup_archive"] = checksum

        if self.verbose:
            archive_size = archive_path.stat().st_size
            console.print(f"  Archive size: {self._format_size(archive_size)}")
            console.print(f"  Checksum: {checksum[:16]}...")

        return archive_path

    def _save_to_destination(self, backup_file: Path) -> Path:
        """Save backup to destination.

        Args:
            backup_file: Path to backup archive

        Returns:
            Final path of backup file
        """
        console.print(f"Saving to {self.destination}...")

        # Ensure destination exists before checking disk space
        self.storage.ensure_destination_exists()

        # Check disk space
        file_size = backup_file.stat().st_size
        if not self.storage.check_disk_space(file_size):
            raise RuntimeError(
                f"Insufficient disk space. Need {self._format_size(file_size)}, "
                f"available {self._format_size(self.storage.get_available_space())}"
            )

        # Save backup
        final_path = self.storage.save_backup(backup_file)

        if self.verbose:
            console.print(f"  Saved to: [cyan]{final_path}[/cyan]")

        return final_path

    @staticmethod
    def _check_zstd_support() -> bool:
        """Check if zstd compression is supported.

        Returns:
            True if zstd is available
        """
        try:
            subprocess.run(
                ["zstd", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def _check_lz4_support() -> bool:
        """Check if lz4 compression is supported.

        Returns:
            True if lz4 is available
        """
        try:
            subprocess.run(
                ["lz4", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted string
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
