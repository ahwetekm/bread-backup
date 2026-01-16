"""Configuration file collection."""

import json
import os
import shutil
import tarfile
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from bread_backup.utils.exclude import ExcludePatternMatcher
from bread_backup.utils.permissions import FilePermissionManager

console = Console()


class ConfigCollector:
    """Collects user configuration files from ~/.config."""

    DEFAULT_EXCLUDE_PATTERNS = [
        "**/.cache/*",
        "**/Cache/*",
        "**/cache/*",
        "**/*.lock",
        "**/*.pid",
        "**/chromium/*",
        "**/google-chrome/*",
        "**/Code/Cache/*",
        "**/Code/CachedData/*",
        "**/Code/logs/*",
        "**/.vscode/extensions/*",
        "**/discord/Cache/*",
        "**/slack/Cache/*",
    ]

    def __init__(self, verbose: bool = False, exclude_patterns: Optional[list[str]] = None):
        """Initialize config collector.

        Args:
            verbose: Enable verbose output
            exclude_patterns: Additional exclude patterns
        """
        self.verbose = verbose

        # Combine default and custom exclude patterns
        patterns = self.DEFAULT_EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            patterns.extend(exclude_patterns)

        self.exclude_matcher = ExcludePatternMatcher(patterns)
        self.permission_manager = FilePermissionManager()

    def collect(self, output_dir: Path, username: Optional[str] = None) -> dict:
        """Collect configuration files.

        Args:
            output_dir: Directory to save collected files
            username: Specific user to collect (None = current user)

        Returns:
            Dictionary with collection summary

        Raises:
            FileNotFoundError: If config directory doesn't exist
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get config directory
        if username:
            config_dir = Path(f"/home/{username}/.config")
        else:
            config_dir = Path.home() / ".config"

        if not config_dir.exists():
            if self.verbose:
                console.print(f"[yellow]Config directory not found: {config_dir}[/yellow]")
            return {"total_files": 0, "total_size_bytes": 0, "skipped_files": 0}

        # Collect files
        temp_dir = output_dir / "temp_config"
        temp_dir.mkdir(exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            # Count files first
            task_count = progress.add_task(
                "[cyan]Scanning config files...", total=None
            )

            files_to_backup = []
            total_size = 0
            skipped_count = 0

            for root, dirs, files in os.walk(config_dir, followlinks=False):
                root_path = Path(root)

                # Filter directories based on exclude patterns
                dirs[:] = [
                    d
                    for d in dirs
                    if not self.exclude_matcher.should_exclude(
                        str((root_path / d).relative_to(config_dir.parent))
                    )
                ]

                for filename in files:
                    file_path = root_path / filename
                    rel_path = file_path.relative_to(config_dir.parent)

                    # Check if should be excluded
                    if self.exclude_matcher.should_exclude(str(rel_path)):
                        skipped_count += 1
                        continue

                    try:
                        # Get file size (don't follow symlinks)
                        stat = os.stat(file_path, follow_symlinks=False)
                        total_size += stat.st_size
                        files_to_backup.append(file_path)
                    except (OSError, PermissionError) as e:
                        if self.verbose:
                            console.print(f"[yellow]Warning: Could not access {file_path}: {e}[/yellow]")
                        skipped_count += 1

            progress.update(
                task_count,
                description=f"[cyan]Found {len(files_to_backup)} files ({self._format_size(total_size)})",
                completed=True,
            )

            # Copy files
            task_copy = progress.add_task(
                "[cyan]Copying config files...", total=len(files_to_backup)
            )

            permissions_data = {}

            for file_path in files_to_backup:
                rel_path = file_path.relative_to(config_dir.parent)
                dest_path = temp_dir / rel_path

                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file or symlink
                if file_path.is_symlink():
                    # Copy symlink as-is
                    link_target = os.readlink(file_path)
                    os.symlink(link_target, dest_path)
                else:
                    # Copy regular file
                    shutil.copy2(file_path, dest_path, follow_symlinks=False)

                # Capture permissions
                try:
                    metadata = self.permission_manager.capture_permissions(file_path)
                    permissions_data[str(rel_path)] = metadata.to_dict()
                except (OSError, PermissionError) as e:
                    if self.verbose:
                        console.print(
                            f"[yellow]Warning: Could not capture permissions for {file_path}: {e}[/yellow]"
                        )

                progress.advance(task_copy)

            # Save permissions data
            progress.update(task_copy, description="[cyan]Saving file permissions...")
            permissions_file = output_dir / "file-permissions.json"
            with open(permissions_file, "w") as f:
                json.dump(permissions_data, f, indent=2)

            # Create tar archive
            progress.update(task_copy, description="[cyan]Creating archive...")
            archive_name = f"{username or 'user'}-config.tar"
            archive_path = output_dir / archive_name

            with tarfile.open(archive_path, "w") as tar:
                tar.add(temp_dir, arcname=".config", recursive=True)

            # Cleanup temp directory
            shutil.rmtree(temp_dir)

        if self.verbose:
            console.print(f"  Files backed up: {len(files_to_backup)}")
            console.print(f"  Files skipped: {skipped_count}")
            console.print(f"  Total size: {self._format_size(total_size)}")

        return {
            "total_files": len(files_to_backup),
            "total_size_bytes": total_size,
            "skipped_files": skipped_count,
            "archive_path": str(archive_path),
            "permissions_file": str(permissions_file),
        }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def get_config_size(self, username: Optional[str] = None) -> int:
        """Get total size of config directory.

        Args:
            username: Specific user (None = current user)

        Returns:
            Total size in bytes
        """
        if username:
            config_dir = Path(f"/home/{username}/.config")
        else:
            config_dir = Path.home() / ".config"

        if not config_dir.exists():
            return 0

        total_size = 0
        for root, dirs, files in os.walk(config_dir):
            for filename in files:
                file_path = Path(root) / filename
                try:
                    total_size += file_path.stat().st_size
                except (OSError, PermissionError):
                    pass

        return total_size
