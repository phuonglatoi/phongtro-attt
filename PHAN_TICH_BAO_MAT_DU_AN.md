# 🔐 PHÂN TÍCH TOÀN DIỆN BẢO MẬT DỰ ÁN PHONGTROATTT

## 📊 TỔNG QUAN DỰ ÁN

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | Hệ thống Quản lý Cho thuê Phòng trọ (PhongTroATTT) |
| **Framework** | Django 4.2.8 |
| **Database** | SQL Server 2019 (Azure SQL Database) |
| **Ngôn ngữ** | Python 3.11 |
| **Deployment** | Azure App Service + ngrok (HTTPS) |
| **Kiến trúc** | 3 tầng: Presentation → Application → Database |

---

## 🎯 PHẦN 1: BẢO MẬT CƠ SỞ DỮ LIỆU (DATABASE SECURITY)

### 1.1 📝 MÃ HÓA MẬT KHẨU TẠI DATABASE

**Phương pháp:** SHA256 + Salt (32 bytes)

**Vị trí áp dụng:**
- **File:** `scripts/database_setup.sql`
- **Bảng:** `TAIKHOAN`
- **Cột:** 
  - `PASSWORD_HASH` (VARBINARY(32)) - Lưu hash SHA256
  - `PASSWORD_SALT` (VARCHAR(36)) - Lưu salt ngẫu nhiên

**Cách hoạt động:**
```sql
-- Khi tạo tài khoản:
1. Tạo SALT ngẫu nhiên (UUID)
2. Hash = SHA256(password + salt)
3. Lưu cả HASH và SALT vào database

-- Khi đăng nhập:
1. Lấy SALT từ database theo username
2. Tính Hash_Input = SHA256(password_nhập + salt)
3. So sánh Hash_Input với PASSWORD_HASH trong DB
```

**Code Python:**
```python
# File: apps/accounts/views.py (dòng 172-175)
def hash_password(password, salt):
    salted_password = f"{password}{salt}".encode('utf-8')
    return hashlib.sha256(salted_password).digest()
```

### 1.2 🔐 STORED PROCEDURES BẢO MẬT

**1. SP_SECURE_LOGIN** (Đăng nhập an toàn)
- **File:** `scripts/database_setup.sql` (dòng 332-401)
- **Chức năng:**
  - Kiểm tra tài khoản có bị khóa không
  - Xác thực password với SHA256
  - Tự động khóa sau 5 lần sai
  - Ghi log đăng nhập

**2. SP_CHANGE_PASSWORD** (Đổi mật khẩu)
- **File:** `scripts/database_setup.sql` (dòng 404-443)
- **Chức năng:**
  - Xác thực mật khẩu cũ
  - Hash mật khẩu mới với salt mới
  - Cập nhật LAST_PASSWORD_CHANGE

**3. SP_LOG_FAILED_LOGIN** (Ghi log thất bại)
- **File:** `scripts/database_setup.sql` (dòng 446-470)
- **Chức năng:**
  - Ghi log vào FAILED_LOGIN_ATTEMPTS
  - Tự động chặn IP sau 10 lần thất bại trong 1 giờ
  - Thêm vào BLOCKED_IPS với thời gian khóa 30 phút

**4. SP_CHECK_IP_BLOCKED** (Kiểm tra IP bị chặn)
- **File:** `scripts/database_setup.sql` (dòng 473-488)
- **Chức năng:**
  - Kiểm tra IP trong bảng BLOCKED_IPS
  - Tự động mở khóa nếu hết thời gian

**5. SP_CLEANUP_OLD_LOGS** (Dọn dẹp log cũ)
- **File:** `scripts/database_setup.sql` (dòng 491-510)
- **Chức năng:**
  - Xóa FAILED_LOGIN_ATTEMPTS > 7 ngày
  - Xóa SECURITY_LOGS > 180 ngày
  - Xóa AUDIT_LOGS > 180 ngày

### 1.3 📝 AUDIT TRIGGERS (Ghi log tự động)

**1. TRG_AUDIT_TAIKHOAN**
- **File:** `scripts/database_setup.sql` (dòng 521-535)
- **Kích hoạt:** Khi UPDATE bảng TAIKHOAN
- **Ghi log:** Thay đổi password, khóa tài khoản, 2FA

