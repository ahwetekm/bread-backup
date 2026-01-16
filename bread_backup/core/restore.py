"""Restore orchestration - coordinates all restore operations."""

import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from bread_backup.core.metadata import BackupMetadata, MetadataManager
from bread_backup.restorers.config_files import ConfigRestorer
from bread_backup.restorers.packages import PackageRestorer

console = Console()


class RestoreOrchestrator:
    """Orchestrates the entire restore process."""

    def __init__(
        self,
        backup_file: Path,
        packages_only: bool = False,
        config_only: bool = False,
        data_only: bool = False,
        dry_run: bool = False,
        no_confirm: bool = False,
        verbose: bool = False,
        aur_helper: str = "yay",
    ):
        """Initialize restore orchestrator.

        Args:
            backup_file: Path to backup file
            packages_only: Restore only packages
            config_only: Restore only configuration
            data_only: Restore only user data
            dry_run: Don't actually restore, just show what would be done
            no_confirm: Skip confirmation prompts
            verbose: Enable verbose output
            aur_helper: AUR helper to use
        """
        self.backup_file = backup_file
        self.packages_only = packages_only
        self.config_only = config_only
        self.data_only = data_only
        self.dry_run = dry_run
        self.no_confirm = no_confirm
        self.verbose = verbose
        self.aur_helper = aur_helper

        self.metadata_manager = MetadataManager()

    def execute(self) -> None:
        """Execute the restore process.

        Raises:
            FileNotFoundError: If backup file doesn't exist
            RuntimeError: If restore fails
        """
        console.print(Panel.fit("Starting Restore Process", style="bold cyan"))

        # Validate backup
        if not self.backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {self.backup_file}")

        # Extract backup to temporary directory
        with tempfile.TemporaryDirectory(prefix="bread-restore-") as temp_dir:
            temp_path = Path(temp_dir)

            if self.verbose:
                console.print(f"Working directory: [cyan]{temp_path}[/cyan]")

            # Extract backup
            console.print("\n[bold]Extracting backup...[/bold]")
            self._extract_backup(temp_path)

            # Load metadata
            metadata = self.metadata_manager.load_metadata(temp_path / "manifest.json")

            if self.verbose:
                self._print_metadata(metadata)

            # Execute restore phases
            if not self.config_only and not self.data_only:
                self._restore_packages(temp_path, metadata)

            if not self.packages_only and not self.data_only:
                self._restore_config(temp_path, metadata)

            if self.data_only:
                console.print("[yellow]User data restore not yet implemented[/yellow]")

        console.print("\n[bold green]✓ Restore completed successfully![/bold green]")

    def verify(self) -> bool:
        """Verify backup integrity.

        Returns:
            True if backup is valid

        Raises:
            FileNotFoundError: If backup file doesn't exist
        """
        if not self.backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {self.backup_file}")

        try:
            # Try to extract metadata
            metadata = self.metadata_manager.read_from_backup(self.backup_file)

            console.print("[green]✓ Backup file is valid[/green]")

            if self.verbose:
                console.print(f"\nBackup Type: [cyan]{metadata.backup_type}[/cyan]")
                console.print(f"Created: [cyan]{metadata.timestamp}[/cyan]")
                console.print(f"Hostname: [cyan]{metadata.hostname}[/cyan]")
                console.print(f"Kernel: [cyan]{metadata.kernel_version}[/cyan]")

            return True

        except Exception as e:
            console.print(f"[red]✗ Backup validation failed: {e}[/red]")
            return False

    def _extract_backup(self, temp_path: Path) -> None:
        """Extract backup archive to temporary directory.

        Args:
            temp_path: Temporary directory to extract to

        Raises:
            RuntimeError: If extraction fails
        """
        try:
            with tarfile.open(self.backup_file, "r:*") as tar:
                tar.extractall(temp_path)

            if self.verbose:
                console.print(f"[green]✓ Backup extracted to {temp_path}[/green]")

        except tarfile.TarError as e:
            raise RuntimeError(f"Failed to extract backup: {e}")

    def _restore_packages(self, temp_path: Path, metadata: BackupMetadata) -> None:
        """Restore packages.

        Args:
            temp_path: Temporary directory with extracted backup
            metadata: Backup metadata
        """
        packages_dir = temp_path / "packages"

        if not packages_dir.exists():
            console.print("[yellow]No packages found in backup[/yellow]")
            return

        restorer = PackageRestorer(
            verbose=self.verbose,
            aur_helper=self.aur_helper,
            dry_run=self.dry_run,
        )

        try:
            stats = restorer.restore(packages_dir)

            if self.verbose:
                console.print(f"\n[bold]Package Restore Summary:[/bold]")
                console.print(f"  Official packages: {stats.get('official_installed', 0)}")
                console.print(f"  AUR packages: {stats.get('aur_installed', 0)}")
                if stats.get("failed", 0) > 0:
                    console.print(f"  Failed: {stats['failed']}")

        except Exception as e:
            console.print(f"[bold red]✗ Package restore failed:[/bold red] {e}")
            raise

    def _restore_config(self, temp_path: Path, metadata: BackupMetadata) -> None:
        """Restore configuration files.

        Args:
            temp_path: Temporary directory with extracted backup
            metadata: Backup metadata
        """
        config_dir = temp_path / "user-config"

        if not config_dir.exists():
            console.print("[yellow]No configuration found in backup[/yellow]")
            return

        restorer = ConfigRestorer(
            verbose=self.verbose,
            dry_run=self.dry_run,
        )

        try:
            stats = restorer.restore(config_dir)

            if self.verbose:
                console.print(f"\n[bold]Config Restore Summary:[/bold]")
                console.print(f"  Files restored: {stats.get('files_restored', 0)}")

        except Exception as e:
            console.print(f"[bold red]✗ Config restore failed:[/bold red] {e}")
            raise

    def _print_metadata(self, metadata: BackupMetadata) -> None:
        """Print backup metadata.

        Args:
            metadata: Backup metadata
        """
        console.print("\n[bold]Backup Information:[/bold]")
        console.print(f"  Backup ID: [cyan]{metadata.backup_id}[/cyan]")
        console.print(f"  Type: [cyan]{metadata.backup_type}[/cyan]")
        console.print(f"  Created: [cyan]{metadata.timestamp}[/cyan]")
        console.print(f"  Hostname: [cyan]{metadata.hostname}[/cyan]")
        console.print(f"  Kernel: [cyan]{metadata.kernel_version}[/cyan]")
        console.print(f"  Compression: [cyan]{metadata.compression}[/cyan]")

        if metadata.components:
            console.print("\n[bold]Components:[/bold]")
            for comp_name, comp_info in metadata.components.items():
                console.print(f"  {comp_name}:")
                for key, value in comp_info.items():
                    if key != "archive_path" and key != "permissions_file":
                        console.print(f"    {key}: [cyan]{value}[/cyan]")
