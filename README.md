# Bread-Backup 🍞

A comprehensive backup and restore tool for Arch Linux systems.

> 🇹🇷 **Türkçe Dokümantasyon:**
> [Hızlı Başlangıç](HIZLIBASLANGIC.md) | [Kullanım Kılavuzu](KULLANIM.md) | [Kurulum](INSTALL.md) | [Senaryolar](SCENARIO.md)

## Features

- **Full System Backup**: Packages, configurations, and user data
- **Portable Format**: Single `.bread` file (compressed tar archive)
- **Incremental Backup**: Only backup changed files (coming soon)
- **Flexible Storage**: Local filesystem, USB drives, or cloud storage
- **Safe & Secure**: Preserves file permissions and ownership
- **Fast**: Uses zstd compression for optimal speed and size

## What Gets Backed Up

- **Packages**: All installed pacman and AUR packages
- **System Config**: Critical system configuration from `/etc`
- **User Config**: Application settings from `~/.config`
- **User Data**: Files from `/home` directories

## Installation

### Quick Install (Recommended)

```bash
# Install dependencies
sudo pacman -S python-click python-rich python-yaml git

# Clone and install
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup
sudo pip install -e .

# Verify installation
bread-backup --version
```

### System Requirements

- **OS**: Arch Linux (or Arch-based distros like Manjaro, EndeavourOS)
- **Python**: 3.10 or higher
- **Required Packages**:
  - `python-click` - CLI framework
  - `python-rich` - Beautiful terminal output
  - `python-yaml` - YAML parsing
- **Required Tools**: `pacman`, `tar`, compression tools (`gzip`/`zstd`)
- **Optional**: `yay` or `paru` for AUR package restoration

### For Users (When Package Available)

```bash
# Future: Install from AUR
yay -S bread-backup
```

## Quick Start

### Creating a Backup

```bash
# Full system backup
sudo bread-backup backup --destination /backup

# Backup to specific location
sudo bread-backup backup --destination /mnt/usb/backups

# Backup only packages and configs (no user data)
bread-backup backup --no-user-data
```

### Restoring from Backup

```bash
# Full system restore
sudo bread-backup restore /backup/backup-hostname-2026-01-16.bread

# Restore only packages
sudo bread-backup restore backup.bread --packages-only

# Preview what will be restored (dry-run)
sudo bread-backup restore backup.bread --dry-run
```

### Managing Backups

```bash
# List available backups
bread-backup list --destination /backup

# Verify backup integrity
bread-backup verify backup.bread

# Show backup information
bread-backup info backup.bread
```

## Usage

### Backup Command

```bash
bread-backup backup [OPTIONS]
```

**Options:**
- `--destination PATH` - Where to save the backup (default: `/var/backups`)
- `--compression TYPE` - Compression algorithm: gzip, zstd, xz, lz4 (default: zstd)
- `--exclude-file PATH` - File containing exclude patterns
- `--no-packages` - Skip package backup
- `--no-config` - Skip configuration backup
- `--no-user-data` - Skip user data backup
- `--verbose, -v` - Verbose output

### Restore Command

```bash
bread-backup restore BACKUP_FILE [OPTIONS]
```

**Options:**
- `--packages-only` - Restore only packages
- `--config-only` - Restore only configurations
- `--data-only` - Restore only user data
- `--dry-run` - Show what would be restored without making changes
- `--no-confirm` - Skip confirmation prompts
- `--verbose, -v` - Verbose output

### List Command

```bash
bread-backup list [OPTIONS]
```

**Options:**
- `--destination PATH` - Directory to search for backups
- `--sort-by DATE|SIZE|NAME` - Sort order
- `--json` - Output in JSON format

### Verify Command

```bash
bread-backup verify BACKUP_FILE
```

Verifies backup integrity by checking checksums and archive structure.

## Backup File Format

```
backup-hostname-2026-01-16.bread  (tar.zst archive)
├── manifest.json                  # Metadata and system info
├── checksums.sha256              # File integrity checksums
├── packages/
│   ├── pacman-explicit.txt       # Explicitly installed pacman packages
│   ├── aur-packages.txt          # AUR packages
│   └── package-versions.json     # Detailed version info
├── system-config/
│   └── etc.tar.zst               # /etc directory backup
├── user-config/
│   └── config.tar.zst            # ~/.config backup
└── user-data/
    └── home.tar.zst              # /home directory backup
```

