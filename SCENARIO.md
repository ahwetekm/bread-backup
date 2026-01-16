# Gerçek Dünya Senaryoları 🌍

Bread-Backup'ın gerçek hayatta nasıl kullanıldığını gösteren senaryolar.

---

## Senaryo 1: Yeni Laptop Satın Alma 💻

### Durum
Ahmet yeni bir laptop satın aldı ve eski laptop'taki sistemini birebir taşımak istiyor.

### Eski Laptop (Kaynak)

**Sistem Bilgileri:**
- Hostname: ahmet-thinkpad
- 1,250 kurulu paket
- 89 AUR paketi (VS Code, Spotify, Discord, vb.)
- Özelleştirilmiş Neovim, Kitty, i3wm konfigürasyonu

**Adım 1: Backup Al**
```bash
# USB disk tak
sudo mount /dev/sdb1 /mnt/usb

# Backup oluştur
bread-backup backup --destination /mnt/usb/backups --verbose

# Çıktı:
# Collecting packages...
# Found 1250 packages
#   Explicit packages: 487
#   AUR packages: 89
#
# Collecting configuration files...
# Found 3,245 files (156.7 MB)
#
# ✓ Backup created: /mnt/usb/backups/backup-ahmet-thinkpad-2026-01-16.bread
# Size: 178.3 MB
```

**Adım 2: Backup'ı Doğrula**
```bash
bread-backup verify /mnt/usb/backups/backup-ahmet-thinkpad-2026-01-16.bread

# ✓ Backup is valid
```

**Adım 3: USB'yi Güvenle Çıkar**
```bash
sudo umount /mnt/usb
# USB'yi çıkar
```

### Yeni Laptop (Hedef)

**Adım 1: Arch Linux Kurulumu**
```bash
# Minimal Arch kurulumu yap
# Base system + network
```

**Adım 2: Bread-Backup Kurulumu**
```bash
sudo pacman -S python-click python-rich python-yaml git base-devel

git clone https://github.com/yourusername/bread-backup.git
cd bread-backup
sudo pip install -e .
```

**Adım 3: Backup'ı Kopyala**
```bash
sudo mount /dev/sdb1 /mnt/usb
cp /mnt/usb/backups/backup-ahmet-thinkpad-2026-01-16.bread /tmp/
sudo umount /mnt/usb
```

**Adım 4: Dry-Run Test**
```bash
bread-backup restore /tmp/backup-ahmet-thinkpad-2026-01-16.bread --dry-run

# DRY RUN - Would install 487 packages
# DRY RUN - Would restore 3,245 config files
```

**Adım 5: Gerçek Restore**
```bash
# Paketleri restore et
sudo bread-backup restore /tmp/backup-ahmet-thinkpad-2026-01-16.bread

# AUR helper kur
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si

# AUR paketlerini restore et
sudo bread-backup restore /tmp/backup-ahmet-thinkpad-2026-01-16.bread --packages-only
```

**Adım 6: Reboot ve Test**
```bash
sudo reboot

# Açıldıktan sonra:
# ✅ i3wm açıldı
# ✅ Kitty terminal aynı görünüm
# ✅ Neovim tüm pluginlerle açıldı
# ✅ VS Code ayarları geldi
# ✅ Spotify login bilgileri kayıtlı
```

**Sonuç:** 🎉
- Toplam süre: ~45 dakika
- Manuel kurulum yerine otomatik restore
- Hiçbir ayar kaybı yok

---

## Senaryo 2: Sistem Bozulması ve Kurtarma 🔧

### Durum
Mehmet sistem güncellemesi yaparken elektrik kesildi. Sistem boot olmuyor.

### Bozulma Öncesi (1 Gün Önce)

**Otomatik Günlük Backup (Cron)**
```bash
# Crontab'da kayıtlı
0 2 * * * bread-backup backup --destination /backup
```

**Mevcut Backup:**
```
/backup/backup-mehmet-pc-2026-01-15-020000.bread
```

### Bozulma Sonrası

**Adım 1: Live USB ile Boot**
```bash
# Arch ISO'dan boot et
```

