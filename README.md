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