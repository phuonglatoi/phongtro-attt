# 🔐 TÓM TẮT BẢO MẬT DỰ ÁN PHONGTROATTT

## 📊 TỔNG QUAN

**Dự án:** Hệ thống Quản lý Cho thuê Phòng trọ  
**Công nghệ:** Django 4.2.8 + SQL Server 2019 + Azure  
**Tổng số biện pháp bảo mật:** 23 biện pháp

---

## 🎯 PHẦN 1: BẢO MẬT CƠ SỞ DỮ LIỆU (8 BIỆN PHÁP)

### 1. Mã hóa mật khẩu (SHA256 + Salt)
- **Vị trí:** `scripts/database_setup.sql` - Bảng TAIKHOAN
- **Cách hoạt động:** Hash = SHA256(password + salt_ngẫu_nhiên)
- **Code:** `apps/accounts/views.py` (dòng 172-175)

### 2. Stored Procedures bảo mật
- **SP_SECURE_LOGIN:** Đăng nhập an toàn, tự động khóa sau 5 lần sai
- **SP_CHANGE_PASSWORD:** Đổi mật khẩu với xác thực
- **SP_LOG_FAILED_LOGIN:** Ghi log và auto-block IP
- **SP_CHECK_IP_BLOCKED:** Kiểm tra IP bị chặn
- **SP_CLEANUP_OLD_LOGS:** Dọn dẹp log cũ
- **Vị trí:** `scripts/database_setup.sql` (dòng 332-510)

### 3. Audit Triggers (Ghi log tự động)
- **TRG_AUDIT_TAIKHOAN:** Log thay đổi tài khoản
- **TRG_AUDIT_PHONGTRO:** Log thay đổi phòng trọ
- **Vị trí:** `scripts/database_setup.sql` (dòng 521-562)

### 4. Ràng buộc dữ liệu (Constraints)
- PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
- Đảm bảo tính toàn vẹn dữ liệu

### 5. Transparent Data Encryption (TDE)
- **Công nghệ:** Azure SQL Database - AES-256
- **Phạm vi:** Toàn bộ database, backups, logs
- **Trạng thái:** ✅ Bật mặc định

### 6. Column Encryption (Always Encrypted)
- **Cấu hình:** `ColumnEncryption=Enabled` trong connection string
- **Mục đích:** Mã hóa cột nhạy cảm (PASSWORD_HASH, TOTP_SECRET)
- **Vị trí:** `config/settings/development.py` (dòng 37)

### 7. Mã hóa truyền tải (TLS 1.2)
- **Connection String:** `Encrypt=yes;TrustServerCertificate=no`
- **Vị trí:** `config/settings/development.py` (dòng 39-52)

### 8. Sao lưu tự động (Azure Backups)
- Point-in-Time Restore: 35 ngày
- Long-term Retention: 10 năm
- RPO: < 5 phút

---

## 🎯 PHẦN 2: BẢO MẬT ỨNG DỤNG WEB (15 BIỆN PHÁP)

### 1. Xác thực người dùng (Custom Session-based)
- **Vị trí:** `apps/accounts/views.py` (dòng 177-379)
- **Session Security:** Secure, HttpOnly, SameSite=Strict
- **Timeout:** 15 phút

### 2. Xác thực 2 yếu tố (2FA - TOTP)
- **Công nghệ:** pyotp + Google Authenticator
- **Vị trí:** `apps/accounts/views.py` (dòng 386-509, 653-730)
- **Bảo mật:** Secret lưu trong DB, QR Code 1 lần, backup codes

### 3. Chống CSRF (Cross-Site Request Forgery)
- **Công nghệ:** Django CSRF Token
- **Vị trí:** `config/settings/security.py` (dòng 59-63)
- **Áp dụng:** Tất cả form POST có `{% csrf_token %}`

### 4. Chống XSS (Cross-Site Scripting)
- **Phương pháp 1:** Django Template Auto-Escaping
- **Phương pháp 2:** Bleach sanitization (`apps/accounts/forms.py` dòng 128, 137)
- **Phương pháp 3:** Content Security Policy (CSP)
- **Phương pháp 4:** WAF pattern detection

