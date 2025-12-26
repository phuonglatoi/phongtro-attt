# 🔒 HƯỚNG DẪN DEPLOY AN TOÀN

## 📋 **TÌNH HUỐNG:**
- **Database:** Ở máy local (Windows) - IP: 192.168.x.x
- **Code:** Clone từ GitHub về máy ảo (Linux/Windows Server)
- **Vấn đề:** Làm sao bảo mật thông tin kết nối?

---

## ⚠️ **NGUY CƠ BẢO MẬT:**

### **1. ❌ KHÔNG BAO GIỜ LÀM:**
```python
# ❌ SAI - Hardcode password trong code
DATABASES = {
    'default': {
        'PASSWORD': 'MyPassword123!',  # ← NGUY HIỂM!
        'HOST': '192.168.1.100',       # ← Lộ IP!
    }
}
```

### **2. ❌ KHÔNG COMMIT LÊN GITHUB:**
- `.env` file (chứa password, secret key)
- `db.sqlite3` (nếu có)
- `*.log` files
- `media/` folder (ảnh người dùng)

---

## ✅ **GIẢI PHÁP AN TOÀN:**

### **BƯỚC 1: Tạo file `.env` trên máy ảo (KHÔNG commit)**

```bash
# Trên máy ảo, sau khi clone code
cd /path/to/PhongTroATTT
nano .env  # hoặc vim .env
```

**Nội dung file `.env`:**
```ini
# ============================================
# DJANGO SETTINGS
# ============================================
SECRET_KEY=Xg0H3KQLvSZWkckXJI8KmQ6EICvWGVbCW4_KeenOTWyKOWahG8Liz7pdGKyYKtdOBrI
DEBUG=False
ALLOWED_HOSTS=your-domain.com,192.168.x.x

# ============================================
# DATABASE - KẾT NỐI ĐẾN MÁY LOCAL
# ============================================
DB_NAME=QuanLyChoThuePhongTro
DB_USER=phongtro_app_user
DB_PASSWORD=StrongP@ssw0rd!2024#Secure
DB_HOST=192.168.1.100  # ← IP máy local của bạn
DB_PORT=1433

# ============================================
# EMAIL (Gmail App Password)
# ============================================
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# ============================================
# RECAPTCHA (Optional)
# ============================================
RECAPTCHA_PUBLIC_KEY=6Lc_your_site_key
RECAPTCHA_PRIVATE_KEY=6Lc_your_secret_key
```

**Lưu ý:**
- File này CHỈ tồn tại trên máy ảo
- KHÔNG commit lên GitHub
- Mỗi môi trường (dev/staging/production) có `.env` riêng

---

### **BƯỚC 2: Cấu hình SQL Server cho phép kết nối từ xa**

#### **2.1. Mở SQL Server Configuration Manager (trên máy local):**

1. Mở **SQL Server Configuration Manager**
2. Vào **SQL Server Network Configuration** → **Protocols for MSSQLSERVER**
3. Enable **TCP/IP**
4. Right-click **TCP/IP** → **Properties** → **IP Addresses**
5. Tìm **IPAll** → Set **TCP Port = 1433**
6. Restart **SQL Server service**

#### **2.2. Mở Firewall (trên máy local):**

```powershell
# Mở PowerShell as Administrator
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
```

#### **2.3. Tạo SQL Login cho remote access:**

```sql
-- Kết nối vào SQL Server Management Studio
USE master;
GO

-- Tạo login
CREATE LOGIN phongtro_app_user WITH PASSWORD = 'StrongP@ssw0rd!2024#Secure';
GO

-- Cho phép kết nối từ xa
USE QuanLyChoThuePhongTro;
GO

CREATE USER phongtro_app_user FOR LOGIN phongtro_app_user;
GO

-- Cấp quyền
ALTER ROLE db_datareader ADD MEMBER phongtro_app_user;
ALTER ROLE db_datawriter ADD MEMBER phongtro_app_user;
GO
```

---

### **BƯỚC 3: Bảo mật kết nối với SSL/TLS**

#### **3.1. Tạo VPN hoặc SSH Tunnel (KHUYẾN NGHỊ):**