## Exclude Patterns

You can exclude files and directories using `.gitignore`-style patterns.

### Default Exclusions

```
# Cache directories
**/.cache/*
**/Cache/*
**/*.tmp
**/*.lock

# Build artifacts
**/node_modules/
**/.venv/
**/__pycache__/

# Browser caches
**/.mozilla/firefox/*/cache2/
**/.config/google-chrome/*/Cache/
```

### Custom Exclude File

Create a file with your patterns:

```bash
# my-excludes.txt
**/Downloads/
**/Videos/
*.iso
*.mp4
```

Use it with:

```bash
bread-backup backup --exclude-file my-excludes.txt
```

## Configuration

Create a config file at `~/.config/bread-backup/config.yaml`:

```yaml
backup:
  destination: /backup/arch-backups
  compression: zstd
  compression_level: 6

  components:
    packages: true
    system_config: true
    user_config: true
    user_data: true

  exclude_file: ~/.config/bread-backup/exclude.txt

restore:
  aur_helper: yay
  no_confirm: false

storage:
  local:
    enabled: true
```

## How It Works

### Backup Process

1. **Collect Package Information**: Lists all installed packages using `pacman`
2. **Backup Configurations**: Archives `/etc` and `~/.config` directories
3. **Backup User Data**: Archives `/home` directories (with exclusions)
4. **Create Metadata**: Generates manifest with system info and checksums
5. **Compress Archive**: Creates a single `.bread` file
6. **Verify Integrity**: Calculates checksums for verification

### Restore Process

1. **Verify Backup**: Validates checksums and archive integrity
2. **Create Restore Point**: Backs up current package list for rollback
3. **Restore Packages**: Reinstalls packages via pacman and AUR helper
4. **Restore Configurations**: Extracts config files with proper permissions
5. **Restore User Data**: Extracts user files with proper ownership
6. **Validate System**: Checks that all files were restored correctly

## Security Considerations

- Backup files are created with `600` permissions (owner read/write only)
- Sensitive files (SSH keys, GPG keys) should be encrypted
- Use `--exclude-file` to avoid backing up sensitive data
- Restore operations require sudo for system-level changes
- Always verify backups before using them for restoration

## Troubleshooting

### Backup Creation Fails

**Problem**: Permission denied errors

**Solution**: Use `sudo` for system-wide backups:
```bash
sudo bread-backup backup
```

### Restore Fails: AUR Helper Not Found

**Problem**: Cannot install AUR packages

**Solution**: Install an AUR helper first:
```bash
sudo pacman -S --needed base-devel git
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si
```

### Large Backup Size

**Problem**: Backup file is too large

**Solution**: Use exclude patterns to skip large directories:
```bash
bread-backup backup --exclude-file excludes.txt
```

Add patterns like:
```
**/Downloads/
**/Videos/
**/.cache/
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bread_backup --cov-report=html

# Run specific test file
pytest tests/test_backup.py
```

### Code Quality

```bash
# Format code
black bread_backup/

# Lint code
ruff check bread_backup/

# Type checking
mypy bread_backup/
```

## Roadmap

### v0.1.0 (Current - MVP)
- [x] Basic project structure
- [x] Package backup and restore
- [x] Config file backup and restore
- [x] Local storage backend
- [x] CLI interface

### v0.2.0
- [ ] Incremental backup support
- [ ] System config backup (`/etc`)
- [ ] User data backup (`/home`)
- [ ] Progress indicators
- [ ] Enhanced error handling

### v0.3.0
- [ ] USB/External drive storage
- [ ] Cloud storage (Google Drive, Dropbox, S3)
- [ ] Encryption support (GPG/Age)
- [ ] Compression options (gzip, xz, lz4)

### v1.0.0
- [ ] Systemd timer integration
- [ ] Web UI (optional)
- [ ] Backup scheduling
- [ ] Comprehensive documentation

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

### Guidelines

1. Follow PEP 8 style guidelines
2. Write tests for new features
3. Update documentation
4. Add type hints where possible

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Timeshift, rsync, and other backup tools
- Built for the Arch Linux community
- Uses Click for CLI, Rich for beautiful terminal output

## Support

- **Issues**: [GitHub Issues](https://github.com/ahwetekm/bread-backup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ahwetekm/bread-backup/discussions)
- **Arch Wiki**: Contribute your experiences!

---

**Made with ❤️ for Arch Linux users**