**Adım 2: Diski Mount Et**
```bash
mount /dev/sda2 /mnt
mount /dev/sda1 /mnt/boot
```

**Adım 3: Backup'a Eriş**
```bash
ls /mnt/backup/
# backup-mehmet-pc-2026-01-15-020000.bread
```

**Seçenek A: Hızlı Düzeltme (Sadece Sistem Paketlerini Geri Yükle)**
```bash
# Chroot yap
arch-chroot /mnt

# Bread-backup zaten kurulu
cd /backup

# Sadece kritik paketleri restore et
bread-backup restore backup-mehmet-pc-2026-01-15-020000.bread --packages-only --dry-run

# Gerçekten restore et
bread-backup restore backup-mehmet-pc-2026-01-15-020000.bread --packages-only

# Kernel yeniden oluştur
mkinitcpio -P

# Reboot
exit
reboot
```

**Seçenek B: Tam Yeniden Kurulum**
```bash
# Partition'ları formatla
mkfs.ext4 /dev/sda2

# Base system kur
pacstrap /mnt base linux linux-firmware

# Bread-backup kur
arch-chroot /mnt
pacman -S python-click python-rich python-yaml git
git clone https://github.com/yourusername/bread-backup.git
cd bread-backup && pip install -e .

# Backup'ı kopyala
cp /backup/backup-mehmet-pc.bread /tmp/

# Full restore
bread-backup restore /tmp/backup-mehmet-pc.bread

# Bootloader kur
grub-install /dev/sda
grub-mkconfig -o /boot/grub/grub.cfg

# Reboot
exit
reboot
```

**Sonuç:** 🎉
- Sistem kurtarıldı
- Son backup'tan sadece 1 gün veri kaybı
- Günlük otomatik backup hayat kurtardı

---

## Senaryo 3: Geliştirme Ortamı Replikasyonu 👨‍💻

### Durum
Bir yazılım şirketinde çalışan Ayşe, ekip arkadaşı Burak'ın geliştirme ortamını birebir kopyalamak istiyor.

### Burak'ın Sistemi

**Kurulu Araçlar:**
- Docker
- Node.js (nvm ile çoklu versiyon)
- Python (pyenv ile 3.10, 3.11, 3.12)
- PostgreSQL
- Redis
- VS Code (uzantılar ve ayarlar)
- Neovim (LSP, DAP, Telescope)

**Adım 1: Backup Al (Burak)**
```bash
# Geliştirme araçlarını backup'a dahil et
bread-backup backup --destination ~/backups --verbose

# ~/.config/nvim
# ~/.config/Code/User/settings.json
# ~/.nvm
# ~/.pyenv
```

**Adım 2: Backup'ı Paylaş**
```bash
# Şirket NAS'ına kopyala
cp ~/backups/backup-burak-dev.bread /mnt/nas/team-backups/
```

### Ayşe'nin Sistemi

**Adım 1: Backup'ı İndir**
```bash
cp /mnt/nas/team-backups/backup-burak-dev.bread /tmp/
```

**Adım 2: Sadece Config'leri Al**
```bash
# Sadece konfigürasyon dosyalarını restore et
# (Paketleri zaten kendisi yükleyecek)
bread-backup restore /tmp/backup-burak-dev.bread --config-only
```

**Adım 3: Paket Listesini İncele**
```bash
# Hangi paketler var görmek için
bread-backup info /tmp/backup-burak-dev.bread

# Çıktı:
# Packages:
#   docker
#   nodejs
#   npm
#   postgresql
#   redis
#   ...
```

**Adım 4: Gerekli Paketleri Seçerek Kur**
```bash
# Sadece ihtiyacı olanları kur
sudo pacman -S docker nodejs postgresql redis
```

**Sonuç:** 🎉
- Ayşe, Burak'ın geliştirme ortamını 30 dakikada kurdu
- VS Code ayarları birebir aynı
- Neovim pluginleri ve kısayolları hazır
- Manuel setup yerine otomatik

---

## Senaryo 4: Çoklu Cihaz Senkronizasyonu 🔄

### Durum
Zeynep hem masaüstü hem laptop kullanıyor. İkisini de senkron tutmak istiyor.

### Masaüstü (Ana Sistem)