**2. TRG_AUDIT_PHONGTRO**
- **File:** `scripts/database_setup.sql` (dòng 538-562)
- **Kích hoạt:** INSERT, UPDATE, DELETE bảng PHONGTRO
- **Ghi log:** Tạo/sửa/xóa phòng trọ

### 1.4 🔒 RÀNG BUỘC DỮ LIỆU (CONSTRAINTS)

| Loại | Bảng | Cột | Mục đích |
|------|------|-----|----------|
| PRIMARY KEY | Tất cả bảng | ID | Đảm bảo tính duy nhất |
| FOREIGN KEY | KHACHHANG | MATK | Liên kết với TAIKHOAN, ON DELETE CASCADE |
| UNIQUE | TAIKHOAN | USERNAME | Email không trùng |
| UNIQUE | KHACHHANG | EMAIL | Email khách hàng duy nhất |
| CHECK | DANHGIA | SAO | Giới hạn 1-5 sao |
| DEFAULT | TAIKHOAN | IS_LOCKED | Mặc định = 0 (không khóa) |

### 1.5 🔐 MÃ HÓA DỮ LIỆU AZURE (Encryption at Rest)

**Transparent Data Encryption (TDE)**
- **Trạng thái:** ✅ Bật mặc định trên Azure SQL Database
- **Thuật toán:** AES-256
- **Phạm vi:** Toàn bộ database, backups, transaction logs
- **File tham khảo:** `docs/AZURE_SECURITY.md` (dòng 9-28)

**Column Encryption (Always Encrypted)**
- **Cấu hình:** `config/settings/development.py` (dòng 37)
- **Connection String:** `ColumnEncryption=Enabled`
- **Mục đích:** Mã hóa cột nhạy cảm (PASSWORD_HASH, TOTP_SECRET)

### 1.6 🔐 MÃ HÓA TRUYỀN TẢI (Encryption in Transit)

**SQL Server Connection**
- **TLS Version:** 1.2+
- **Connection String:** `Encrypt=yes;TrustServerCertificate=no`
- **File:** `config/settings/development.py` (dòng 39-52)

### 1.7 💾 SAO LƯU TỰ ĐỘNG (Automated Backups)

**Azure SQL Database:**
- ✅ Point-in-Time Restore: 35 ngày
- ✅ Long-term Retention: 10 năm
- ✅ Geo-redundant: Có thể bật
- ✅ RPO: < 5 phút

### 1.8 🔑 PHÂN QUYỀN TỐI THIỂU (Principle of Least Privilege)

**User Database:** `phongtro_app_user`
- ✅ Chỉ có quyền: SELECT, INSERT, UPDATE, DELETE
- ❌ Không có quyền: DROP, ALTER, CREATE
- ✅ Chỉ truy cập các bảng cần thiết
- ✅ Không có quyền sysadmin

---

## 🎯 PHẦN 2: BẢO MẬT ỨNG DỤNG WEB (APPLICATION SECURITY)

### 2.1 🔐 XÁC THỰC NGƯỜI DÙNG (Authentication)

**Phương pháp:** Custom Session-based Authentication

**Luồng đăng nhập:**
```
1. User nhập email + password
2. Kiểm tra IP có bị chặn không (IPFilterMiddleware)
3. Kiểm tra tài khoản có bị khóa không
4. Xác thực password với SHA256 + Salt
5. Nếu có 2FA → Redirect sang trang 2FA
6. Nếu không có 2FA → Tạo session và đăng nhập
7. Ghi log LOGIN_HISTORY
```

**File:** `apps/accounts/views.py` (dòng 177-379)

**Session Security:**
- `SESSION_COOKIE_SECURE = True` - Chỉ gửi qua HTTPS
- `SESSION_COOKIE_HTTPONLY = True` - JavaScript không đọc được
- `SESSION_COOKIE_SAMESITE = 'Strict'` - Chống CSRF
- `SESSION_COOKIE_AGE = 900` - Timeout 15 phút

**File:** `config/settings/security.py` (dòng 45-57)

