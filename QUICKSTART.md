# Quick Start Guide 🚀

Get up and running with Bread-Backup in 5 minutes!

> 🇹🇷 [Bu kılavuzun Türkçe versiyonu için tıklayın](HIZLIBASLANGIC.md)

## Prerequisites

- Arch Linux (or Arch-based distro)
- Python 3.10+
- Internet connection

## Installation (2 minutes)

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

## Your First Backup (2 minutes)

```bash
# Create a backup
bread-backup backup --destination ~/my-backups

# That's it! Your backup is ready.
```

**What was backed up?**
- ✅ All installed packages (pacman + AUR)
- ✅ Your configuration files (~/.config)
- ✅ File permissions and symlinks

**Backup file location:**
```
~/my-backups/backup-yourhostname-2026-01-16-153045.bread
```

## Restore on New Machine (3 minutes)

```bash
# 1. Fresh Arch Linux installation complete
# 2. Install Bread-Backup (same as above)

# 3. Copy backup file
cp /mnt/usb/backup-*.bread /tmp/

# 4. Verify backup (optional but recommended)
bread-backup verify /tmp/backup-*.bread

# 5. Restore everything
sudo bread-backup restore /tmp/backup-*.bread

# 6. Install AUR helper if needed
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si

# 7. Restore AUR packages
sudo bread-backup restore /tmp/backup-*.bread --packages-only

# 8. Reboot
sudo reboot
```

## Common Commands

```bash
# List all backups
bread-backup list --destination ~/my-backups

# View backup details
bread-backup info backup-file.bread

# Verify backup integrity
bread-backup verify backup-file.bread

# Test restore (no changes)
bread-backup restore backup-file.bread --dry-run

# Restore only packages
sudo bread-backup restore backup-file.bread --packages-only

# Restore only configs
bread-backup restore backup-file.bread --config-only
```

## Tips

1. **Regular backups**: Create weekly backups of your system
2. **Test your backups**: Occasionally verify them with `--verify`
3. **Multiple copies**: Keep backups in different locations (USB + Cloud)
4. **Exclude unnecessary files**: Use `--exclude-file` for large cache directories

## Need Help?

- 📖 Full documentation: [KULLANIM.md](KULLANIM.md) (Turkish)
- 📖 Full documentation: [README.md](README.md) (English)
- 🐛 Report issues: [GitHub Issues](https://github.com/ahwetekm/bread-backup/issues)
- 💬 Ask questions: [GitHub Discussions](https://github.com/ahwetekm/bread-backup/discussions)

## Example Workflow

```bash
# Day 1: Setup
cd ~/Projects
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup
sudo pip install -e .

# Day 1: First backup
bread-backup backup --destination /backup

# Day 7: Weekly backup
bread-backup backup --destination /backup

# Day 30: Disaster strikes - laptop stolen!
# Buy new laptop, install Arch

# Day 30: Restore everything
sudo bread-backup restore /backup/backup-old-laptop.bread
sudo reboot

# Day 30: Back to work! 🎉
```

---

**Backup your system. Restore your peace of mind.** 🍞