**Haftalık Backup**
```bash
# Her Pazar backup al
# Crontab:
0 2 * * 0 bread-backup backup --destination /backup

# Backup listesi:
bread-backup list --destination /backup

# backup-desktop-2026-01-05.bread
# backup-desktop-2026-01-12.bread
# backup-desktop-2026-01-19.bread (en güncel)
```

### Laptop (İkincil Sistem)

**Adım 1: En Son Backup'ı Kopyala**
```bash
# Network üzerinden kopyala
scp zeynep@desktop:/backup/backup-desktop-2026-01-19.bread /tmp/
```

**Adım 2: Sadece Eksik Paketleri Kur**
```bash
# Backup'taki paket listesini çıkar
mkdir /tmp/extract
cd /tmp/extract
tar -xf /tmp/backup-desktop-2026-01-19.bread

# Paket listesini oku
cat packages/pacman-explicit.txt

# Laptop'ta olmayan paketleri bul
comm -23 \
  <(cat packages/pacman-explicit.txt | sort) \
  <(pacman -Qe | awk '{print $1}' | sort) \
  > missing-packages.txt

# Eksik paketleri kur
sudo pacman -S $(cat missing-packages.txt)
```

**Adım 3: Config'leri Senkronize Et**
```bash
# Config'leri güncelle
bread-backup restore /tmp/backup-desktop-2026-01-19.bread --config-only
```

**Sonuç:** 🎉
- Masaüstü ve laptop artık senkron
- Yeni paketler iki tarafta da var
- Ayarlar birebir aynı

---

## Senaryo 5: Distro Değiştirme 🔀

### Durum
Can, Arch Linux'tan Manjaro'ya geçmek istiyor ama ayarlarını kaybetmek istemiyor.

### Arch Linux (Mevcut)

**Adım 1: Full Backup**
```bash
bread-backup backup --destination /home/can/backup
```

### Manjaro (Yeni)

**Adım 2: Manjaro Kurulumu**
```bash
# Manjaro ISO'dan kur
# Masaüstü ortamını seç (KDE, XFCE, vb.)
```

**Adım 3: Bread-Backup Kur**
```bash
sudo pacman -S python-click python-rich python-yaml git
git clone https://github.com/yourusername/bread-backup.git
cd bread-backup && sudo pip install -e .
```

**Adım 4: Backup'ı Kopyala**
```bash
cp /run/media/can/USB/backup-arch-can.bread /tmp/
```

**Adım 5: Selective Restore**

⚠️ **DİKKAT:** Manjaro'da bazı paketler farklı adlandırılmış olabilir.

```bash
# Önce paket listesini incele
bread-backup info /tmp/backup-arch-can.bread

# Sadece config'leri restore et
bread-backup restore /tmp/backup-arch-can.bread --config-only

# Paket listesini manuel gözden geçir
mkdir /tmp/extract
cd /tmp/extract
tar -xf /tmp/backup-arch-can.bread
cat packages/pacman-explicit.txt

# İstediğin paketleri tek tek kur
sudo pacman -S firefox discord spotify ...
```

**Sonuç:** 🎉
- Config dosyaları Manjaro'ya taşındı
- Özelleştirilmiş terminal, editor ayarları korundu
- Paketler manuel seçilerek kuruldu

---

## Senaryo 6: Güvenli Deneyler 🧪

### Durum
Ali, sistemiyle deney yapmak istiyor ama geri dönüş noktası olsun istiyor.

### Deney Öncesi

**Snapshot Al**
```bash
# Hızlı backup (config dahil değil, sadece paketler)
bread-backup backup --no-config --destination /backup/experiments

# backup-before-experiment.bread oluştu
```

### Deney Sırasında

**Tehlikeli İşlemler**
```bash
# Experimental paketler kur
yay -S experimental-driver-git

# Sistem ayarlarını değiştir
sudo nano /etc/X11/xorg.conf

# Kernel parametreleri değiştir
sudo nano /etc/default/grub
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

**Sonuç:** ❌ Sistem boot olmuyor!

### Geri Dönüş

**Adım 1: Live USB Boot**
```bash
# Arch ISO'dan boot et
```

**Adım 2: Chroot**
```bash
mount /dev/sda2 /mnt
arch-chroot /mnt
```

**Adım 3: Restore**
```bash
cd /backup/experiments
bread-backup restore backup-before-experiment.bread --packages-only