### 2.2 🔑 XÁC THỰC 2 YẾU TỐ (Two-Factor Authentication - 2FA)

**Công nghệ:** TOTP (Time-based One-Time Password) với pyotp

**Luồng hoạt động:**
```
1. User bật 2FA → Hệ thống tạo TOTP_SECRET (base32)
2. Tạo QR Code với URI: otpauth://totp/PhongTro.vn:email?secret=xxx
3. User quét QR bằng Google Authenticator
4. User nhập mã 6 số để xác nhận
5. Lưu TOTP_SECRET vào database (bảng KHACHHANG)
6. Khi đăng nhập → Yêu cầu nhập mã OTP
7. Verify OTP với valid_window=2 (±60 giây)
```

**File áp dụng:**
- `apps/accounts/models.py` (dòng 78-79, 101-146) - Model và methods
- `apps/accounts/views.py` (dòng 653-730) - Setup 2FA view
- `apps/accounts/views.py` (dòng 386-509) - Login 2FA view
- `config/settings/security.py` (dòng 125-135) - Cấu hình

**Bảo mật:**
- ✅ Secret được lưu an toàn trong database
- ✅ QR Code chỉ hiển thị 1 lần khi setup
- ✅ Có backup codes (10 mã dự phòng)
- ✅ Email cảnh báo khi bật/tắt 2FA

### 2.3 🛡️ CHỐNG TẤN CÔNG CSRF (Cross-Site Request Forgery)

**Công nghệ:** Django CSRF Token

**Cách hoạt động:**
```
1. Server tạo CSRF token ngẫu nhiên cho mỗi session
2. Token được gửi trong cookie và form
3. Khi submit form, server so sánh 2 token
4. Nếu không khớp → Từ chối request
```

**Cấu hình:**
- `CSRF_COOKIE_SECURE = True` - Chỉ gửi qua HTTPS
- `CSRF_COOKIE_HTTPONLY = True` - JS không đọc được
- `CSRF_COOKIE_SAMESITE = 'Strict'` - Chặn cross-site

**File:** `config/settings/security.py` (dòng 59-63)

**Áp dụng trong template:**
```html
<form method="POST">
    {% csrf_token %}
    <!-- Form fields -->
</form>
```

**Middleware:** `django.middleware.csrf.CsrfViewMiddleware`
**File:** `config/settings/base.py` (dòng 89)

### 2.4 🚫 CHỐNG TẤN CÔNG XSS (Cross-Site Scripting)

**Phương pháp 1: Django Template Auto-Escaping**
- ✅ Tự động escape HTML trong `{{ variable }}`
- ✅ Chuyển `<script>` thành `&lt;script&gt;`

**Phương pháp 2: Input Sanitization với Bleach**
```python
# File: apps/accounts/forms.py (dòng 128, 137)
import bleach
username = bleach.clean(username, strip=True)
email = bleach.clean(email, strip=True).lower()
```

**Phương pháp 3: Content Security Policy (CSP)**
```python
# File: config/settings/security.py (dòng 77-106)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://www.google.com/recaptcha/")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

**Phương pháp 4: WAF (Web Application Firewall)**
- Phát hiện pattern XSS: `<script>`, `javascript:`, `onerror=`
- **File:** `apps/security/middleware/waf.py` (dòng 78-81)

### 2.5 🛡️ CHỐNG TẤN CÔNG SQL INJECTION

**Phương pháp 1: Django ORM (Parameterized Queries)**
```python
# ✅ AN TOÀN - Django ORM tự động escape
Khachhang.objects.filter(email=user_input)