**Option A: SSH Tunnel (An toàn nhất)**
```bash
# Trên máy ảo, tạo SSH tunnel đến máy local
ssh -L 1433:localhost:1433 user@192.168.1.100 -N -f

# Sau đó trong .env, dùng:
DB_HOST=localhost  # ← Kết nối qua tunnel
```

**Option B: VPN (Nếu có)**
- Dùng OpenVPN, WireGuard, hoặc Tailscale
- Cả 2 máy cùng trong 1 mạng VPN
- Kết nối qua IP VPN thay vì IP public

---

### **BƯỚC 4: Kiểm tra `.gitignore`**

```bash
# Đảm bảo file .gitignore có:
cat .gitignore
```

**Nội dung cần có:**
```
# Environment variables
.env
.env.local
.env.production

# Database
*.sqlite3
db.sqlite3

# Logs
*.log

# Media files
media/

# Python
__pycache__/
*.pyc
```

---

### **BƯỚC 5: Test kết nối từ máy ảo**

```python
# test_connection.py
import pyodbc

conn_str = (
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=192.168.1.100,1433;'
    'DATABASE=QuanLyChoThuePhongTro;'
    'UID=phongtro_app_user;'
    'PWD=StrongP@ssw0rd!2024#Secure;'
    'TrustServerCertificate=yes;'
)

try:
    conn = pyodbc.connect(conn_str)
    print("✅ Kết nối thành công!")
    conn.close()
except Exception as e:
    print(f"❌ Lỗi: {e}")
```

---

## 🔐 **CÁC LỚP BẢO MẬT:**

| Lớp | Biện pháp | Mục đích |
|-----|-----------|----------|
| **1. Network** | Firewall, VPN, SSH Tunnel | Chặn truy cập trái phép |
| **2. Authentication** | SQL Login + Password | Xác thực người dùng |
| **3. Encryption** | TLS/SSL | Mã hóa dữ liệu truyền |
| **4. Application** | `.env` file | Tách code và config |
| **5. Access Control** | SQL Roles (db_datareader) | Giới hạn quyền |

---

## 📊 **SO SÁNH CÁC PHƯƠNG ÁN:**

| Phương án | Độ an toàn | Độ phức tạp | Chi phí |
|-----------|------------|-------------|---------|
| **Direct Connection** | ⭐⭐ | ⭐ | Miễn phí |
| **Firewall + Strong Password** | ⭐⭐⭐ | ⭐⭐ | Miễn phí |
| **SSH Tunnel** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Miễn phí |
| **VPN (WireGuard)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Miễn phí |
| **Azure SQL Database** | ⭐⭐⭐⭐⭐ | ⭐⭐ | Tốn phí |

---

## 🚀 **KHUYẾN NGHỊ CHO ĐỒ ÁN:**

### **Phương án 1: SSH Tunnel (Tốt nhất cho demo)**
```bash
# Trên máy ảo
ssh -L 1433:localhost:1433 user@192.168.1.100 -N -f

# .env
DB_HOST=localhost
DB_PORT=1433
```

### **Phương án 2: Tailscale VPN (Dễ nhất)**
1. Cài Tailscale trên cả 2 máy: https://tailscale.com/
2. Kết nối cùng 1 mạng
3. Dùng IP Tailscale trong `.env`

---

## ✅ **CHECKLIST TRƯỚC KHI DEPLOY:**

- [ ] File `.env` đã tạo trên máy ảo (KHÔNG commit)
- [ ] `.gitignore` đã có `.env`
- [ ] SQL Server đã enable TCP/IP
- [ ] Firewall đã mở port 1433
- [ ] SQL Login đã tạo với password mạnh
- [ ] Test kết nối thành công
- [ ] (Optional) SSH Tunnel hoặc VPN đã setup
- [ ] `DEBUG=False` trong production
- [ ] `ALLOWED_HOSTS` đã cấu hình đúng

---

**Tiếp theo: Xem file `HUONG_DAN_DEPLOY_AN_TOAN_PART2.md` để biết cách deploy code!**

