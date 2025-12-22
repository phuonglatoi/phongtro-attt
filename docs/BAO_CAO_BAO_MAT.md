# 📋 BÁO CÁO TỔNG HỢP BẢO MẬT DỰ ÁN PHONGTROATTT

## 1. TỔNG QUAN DỰ ÁN

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | Hệ thống Quản lý Cho thuê Phòng trọ (PhongTroATTT) |
| **Framework** | Django 4.2.8 |
| **Database** | SQL Server 2019 (mssql-django) |
| **Ngôn ngữ** | Python 3.12 |
| **Deployment** | ngrok (HTTPS tunnel) |
| **Kiến trúc** | 3 tầng: Presentation → Application → Database |

---

## 2. TỔNG QUAN CÁC LOẠI BẢO MẬT

### 2.1 BẢO MẬT TẦNG WEB (APPLICATION LAYER)

| STT | Loại bảo mật | Mô tả | Công nghệ |
|-----|--------------|-------|-----------|
| 1 | **Authentication** | Xác thực người dùng | Django Session + Custom |
| 2 | **2FA (TOTP)** | Xác thực 2 yếu tố | pyotp, QR Code |
| 3 | **Password Hashing** | Mã hóa mật khẩu | SHA256 + Salt, Argon2 |
| 4 | **CSRF Protection** | Chống tấn công CSRF | Django CSRF Token |
| 5 | **XSS Protection** | Chống tấn công XSS | Django Template + WAF |
| 6 | **SQL Injection** | Chống SQL Injection | Django ORM + WAF |
| 7 | **Rate Limiting** | Giới hạn request | django-ratelimit |
| 8 | **IP Blocking** | Chặn IP độc hại | Custom Middleware |
| 9 | **WAF** | Tường lửa ứng dụng | Custom Middleware |
| 10 | **Session Security** | Bảo mật phiên | Secure Cookies |
| 11 | **Account Lockout** | Khóa tài khoản | Custom Logic |
| 12 | **Security Questions** | Câu hỏi bảo mật | SHA256 Hash |
| 13 | **Audit Logging** | Ghi log kiểm toán | Custom Middleware |
| 14 | **Device Tracking** | Theo dõi thiết bị | Custom Middleware |
| 15 | **reCAPTCHA** | Chống bot | Google reCAPTCHA v3 |
| 16 | **HTTPS/TLS** | Mã hóa truyền tải | ngrok SSL |
| 17 | **CSP Headers** | Content Security Policy | Django Settings |
| 18 | **OAuth 2.0** | Đăng nhập Google | django-allauth |

### 2.2 BẢO MẬT TẦNG CƠ SỞ DỮ LIỆU (DATABASE LAYER)

| STT | Loại bảo mật | Mô tả | Công nghệ |
|-----|--------------|-------|-----------|
| 1 | **Password Hashing (DB)** | Hash password tại DB | `HASHBYTES('SHA2_256')` |
| 2 | **Stored Procedures** | Thực thi an toàn | `SP_SECURE_LOGIN`, `SP_CHANGE_PASSWORD` |
| 3 | **Audit Triggers** | Ghi log thay đổi dữ liệu | `TRG_AUDIT_TAIKHOAN`, `TRG_AUDIT_PHONGTRO` |
| 4 | **Constraints** | Ràng buộc dữ liệu | `CHECK`, `UNIQUE`, `FOREIGN KEY` |
| 5 | **IP Blocking (DB)** | Chặn IP từ DB | `SP_LOG_FAILED_LOGIN`, `SP_CHECK_IP_BLOCKED` |
| 6 | **Auto Cleanup** | Dọn dẹp log cũ | `SP_CLEANUP_OLD_LOGS` |
| 7 | **Index Optimization** | Tối ưu truy vấn | `IX_SECURITY_LOGS_TIME`, `IX_LOGIN_HISTORY_MAKH` |
| 8 | **Principle of Least Privilege** | Phân quyền tối thiểu | User `phongtro_app` chỉ có quyền cần thiết |

### 2.3 BẢO MẬT TẦNG SERVER/NETWORK