# ❌ NGUY HIỂM - Raw SQL không escape
cursor.execute(f"SELECT * FROM KHACHHANG WHERE EMAIL = '{user_input}'")
```

**Phương pháp 2: Stored Procedures**
- Sử dụng SP với parameters
- **File:** `scripts/database_setup.sql`

**Phương pháp 3: WAF Pattern Detection**
```python
# File: apps/security/middleware/waf.py (dòng 74-76)
sql_patterns = [
    r"(\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP)\b)",
    r"(--|#|/\*|\*/|;)",
    r"(\bOR\b.*=.*|AND\b.*=.*)",
]
```

**File:** `config/settings/security.py` (dòng 280-283)

### 2.6 ⏱️ GIỚI HẠN REQUEST (Rate Limiting)

**Công nghệ:** django-ratelimit

**Cấu hình:**
```python
# File: config/settings/security.py (dòng 178-184)
RATELIMIT_LOGIN = '5/m'        # 5 lần/phút
RATELIMIT_REGISTER = '3/10m'   # 3 lần/10 phút
RATELIMIT_API = '60/m'         # 60 request/phút
RATELIMIT_UPLOAD = '10/h'      # 10 file/giờ
```

**Áp dụng:**
```python
# File: apps/accounts/views.py (dòng 443)
@ratelimit(key='ip', rate=settings.RATELIMIT_REGISTER, method='POST')
def register_view(request):
    ...
```

### 2.7 🔒 KHÓA TÀI KHOẢN TỰ ĐỘNG (Account Lockout)

**Cơ chế:**
```
1. Đăng nhập sai → Tăng FAILED_LOGIN_COUNT
2. Sau 3 lần sai → Hiện CAPTCHA
3. Sau 5 lần sai → Khóa tài khoản 15 phút
4. Sau 10 lần sai → Khóa vĩnh viễn (cần admin mở)
```

**File áp dụng:**
- `apps/accounts/views.py` (dòng 259-264) - Logic khóa
- `apps/accounts/security.py` (dòng 89-128) - Helper functions
- `config/settings/security.py` (dòng 186-196) - Cấu hình

**Bảng database:**
- `TAIKHOAN.IS_LOCKED` - Trạng thái khóa
- `TAIKHOAN.LOCK_TIME` - Thời gian mở khóa
- `TAIKHOAN.FAILED_LOGIN_COUNT` - Số lần sai

### 2.8 🌐 CHẶN IP ĐỘC HẠI (IP Blocking)

**Cơ chế tự động:**
```
1. Ghi log mỗi lần đăng nhập thất bại vào FAILED_LOGIN_ATTEMPTS
2. Đếm số lần thất bại trong 1 giờ
3. Nếu >= 10 lần → Tự động thêm vào BLOCKED_IPS
4. Khóa IP trong 30 phút
5. Middleware kiểm tra IP trước khi xử lý request
```

**File áp dụng:**
- `apps/security/middleware/ip_filter.py` (dòng 18-55) - Middleware
- `apps/accounts/security.py` (dòng 44-73) - Auto-block logic
- `apps/accounts/models.py` (dòng 206-220) - Model BLOCKED_IPS

**Whitelist/Blacklist:**
```python
# File: config/settings/security.py (dòng 218-222)
IP_WHITELIST = ['127.0.0.1']  # Không bao giờ chặn
IP_BLACKLIST = []  # Load từ database
```

### 2.9 🛡️ WEB APPLICATION FIREWALL (WAF)

**Chức năng:** Phát hiện và chặn các pattern tấn công

**Các loại tấn công được phát hiện:**
1. **SQL Injection:** `SELECT`, `UNION`, `DROP`, `--`, `;`
2. **XSS:** `<script>`, `javascript:`, `onerror=`
3. **Path Traversal:** `../`, `../../etc/passwd`
4. **Command Injection:** `|`, `;`, `bash -i`, `cmd.exe`

**File:** `apps/security/middleware/waf.py` (dòng 20-93)

**Cách hoạt động:**
```python
def _check_request(self, request):
    # Lấy tất cả input từ GET, POST, headers
    all_input = list(request.GET.values()) + list(request.POST.values())

    # Kiểm tra từng pattern
    for value in all_input:
        for pattern in sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return 'sql_injection'

    return None  # An toàn
