"""Configuration files restoration."""

import json
import shutil
import tarfile
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from bread_backup.utils.permissions import FilePermissionManager, FileMetadata

console = Console()


class ConfigRestorer:
    """Restores configuration files from backup."""

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        """Initialize config restorer.

        Args:
            verbose: Enable verbose output
            dry_run: Don't actually restore files
        """
        self.verbose = verbose
        self.dry_run = dry_run
        self.permission_manager = FilePermissionManager()

    def restore(
        self,
        config_dir: Path,
        target_home: Optional[Path] = None,
    ) -> dict:
        """Restore configuration files.

        Args:
            config_dir: Directory containing config backup
            target_home: Target home directory (default: current user's home)

        Returns:
            Dictionary with restoration summary

        Raises:
            FileNotFoundError: If config backup not found
            RuntimeError: If restoration fails
        """
        if not config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {config_dir}")

        console.print("\n[bold]Restoring configuration files...[/bold]")

        # Determine target home directory
        if target_home is None:
            target_home = Path.home()

        target_config = target_home / ".config"

        # Find config archive
        archive = self._find_config_archive(config_dir)
        if not archive:
            console.print("[yellow]No config archive found[/yellow]")
            return {"files_restored": 0}

        # Load permissions data
        permissions = self._load_permissions(config_dir)

        # Extract and restore
        files_restored = self._extract_and_restore(
            archive, target_home, permissions
        )

        return {"files_restored": files_restored}

    def _find_config_archive(self, config_dir: Path) -> Optional[Path]:
        """Find config tar archive.

        Args:
            config_dir: Directory to search

        Returns:
            Path to archive or None
        """
        # Look for various archive names
        patterns = ["*-config.tar", "*-config.tar.gz", "*-config.tar.zst"]

        for pattern in patterns:
            archives = list(config_dir.glob(pattern))
            if archives:
                return archives[0]

        return None

    def _load_permissions(self, config_dir: Path) -> dict[str, FileMetadata]:
        """Load file permissions from JSON.

        Args:
            config_dir: Directory containing permissions file

        Returns:
            Dictionary mapping paths to FileMetadata
        """
        permissions_file = config_dir / "file-permissions.json"

        if not permissions_file.exists():
            if self.verbose:
                console.print("[yellow]No permissions file found[/yellow]")
            return {}

        with open(permissions_file, "r") as f:
            data = json.load(f)

        # Convert dict to FileMetadata objects
        permissions = {}
        for path, metadata_dict in data.items():
            permissions[path] = FileMetadata.from_dict(metadata_dict)

        return permissions

    def _extract_and_restore(
        self,
        archive: Path,
        target_home: Path,
        permissions: dict[str, FileMetadata],
    ) -> int:
        """Extract archive and restore files.

        Args:
            archive: Path to tar archive
            target_home: Target home directory
            permissions: File permissions mapping

        Returns:
            Number of files restored
        """
        if self.dry_run:
            console.print("[yellow]DRY RUN - Would extract archive to:[/yellow]")
            console.print(f"  {target_home / '.config'}")
            with tarfile.open(archive, "r:*") as tar:
                members = tar.getmembers()
                console.print(f"  {len(members)} files would be restored")
                if self.verbose:
                    for member in members[:10]:
                        console.print(f"    - {member.name}")
                    if len(members) > 10:
                        console.print(f"    ... and {len(members) - 10} more")
            return len(members)

        files_restored = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Extracting files...", total=None)

            # Extract archive
            with tarfile.open(archive, "r:*") as tar:
                # Use filter='data' to allow absolute path symlinks (Python 3.12+)
                # For older Python, we need to handle it manually
                try:
                    tar.extractall(target_home, filter='data')
                except TypeError:
                    # Python < 3.12 doesn't have filter parameter
                    tar.extractall(target_home)
                members = tar.getmembers()
                files_restored = len(members)

            progress.update(task, description=f"[cyan]Extracted {files_restored} files")

            # Restore permissions
            if permissions:
                progress.update(task, description="[cyan]Restoring file permissions...")

                for rel_path, metadata in permissions.items():
                    full_path = target_home / rel_path

                    if not full_path.exists():
                        if self.verbose:
                            console.print(
                                f"[yellow]Warning: File {full_path} not found, "
                                f"skipping permission restore[/yellow]"
                            )
                        continue

                    try:
                        self.permission_manager.restore_permissions(full_path, metadata)
                    except Exception as e:
                        if self.verbose:
                            console.print(
                                f"[yellow]Warning: Could not restore permissions "
                                f"for {full_path}: {e}[/yellow]"
                            )

            progress.update(task, description="[green]✓ Configuration restored")

        if self.verbose:
            console.print(f"  Files restored: {files_restored}")

        return files_restored