| STT | Loại bảo mật | Mô tả | Công nghệ |
|-----|--------------|-------|-----------|
| 1 | **HTTPS/TLS** | Mã hóa kênh truyền | ngrok SSL Certificate |
| 2 | **Secure Headers** | HTTP Security Headers | HSTS, X-Frame-Options, X-Content-Type-Options |
| 3 | **CORS** | Cross-Origin Resource Sharing | django-corsheaders |
| 4 | **Whitenoise** | Static files security | WhiteNoise Middleware |

---

## 3. CHI TIẾT VỊ TRÍ CODE

### 3.1 🔐 PASSWORD HASHING

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/security.py` | 20-24 | Cấu hình Argon2/PBKDF2 hashers |
| `apps/accounts/views.py` | 155-169 | `verify_password()` - xác thực SHA256+Salt |
| `apps/accounts/views.py` | 172-175 | `hash_password()` - tạo hash mới |
| `apps/accounts/views.py` | 456-458 | Hash password khi đăng ký |

### 3.2 🔑 TWO-FACTOR AUTHENTICATION (2FA)

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/security.py` | 125-135 | Cấu hình 2FA (issuer, digits, period) |
| `apps/accounts/models.py` | 78-79 | Fields `is_2fa_enabled`, `totp_secret` |
| `apps/accounts/models.py` | 101-123 | Methods `enable_2fa()`, `verify_totp()` |
| `apps/accounts/views.py` | 653-704 | View setup 2FA + sinh QR Code |

### 3.3 🛡️ CSRF PROTECTION

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/base.py` | 86 | Middleware `CsrfViewMiddleware` |
| `config/settings/security.py` | 59-63 | Cấu hình CSRF Cookie (HttpOnly, Secure) |
| `config/settings/base.py` | 21-28 | `CSRF_TRUSTED_ORIGINS` cho ngrok |

### 3.4 🚫 RATE LIMITING

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/security.py` | 172-184 | Cấu hình Rate Limit (10/min login, 100/hour) |
| `apps/accounts/views.py` | 443 | Decorator `@ratelimit` cho register view |

### 3.5 🔒 ACCOUNT LOCKOUT

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/security.py` | 186-196 | Cấu hình lockout (5 attempts, 15 min) |
| `apps/accounts/security.py` | 89-93 | `lock_account()` - khóa tài khoản |
| `apps/accounts/security.py` | 104-114 | `check_account_locked()` - kiểm tra |
| `apps/accounts/security.py` | 117-128 | `increment_failed_login()` - đếm thất bại |
| `apps/accounts/views.py` | 259-264 | Logic khóa sau 5 lần sai password |

### 3.6 🌐 IP FILTERING & BLOCKING

| File | Dòng | Chức năng |
|------|------|-----------|
| `apps/security/middleware/ip_filter.py` | 18-55 | Class `IPFilterMiddleware` |
| `apps/accounts/security.py` | 44-73 | `log_failed_login()` + auto-block IP |
| `apps/accounts/models.py` | 206-220 | Model `BlockedIps` |
| `config/settings/security.py` | 198-222 | Cấu hình IP blocking rules |

### 3.7 🛡️ WAF (Web Application Firewall)

| File | Dòng | Chức năng |
|------|------|-----------|
| `apps/security/middleware/waf.py` | 20-93 | Class `WAFMiddleware` |
| `apps/security/middleware/waf.py` | 55-91 | `_check_request()` - detect attacks |
| `config/settings/security.py` | 273-297 | WAF patterns (SQL, XSS, Path Traversal, Command Injection) |

### 3.8 🍪 SESSION SECURITY

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/security.py` | 45-57 | Cấu hình Session Cookie (Secure, HttpOnly, SameSite) |
| `config/settings/base.py` | 83 | Middleware `SessionMiddleware` |

### 3.9 📝 AUDIT LOGGING

| File | Dòng | Chức năng |
|------|------|-----------|
| `apps/security/middleware/audit.py` | 13-50 | Class `AuditMiddleware` |
| `apps/accounts/models.py` | 240-255 | Model `AuditLogs` |
| `apps/accounts/models.py` | 223-237 | Model `SecurityLogs` |

