# Kurulum Talimatları 🔧

Bread-Backup'ı sisteminize kurmak için detaylı adımlar.

## Sistem Gereksinimleri

### İşletim Sistemi
- ✅ Arch Linux
- ✅ Manjaro
- ✅ EndeavourOS
- ✅ Artix Linux
- ✅ Diğer Arch tabanlı dağıtımlar
- ❌ Ubuntu/Debian (pacman gerektirir)
- ❌ Fedora/RHEL (pacman gerektirir)

### Python Versiyonu
- **Minimum:** Python 3.10
- **Önerilen:** Python 3.11 veya 3.12

Versiyonunuzu kontrol edin:
```bash
python --version
# Python 3.12.1
```

### Gerekli Bağımlılıklar

#### Python Paketleri
```bash
sudo pacman -S \
  python-click \
  python-rich \
  python-yaml
```

**Açıklama:**
- `python-click` - CLI framework (komut satırı)
- `python-rich` - Güzel terminal çıktısı (renkli, progress bar)
- `python-yaml` - YAML config dosyası okuma

#### Sistem Araçları
```bash
sudo pacman -S \
  git \
  base-devel
```

**Açıklama:**
- `git` - Projeyi klonlamak için
- `base-devel` - Geliştirme araçları (gcc, make, vb.)

#### Opsiyonel Bağımlılıklar

**AUR Paketleri için:**
```bash
# yay veya paru kurulu olmalı
yay --version || paru --version
```

Yoksa yay'ı kurun:
```bash
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

**Sıkıştırma Araçları:**
```bash
# Varsayılan (zaten kurulu olmalı)
sudo pacman -S gzip tar

# Önerilen (daha iyi sıkıştırma)
sudo pacman -S zstd

# Opsiyonel
sudo pacman -S xz lz4
```

---

## Kurulum Yöntemleri

### Yöntem 1: Pipx ile Kurulum (Önerilen) ⭐

Modern Arch Linux sistemlerinde (Python 3.11+) en iyi yöntem budur. Pipx, otomatik olarak izole bir virtual environment oluşturur.

```bash
# 1. Pipx'i kur
sudo pacman -S python-pipx git

# 2. Projeyi klonla
cd ~/Projects  # veya istediğiniz dizin
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup

# 3. Pipx ile kur (editable mode)
pipx install -e .

# 4. Shell'i yenile (özellikle fish shell için)
hash -r 2>/dev/null || fish_update_completions 2>/dev/null || true

# 5. Kurulumu test et
bread-backup --version
# bread-backup, version 0.1.0

# Eğer "command not found" hatası alırsanız:
# ~/.local/bin/bread-backup --version
# veya yeni bir terminal açın
```

**Avantajlar:**
- ✅ Modern ve temiz yaklaşım
- ✅ Otomatik virtual environment yönetimi
- ✅ Global olarak erişilebilir komut
- ✅ `externally-managed-environment` hatası yok
- ✅ Kolay güncelleme (`git pull && pipx reinstall bread-backup`)

**Dezavantajlar:**
- ⚠️ Proje dizinini silmemelisiniz

---

### Yöntem 2: Virtual Environment (İzole Ortam)

Tamamen izole bir ortamda kurulum. Geliştirme için idealdir.

```bash
# 1. Bağımlılıkları kur
sudo pacman -S python git

# 2. Projeyi klonla
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup

# 3. Virtual environment oluştur
python -m venv venv
source venv/bin/activate

# 4. Kur
pip install -e .

# 5. Test et
bread-backup --version

# Kullanım (her seferinde):
# source ~/bread-backup/venv/bin/activate
# bread-backup backup ...
```

**Avantajlar:**
- ✅ Tamamen izole
- ✅ Sistem temiz kalır
- ✅ Geliştirme için ideal

**Dezavantajlar:**
- ⚠️ Her kullanımda `source venv/bin/activate` gerekli
- ⚠️ Daha karmaşık

---

### Yöntem 3: Arch Sistem Paketleri ile (Geliştiriciler için)

**Not:** Bu yöntem artık önerilmiyor çünkü `externally-managed-environment` hatası verir. Ancak geliştirme ortamında kullanılabilir.

```bash
# 1. Sistem paketlerini kur
sudo pacman -S python-click python-rich python-yaml git

# 2. Projeyi klonla
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup

# 3. Virtual environment ile kur (zorunlu)
python -m venv venv
source venv/bin/activate
pip install -e .

# Test et
bread-backup --version
```

**Avantajlar:**
- ✅ Sistem paketleri kullanır
- ✅ Bağımlılıklar pacman ile yönetilir

**Dezavantajlar:**
- ⚠️ Yine de virtual environment gerekli
- ⚠️ Her kullanımda activate gerekli

---

### Yöntem 4: AUR Paketi (Gelecek)

Gelecekte AUR'da paket olarak yayınlanacak.

```bash
# Gelecekte:
yay -S bread-backup

# veya
paru -S bread-backup
```

**Şu an bu yöntem mevcut değil** (v1.0'da gelecek).

---

## Kurulum Sonrası Kontroller

### 1. Versiyon Kontrolü
```bash
bread-backup --version
```

Beklenen çıktı:
```
bread-backup, version 0.1.0
```

### 2. Yardım Menüsü
```bash
bread-backup --help
```

Beklenen çıktı:
```
Usage: bread-backup [OPTIONS] COMMAND [ARGS]...

  Bread-Backup: Comprehensive backup and restore tool for Arch Linux.

