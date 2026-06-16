# Hướng dẫn cài đặt Lasotuvi Engine

## 📋 Tổng quan

Package `lasotuvi` là engine tính toán Tử Vi được phát triển bởi doanguyen. Package này có vấn đề với dependencies lỗi thời, vì vậy cần cài đặt đúng cách để tránh lỗi.

**Trang GitHub**: https://github.com/doanguyen/lasotuvi

---

## ⚠️ Vấn đề với cài đặt thông thường

Nếu cài `lasotuvi` trực tiếp bằng:
```bash
pip install lasotuvi
```

Bạn sẽ gặp lỗi do các dependencies lỗi thời:
- `Pillow==2.6.1` - version cũ không tương thích với Python 3.11+
- `gnureadline==6.3.3` - deprecated và không cần thiết cho project này

---

## ✅ Cách cài đặt đúng

### Option 1: Sử dụng setup script (Khuyến nghị)

Windows PowerShell:

```powershell
cd tuvi-battu-graphrag\backend
.\setup_lasotuvi.ps1
```

Linux/macOS/WSL:

```bash
cd tuvi-battu-graphrag/backend
chmod +x setup_lasotuvi.sh
./setup_lasotuvi.sh
```

Náº¿u cháº¡y `bash setup_lasotuvi.sh` trÃªn Windows vÃ  gáº·p lá»—i
`execvpe(/bin/bash) failed: No such file or directory`, mÃ¡y khÃ´ng cÃ³ WSL/bash.
HÃ£y dÃ¹ng script PowerShell á»Ÿ trÃªn.

Script này sẽ:
1. Kiểm tra Python version
2. Cài đặt `ephem>=3.7.6.0` (dependency cần thiết)
3. Cài đặt `lasotuvi` với flag `--no-deps` (bỏ qua dependencies lỗi thời)
4. Verify installation

### Option 2: Cài đặt thủ công

```bash
# Bước 1: Cài ephem dependency
pip install "ephem>=3.7.6.0"

# Bước 2: Cài lasotuvi WITHOUT dependencies
pip install --no-deps lasotuvi

# Bước 3: Verify
python -c "from lasotuvi.DiaBan import diaBan; from lasotuvi.App import lapDiaBan; print('OK')"
```

---

## 📦 Dependencies

### Requirements đã được cập nhật:

File `requirements.txt`:
```txt
# Tử Vi Engine
# Install lasotuvi with: pip install --no-deps lasotuvi
ephem>=3.7.6.0
vnlunar
```

File `pyproject.toml`:
```toml
dependencies = [
  # ... other deps
  "ephem>=3.7.6.0"
]
```

---

## 🔍 Verify Installation

Sau khi cài đặt, chạy:

```bash
python -c "
from lasotuvi.DiaBan import diaBan
from lasotuvi.App import lapDiaBan
print('✓ Lasotuvi imported successfully')
print('✓ All modules available')
"
```

Nếu không có lỗi, cài đặt thành công!

---

## 🚀 Sử dụng trong project

### 1. Import modules

```python
from lasotuvi.DiaBan import diaBan
from lasotuvi.App import lapDiaBan
```

### 2. Sinh lá số (Generate birth chart)

```python
# Generate địa bàn
dia_ban = lapDiaBan(
    diaBan=diaBan,        # Pass CLASS, not instance!
    nn=15,                # ngày sinh
    tt=10,                # tháng sinh
    nnnn=1990,            # năm sinh
    gioSinh=6,            # giờ sinh (1-12)
    gioiTinh=1,           # 1=Nam, -1=Nữ
    duongLich=True,       # True=Dương lịch, False=Âm lịch
    timeZone=7            # UTC+7 cho Việt Nam
)

# Access kết quả
print(f"Cung Mệnh: {dia_ban.cungMenh}")
print(f"Cung Thân: {dia_ban.cungThan}")

# Duyệt qua 12 cung
for i in range(1, 13):
    cung = dia_ban.thapNhiCung[i]
    print(f"Cung {cung.cungTen}: {cung.cungChu}")
    
    # Sao trong cung
    for sao in cung.cungSao:
        print(f"  - {sao['saoTen']}: {sao['saoDacTinh']}")
```

---

## ⚠️ Lưu ý quan trọng

### 1. Pass CLASS không phải instance
```python
# ✅ ĐÚNG
dia_ban = lapDiaBan(diaBan=diaBan, ...)

# ❌ SAI
dia_ban_instance = diaBan()
dia_ban = lapDiaBan(diaBan=dia_ban_instance, ...)  # Sẽ lỗi!
```

### 2. Giờ sinh (1-12)
- Giờ sinh sử dụng địa chi: 1=Tý, 2=Sửu, ..., 12=Hợi
- Không sử dụng 0-23!

### 3. Giới tính
- `1` = Nam (Male)
- `-1` = Nữ (Female)

### 4. Index của cung
- `thapNhiCung[0]` = undefined
- `thapNhiCung[1-12]` = 12 cung

---

## 🐛 Troubleshooting

### Lỗi: "No module named 'lasotuvi'"

```bash
# Reinstall
pip uninstall lasotuvi
pip install "ephem>=3.7.6.0"
pip install --no-deps lasotuvi
```

### Lỗi: "cannot import name 'diaBan'"

Kiểm tra import statement:
```python
# ✅ ĐÚNG
from lasotuvi.DiaBan import diaBan

# ❌ SAI
from lasotuvi import diaBan
```

### Lỗi: Pillow version conflict

Nếu bạn đã cài lasotuvi trước đó:
```bash
pip uninstall lasotuvi Pillow
pip install "ephem>=3.7.6.0"
pip install --no-deps lasotuvi
pip install Pillow  # Latest version
```

---

## 📚 Tài liệu bổ sung

- [LASOTUVI_USAGE.md](./LASOTUVI_USAGE.md) - Hướng dẫn sử dụng API
- [GitHub: doanguyen/lasotuvi](https://github.com/doanguyen/lasotuvi)
- [PyPI: lasotuvi](https://pypi.org/project/lasotuvi/)

---

## 🔄 Update log

- **2026-06-13**: Initial setup guide
  - Added setup script
  - Updated requirements.txt và pyproject.toml
  - Created service wrapper