```

**Khi phát hiện tấn công:**
- ✅ Ghi log vào SECURITY_LOGS
- ✅ Trả về HTTP 403 Forbidden
- ✅ Gửi cảnh báo (nếu cấu hình)

### 2.10 🤖 GOOGLE reCAPTCHA v3

**Mục đích:** Chống bot, spam, brute-force

**Khi nào hiện CAPTCHA:**
- ✅ Sau 3 lần đăng nhập thất bại
- ✅ Khi đăng ký tài khoản
- ✅ Khi reset password

**File áp dụng:**
- `config/settings/security.py` (dòng 108-123) - Cấu hình
- `apps/accounts/views.py` (dòng 219-227) - Verify CAPTCHA

**Cách hoạt động:**
```python
def verify_recaptcha(token):
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': token
    })
    result = response.json()
    return result.get('success', False) and result.get('score', 0) >= 0.5
```

### 2.11 📝 GHI LOG KIỂM TOÁN (Audit Logging)

**Các sự kiện được ghi log:**
- ✅ Đăng nhập/đăng xuất (thành công/thất bại)
- ✅ Đổi mật khẩu
- ✅ Bật/tắt 2FA
- ✅ Cập nhật profile
- ✅ Tạo/sửa/xóa phòng trọ
- ✅ Upload/xóa file
- ✅ Truy cập admin
- ✅ Hoạt động đáng ngờ

**Bảng database:**
- `AUDIT_LOGS` - Log hành động người dùng
- `SECURITY_LOGS` - Log sự kiện bảo mật
- `LOGIN_HISTORY` - Lịch sử đăng nhập

**Middleware:** `apps/security/middleware/audit.py` (dòng 13-50)

**Thông tin ghi log:**
- User ID, IP address, User Agent
- Action type, timestamp
- Request path, method
- Chi tiết thay đổi (JSON)

### 2.12 📱 THEO DÕI THIẾT BỊ (Device Tracking)

**Mục đích:** Phát hiện đăng nhập từ thiết bị lạ

**Thông tin thu thập:**
- Device type (Mobile/Tablet/Desktop)
- Browser (Chrome, Firefox, Safari, Edge)
- OS (Windows, macOS, Linux, Android, iOS)
- IP address, User Agent

**File:** `apps/security/middleware/device_tracking.py` (dòng 21-54)

**Cảnh báo:**
- ✅ Email khi đăng nhập từ thiết bị mới
- ✅ Email khi đăng nhập từ IP mới
- ✅ Giới hạn 3 thiết bị đồng thời

**Cấu hình:**
```python
# File: config/settings/security.py (dòng 239-244)
TRACK_USER_DEVICES = True
MAX_CONCURRENT_SESSIONS = 3
ALERT_ON_NEW_DEVICE = True
```

### 2.13 ❓ CÂU HỎI BẢO MẬT (Security Questions)

**Mục đích:** Khôi phục tài khoản khi quên mật khẩu

**Danh sách câu hỏi:**
1. Tên thú cưng đầu tiên?
2. Tên trường tiểu học?
3. Thành phố sinh ra?
4. Tên người bạn thân nhất?
5. Món ăn yêu thích?

**Bảo mật:**
- ✅ Câu trả lời được hash SHA256
- ✅ Không lưu plain text
- ✅ So sánh hash khi verify

**File:** `apps/accounts/models.py` (dòng 258-308)

```python
def set_answer(self, answer):
    clean_answer = answer.strip().lower()
    self.answer_hash = hashlib.sha256(clean_answer.encode()).hexdigest()

def verify_answer(self, answer):
    clean_answer = answer.strip().lower()
    answer_hash = hashlib.sha256(clean_answer.encode()).hexdigest()
    return answer_hash == self.answer_hash