### 5. Chống SQL Injection
- **Phương pháp 1:** Django ORM (Parameterized Queries)
- **Phương pháp 2:** Stored Procedures
- **Phương pháp 3:** WAF pattern detection
- **Vị trí:** `apps/security/middleware/waf.py` (dòng 74-76)

### 6. Giới hạn request (Rate Limiting)
- **Công nghệ:** django-ratelimit
- **Cấu hình:** Login 5/phút, Register 3/10phút
- **Vị trí:** `config/settings/security.py` (dòng 178-184)

### 7. Khóa tài khoản tự động (Account Lockout)
- **Cơ chế:** 3 lần sai → CAPTCHA, 5 lần → Khóa 15 phút, 10 lần → Khóa vĩnh viễn
- **Vị trí:** `apps/accounts/views.py` (dòng 259-264)

### 8. Chặn IP độc hại (IP Blocking)
- **Cơ chế:** Tự động chặn sau 10 lần đăng nhập sai trong 1 giờ
- **Vị trí:** `apps/security/middleware/ip_filter.py` (dòng 18-55)

### 9. Web Application Firewall (WAF)
- **Phát hiện:** SQL Injection, XSS, Path Traversal, Command Injection
- **Vị trí:** `apps/security/middleware/waf.py` (dòng 20-93)

### 10. Google reCAPTCHA v3
- **Khi nào:** Sau 3 lần đăng nhập sai, Register, Reset password
- **Vị trí:** `apps/accounts/views.py` (dòng 219-227)

### 11. Ghi log kiểm toán (Audit Logging)
- **Bảng:** AUDIT_LOGS, SECURITY_LOGS, LOGIN_HISTORY
- **Vị trí:** `apps/security/middleware/audit.py` (dòng 13-50)

### 12. Theo dõi thiết bị (Device Tracking)
- **Thu thập:** Device type, Browser, OS, IP, User Agent
- **Cảnh báo:** Email khi đăng nhập từ thiết bị mới
- **Vị trí:** `apps/security/middleware/device_tracking.py` (dòng 21-54)

### 13. Câu hỏi bảo mật (Security Questions)
- **Bảo mật:** Câu trả lời hash SHA256
- **Vị trí:** `apps/accounts/models.py` (dòng 258-308)

### 14. HTTPS/TLS + Security Headers
- **HTTPS:** Bắt buộc, HSTS 1 năm
- **Headers:** X-Frame-Options, X-Content-Type-Options, CSP
- **Vị trí:** `config/settings/security.py` (dòng 65-106)

### 15. OAuth 2.0 (Đăng nhập Google)
- **Công nghệ:** django-allauth
- **Vị trí:** `config/settings/security.py` (dòng 137-170)

---

## 🗺️ PHẦN 3: VỊ TRÍ ÁP DỤNG TRONG ĐỒ ÁN

### Cấu trúc thư mục bảo mật:
```
apps/accounts/          → Authentication, 2FA, Password
apps/security/          → WAF, IP Filter, Audit, Device Tracking
config/settings/        → Tất cả cấu hình bảo mật
scripts/                → Stored Procedures, Triggers
templates/accounts/     → CSRF token trong forms
```

### File quan trọng nhất:
1. **`config/settings/security.py`** - Tất cả cấu hình bảo mật (297 dòng)
2. **`apps/accounts/views.py`** - Login, 2FA, Password (1253 dòng)
3. **`scripts/database_setup.sql`** - SP, Triggers, Constraints (614 dòng)
4. **`apps/security/middleware/`** - WAF, IP Filter, Audit, Device Tracking

---

## 📈 TỔNG KẾT

✅ **23 biện pháp bảo mật** được áp dụng toàn diện  
✅ **Bảo mật đa tầng:** Database → Application → Network  
✅ **Mã hóa toàn diện:** At rest (TDE) + In transit (TLS)  
✅ **Xác thực mạnh:** Password + 2FA + OAuth  
✅ **Phòng thủ chủ động:** WAF, Rate Limiting, IP Blocking  
✅ **Ghi log đầy đủ:** Audit, Security, Login History  

---

**File chi tiết:** `PHAN_TICH_BAO_MAT_DU_AN.md` (700 dòng)  
**Ngày tạo:** 24/12/2025
