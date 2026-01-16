"""Package restoration for Arch Linux."""

import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class PackageRestorer:
    """Restores packages from backup."""

    def __init__(self, verbose: bool = False, aur_helper: str = "yay", dry_run: bool = False):
        """Initialize package restorer.

        Args:
            verbose: Enable verbose output
            aur_helper: AUR helper to use (yay, paru, etc.)
            dry_run: Don't actually install packages
        """
        self.verbose = verbose
        self.aur_helper = aur_helper
        self.dry_run = dry_run

    def restore(self, packages_dir: Path) -> dict:
        """Restore packages from backup.

        Args:
            packages_dir: Directory containing package lists

        Returns:
            Dictionary with restoration summary

        Raises:
            FileNotFoundError: If package lists not found
            RuntimeError: If restoration fails
        """
        if not packages_dir.exists():
            raise FileNotFoundError(f"Packages directory not found: {packages_dir}")

        console.print("\n[bold]Restoring packages...[/bold]")

        # Load package lists
        official_packages = self._load_package_list(packages_dir / "pacman-official-explicit.txt")
        aur_packages = self._load_package_list(packages_dir / "aur-packages.txt")

        if not official_packages and not aur_packages:
            console.print("[yellow]No packages to restore[/yellow]")
            return {"official_installed": 0, "aur_installed": 0, "failed": 0}

        stats = {"official_installed": 0, "aur_installed": 0, "failed": 0}

        # Update package database first
        if not self.dry_run:
            console.print("Updating package database...")
            try:
                self._run_command(["pacman", "-Sy"])
            except RuntimeError as e:
                console.print(f"[yellow]Warning: Failed to update database: {e}[/yellow]")

        # Restore official packages
        if official_packages:
            stats["official_installed"] = self._restore_official_packages(official_packages)

        # Restore AUR packages
        if aur_packages:
            stats["aur_installed"] = self._restore_aur_packages(aur_packages)

        return stats

    def _load_package_list(self, file_path: Path) -> list[str]:
        """Load package list from file.

        Args:
            file_path: Path to package list file

        Returns:
            List of package names
        """
        if not file_path.exists():
            return []

        packages = []
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (ignore version if present)
                    package_name = line.split()[0]
                    packages.append(package_name)

        return packages

    def _restore_official_packages(self, packages: list[str]) -> int:
        """Restore official pacman packages.

        Args:
            packages: List of package names

        Returns:
            Number of successfully installed packages
        """
        console.print(f"\nInstalling {len(packages)} official packages...")

        if self.dry_run:
            console.print("[yellow]DRY RUN - Would install:[/yellow]")
            for pkg in packages[:10]:
                console.print(f"  - {pkg}")
            if len(packages) > 10:
                console.print(f"  ... and {len(packages) - 10} more")
            return len(packages)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Installing packages...", total=None)

            try:
                # Use --needed to skip already installed packages
                # Use --noconfirm to avoid prompts
                cmd = ["pacman", "-S", "--needed", "--noconfirm"] + packages

                self._run_command(cmd, check=True)

                progress.update(task, description="[green]✓ Official packages installed")
                return len(packages)

            except RuntimeError as e:
                progress.update(task, description="[red]✗ Installation failed")
                console.print(f"[red]Error installing official packages: {e}[/red]")
                return 0

    def _restore_aur_packages(self, packages: list[str]) -> int:
        """Restore AUR packages.

        Args:
            packages: List of AUR package names

        Returns:
            Number of successfully installed packages
        """
        # Check if AUR helper is available
        if not self._check_aur_helper():
            console.print(
                f"[yellow]Warning: AUR helper '{self.aur_helper}' not found. "
                f"Skipping AUR packages.[/yellow]"
            )
            console.print(
                f"[yellow]Install {self.aur_helper} first, then restore again with --packages-only[/yellow]"
            )
            return 0

        console.print(f"\nInstalling {len(packages)} AUR packages...")

        if self.dry_run:
            console.print("[yellow]DRY RUN - Would install:[/yellow]")
            for pkg in packages[:10]:
                console.print(f"  - {pkg}")
            if len(packages) > 10:
                console.print(f"  ... and {len(packages) - 10} more")
            return len(packages)

        installed_count = 0
        failed_packages = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Installing AUR packages...", total=len(packages))

            for package in packages:
                try:
                    progress.update(task, description=f"[cyan]Installing {package}...")

                    # Most AUR helpers support similar syntax
                    cmd = [self.aur_helper, "-S", "--needed", "--noconfirm", package]

                    self._run_command(cmd, check=True)
                    installed_count += 1

                except RuntimeError as e:
                    if self.verbose:
                        console.print(f"[yellow]Warning: Failed to install {package}: {e}[/yellow]")
                    failed_packages.append(package)

                progress.advance(task)

            if failed_packages:
                progress.update(
                    task,
                    description=f"[yellow]AUR packages installed with {len(failed_packages)} failures",
                )
            else:
                progress.update(task, description="[green]✓ AUR packages installed")

        if failed_packages and self.verbose:
            console.print(f"\n[yellow]Failed to install {len(failed_packages)} AUR packages:[/yellow]")
            for pkg in failed_packages:
                console.print(f"  - {pkg}")

        return installed_count

    def _check_aur_helper(self) -> bool:
        """Check if AUR helper is available.

        Returns:
            True if AUR helper is found
        """
        try:
            subprocess.run(
                [self.aur_helper, "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _run_command(self, cmd: list[str], check: bool = True) -> str:
        """Run a shell command.

        Args:
            cmd: Command to run
            check: Raise exception on error

        Returns:
            Command output

        Raises:
            RuntimeError: If command fails and check=True
        """
        try:
            if self.verbose:
                console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
            )

            return result.stdout

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed: {e.stderr}")