### 3.10 📱 DEVICE TRACKING

| File | Dòng | Chức năng |
|------|------|-----------|
| `apps/security/middleware/device_tracking.py` | 21-54 | Class `DeviceTrackingMiddleware` |
| `config/settings/security.py` | 239-244 | Cấu hình device tracking |

### 3.11 ❓ SECURITY QUESTIONS

| File | Dòng | Chức năng |
|------|------|-----------|
| `apps/accounts/models.py` | 258-308 | Model `SecurityQuestion` |
| `apps/accounts/models.py` | 293-298 | `set_answer()` - hash câu trả lời SHA256 |
| `apps/accounts/models.py` | 300-305 | `verify_answer()` - xác thực câu trả lời |

### 3.12 🤖 reCAPTCHA

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/security.py` | 108-123 | Cấu hình reCAPTCHA v3 keys |
| `apps/accounts/views.py` | 219-227 | Verify reCAPTCHA khi login |

### 3.13 🔐 HTTPS & SECURITY HEADERS

| File | Dòng | Chức năng |
|------|------|-----------|
| `config/settings/security.py` | 65-75 | HTTPS redirect, HSTS, X-Frame-Options |
| `config/settings/security.py` | 77-106 | Content Security Policy (CSP) |

---

## 4. CHI TIẾT BẢO MẬT CƠ SỞ DỮ LIỆU (SQL SERVER)

### 4.1 🔐 STORED PROCEDURES BẢO MẬT

| Stored Procedure | File | Dòng | Chức năng |
|------------------|------|------|-----------|
| `SP_SECURE_LOGIN` | `scripts/database_setup.sql` | 332-401 | Đăng nhập an toàn với kiểm tra khóa tài khoản |
| `SP_CHANGE_PASSWORD` | `scripts/database_setup.sql` | 404-443 | Đổi mật khẩu với xác thực mật khẩu cũ |
| `SP_LOG_FAILED_LOGIN` | `scripts/database_setup.sql` | 446-470 | Ghi log và auto-block IP sau 10 lần thất bại |
| `SP_CHECK_IP_BLOCKED` | `scripts/database_setup.sql` | 473-488 | Kiểm tra IP có bị chặn không |
| `SP_CLEANUP_OLD_LOGS` | `scripts/database_setup.sql` | 491-510 | Dọn dẹp log cũ (7-180 ngày) |

### 4.2 📝 AUDIT TRIGGERS

| Trigger | File | Dòng | Chức năng |
|---------|------|------|-----------|
| `TRG_AUDIT_TAIKHOAN` | `scripts/database_setup.sql` | 521-535 | Ghi log thay đổi bảng TAIKHOAN |
| `TRG_AUDIT_PHONGTRO` | `scripts/database_setup.sql` | 538-562 | Ghi log INSERT/UPDATE/DELETE bảng PHONGTRO |

### 4.3 🔒 RÀNG BUỘC DỮ LIỆU (CONSTRAINTS)

| Loại | Bảng | Cột | Mô tả |
|------|------|-----|-------|
| `PRIMARY KEY` | Tất cả bảng | ID columns | Đảm bảo tính duy nhất |
| `FOREIGN KEY` | `KHACHHANG` | `MATK` | Ràng buộc với TAIKHOAN, `ON DELETE CASCADE` |
| `UNIQUE` | `TAIKHOAN` | `USERNAME` | Email không trùng lặp |
| `UNIQUE` | `KHACHHANG` | `EMAIL` | Email khách hàng duy nhất |
| `CHECK` | `DANHGIA` | `SAO` | Giới hạn đánh giá 1-5 sao |
| `DEFAULT` | `TAIKHOAN` | `IS_LOCKED` | Mặc định `0` (không khóa) |
| `DEFAULT` | `KHACHHANG` | `IS_2FA_ENABLED` | Mặc định `0` (chưa bật 2FA) |

### 4.4 📊 INDEX BẢO MẬT

| Index | Bảng | Cột | Mục đích |
|-------|------|-----|----------|
| `IX_TAIKHOAN_USERNAME` | `TAIKHOAN` | `USERNAME` | Tìm kiếm đăng nhập nhanh |
| `IX_KHACHHANG_EMAIL` | `KHACHHANG` | `EMAIL` | Tra cứu email nhanh |
| `IX_LOGIN_HISTORY_MAKH` | `LOGIN_HISTORY` | `MAKH, TIMESTAMP` | Lịch sử đăng nhập |
| `IX_SECURITY_LOGS_TIME` | `SECURITY_LOGS` | `LOG_TIME DESC` | Truy vấn log bảo mật |
| `IX_FAILED_LOGINS_IP` | `FAILED_LOGIN_ATTEMPTS` | `IP_ADDRESS, ATTEMPT_TIME` | Đếm login thất bại theo IP |

### 4.5 🗃️ BẢNG BẢO MẬT TRONG CSDL

| Bảng | Mô tả | File | Dòng |
|------|-------|------|------|
| `TAIKHOAN` | Lưu password_hash, salt, is_locked, 2FA secret | `scripts/database_setup.sql` | 46-66 |
| `KHACHHANG` | is_2fa_enabled, totp_secret, is_locked | `scripts/database_setup.sql` | 69-93 |
| `LOGIN_HISTORY` | Lịch sử đăng nhập (IP, device, location) | `scripts/database_setup.sql` | 96-113 |
| `FAILED_LOGIN_ATTEMPTS` | Theo dõi đăng nhập thất bại | `scripts/database_setup.sql` | 254-263 |
| `BLOCKED_IPS` | Danh sách IP bị chặn | `scripts/database_setup.sql` | 239-251 |
| `SECURITY_LOGS` | Log sự kiện bảo mật | `scripts/database_setup.sql` | 266-274 |
| `AUDIT_LOGS` | Log kiểm toán thay đổi dữ liệu | `scripts/database_setup.sql` | 277-287 |

### 4.6 🔑 PHÂN QUYỀN DATABASE

```sql
-- File: scripts/database_setup.sql, Dòng 574-597
-- Principle of Least Privilege

