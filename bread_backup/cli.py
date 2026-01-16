"""Command-line interface for bread-backup."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bread_backup import __version__

console = Console()


def check_root():
    """Check if running with root privileges."""
    return os.geteuid() == 0


def require_root(func):
    """Decorator to ensure root privileges for operations that need them."""

    def wrapper(*args, **kwargs):
        if not check_root():
            console.print(
                "[bold red]Error:[/bold red] This operation requires root privileges.",
                style="red",
            )
            console.print("Please run with sudo: [cyan]sudo bread-backup ...[/cyan]")
            sys.exit(1)
        return func(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option(version=__version__, prog_name="bread-backup")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to config file",
    default=None,
)
@click.pass_context
def main(ctx, verbose, config):
    """Bread-Backup: Comprehensive backup and restore tool for Arch Linux.

    Create portable backups of your entire Arch Linux system including packages,
    configurations, and user data. Restore them on any Arch Linux machine.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config


@main.command()
@click.option(
    "--destination",
    "-d",
    type=click.Path(file_okay=False, writable=True),
    default="/var/backups/bread-backup",
    help="Backup destination directory",
)
@click.option(
    "--compression",
    "-c",
    type=click.Choice(["gzip", "zstd", "xz", "lz4"], case_sensitive=False),
    default="zstd",
    help="Compression algorithm",
)
@click.option(
    "--exclude-file",
    type=click.Path(exists=True),
    help="File containing exclude patterns",
)
@click.option("--no-packages", is_flag=True, help="Skip package backup")
@click.option("--no-config", is_flag=True, help="Skip configuration backup")
@click.option("--no-user-data", is_flag=True, help="Skip user data backup")
@click.option(
    "--incremental",
    is_flag=True,
    help="Create incremental backup (based on last backup)",
)
@click.pass_context
def backup(
    ctx,
    destination,
    compression,
    exclude_file,
    no_packages,
    no_config,
    no_user_data,
    incremental,
):
    """Create a system backup.

    Examples:
      bread-backup backup
      bread-backup backup --destination /mnt/usb/backups
      bread-backup backup --compression zstd --no-user-data
    """
    verbose = ctx.obj["verbose"]

    console.print(Panel.fit("🍞 Bread-Backup", style="bold cyan"))
    console.print(f"Creating backup at: [cyan]{destination}[/cyan]")
    console.print(f"Compression: [cyan]{compression}[/cyan]")

    if verbose:
        console.print("\n[bold]Configuration:[/bold]")
        console.print(f"  Packages: [{'red]Disabled' if no_packages else 'green]Enabled'}[/]")
        console.print(f"  Config: [{'red]Disabled' if no_config else 'green]Enabled'}[/]")
        console.print(f"  User Data: [{'red]Disabled' if no_user_data else 'green]Enabled'}[/]")
        console.print(f"  Incremental: [{'green]Yes' if incremental else 'yellow]No'}[/]")

    # Import here to avoid circular imports
    from bread_backup.core.backup import BackupOrchestrator

    try:
        orchestrator = BackupOrchestrator(
            destination=Path(destination),
            compression=compression,
            exclude_file=Path(exclude_file) if exclude_file else None,
            include_packages=not no_packages,
            include_config=not no_config,
            include_user_data=not no_user_data,
            incremental=incremental,
            verbose=verbose,
        )

        backup_file = orchestrator.execute()
        console.print(f"\n[bold green]✓[/bold green] Backup created: [cyan]{backup_file}[/cyan]")

    except KeyboardInterrupt:
        console.print("\n[bold red]✗[/bold red] Backup cancelled by user")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("backup_file", type=click.Path(exists=True))