Commands:
  backup   Create a system backup.
  restore  Restore from a backup file.
  list     List available backups.
  verify   Verify backup integrity.
  info     Show detailed backup information.
```

### 3. Pacman Kontrolü
```bash
pacman --version
```

Çıktı görmelisiniz (Arch Linux'ta varsayılan olarak vardır).

### 4. Test Backup (Dry-Run)
```bash
# Hiçbir şey oluşturmadan test et
bread-backup backup --destination /tmp/test-backup --no-config --verbose
```

Hatasız çalışmalı ve paket sayısını göstermeli.

---

## Güncelleme

### Pipx Kurulum Güncelleme (Yöntem 1)

```bash
cd ~/Projects/bread-backup
git pull
pipx reinstall bread-backup
```

### Virtual Environment Güncelleme (Yöntem 2)

```bash
cd ~/Projects/bread-backup
git pull
source venv/bin/activate
pip install -e .
```

---

## Kaldırma

### Pipx Kurulumunu Kaldırma

```bash
# Paketi kaldır
pipx uninstall bread-backup

# Projeyi sil (opsiyonel)
rm -rf ~/Projects/bread-backup
```

### Virtual Environment Kurulumunu Kaldırma

```bash
# Projeyi sil (environment dahil)
rm -rf ~/Projects/bread-backup
```

---

## Sorun Giderme

### Sorun 1: "command not found: bread-backup"

**Neden:** PATH'de yok.

**Çözüm:**
```bash
# Hangi yöntemle kurdunuz?

# Yöntem 1 (sudo pip):
which bread-backup
# /usr/local/bin/bread-backup veya /usr/bin/bread-backup

# Yöntem 2 (pip --user):
echo $PATH | grep ".local/bin"
# Yoksa ekleyin:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Yöntem 3 (venv):
source ~/bread-backup/venv/bin/activate
```

---

### Sorun 2: "ModuleNotFoundError: No module named 'click'"

**Neden:** Bağımlılıklar kurulu değil.

**Çözüm:**
```bash
sudo pacman -S python-click python-rich python-yaml
```

---

### Sorun 3: "pip: command not found"

**Neden:** Python pip kurulu değil.

**Çözüm:**
```bash
sudo pacman -S python-pip
```

---

### Sorun 4: "Permission denied" veya "externally-managed-environment"

**Neden:** Python 3.11+ Arch Linux, sistem Python'una paket kurulmasını engelliyor (PEP 668).

**Çözüm 1 (Önerilen):** Pipx kullanın:
```bash
sudo pacman -S python-pipx
pipx install -e .
```

**Çözüm 2:** Virtual environment kullanın:
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

---

### Sorun 5: "command not found: bread-backup" (pipx kurulumundan sonra)

**Neden 1:** Shell cache güncel değil (özellikle fish shell)

**Çözüm 1:**
```bash
# Yeni terminal aç veya shell'i yenile
hash -r  # bash/zsh için
fish_update_completions  # fish için

# Direkt çalıştır
~/.local/bin/bread-backup --version
```

**Neden 2:** PATH'de `~/.local/bin` yok

**Çözüm 2:**
```bash
# Bash/Zsh için
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Fish için
fish_add_path ~/.local/bin
```

---

## Ek Yapılandırma

### Bash Completion (Gelecek)

```bash
# Gelecekte otomatik tamamlama için
bread-backup --install-completion bash
source ~/.bashrc
```

### Alias Oluşturma

```bash
# Kısa komutlar için
echo "alias bb='bread-backup'" >> ~/.bashrc
echo "alias bb-backup='bread-backup backup --destination /backup'" >> ~/.bashrc
source ~/.bashrc

# Kullanım:
bb --version
bb-backup
```

### Config Dosyası

Varsayılan ayarlar için:
```bash
mkdir -p ~/.config/bread-backup
cp configs/default_exclude.txt ~/.config/bread-backup/excludes.txt

# Özelleştir
nano ~/.config/bread-backup/excludes.txt
```

---

## Platform Notları

### Manjaro
```bash
# Pamac yerine pacman kullanın
sudo pacman -S python-click python-rich python-yaml
```

### EndeavourOS
```bash
# Standart Arch ile aynı
sudo pacman -S python-click python-rich python-yaml
```

### Artix Linux
```bash
# Systemd yoksa bazı özellikler çalışmayabilir
# Temel işlevler çalışır
sudo pacman -S python-click python-rich python-yaml
```

---

## Geliştirici Kurulumu

Projeye katkıda bulunmak istiyorsanız:

```bash
# 1. Fork & Clone
git clone https://github.com/yourfork/bread-backup.git
cd bread-backup

# 2. Dev bağımlılıkları
sudo pacman -S \
  python-click python-rich python-yaml \
  python-pytest python-black python-mypy

# Veya pip ile:
pip install -e ".[dev]"

# 3. Pre-commit hooks (opsiyonel)
pip install pre-commit
pre-commit install

# 4. Test et
pytest
black bread_backup/
mypy bread_backup/
```

---

## Destek

Kurulum sorunlarında:
1. Bu dokümanı okuyun
2. [KULLANIM.md](KULLANIM.md) - Sorun giderme bölümü
3. [GitHub Issues](https://github.com/ahwetekm/bread-backup/issues)
4. [GitHub Discussions](https://github.com/ahwetekm/bread-backup/discussions)

---

**Kurulum tamamlandı mı? [QUICKSTART.md](QUICKSTART.md) ile devam edin!** 🚀
