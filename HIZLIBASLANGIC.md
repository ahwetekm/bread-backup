# Hızlı Başlangıç Kılavuzu 🚀

Bread-Backup ile 5 dakikada başlayın!

## Ön Gereksinimler

- Arch Linux (veya Arch tabanlı dağıtım)
- Python 3.10+
- İnternet bağlantısı

## Kurulum (2 dakika)

```bash
# Bağımlılıkları kurun
sudo pacman -S python-click python-rich python-yaml git

# Klonlayın ve kurun
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup
pip install --user -e .

# PATH'e ekleyin (gerekirse)
export PATH="$HOME/.local/bin:$PATH"

# Kurulumu doğrulayın
bread-backup --version
```

## İlk Backup'ınız (2 dakika)

```bash
# Bir backup oluşturun
bread-backup backup --destination ~/yedeklerim

# Bu kadar! Backup'ınız hazır.
```

**Ne yedeklendi?**
- ✅ Tüm kurulu paketler (pacman + AUR)
- ✅ Konfigürasyon dosyalarınız (~/.config)
- ✅ Dosya izinleri ve symlink'ler

**Backup dosyası konumu:**
```
~/yedeklerim/backup-makineadi-2026-01-16-153045.bread
```

## Yeni Makinede Geri Yükleme (3 dakika)

```bash
# 1. Temiz Arch Linux kurulumu tamamlandı
# 2. Bread-Backup'ı kurun (yukarıdaki gibi)

# 3. Backup dosyasını kopyalayın
cp /mnt/usb/backup-*.bread /tmp/

# 4. Backup'ı doğrulayın (opsiyonel ama önerilen)
bread-backup verify /tmp/backup-*.bread

# 5. Her şeyi geri yükleyin
sudo bread-backup restore /tmp/backup-*.bread

# 6. AUR helper kurulumu gerekirse
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si

# 7. AUR paketlerini geri yükleyin
sudo bread-backup restore /tmp/backup-*.bread --packages-only

# 8. Yeniden başlatın
sudo reboot
```

## Yaygın Komutlar

```bash
# Tüm backup'ları listele
bread-backup list --destination ~/yedeklerim

# Backup detaylarını görüntüle
bread-backup info backup-dosyasi.bread

# Backup bütünlüğünü doğrula
bread-backup verify backup-dosyasi.bread

# Test restore (değişiklik yapmaz)
bread-backup restore backup-dosyasi.bread --dry-run

# Sadece paketleri geri yükle
sudo bread-backup restore backup-dosyasi.bread --packages-only

# Sadece konfigürasyonları geri yükle
bread-backup restore backup-dosyasi.bread --config-only
```

## İpuçları

1. **Düzenli backup**: Sisteminizi haftalık yedekleyin
2. **Backup'larınızı test edin**: Ara sıra `--verify` ile kontrol edin
3. **Çoklu kopya**: Backup'ları farklı yerlerde saklayın (USB + Cloud)
4. **Gereksiz dosyaları hariç tutun**: Büyük cache dizinleri için `--exclude-file` kullanın

## Yardım mı Lazım?

- 📖 Tam dokümantasyon: [KULLANIM.md](KULLANIM.md) (Türkçe)
- 📖 İngilizce versiyon: [README.md](README.md)
- 🐛 Hata bildirin: [GitHub Issues](https://github.com/ahwetekm/bread-backup/issues)
- 💬 Soru sorun: [GitHub Discussions](https://github.com/ahwetekm/bread-backup/discussions)

## Örnek İş Akışı

```bash
# Gün 1: Kurulum
cd ~/Projects
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup
pip install --user -e .
export PATH="$HOME/.local/bin:$PATH"

# Gün 1: İlk backup
bread-backup backup --destination /backup

# Gün 7: Haftalık backup
bread-backup backup --destination /backup

# Gün 30: Felaket! Laptop çalındı
# Yeni laptop alın, Arch kurun

# Gün 30: Her şeyi geri yükleyin
sudo bread-backup restore /backup/backup-eski-laptop.bread
sudo reboot

# Gün 30: İşe geri dönün! 🎉
```

---

**Sisteminizi yedekleyin. Huzurunuzu geri yükleyin.** 🍞