@click.option(
    "--packages-only",
    is_flag=True,
    help="Restore only packages",
)
@click.option(
    "--config-only",
    is_flag=True,
    help="Restore only configurations",
)
@click.option(
    "--data-only",
    is_flag=True,
    help="Restore only user data",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be restored without making changes",
)
@click.option(
    "--no-confirm",
    is_flag=True,
    help="Skip confirmation prompts",
)
@click.pass_context
def restore(ctx, backup_file, packages_only, config_only, data_only, dry_run, no_confirm):
    """Restore from a backup file.

    Examples:
      sudo bread-backup restore backup.bread
      sudo bread-backup restore backup.bread --packages-only
      bread-backup restore backup.bread --dry-run
    """
    verbose = ctx.obj["verbose"]

    # Check for root unless dry-run
    if not dry_run and not check_root():
        console.print(
            "[bold red]Error:[/bold red] Restore operations require root privileges.",
            style="red",
        )
        console.print("Please run with sudo: [cyan]sudo bread-backup restore ...[/cyan]")
        sys.exit(1)

    console.print(Panel.fit("🍞 Bread-Backup Restore", style="bold cyan"))
    console.print(f"Backup file: [cyan]{backup_file}[/cyan]")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    # Import here to avoid circular imports
    from bread_backup.core.restore import RestoreOrchestrator

    try:
        orchestrator = RestoreOrchestrator(
            backup_file=Path(backup_file),
            packages_only=packages_only,
            config_only=config_only,
            data_only=data_only,
            dry_run=dry_run,
            no_confirm=no_confirm,
            verbose=verbose,
        )

        if not dry_run and not no_confirm:
            console.print("\n[bold yellow]⚠ Warning:[/bold yellow] This will restore system files.")
            if not click.confirm("Do you want to continue?"):
                console.print("[yellow]Restore cancelled[/yellow]")
                sys.exit(0)

        orchestrator.execute()
        console.print("\n[bold green]✓[/bold green] Restore completed successfully")

    except KeyboardInterrupt:
        console.print("\n[bold red]✗[/bold red] Restore cancelled by user")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option(
    "--destination",
    "-d",
    type=click.Path(exists=True, file_okay=False),
    default="/var/backups/bread-backup",
    help="Directory to search for backups",
)
@click.option(
    "--sort-by",
    type=click.Choice(["date", "size", "name"], case_sensitive=False),
    default="date",
    help="Sort order",
)
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.pass_context
def list(ctx, destination, sort_by, output_json):
    """List available backups.

    Examples:
      bread-backup list
      bread-backup list --destination /mnt/usb/backups
      bread-backup list --sort-by size --json
    """
    from bread_backup.storage.local import LocalStorage

    try:
        storage = LocalStorage(Path(destination))
        backups = storage.list_backups(sort_by=sort_by)

        if not backups:
            console.print(f"[yellow]No backups found in {destination}[/yellow]")
            return

        if output_json:
            import json

            print(json.dumps([b.to_dict() for b in backups], indent=2))
        else:
            table = Table(title=f"Backups in {destination}")
            table.add_column("Filename", style="cyan")
            table.add_column("Date", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Type", style="magenta")

            for backup in backups:
                table.add_row(
                    backup.filename,
                    backup.date.strftime("%Y-%m-%d %H:%M:%S"),
                    backup.size_human,
                    backup.backup_type,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.argument("backup_file", type=click.Path(exists=True))
@click.pass_context
def verify(ctx, backup_file):
    """Verify backup integrity.

    Examples:
      bread-backup verify backup.bread
    """
    verbose = ctx.obj["verbose"]

    console.print(Panel.fit("🍞 Verifying Backup", style="bold cyan"))
    console.print(f"File: [cyan]{backup_file}[/cyan]\n")

    from bread_backup.core.restore import RestoreOrchestrator

    try:
        orchestrator = RestoreOrchestrator(backup_file=Path(backup_file), verbose=verbose)
        is_valid = orchestrator.verify()

        if is_valid:
            console.print("[bold green]✓[/bold green] Backup is valid")
        else:
            console.print("[bold red]✗[/bold red] Backup is corrupted")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("backup_file", type=click.Path(exists=True))
@click.pass_context
def info(ctx, backup_file):
    """Show detailed backup information.

    Examples:
      bread-backup info backup.bread
    """
    console.print(Panel.fit("🍞 Backup Information", style="bold cyan"))
    console.print(f"File: [cyan]{backup_file}[/cyan]\n")

    from bread_backup.core.metadata import MetadataManager

    try:
        metadata_mgr = MetadataManager()
        metadata = metadata_mgr.read_from_backup(Path(backup_file))

        console.print("[bold]System Information:[/bold]")
        console.print(f"  Hostname: [cyan]{metadata.hostname}[/cyan]")
        console.print(f"  Kernel: [cyan]{metadata.kernel_version}[/cyan]")
        console.print(f"  Backup Type: [cyan]{metadata.backup_type}[/cyan]")
        console.print(f"  Date: [cyan]{metadata.timestamp}[/cyan]")
        console.print(f"  Compression: [cyan]{metadata.compression}[/cyan]")

        console.print("\n[bold]Components:[/bold]")
        for comp_name, comp_info in metadata.components.items():
            console.print(f"  {comp_name}:")
            for key, value in comp_info.items():
                console.print(f"    {key}: [cyan]{value}[/cyan]")

    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
