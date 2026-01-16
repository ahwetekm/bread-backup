"""Package collection for Arch Linux (pacman and AUR)."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class PackageInfo:
    """Information about an installed package."""

    name: str
    version: str
    is_explicit: bool  # Explicitly installed or dependency
    is_aur: bool  # AUR package or official repo


class PackageCollector:
    """Collects information about installed packages."""

    def __init__(self, verbose: bool = False):
        """Initialize package collector.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose

    def collect(self, output_dir: Path) -> dict:
        """Collect all package information.

        Args:
            output_dir: Directory to save package lists

        Returns:
            Dictionary with collection summary

        Raises:
            RuntimeError: If pacman is not available
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Collecting package information...", total=None)

            # Get all packages
            all_packages = self._get_all_packages()
            progress.update(task, description=f"[cyan]Found {len(all_packages)} packages")

            # Get explicit packages
            explicit_packages = self._get_explicit_packages()

            # Get AUR packages
            aur_packages = self._get_aur_packages()

            # Save to files
            progress.update(task, description="[cyan]Saving package lists...")
            self._save_package_lists(output_dir, all_packages, explicit_packages, aur_packages)

            # Create detailed JSON
            progress.update(task, description="[cyan]Creating package metadata...")
            package_details = self._create_package_details(
                all_packages, explicit_packages, aur_packages
            )
            self._save_package_json(output_dir, package_details)

        if self.verbose:
            console.print(f"  Total packages: {len(all_packages)}")
            console.print(f"  Explicit packages: {len(explicit_packages)}")
            console.print(f"  AUR packages: {len(aur_packages)}")

        return {
            "total_count": len(all_packages),
            "explicit_count": len(explicit_packages),
            "aur_count": len(aur_packages),
            "official_count": len(all_packages) - len(aur_packages),
        }

    def _run_pacman(self, args: list[str]) -> str:
        """Run pacman command and return output.

        Args:
            args: Arguments to pass to pacman

        Returns:
            Command output

        Raises:
            RuntimeError: If pacman command fails
        """
        try:
            result = subprocess.run(
                ["pacman"] + args,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"pacman command failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("pacman not found. Is this an Arch Linux system?")

    def _get_all_packages(self) -> list[tuple[str, str]]:
        """Get all installed packages.

        Returns:
            List of (package_name, version) tuples
        """
        output = self._run_pacman(["-Q"])
        packages = []

        for line in output.strip().split("\n"):
            if line:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    packages.append((parts[0], parts[1]))

        return packages

    def _get_explicit_packages(self) -> list[str]:
        """Get explicitly installed packages.

        Returns:
            List of package names
        """
        output = self._run_pacman(["-Qe"])
        packages = []

        for line in output.strip().split("\n"):
            if line:
                package_name = line.split()[0]
                packages.append(package_name)

        return packages

    def _get_aur_packages(self) -> list[str]:
        """Get AUR (foreign) packages.

        Returns:
            List of package names
        """
        try:
            output = self._run_pacman(["-Qm"])
            packages = []

            for line in output.strip().split("\n"):
                if line:
                    package_name = line.split()[0]
                    packages.append(package_name)

            return packages
        except RuntimeError:
            # If no foreign packages, pacman might return error
            return []

    def _save_package_lists(
        self,
        output_dir: Path,
        all_packages: list[tuple[str, str]],
        explicit_packages: list[str],
        aur_packages: list[str],
    ) -> None:
        """Save package lists to text files.

        Args:
            output_dir: Directory to save files
            all_packages: All packages (name, version)
            explicit_packages: Explicit package names
            aur_packages: AUR package names
        """
        # Save all packages
        with open(output_dir / "pacman-all.txt", "w") as f:
            for name, version in all_packages:
                f.write(f"{name} {version}\n")

        # Save explicit packages
        with open(output_dir / "pacman-explicit.txt", "w") as f:
            for name in explicit_packages:
                f.write(f"{name}\n")

        # Save AUR packages
        with open(output_dir / "aur-packages.txt", "w") as f:
            for name in aur_packages:
                f.write(f"{name}\n")

        # Also save official packages (explicit, non-AUR)
        official_explicit = [pkg for pkg in explicit_packages if pkg not in aur_packages]
        with open(output_dir / "pacman-official-explicit.txt", "w") as f:
            for name in official_explicit:
                f.write(f"{name}\n")

    def _create_package_details(
        self,
        all_packages: list[tuple[str, str]],
        explicit_packages: list[str],
        aur_packages: list[str],
    ) -> list[dict]:
        """Create detailed package information.

        Args:
            all_packages: All packages (name, version)
            explicit_packages: Explicit package names
            aur_packages: AUR package names

        Returns:
            List of package dictionaries
        """
        package_details = []

        for name, version in all_packages:
            package_details.append(
                {
                    "name": name,
                    "version": version,
                    "is_explicit": name in explicit_packages,
                    "is_aur": name in aur_packages,
                }
            )

        return package_details

    def _save_package_json(self, output_dir: Path, package_details: list[dict]) -> None:
        """Save detailed package information as JSON.

        Args:
            output_dir: Directory to save file
            package_details: List of package dictionaries
        """
        json_path = output_dir / "package-versions.json"

        with open(json_path, "w") as f:
            json.dump(
                {
                    "packages": package_details,
                    "total": len(package_details),
                },
                f,
                indent=2,
            )

    @staticmethod
    def check_pacman_available() -> bool:
        """Check if pacman is available.

        Returns:
            True if pacman is available
        """
        try:
            subprocess.run(
                ["pacman", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_pacman_conf_path() -> Optional[Path]:
        """Get path to pacman.conf.

        Returns:
            Path to pacman.conf or None if not found
        """
        conf_path = Path("/etc/pacman.conf")
        return conf_path if conf_path.exists() else None

    @staticmethod
    def get_mirrorlist_path() -> Optional[Path]:
        """Get path to mirrorlist.

        Returns:
            Path to mirrorlist or None if not found
        """
        mirrorlist_path = Path("/etc/pacman.d/mirrorlist")
        return mirrorlist_path if mirrorlist_path.exists() else None