```

### 2.14 🔐 HTTPS & SECURITY HEADERS

**HTTPS/TLS:**
- ✅ Bắt buộc HTTPS: `SECURE_SSL_REDIRECT = True`
- ✅ HSTS: `SECURE_HSTS_SECONDS = 31536000` (1 năm)
- ✅ HSTS Preload: `SECURE_HSTS_PRELOAD = True`

**Security Headers:**
```python
# File: config/settings/security.py (dòng 65-75)
SECURE_CONTENT_TYPE_NOSNIFF = True  # Chống MIME sniffing
SECURE_BROWSER_XSS_FILTER = True    # Bật XSS filter
X_FRAME_OPTIONS = 'DENY'            # Chống Clickjacking
```

**Content Security Policy (CSP):**
- Chỉ cho phép script từ domain tin cậy
- Chặn inline script nguy hiểm
- **File:** `config/settings/security.py` (dòng 77-106)

### 2.15 🌐 OAUTH 2.0 (Đăng nhập Google)

**Công nghệ:** django-allauth

**Luồng hoạt động:**
```
1. User click "Đăng nhập bằng Google"
2. Redirect sang Google OAuth
3. User cho phép truy cập email, profile
4. Google trả về access token
5. Hệ thống lấy thông tin user từ Google
6. Tạo/cập nhật tài khoản trong database
7. Tự động đăng nhập
```

**File cấu hình:**
- `config/settings/security.py` (dòng 137-170)
- `.env` - Lưu GOOGLE_OAUTH_CLIENT_ID, CLIENT_SECRET

**Bảo mật:**
- ✅ Email đã được Google verify
- ✅ Không cần lưu password
- ✅ Token được mã hóa
- ✅ Scope giới hạn (chỉ email, profile)

---

## 🎯 PHẦN 3: VỊ TRÍ ÁP DỤNG TRONG ĐỒ ÁN

### 3.1 📂 CẤU TRÚC THƯ MỤC BẢO MẬT

```
PhongTroATTT/
├── apps/
│   ├── accounts/           # ✅ Authentication, 2FA, Password
│   │   ├── models.py       # ✅ User models, Security models
│   │   ├── views.py        # ✅ Login, Register, 2FA views
│   │   ├── forms.py        # ✅ Input validation với Bleach
│   │   └── security.py     # ✅ Security helper functions
│   │
│   └── security/           # ✅ Security middleware
│       └── middleware/
│           ├── waf.py              # ✅ Web Application Firewall
│           ├── ip_filter.py        # ✅ IP Blocking
│           ├── audit.py            # ✅ Audit Logging
│           └── device_tracking.py  # ✅ Device Tracking
│
├── config/
│   └── settings/
│       ├── base.py         # ✅ Middleware, CSRF config
│       ├── security.py     # ✅ TẤT CẢ cấu hình bảo mật
│       ├── development.py  # ✅ Database encryption config
│       └── production.py   # ✅ Production security
│
├── scripts/
│   └── database_setup.sql  # ✅ Stored Procedures, Triggers, Constraints
│
├── templates/
│   └── accounts/
│       ├── login.html      # ✅ CSRF token trong form
│       ├── login_2fa.html  # ✅ 2FA verification
│       └── setup_2fa.html  # ✅ QR Code setup
│
└── docs/
    ├── BAO_CAO_BAO_MAT.md  # ✅ Báo cáo bảo mật chi tiết
    └── AZURE_SECURITY.md   # ✅ Bảo mật Azure
```

### 3.2 🗺️ SƠ ĐỒ LUỒNG BẢO MẬT

**Luồng đăng nhập có 2FA:**
```
[User nhập email/password]
         ↓
[IPFilterMiddleware] → Kiểm tra IP có bị chặn?
         ↓
[login_view] → Xác thực password (SHA256+Salt)
         ↓
[Kiểm tra 2FA enabled?]
         ↓ YES
[Redirect → login_2fa_view]
         ↓
[User nhập OTP 6 số]
         ↓
[verify_totp()] → Xác thực với TOTP_SECRET
         ↓
[Tạo session + Ghi log]
         ↓
[DeviceTrackingMiddleware] → Lưu thông tin thiết bị
         ↓
[AuditMiddleware] → Ghi log AUDIT_LOGS
         ↓
[Redirect → Dashboard]
```

**Luồng xử lý request:**
```
[HTTP Request]
         ↓
[SecurityMiddleware] → HTTPS redirect
         ↓
[IPFilterMiddleware] → Kiểm tra IP blacklist
         ↓
[WAFMiddleware] → Phát hiện SQL Injection, XSS
         ↓
[CsrfViewMiddleware] → Verify CSRF token
         ↓
[RateLimitMiddleware] → Kiểm tra rate limit
         ↓
[DeviceTrackingMiddleware] → Track thiết bị
         ↓
[View Function] → Xử lý logic
         ↓
[AuditMiddleware] → Ghi log hành động
         ↓