# Experimental paketi kaldır
pacman -R experimental-driver-git

# Grub'ı düzelt
grub-mkconfig -o /boot/grub/grub.cfg
```

**Adım 4: Reboot**
```bash
exit
reboot
```

**Sonuç:** 🎉
- Sistem eski haline döndü
- Experimental değişiklikler geri alındı
- Güvenli deney ortamı sağlandı

---

## Senaryo 7: Şirket Standart Kurulum 🏢

### Durum
Bir yazılım şirketi, yeni işe başlayan geliştiriciler için standart bir Arch Linux kurulumu hazırlamak istiyor.

### Ana Template Hazırlama

**Sistem Yöneticisi (Admin)**
```bash
# "Golden image" sistemi kur
# Tüm geliştirme araçlarını kur:
sudo pacman -S \
  docker docker-compose \
  git git-lfs \
  nodejs npm \
  python python-pip python-virtualenv \
  postgresql redis \
  code vim neovim \
  tmux htop

# AUR araçları
yay -S \
  google-chrome \
  slack-desktop \
  postman-bin

# Şirket standart config'lerini hazırla
cp /company/configs/.gitconfig ~/
cp -r /company/configs/nvim ~/.config/
cp -r /company/configs/vscode ~/.config/Code/

# Template backup al
bread-backup backup --destination /company/templates

# Template adını değiştir
mv /company/templates/backup-*.bread \
   /company/templates/company-dev-environment-v1.0.bread
```

### Yeni Çalışan Kurulumu

**Yeni Geliştirici**
```bash
# 1. Fresh Arch kur
# 2. Bread-backup kur
sudo pacman -S python-click python-rich python-yaml git
git clone https://github.com/company/bread-backup.git
cd bread-backup && sudo pip install -e .

# 3. Şirket template'ini indir
cp /mnt/nas/templates/company-dev-environment-v1.0.bread /tmp/

# 4. Full restore
sudo bread-backup restore /tmp/company-dev-environment-v1.0.bread

# 5. AUR helper kur
cd /tmp && git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si

# 6. AUR paketlerini restore et
sudo bread-backup restore /tmp/company-dev-environment-v1.0.bread --packages-only

# 7. Kişisel ayarları yap
git config user.name "Yeni Çalışan"
git config user.email "yeni@company.com"
```

**Sonuç:** 🎉
- Yeni çalışan 1 saatte hazır
- Tüm araçlar standart şekilde kurulu
- Manuel setup hataları yok
- Takım üyeleri aynı ortamda çalışıyor

---

## Özet: Senaryoları Karşılaştırma

| Senaryo | Kullanım | Süre | Zorluk |
|---------|----------|------|--------|
| 1. Yeni Laptop | Full sistem taşıma | 45 dk | ⭐⭐ |
| 2. Sistem Kurtarma | Bozulan sistemi düzelt | 30 dk | ⭐⭐⭐ |
| 3. Geliştirme Replikasyonu | Config paylaşımı | 15 dk | ⭐ |
| 4. Çoklu Cihaz Sync | İki bilgisayarı senkronla | 20 dk | ⭐⭐ |
| 5. Distro Değiştirme | Arch → Manjaro | 40 dk | ⭐⭐⭐ |
| 6. Güvenli Deneyler | Snapshot & rollback | 10 dk | ⭐ |
| 7. Şirket Standart | Template kurulum | 60 dk | ⭐⭐ |

---

## İpuçları

1. **Düzenli backup alın** - Günlük/haftalık otomatik backup
2. **Backup'ları test edin** - `--dry-run` ile test edin
3. **Çoklu kopya tutun** - Lokal + USB + Cloud
4. **Template'ler oluşturun** - Yaygın senaryolar için hazır backup'lar
5. **Dokümante edin** - Hangi backup ne içeriyor not alın

---

**Daha fazla senaryo eklemek için katkıda bulunun!** 🚀