CREATE LOGIN phongtro_app WITH PASSWORD = 'PhongTro@SecurePass2024!';
CREATE USER phongtro_app FOR LOGIN phongtro_app;

-- Chỉ cấp quyền cần thiết
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO phongtro_app;
GRANT EXECUTE ON SCHEMA::dbo TO phongtro_app;
```

---

## 5. MIDDLEWARE SECURITY STACK

```
File: config/settings/base.py (Dòng 80-98)
```

| Thứ tự | Middleware | Chức năng |
|--------|------------|-----------|
| 1 | `SecurityMiddleware` | HTTPS redirect, Security headers |
| 2 | `WhiteNoiseMiddleware` | Static files security |
| 3 | `SessionMiddleware` | Session management |
| 4 | `CorsMiddleware` | CORS protection |
| 5 | `CommonMiddleware` | Common security |
| 6 | `CsrfViewMiddleware` | CSRF protection |
| 7 | `AuthenticationMiddleware` | User authentication |
| 8 | `OTPMiddleware` | 2FA support |
| 9 | `XFrameOptionsMiddleware` | Clickjacking protection |
| 10 | `IPFilterMiddleware` | IP blocking (custom) |
| 11 | `WAFMiddleware` | Attack detection (custom) |
| 12 | `AuditMiddleware` | Audit logging (custom) |
| 13 | `DeviceTrackingMiddleware` | Device tracking (custom) |

---

## 6. SƠ ĐỒ KIẾN TRÚC BẢO MẬT 3 TẦNG

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🌐 CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Browser → HTTPS/TLS (ngrok) → Django Templates → JavaScript           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🛡️ APPLICATION LAYER (Django)                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         SECURITY MIDDLEWARE                          │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │  │
│  │  │ IP Filter  │→│    WAF     │→│   CSRF     │→│  Session   │        │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘        │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │  │
│  │  │   Auth     │→│    OTP     │→│   Audit    │→│  Device    │        │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         SECURITY FEATURES                            │  │
│  │  • Password Hashing (SHA256+Salt, Argon2)                           │  │
│  │  • 2FA (TOTP + QR Code)                                             │  │
│  │  • Rate Limiting (10 login/min)                                     │  │
│  │  • Account Lockout (5 failures → 15min lock)                        │  │
│  │  • reCAPTCHA v3                                                     │  │
│  │  • Security Questions                                               │  │
│  │  • OAuth 2.0 (Google)                                               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        💾 DATABASE LAYER (SQL Server)                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       STORED PROCEDURES                              │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│  │  │ SP_SECURE_LOGIN │  │SP_CHANGE_PASSWORD│ │SP_LOG_FAILED_LOGIN│    │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │  │
│  │  ┌─────────────────┐  ┌─────────────────────────────────────┐       │  │
│  │  │SP_CHECK_IP_BLOCKED│ │      SP_CLEANUP_OLD_LOGS          │       │  │
│  │  └─────────────────┘  └─────────────────────────────────────┘       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         AUDIT TRIGGERS                               │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                   │  │
│  │  │ TRG_AUDIT_TAIKHOAN  │  │  TRG_AUDIT_PHONGTRO │                   │  │
│  │  └─────────────────────┘  └─────────────────────┘                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       SECURITY TABLES                                │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │  │
│  │  │ TAIKHOAN    │ │ BLOCKED_IPS │ │SECURITY_LOGS│ │ AUDIT_LOGS  │    │  │
│  │  │ (hash,salt) │ │             │ │             │ │             │    │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  CONSTRAINTS: PRIMARY KEY | FOREIGN KEY | UNIQUE | CHECK | DEFAULT  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. OWASP TOP 10 COVERAGE

| OWASP ID | Lỗ hổng | Đã bảo vệ | Giải pháp |
|----------|---------|-----------|-----------|
| A01:2021 | Broken Access Control | ✅ | Session, Middleware, Role-based |
| A02:2021 | Cryptographic Failures | ✅ | SHA256+Salt, Argon2, HTTPS |
| A03:2021 | Injection (SQL, XSS) | ✅ | Django ORM, WAF Middleware |
| A04:2021 | Insecure Design | ✅ | Defense in Depth, 3-tier |
| A05:2021 | Security Misconfiguration | ✅ | Secure defaults, CSP headers |
| A06:2021 | Vulnerable Components | ✅ | Updated packages |
| A07:2021 | Auth Failures | ✅ | 2FA, Rate Limit, Lockout |
| A08:2021 | Software Integrity | ✅ | CSRF, Audit Triggers |
| A09:2021 | Logging Failures | ✅ | Audit & Security Logs (DB+App) |
| A10:2021 | SSRF | ✅ | Input validation, WAF |

---

## 8. TỔNG KẾT CÁC FILE BẢO MẬT

| Tầng | File | Dòng quan trọng | Mô tả |
|------|------|-----------------|-------|
| **Config** | `config/settings/security.py` | 1-297 | Cấu hình bảo mật tổng thể |
| **Config** | `config/settings/base.py` | 80-98 | Middleware stack |
| **App** | `apps/accounts/views.py` | 155-175, 208-379, 653-704 | Login, Password, 2FA |
| **App** | `apps/accounts/security.py` | 44-134 | Security utilities |
| **App** | `apps/accounts/models.py` | 26-308 | Models bảo mật |
| **Middleware** | `apps/security/middleware/ip_filter.py` | 18-55 | IP Filtering |
| **Middleware** | `apps/security/middleware/waf.py` | 20-93 | Web Application Firewall |
| **Middleware** | `apps/security/middleware/audit.py` | 13-50 | Audit Logging |
| **Middleware** | `apps/security/middleware/device_tracking.py` | 21-54 | Device Tracking |
| **Database** | `scripts/database_setup.sql` | 332-562 | Stored Procedures, Triggers |

---

**📅 Ngày tạo:** 2025-12-19
**👤 Dự án:** PhongTroATTT - Hệ thống Quản lý Cho thuê Phòng trọ
**🔐 Phiên bản:** 1.0