[HTTP Response]
```

### 3.3 📊 BẢNG TỔNG HỢP VỊ TRÍ CODE

| Tính năng bảo mật | File chính | Dòng code | Áp dụng ở đâu |
|-------------------|------------|-----------|---------------|
| **Password Hashing** | `apps/accounts/views.py` | 155-175 | Đăng ký, Đăng nhập, Đổi MK |
| **2FA (TOTP)** | `apps/accounts/views.py` | 386-509, 653-730 | Đăng nhập, Setup 2FA |
| **CSRF Protection** | `config/settings/security.py` | 59-63 | Tất cả form POST |
| **XSS Protection** | `apps/accounts/forms.py` | 128, 137 | Input validation |
| **SQL Injection** | Django ORM | - | Tất cả database queries |
| **Rate Limiting** | `apps/accounts/views.py` | 443 | Register, Login |
| **Account Lockout** | `apps/accounts/views.py` | 259-264 | Login thất bại |
| **IP Blocking** | `apps/security/middleware/ip_filter.py` | 18-55 | Tất cả requests |
| **WAF** | `apps/security/middleware/waf.py` | 20-93 | Tất cả requests |
| **Audit Logging** | `apps/security/middleware/audit.py` | 13-50 | Tất cả actions |
| **Device Tracking** | `apps/security/middleware/device_tracking.py` | 21-54 | Sau login |
| **Security Questions** | `apps/accounts/models.py` | 258-308 | Password reset |
| **reCAPTCHA** | `apps/accounts/views.py` | 219-227 | Login, Register |
| **HTTPS/TLS** | `config/settings/security.py` | 65-75 | Toàn bộ site |
| **OAuth 2.0** | `config/settings/security.py` | 137-170 | Đăng nhập Google |
| **Stored Procedures** | `scripts/database_setup.sql` | 332-510 | Database operations |
| **Audit Triggers** | `scripts/database_setup.sql` | 521-562 | Auto-log DB changes |

---

## 📈 TỔNG KẾT

### ✅ ĐIỂM MẠNH

1. **Bảo mật đa tầng:** Database → Application → Network
2. **Mã hóa toàn diện:** At rest (TDE) + In transit (TLS)
3. **Xác thực mạnh:** Password + 2FA + OAuth
4. **Phòng thủ chủ động:** WAF, Rate Limiting, IP Blocking
5. **Ghi log đầy đủ:** Audit, Security, Login History
6. **Tự động hóa:** Auto-lock, Auto-block, Auto-cleanup

### 🎯 CÁC BIỆN PHÁP BẢO MẬT ĐÃ ÁP DỤNG

**Tầng Database (8 biện pháp):**
1. ✅ Password Hashing (SHA256 + Salt)
2. ✅ Stored Procedures bảo mật
3. ✅ Audit Triggers tự động
4. ✅ Constraints & Validation
5. ✅ Transparent Data Encryption (TDE)
6. ✅ Column Encryption (Always Encrypted)
7. ✅ Encrypted Connection (TLS 1.2)
8. ✅ Automated Backups

**Tầng Application (15 biện pháp):**
1. ✅ Custom Authentication
2. ✅ Two-Factor Authentication (2FA)
3. ✅ CSRF Protection
4. ✅ XSS Protection
5. ✅ SQL Injection Prevention
6. ✅ Rate Limiting
7. ✅ Account Lockout
8. ✅ IP Blocking
9. ✅ Web Application Firewall (WAF)
10. ✅ reCAPTCHA v3
11. ✅ Audit Logging
12. ✅ Device Tracking
13. ✅ Security Questions
14. ✅ HTTPS/TLS + Security Headers
15. ✅ OAuth 2.0 (Google Login)

**Tổng cộng: 23 biện pháp bảo mật**

---

## 📞 LIÊN HỆ

Nếu có thắc mắc về bảo mật dự án, vui lòng liên hệ:
- Email: phuonglatoi@gmail.com
- GitHub: https://github.com/phuonglatoi/phongtro-attt

---

**Ngày tạo:** 24/12/2025
**Phiên bản:** 1.0
**Tác giả:** PhongTroATTT Team

