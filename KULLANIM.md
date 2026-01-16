# Bread-Backup Kullanım Kılavuzu 🍞

Bu kılavuz, Bread-Backup aracını kullanarak Arch Linux sisteminizi yedeklemenizi ve geri yüklemenizi adım adım anlatır.

## İçindekiler

1. [Kurulum](#kurulum)
2. [İlk Backup Alma](#ilk-backup-alma)
3. [Backup'ları Listeleme ve Kontrol](#backupları-listeleme-ve-kontrol)
4. [Yeni Sisteme Restore Etme](#yeni-sisteme-restore-etme)
5. [Sık Sorulan Sorular](#sık-sorulan-sorular)
6. [Sorun Giderme](#sorun-giderme)

---

## Kurulum

### Adım 1: Gerekli Paketleri Kurun

```bash
# Python bağımlılıklarını kurun
sudo pacman -S python-click python-rich python-yaml git
```

### Adım 2: Bread-Backup'ı İndirin ve Kurun

```bash
# Projeyi klonlayın
cd ~/Downloads
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup

# Kurun (pipx ile - önerilen)
pipx install -e .
```

### Adım 3: Kurulumu Test Edin

```bash
# Sürümü kontrol edin
bread-backup --version

# Yardım menüsünü görün
bread-backup --help
```

**Beklenen Çıktı:**
```
bread-backup, version 0.1.0

Usage: bread-backup [OPTIONS] COMMAND [ARGS]...

  Bread-Backup: Comprehensive backup and restore tool for Arch Linux.
  ...
```

✅ Kurulum tamamlandı!

---

## İlk Backup Alma

### Senaryo 1: Hızlı Backup (Önerilen)

En basit ve hızlı yöntem:

```bash
# Paketler + Konfigürasyon backup'ı al
bread-backup backup --destination ~/backup
```

**Ne yedeklenir?**
- ✅ Tüm kurulu paketler (pacman + AUR)
- ✅ Kullanıcı ayarları (~/.config)
- ❌ Kullanıcı dosyaları (henüz desteklenmiyor)

**Süre:** ~2-5 dakika (sistemin büyüklüğüne göre)

**Çıktı:**
```
🍞 Bread-Backup
Creating backup at: /home/ahmet/backup
Compression: zstd

Collecting packages...
Found 1234 packages
  Total packages: 1234
  Explicit packages: 456
  AUR packages: 89

Collecting configuration files...
Scanning config files...
Found 2567 files (45.0 MB)
Copying config files...
[████████████████████████████] 2567/2567

Finalizing backup...
Creating archive with zstd compression...
Compressing backup...
Calculating checksum...

✓ Backup completed successfully!
✓ Backup created: /home/ahmet/backup/backup-arch-2026-01-16-153045.bread
```

### Senaryo 2: USB/Harici Diske Backup

```bash
# USB'yi mount edin (örnek: /mnt/usb)
sudo mount /dev/sdb1 /mnt/usb

# USB'ye backup alın
bread-backup backup --destination /mnt/usb/backups

# Bittikten sonra güvenli çıkarın
sudo umount /mnt/usb
```

### Senaryo 3: Sadece Paket Listesi

Config dosyalarını atlamak isterseniz (çok hızlı):

```bash
bread-backup backup --no-config --destination ~/backup
```

### Senaryo 4: Özelleştirilmiş Backup

```bash
# Farklı sıkıştırma algoritması
bread-backup backup --compression gzip --destination ~/backup

# Belirli dosyaları hariç tutma
bread-backup backup --exclude-file ~/my-excludes.txt --destination ~/backup

# Verbose (detaylı) çıktı
bread-backup backup --destination ~/backup --verbose
```

---

## Backup'ları Listeleme ve Kontrol

### Backup'ları Listeleyin

```bash
# Belirli dizindeki tüm backup'ları listele
bread-backup list --destination ~/backup
```

**Çıktı:**
```
                    Backups in /home/ahmet/backup
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ Filename                         ┃ Date                ┃ Size    ┃ Type  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ backup-arch-2026-01-16-153045... │ 2026-01-16 15:30:45 │ 125.3 MB│ full  │
│ backup-arch-2026-01-15-020000... │ 2026-01-15 02:00:00 │ 118.7 MB│ full  │
│ backup-arch-2026-01-14-020000... │ 2026-01-14 02:00:00 │ 120.1 MB│ full  │
└──────────────────────────────────┴─────────────────────┴─────────┴───────┘
```

### Backup Detaylarını Görüntüleyin

```bash
bread-backup info ~/backup/backup-arch-2026-01-16-153045.bread
```

**Çıktı:**
```
🍞 Backup Information
File: /home/ahmet/backup/backup-arch-2026-01-16-153045.bread

System Information:
  Hostname: ahmet-laptop
  Kernel: 6.18.5-2-cachyos
  Backup Type: full
  Date: 2026-01-16T15:30:45.123456
  Compression: zstd

Components:
  packages:
    total_count: 1234
    explicit_count: 456
    aur_count: 89
    official_count: 1145

  user_config:
    total_files: 2567
    total_size_bytes: 47185920
    skipped_files: 342
    archive_path: user-config/user-config.tar
```

### Backup'ı Doğrulayın

Backup dosyasının bozulmadığını kontrol edin:

```bash
bread-backup verify ~/backup/backup-arch-2026-01-16-153045.bread
```

**Çıktı (Başarılı):**
```
🍞 Verifying Backup
File: /home/ahmet/backup/backup-arch-2026-01-16-153045.bread

✓ Backup is valid
```

**Çıktı (Başarısız):**
```
✗ Backup is corrupted
Error: manifest.json not found in archive
```

---

## Yeni Sisteme Restore Etme

### Ön Hazırlık: Fresh Arch Linux Kurulumu

Bu adımlar, yeni bir laptop/PC'ye Arch Linux kurduktan sonra yapılır.

#### 1. Minimal Sistem Kurulumu

```bash
# Arch Linux ISO'dan boot ettiniz
# Disk bölümleme, pacstrap, chroot vb. yaptınız
# Yeni sistem açıldı ve network çalışıyor
```

#### 2. Gerekli Araçları Kurun

```bash
# Base development tools
sudo pacman -S base-devel git

# Python ve bağımlılıklar
sudo pacman -S python python-pip python-click python-rich python-yaml
```

#### 3. Bread-Backup'ı Kurun

```bash
cd /tmp
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup
pipx install -e .
```

### Backup Dosyasını Yeni Sisteme Aktarın

Birkaç yöntem var:

#### Yöntem 1: USB/Harici Disk

```bash
# USB'yi takın ve mount edin
sudo mount /dev/sdb1 /mnt/usb

# Backup'ı kopyalayın
cp /mnt/usb/backups/backup-arch-2026-01-16.bread /tmp/

# USB'yi çıkarın
sudo umount /mnt/usb
```

#### Yöntem 2: Network (SCP)

```bash
# Eski bilgisayardan yeni bilgisayara
scp ~/backup/backup-arch-2026-01-16.bread username@newlaptop:/tmp/
```

#### Yöntem 3: Cloud (Manuel - Gelecekte Otomatik Olacak)

```bash
# Google Drive, Dropbox vb. kullanarak indirin
```

### Restore İşlemi

#### Adım 1: Backup'ı Doğrulayın

```bash
bread-backup verify /tmp/backup-arch-2026-01-16.bread
```

#### Adım 2: Backup Bilgilerini İnceleyin

```bash
bread-backup info /tmp/backup-arch-2026-01-16.bread
```

Özellikle şunlara bakın:
- Kaç paket yüklenecek?
- Toplam boyut ne kadar?
- Yeterli disk alanınız var mı?

#### Adım 3: Test Modu (Dry-Run) - Opsiyonel ama Önerilen

Hiçbir şey kurmadan ne yapacağını görün:

```bash
bread-backup restore /tmp/backup-arch-2026-01-16.bread --dry-run
```

**Çıktı:**
```
🍞 Bread-Backup Restore
Backup file: /tmp/backup-arch-2026-01-16.bread
DRY RUN MODE - No changes will be made

Starting Restore Process

Extracting backup...
✓ Backup extracted to /tmp/bread-restore-xyz

Backup Information:
  Backup ID: a3f5c9d2-...
  Type: full
  Created: 2026-01-16T15:30:45
  Hostname: oldlaptop
  Kernel: 6.18.5-2-cachyos
  Compression: zstd

Restoring packages...
DRY RUN - Would install:
  - base
  - linux
  - python
  - firefox
  - discord
  ... and 451 more

✓ Restore completed successfully!
```

#### Adım 4: Gerçek Restore (Tam)

⚠️ **DİKKAT:** Bu işlem sisteminizi değiştirecek! Devam etmeden önce emin olun.

```bash
# Tam restore (paketler + config)
sudo bread-backup restore /tmp/backup-arch-2026-01-16.bread
```

**İşlem Sırası:**

1. **Backup Çıkarılıyor**
```
Extracting backup...
✓ Backup extracted
```

2. **Paketler Yükleniyor**
```
Restoring packages...
Updating package database...

Installing 456 official packages...
[████████████████████░░░░░░░] 456/456
✓ Official packages installed
```

3. **AUR Paketleri Yükleniyor**

⚠️ **ÖNEMLİ:** İlk kez restore ediyorsanız, AUR helper (yay/paru) olmayabilir.

**Eğer bu uyarıyı alırsanız:**
```
Warning: AUR helper 'yay' not found. Skipping AUR packages.
Install yay first, then restore again with --packages-only
```

**Çözüm:**
```bash
# Önce yay'ı manuel kurun
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si

# Sonra sadece AUR paketlerini restore edin
sudo bread-backup restore /tmp/backup-arch-2026-01-16.bread --packages-only
```

4. **Konfigürasyon Dosyaları Geri Yükleniyor**
```
Restoring configuration files...
Extracting files...
Extracted 2567 files
Restoring file permissions...
✓ Configuration restored
```

5. **Tamamlandı!**
```
✓ Restore completed successfully!

Package Restore Summary:
  Official packages: 456
  AUR packages: 89

Config Restore Summary:
  Files restored: 2567
```

#### Adım 5: Post-Restore İşlemler

```bash
# Sistemi güncelleyin (opsiyonel)
sudo pacman -Syu

# Reboot önerilir
sudo reboot
```

### Kısmi Restore Seçenekleri

#### Sadece Paketleri Restore Et

```bash
sudo bread-backup restore backup.bread --packages-only
```

Kullanım senaryoları:
- Sadece yazılımları geri yüklemek istiyorsunuz
- Config dosyalarını manuel ayarlamak istiyorsunuz

#### Sadece Config'leri Restore Et

```bash
bread-backup restore backup.bread --config-only
```

⚠️ **NOT:** Config restore için sudo gerekmez (kendi kullanıcınızın dosyaları).

Kullanım senaryoları:
- Paketler zaten kurulu
- Sadece ayarları geri yüklemek istiyorsunuz

---

## Sık Sorulan Sorular

### 1. Backup ne kadar sürer?

**Cevap:** Sistemin büyüklüğüne bağlı:
- Küçük sistem (500 paket, az config): ~2 dakika
- Orta sistem (1000 paket, orta config): ~5 dakika
- Büyük sistem (2000+ paket, çok config): ~10-15 dakika

Config dosyalarının sayısı ve büyüklüğü süreyi etkiler.

### 2. Backup dosyası ne kadar yer kaplar?

**Cevap:** Tipik olarak:
- Paket listesi: ~50-100 KB (sadece metin)
- Config dosyaları (sıkıştırılmış): 50-200 MB
- **Toplam:** 50-200 MB

Not: Kullanıcı verisi (home directory) dahil DEĞİL (henüz).

### 3. Backup'ı farklı Arch dağıtımında kullanabilir miyim?

**Cevap:** Evet, ama dikkatli olun:
- ✅ Arch → Arch: Sorunsuz
- ✅ Arch → Manjaro: Çoğunlukla çalışır
- ✅ Arch → EndeavourOS: Çalışır
- ⚠️ Arch → Artix: Systemd yoksa sorun olabilir
- ❌ Arch → Ubuntu/Debian: Çalışmaz (pacman yok)

### 4. Eski backup'ları otomatik silebilir miyim?

**Cevap:** Şu an manuel yapmalısınız:

```bash
# Eski backup'ları listele
bread-backup list --destination ~/backup --sort-by date

# Manuel sil
rm ~/backup/backup-old-file.bread
```

Gelecek versiyonda otomatik cleanup eklenecek:
```bash
# Gelecekte (Faz 2)
bread-backup backup --keep-last 7
```

### 5. Backup'ı şifreleyebilir miyim?

**Cevap:** Henüz dahili destek yok, ama manuel yapabilirsiniz:

```bash
# Backup al
bread-backup backup --destination /tmp

# GPG ile şifrele
gpg -c /tmp/backup-arch-2026.bread

# Şifreli dosya: backup-arch-2026.bread.gpg

# Şifreyi çöz (restore öncesi)
gpg -d backup-arch-2026.bread.gpg > backup-arch-2026.bread
```

Faz 4'te otomatik şifreleme gelecek.

### 6. Incremental backup var mı?

**Cevap:** Henüz yok, Faz 2'de eklenecek.

Şu an her backup tam backup (full). Günlük backup alırsanız:
- backup-2026-01-14.bread (125 MB)
- backup-2026-01-15.bread (126 MB)
- backup-2026-01-16.bread (128 MB)

Her biri tam yedek. Incremental gelince:
- backup-full-001.bread (125 MB)
- backup-incr-002.bread (5 MB, sadece değişenler)
- backup-incr-003.bread (3 MB)

### 7. Cloud backup nasıl çalışıyor?

**Cevap:** Henüz otomatik cloud backup yok (Faz 3).

Şu an manuel:
```bash
# Backup al
bread-backup backup --destination ~/backup

# Manuel upload et
rclone copy ~/backup/backup-arch.bread gdrive:backups/
```

Faz 3'te otomatik:
```bash
bread-backup backup --storage gdrive
```

### 8. Farklı kullanıcı adında restore edebilir miyim?

**Cevap:** Evet ama manuel düzeltme gerekebilir:

```bash
# Eski sistem: /home/ahmet
# Yeni sistem: /home/mehmet

# Restore sonrası dosyaları taşı
sudo mv /home/ahmet/.config /home/mehmet/
sudo chown -R mehmet:mehmet /home/mehmet/.config
```

Gelecekte kullanıcı adı mapping özelliği eklenebilir.

---

## Sorun Giderme

### Sorun 1: "pacman not found"

**Hata:**
```
RuntimeError: pacman not found. Is this an Arch Linux system?
```

**Çözüm:** Bread-Backup sadece Arch Linux için çalışır. Başka dağıtımda kullanamazsınız.

---

### Sorun 2: "No module named 'click'"

**Hata:**
```
ModuleNotFoundError: No module named 'click'
```

**Çözüm:**
```bash
sudo pacman -S python-click python-rich python-yaml
```

---

### Sorun 3: Backup çok büyük

**Sorun:** Backup 5GB+ oluyor, çok yer kaplıyor.

**Çözüm:** Exclude pattern kullanın:

```bash
# Exclude dosyası oluştur
cat > ~/my-excludes.txt <<EOF
**/Downloads/
**/Videos/
**/Music/
**/.cache/
**/node_modules/
**/.venv/
EOF

# Exclude ile backup al
bread-backup backup --exclude-file ~/my-excludes.txt --destination ~/backup
```

---

### Sorun 4: "target not found: some-package"

**Hata:**
```
error: target not found: some-old-package
```

**Neden:** Paket repo'dan kaldırılmış veya yeniden adlandırılmış.

**Çözüm 1:** Package listesini düzenle:
```bash
# Backup'ı extract et
mkdir /tmp/fix-backup
cd /tmp/fix-backup
tar -xf ~/backup/backup-arch.bread

# Package listesini düzenle
nano packages/pacman-explicit.txt
# Problematik satırı sil veya # ile yorum yap

# Yeniden paketie
tar -czf backup-arch-fixed.bread *

# Fixed backup'ı kullan
sudo bread-backup restore backup-arch-fixed.bread
```

**Çözüm 2:** Manuel devam et:
```bash
# Restore ederken hata olsa da devam et
# Sonra eksik paketi manuel kur
sudo pacman -S alternative-package
```

---

### Sorun 5: AUR paketleri kurulmuyor

**Hata:**
```
Warning: AUR helper 'yay' not found. Skipping AUR packages.
```

**Çözüm:**
```bash
# yay'ı kur
sudo pacman -S --needed base-devel git
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si

# Sonra tekrar restore et
sudo bread-backup restore backup.bread --packages-only
```

---

### Sorun 6: Disk doldu

**Hata:**
```
error: Partition / is full
error: failed to commit transaction (not enough free disk space)
```

**Çözüm:**
```bash
# Pacman cache'i temizle
sudo pacman -Sc

# Gereksiz paketleri kaldır
sudo pacman -Rns $(pacman -Qtdq)

# Yer kontrol et
df -h /

# Tekrar dene
sudo bread-backup restore backup.bread
```

---

### Sorun 7: Permission denied (config restore)

**Hata:**
```
PermissionError: [Errno 13] Permission denied: '/home/user/.config/...'
```

**Çözüm:** Config restore için sudo kullanmayın:
```bash
# YANLIŞ
sudo bread-backup restore backup.bread --config-only

# DOĞRU
bread-backup restore backup.bread --config-only
```

Config dosyaları kullanıcıya aittir, root'a değil.

---

### Sorun 8: Restore sonrası program açılmıyor

**Sorun:** Restore ettiniz ama bazı programlar çalışmıyor.

**Olası nedenler:**
1. Bağımlılıklar eksik
2. Cache temizlenmeli
3. Reboot gerekli

**Çözüm:**
```bash
# Eksik bağımlılıkları kur
sudo pacman -S --needed $(pacman -Qq)

# Font cache güncelle
fc-cache -fv

# Icon cache güncelle
gtk-update-icon-cache

# Reboot et
sudo reboot
```

---

### Sorun 9: Backup verify başarısız

**Hata:**
```
✗ Backup is corrupted
```

**Neden:** Dosya transfer sırasında bozulmuş olabilir.

**Çözüm:**
```bash
# Backup'ı tekrar kopyalayın
# Checksum kontrol edin
sha256sum backup.bread

# USB/Network transfer tekrar deneyin
```

---

### Sorun 10: Çok uzun sürüyor

**Sorun:** Restore 1 saatten uzun sürüyor.

**Olası nedenler:**
- Çok fazla AUR paketi var (derleme gerekiyor)
- Yavaş internet bağlantısı
- Eski mirror kullanılıyor

**Çözüm:**
```bash
# Hızlı mirror seç
sudo pacman-mirrors --fasttrack

# Veya manuel mirror ekle
sudo nano /etc/pacman.d/mirrorlist

# Parallel download aktif et
sudo nano /etc/pacman.conf
# ParallelDownloads = 5 satırını ekle

# Tekrar dene
sudo bread-backup restore backup.bread
```

---

## Gelişmiş Kullanım

### Otomatik Günlük Backup (Cron)

```bash
# Crontab düzenle
crontab -e

# Her gece saat 2'de backup al
0 2 * * * bread-backup backup --destination /backup --no-user-data

# Haftalık tam backup
0 2 * * 0 bread-backup backup --destination /backup
```

### Backup Script Oluşturma

```bash
#!/bin/bash
# ~/bin/my-backup.sh

BACKUP_DIR="/backup"
DATE=$(date +%Y-%m-%d)

echo "Starting backup: $DATE"

bread-backup backup \
    --destination "$BACKUP_DIR" \
    --exclude-file ~/.config/bread-backup/excludes.txt \
    --verbose

# Eski backup'ları temizle (7 günden eski)
find "$BACKUP_DIR" -name "backup-*.bread" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x ~/bin/my-backup.sh
~/bin/my-backup.sh
```

---

## Destek ve Katkı

### Hata Bildirimi

GitHub Issues: https://github.com/ahwetekm/bread-backup/issues

### Dokümantasyon

- README.md - Genel bakış
- KULLANIM.md - Bu kılavuz (Türkçe)
- Plan: `/home/ahmet/.claude/plans/hidden-jingling-emerson.md`

### Katkıda Bulunma

```bash
# Fork & Clone
git clone https://github.com/yourfork/bread-backup
cd bread-backup

# Branch oluştur
git checkout -b yeni-ozellik

# Değişiklik yap, commit at
git commit -m "Yeni özellik eklendi"

# Push & Pull Request
git push origin yeni-ozellik
```

---

## Sürüm Geçmişi

### v0.1.0 (Şu An - MVP)
- ✅ Paket backup/restore
- ✅ Config backup/restore
- ✅ Local storage
- ✅ CLI interface

### v0.2.0 (Planlanan)
- ⏳ Incremental backup
- ⏳ Sistem config (/etc) backup
- ⏳ User data (/home) backup
- ⏳ Progress bars

### v0.3.0 (Planlanan)
- ⏳ USB storage
- ⏳ Cloud storage (GDrive, Dropbox, S3)
- ⏳ Encryption (GPG/Age)

### v1.0.0 (Planlanan)
- ⏳ Systemd timer
- ⏳ Web UI (opsiyonel)
- ⏳ Automatic cleanup

---

## Lisans

MIT License - Özgürce kullanabilirsiniz!

---

**Made with ❤️ for Arch Linux users**

Herhangi bir sorunuz varsa: https://github.com/ahwetekm/bread-backup/discussions
