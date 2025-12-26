# 🏠 PhongTro.vn - Hệ thống Cho thuê Phòng trọ Bảo mật

Hệ thống quản lý cho thuê phòng trọ với bảo mật cao cấp, áp dụng các biện pháp bảo vệ theo tiêu chuẩn quốc tế.

## ✨ Tính năng Bảo mật

- ✅ **2FA/TOTP** - Xác thực 2 yếu tố với Google Authenticator
- ✅ **Google OAuth** - Đăng nhập bằng tài khoản Google
- ✅ **CAPTCHA** - Google reCAPTCHA v3
- ✅ **Rate Limiting** - Giới hạn request chống brute-force
- ✅ **IP Blocking** - Tự động chặn IP đáng ngờ
- ✅ **WAF** - Web Application Firewall chặn SQL Injection, XSS
- ✅ **Device Tracking** - Theo dõi thiết bị đăng nhập
- ✅ **Audit Logging** - Ghi log mọi hành động quan trọng
- ✅ **Email Alerts** - Cảnh báo hoạt động bất thường

## 🚀 Quick Start

### Cài đặt

```bash
# Clone repository
git clone [https://github.com/your-repo/phongtro-secure.git](https://github.com/your-repo/phongtro-secure.git)
cd phongtro-secure

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Copy .env.example
cp .env.example .env
# Sửa các thông tin trong .env

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy server
python manage.py runserver
```

---

## 🔐 **DEPLOY AN TOÀN**

### **Vấn đề:**
> "Database ở máy local, code clone từ GitHub về máy ảo. Làm sao bảo mật thông tin?"

### **Giải pháp:**
✅ **File `.env`** - Chứa thông tin nhạy cảm (KHÔNG commit lên Git)
✅ **SSH Tunnel** - Mã hóa kết nối database
✅ **Firewall** - Giới hạn IP truy cập
✅ **5 lớp bảo mật** - Network, Transport, Auth, App, File System

### **Tài liệu chi tiết:**
📖 **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Tóm tắt giải pháp
📖 **[docs/README_DEPLOY.md](docs/README_DEPLOY.md)** - Hướng dẫn đầy đủ
📖 **[docs/TOM_TAT_DEPLOY_AN_TOAN.md](docs/TOM_TAT_DEPLOY_AN_TOAN.md)** - Quick start

### **Scripts tự động:**
🔧 **[scripts/setup_ssh_tunnel.sh](scripts/setup_ssh_tunnel.sh)** - Setup SSH Tunnel
🔍 **[scripts/test_db_connection.py](scripts/test_db_connection.py)** - Test kết nối DB

### **Quick Deploy:**
```bash
# 1. Clone code
git clone https://github.com/phuonglatoi/phongtro-attt.git
cd phongtro-attt

# 2. Tạo .env (KHÔNG commit)
cp .env.example .env
nano .env  # Điền thông tin thật
chmod 600 .env

# 3. Setup SSH Tunnel (Optional)
bash scripts/setup_ssh_tunnel.sh

# 4. Test connection
python scripts/test_db_connection.py

# 5. Deploy
python manage.py migrate
python manage.py runserver 0.0.0.0:8000