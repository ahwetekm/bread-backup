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

### Yöntem 1: Kaynak Koddan (Geliştirme Modu) - Önerilen

Bu yöntem, projeyi düzenlenebilir modda kurar. Güncellemeler için `git pull` yapmanız yeterlidir.

```bash
# 1. Bağımlılıkları kur
sudo pacman -S python-click python-rich python-yaml git base-devel

# 2. Projeyi klonla
cd ~/Projects  # veya istediğiniz dizin
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup

# 3. Geliştirme modunda kur
pip install --user -e .

# 4. PATH'e ekle (gerekirse)
export PATH="$HOME/.local/bin:$PATH"

# 5. Kurulumu test et
bread-backup --version
# bread-backup, version 0.1.0
```

**Avantajlar:**
- ✅ Kolay güncelleme (`git pull`)
- ✅ Kod değişiklikleri anında aktif
- ✅ Geliştirme için ideal

**Dezavantajlar:**
- ⚠️ Proje dizinini silmemelisiniz
- ⚠️ PATH ayarı gerekebilir (ilk kullanımda)

---

### Yöntem 2: Pip ile Kurulum (Lokal)

Sisteme karışmadan sadece kullanıcı için kurulum.

```bash
# 1. Bağımlılıkları kur
sudo pacman -S python-click python-rich python-yaml git

# 2. Projeyi klonla
git clone https://github.com/ahwetekm/bread-backup.git
cd bread-backup

# 3. Kullanıcı için kur (sudo yok)
pip install --user .

# 4. PATH'e ekle (eğer yoksa)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 5. Test et
bread-backup --version
```

**Avantajlar:**
- ✅ Sistem-wide değil, sadece kullanıcı
- ✅ sudo gerektirmez

**Dezavantajlar:**
- ⚠️ PATH ayarı gerekebilir
- ⚠️ Her kullanıcı ayrı kurmalı

---

### Yöntem 3: Virtual Environment (İzole)

Tamamen izole bir ortamda kurulum.

```bash
# 1. Bağımlılıkları kur
sudo pacman -S python-click python-rich python-yaml git

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

**Dezavantajlar:**
- ⚠️ Her kullanımda `source venv/bin/activate` gerekli
- ⚠️ Daha karmaşık

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

### Kaynak Koddan Kurulum Güncelleme

```bash
cd ~/Projects/bread-backup
git pull
pip install --user -e .
```

### Pip Kurulum Güncelleme

```bash
cd ~/Projects/bread-backup
git pull
pip install --user --upgrade .
```

---

## Kaldırma

### Kaynak Koddan Kurulumu Kaldırma

```bash
# Paketi kaldır
pip uninstall bread-backup

# Projeyi sil (opsiyonel)
rm -rf ~/Projects/bread-backup
```

### Pip Kurulumu Kaldırma

```bash
pip uninstall bread-backup
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

### Sorun 4: "Permission denied" (sudo pip install)

**Neden:** Yazma izni yok veya externally-managed-environment hatası.

**Çözüm (Önerilen):** Kullanıcı modunda kurun:
```bash
pip install --user -e .
export PATH="$HOME/.local/bin:$PATH"
```

---

### Sorun 5: "externally-managed-environment" hatası

Python 3.11+ ile gelebilir.

**Hata:**
```
error: externally-managed-environment

× This environment is externally managed
```

**Çözüm 1:** Virtual environment kullanın (Önerilen):
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

**Çözüm 2:** `--break-system-packages` flag (Dikkatli):
```bash
pip install --break-system-packages .
```

**Çözüm 3:** Arch paketlerini kullanın:
```bash
sudo pacman -S python-click python-rich python-yaml
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
