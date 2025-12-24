# 📚 BÁO CÁO ĐỒ ÁN
# HỆ THỐNG QUẢN LÝ CHO THUÊ PHÒNG TRỌ VỚI BẢO MẬT NÂNG CAO
## (PhongTroATTT - An Toàn Thông Tin)

---

## 📋 THÔNG TIN CHUNG

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên đồ án** | Hệ thống Quản lý Cho thuê Phòng trọ với Bảo mật nâng cao |
| **Mã đồ án** | PhongTroATTT |
| **Framework** | Django 4.2.8 (Python Web Framework) |
| **Ngôn ngữ lập trình** | Python 3.12 |
| **Cơ sở dữ liệu** | Microsoft SQL Server 2019 |
| **Kiến trúc** | MVC (Model-View-Controller) / 3-Tier Architecture |
| **Deployment** | ngrok (HTTPS tunnel) / Docker |
| **Version Control** | Git + GitHub |

---

## 🎯 MỤC TIÊU ĐỒ ÁN

### 1. Mục tiêu chính
- Xây dựng hệ thống web cho thuê phòng trọ trực tuyến
- Áp dụng các biện pháp bảo mật theo chuẩn OWASP Top 10
- Triển khai bảo mật đa tầng (Defense in Depth)

### 2. Mục tiêu cụ thể
- ✅ Quản lý thông tin phòng trọ, nhà trọ
- ✅ Hệ thống đăng ký, đăng nhập an toàn
- ✅ Xác thực 2 yếu tố (2FA/TOTP)
- ✅ Bảo vệ chống các cuộc tấn công phổ biến (SQL Injection, XSS, CSRF)
- ✅ Ghi log kiểm toán (Audit Logging)
- ✅ Quản lý thiết bị đăng nhập

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### 1. Kiến trúc 3 tầng

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                  (Giao diện người dùng)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  Bootstrap  │ │   HTML/CSS  │ │ JavaScript  │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│  ┌─────────────────────────────────────────────┐            │
│  │          Django Templates Engine            │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                   (Django Framework)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Security Middleware                   │   │
│  │  • IP Filter    • WAF        • CSRF    • Session     │   │
│  │  • Auth         • OTP        • Audit   • Device      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Django Apps                        │   │
│  │  • accounts  • rooms    • bookings  • chat           │   │
│  │  • security  • reviews  • notifications              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                           │
│                  (Microsoft SQL Server)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Stored Procedures & Triggers             │   │
│  │  • SP_SECURE_LOGIN      • TRG_AUDIT_TAIKHOAN         │   │
│  │  • SP_CHANGE_PASSWORD   • TRG_AUDIT_PHONGTRO         │   │
│  │  • SP_LOG_FAILED_LOGIN  • SP_CLEANUP_OLD_LOGS        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Data Tables                        │   │
│  │  • TAIKHOAN  • KHACHHANG  • PHONGTRO   • NHATRO      │   │
│  │  • THUETRO   • DANHGIA    • TINNHAN    • THONGBAO    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Security Tables                       │   │
│  │  • SECURITY_LOGS  • AUDIT_LOGS  • BLOCKED_IPS        │   │
│  │  • LOGIN_HISTORY  • FAILED_LOGIN_ATTEMPTS            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2. Cấu trúc thư mục dự án

```
PhongTroATTT/
├── apps/                      # Các ứng dụng Django
│   ├── accounts/              # Quản lý tài khoản, xác thực
│   ├── bookings/              # Đặt phòng, yêu cầu thuê
│   ├── chat/                  # Nhắn tin
│   ├── core/                  # Chức năng cốt lõi
│   ├── notifications/         # Thông báo
│   ├── reviews/               # Đánh giá
│   ├── rooms/                 # Quản lý phòng trọ
│   └── security/              # Middleware bảo mật
├── config/                    # Cấu hình Django
│   ├── settings/              # Settings phân tách
│   │   ├── base.py           # Cấu hình chung
│   │   ├── development.py    # Môi trường dev
│   │   ├── production.py     # Môi trường prod
│   │   └── security.py       # Cấu hình bảo mật
│   └── urls.py               # URL routing
├── templates/                 # HTML templates
├── static/                    # CSS, JS, images
├── media/                     # User uploads
├── scripts/                   # Database scripts
├── docs/                      # Tài liệu
└── requirements.txt           # Dependencies
```

---

## 🔐 CÁC TÍNH NĂNG BẢO MẬT

### Tổng quan 18 tính năng bảo mật đã triển khai

| STT | Tính năng | Mô tả | Công nghệ |
|-----|-----------|-------|-----------|
| 1 | **Authentication** | Xác thực người dùng | Django Session + Custom |
| 2 | **2FA (TOTP)** | Xác thực 2 yếu tố | pyotp + QR Code |
| 3 | **Password Hashing** | Mã hóa mật khẩu | SHA256 + Salt |
| 4 | **CSRF Protection** | Chống tấn công CSRF | Django CSRF Token |
| 5 | **XSS Protection** | Chống tấn công XSS | Template escaping + WAF |
| 6 | **SQL Injection Protection** | Chống SQL Injection | Django ORM + WAF |
| 7 | **Rate Limiting** | Giới hạn request | django-ratelimit |
| 8 | **IP Blocking** | Chặn IP độc hại | Custom Middleware |
| 9 | **WAF** | Tường lửa ứng dụng | Custom Middleware |
| 10 | **Session Security** | Bảo mật phiên | Secure Cookies |
| 11 | **Account Lockout** | Khóa tài khoản | Custom Logic |
| 12 | **Security Questions** | Câu hỏi bảo mật | SHA256 Hash |
| 13 | **Audit Logging** | Ghi log kiểm toán | Database + Files |
| 14 | **Device Tracking** | Theo dõi thiết bị | Custom Middleware |
| 15 | **reCAPTCHA** | Chống bot | Google reCAPTCHA v3 |
| 16 | **HTTPS/TLS** | Mã hóa truyền tải | ngrok SSL |
| 17 | **CSP Headers** | Content Security Policy | Django Settings |
| 18 | **OAuth 2.0** | Đăng nhập Google | django-allauth |

---

## 📊 SƠ ĐỒ CƠ SỞ DỮ LIỆU (ERD)

### Các bảng chính trong hệ thống

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           ENTITY RELATIONSHIP DIAGRAM                     │
└──────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │   VAITRO    │         │  TAIKHOAN   │         │  KHACHHANG  │
    │─────────────│         │─────────────│         │─────────────│
    │ MAVT (PK)   │◄───┐    │ MATK (PK)   │◄───┐    │ MAKH (PK)   │
    │ TENVT       │    │    │ USERNAME    │    │    │ HOTEN       │
    │ MOTA        │    │    │ PASS_HASH   │    │    │ EMAIL       │
    └─────────────┘    │    │ PASS_SALT   │    │    │ SDT         │
                       │    │ IS_LOCKED   │    └────│ MATK (FK)   │
                       │    │ FAILED_COUNT│         │ MAVT (FK)   │───┐
                       │    └─────────────┘         │ IS_2FA      │   │
                       │                            │ TOTP_SECRET │   │
                       └────────────────────────────│             │   │
                                                    └─────────────┘   │
                                                           │          │
                    ┌──────────────────────────────────────┤          │
                    │                                      │          │
                    ▼                                      ▼          │
    ┌─────────────────────┐                 ┌─────────────────────┐   │
    │    LOGIN_HISTORY    │                 │       NHATRO        │   │
    │─────────────────────│                 │─────────────────────│   │
    │ MALS (PK)           │                 │ MANH (PK)           │   │
    │ MAKH (FK)           │                 │ MAKH (FK)           │◄──┘
    │ TIMESTAMP           │                 │ DIACHI              │
    │ IP_ADDRESS          │                 │ TIEN_DIEN           │
    │ USER_AGENT          │                 │ TIEN_NUOC           │
    │ SUCCESS             │                 └─────────────────────┘
    └─────────────────────┘                            │
                                                       │
                                                       ▼
    ┌─────────────────────┐                 ┌─────────────────────┐
    │      DANHGIA        │                 │      PHONGTRO       │
    │─────────────────────│                 │─────────────────────│
    │ MADG (PK)           │                 │ MAPT (PK)           │
    │ MAPT (FK)           │◄────────────────│ MANH (FK)           │
    │ MAKH (FK)           │                 │ TENPT               │
    │ SAO                 │                 │ GIATHUE             │
    │ NOIDUNG             │                 │ DIENTICH            │
    └─────────────────────┘                 │ TRANGTHAI           │
                                            │ MOTA                │
    ┌─────────────────────┐                 └─────────────────────┘
    │      LICHHEN        │                            │
    │─────────────────────│                            │
    │ MALH (PK)           │                            │
    │ MAPT (FK)           │◄───────────────────────────┘
    │ MAKH (FK)           │
    │ NGAYHEN             │
    │ TRANGTHAI           │
    └─────────────────────┘

    ════════════════════════════════════════════════════════════════
                           SECURITY TABLES
    ════════════════════════════════════════════════════════════════

    ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
    │    BLOCKED_IPS      │    │   SECURITY_LOGS     │    │    AUDIT_LOGS       │
    │─────────────────────│    │─────────────────────│    │─────────────────────│
    │ ID (PK)             │    │ ID (PK)             │    │ ID (PK)             │
    │ IP_ADDRESS          │    │ ACTION_TYPE         │    │ TABLE_NAME          │
    │ REASON              │    │ MATK (FK)           │    │ RECORD_ID           │
    │ BLOCKED_UNTIL       │    │ IP_ADDRESS          │    │ ACTION              │
    │ CREATED_AT          │    │ DETAILS             │    │ OLD_VALUES          │
    └─────────────────────┘    │ LOG_TIME            │    │ NEW_VALUES          │
                               └─────────────────────┘    │ CHANGED_BY          │
                                                          │ CHANGED_AT          │
    ┌─────────────────────┐                               └─────────────────────┘
    │ FAILED_LOGIN_ATTEMPTS│
    │─────────────────────│
    │ ID (PK)             │
    │ IP_ADDRESS          │
    │ EMAIL_ATTEMPTED     │
    │ ATTEMPT_TIME        │
    │ FAILURE_REASON      │
    └─────────────────────┘
```

---

## 🔒 CHI TIẾT TRIỂN KHAI BẢO MẬT

### 1. 🔐 Password Hashing (Mã hóa mật khẩu)

**Thuật toán:** SHA256 với Salt ngẫu nhiên

```python
# File: apps/accounts/views.py

import hashlib
import os

def hash_password(password: str) -> tuple:
    """Tạo hash và salt cho password mới"""
    salt = os.urandom(32).hex()  # 64 ký tự hex
    password_hash = hashlib.sha256(
        (password + salt).encode()
    ).hexdigest()
    return password_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Xác thực password với hash và salt đã lưu"""
    computed_hash = hashlib.sha256(
        (password + salt).encode()
    ).hexdigest()
    return computed_hash == stored_hash
```

**Lợi ích:**
- Salt ngẫu nhiên ngăn chặn Rainbow Table Attack
- SHA256 là hàm băm một chiều, không thể giải mã ngược

---

### 2. 🔑 Two-Factor Authentication (2FA)

**Công nghệ:** Time-based One-Time Password (TOTP) theo RFC 6238

```python
# File: apps/accounts/models.py

import pyotp

class Khachhang(models.Model):
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, null=True)

    def enable_2fa(self):
        """Bật 2FA và tạo secret key"""
        self.totp_secret = pyotp.random_base32()
        self.is_2fa_enabled = True
        self.save()
        return self.get_totp_uri()

    def verify_totp(self, token):
        """Xác thực mã OTP"""
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=2)  # ±60 giây

    def get_totp_uri(self):
        """Tạo URI cho QR Code"""
        totp = pyotp.TOTP(self.totp_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name='PhongTro.vn'
        )
```

**Quy trình 2FA:**
1. Người dùng bật 2FA → Hệ thống tạo secret key
2. Hiển thị QR Code → Người dùng quét bằng Google Authenticator
3. Khi đăng nhập → Nhập mã 6 số từ app
4. Hệ thống verify mã với secret key đã lưu

---

### 3. 🛡️ CSRF Protection

**Cơ chế:** Django CSRF Token

```python
# File: config/settings/security.py

CSRF_COOKIE_SECURE = True       # Chỉ gửi qua HTTPS
CSRF_COOKIE_HTTPONLY = True     # JavaScript không đọc được
CSRF_COOKIE_SAMESITE = 'Strict' # Chống tấn công cross-site
```

```html
<!-- Trong template HTML -->
<form method="POST">
    {% csrf_token %}
    <!-- Form fields -->
</form>
```

---

### 4. 🚫 Rate Limiting (Giới hạn request)

**Cấu hình:**
```python
# File: config/settings/security.py

RATELIMIT_LOGIN = '5/m'        # 5 lần đăng nhập/phút
RATELIMIT_REGISTER = '3/10m'   # 3 lần đăng ký/10 phút
RATELIMIT_API = '60/m'         # 60 API calls/phút
```

**Áp dụng:**
```python
# File: apps/accounts/views.py

from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate=settings.RATELIMIT_LOGIN, method='POST')
def login_view(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Quá nhiều lần thử. Vui lòng đợi.')
        return redirect('accounts:login')
    # ... xử lý đăng nhập
```

---

### 5. 🔒 Account Lockout (Khóa tài khoản)

**Logic khóa tài khoản:**
```python
# File: apps/accounts/security.py

MAX_LOGIN_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15

def increment_failed_login(taikhoan, ip_address):
    """Tăng số lần đăng nhập thất bại"""
    taikhoan.failed_login_count = (taikhoan.failed_login_count or 0) + 1
    taikhoan.save()

    # Khóa tài khoản sau 5 lần sai
    if taikhoan.failed_login_count >= MAX_LOGIN_ATTEMPTS:
        lock_account(taikhoan, minutes=LOCK_DURATION_MINUTES)
        log_security_event('ACCOUNT_LOCKED', taikhoan, ip_address,
                          f'Locked after {taikhoan.failed_login_count} failed attempts')
        return True
    return False

def lock_account(taikhoan, minutes=15):
    """Khóa tài khoản trong X phút"""
    taikhoan.is_locked = True
    taikhoan.lock_time = timezone.now() + timedelta(minutes=minutes)
    taikhoan.save()
```

---

### 6. 🌐 IP Blocking (Chặn IP)

**Middleware tự động chặn IP:**
```python
# File: apps/security/middleware/ip_filter.py

class IPFilterMiddleware:
    def __call__(self, request):
        ip_address = get_client_ip(request)

        # Whitelist - Luôn cho phép
        if ip_address in settings.IP_WHITELIST:
            return self.get_response(request)

        # Kiểm tra IP có bị block không
        blocked_ip = BlockedIps.objects.filter(ip_address=ip_address).first()

        if blocked_ip:
            if blocked_ip.blocked_until < timezone.now():
                blocked_ip.delete()  # Hết hạn block
            else:
                return render(request, 'security/ip_blocked.html',
                             status=403)

        return self.get_response(request)
```

**Auto-block sau nhiều lần thất bại:**
```python
# File: apps/accounts/security.py

def log_failed_login(ip_address, email_attempted):
    """Ghi log và auto-block IP sau 10 lần thất bại"""
    FailedLoginAttempts.objects.create(
        ip_address=ip_address,
        email_attempted=email_attempted
    )

    # Đếm số lần thất bại trong 1 giờ
    one_hour_ago = timezone.now() - timedelta(hours=1)
    fail_count = FailedLoginAttempts.objects.filter(
        ip_address=ip_address,
        attempt_time__gte=one_hour_ago
    ).count()

    # Auto-block IP nếu >= 10 lần thất bại
    if fail_count >= 10:
        BlockedIps.objects.create(
            ip_address=ip_address,
            reason='Too many failed login attempts',
            blocked_until=timezone.now() + timedelta(minutes=30)
        )
```

---

### 7. 🛡️ WAF - Web Application Firewall

**Phát hiện và chặn các cuộc tấn công:**
```python
# File: apps/security/middleware/waf.py

class WAFMiddleware:
    def _check_request(self, request):
        """Kiểm tra request có chứa mẫu tấn công không"""
        patterns = settings.WAF_BLOCK_PATTERNS

        # Kiểm tra SQL Injection
        for pattern in patterns['sql_injection']:
            if re.search(pattern, request_data, re.IGNORECASE):
                return 'SQL Injection detected'

        # Kiểm tra XSS
        for pattern in patterns['xss']:
            if re.search(pattern, request_data, re.IGNORECASE):
                return 'XSS attack detected'

        # Kiểm tra Path Traversal
        for pattern in patterns['path_traversal']:
            if re.search(pattern, request.path):
                return 'Path traversal detected'

        return None  # Không phát hiện tấn công
```

**Các pattern được phát hiện:**
| Loại tấn công | Pattern mẫu |
|---------------|-------------|
| SQL Injection | `UNION SELECT`, `DROP TABLE`, `--`, `OR 1=1` |
| XSS | `<script>`, `javascript:`, `onerror=` |
| Path Traversal | `../`, `etc/passwd`, `C:\Windows` |
| Command Injection | `; cat`, `| ls`, `` `whoami` `` |

---

### 8. 📝 Audit Logging (Ghi log kiểm toán)

**Middleware ghi log mọi request:**
```python
# File: apps/security/middleware/audit.py

class AuditMiddleware:
    def __call__(self, request):
        response = self.get_response(request)

        if settings.AUDIT_LOG_ENABLED:
            AuditLogs.objects.create(
                user_id=request.session.get('makh'),
                action=request.method,
                path=request.path,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                response_code=response.status_code
            )

        return response
```

**Database Trigger ghi log thay đổi dữ liệu:**
```sql
-- File: scripts/database_setup.sql

CREATE TRIGGER TRG_AUDIT_TAIKHOAN
ON TAIKHOAN
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    INSERT INTO AUDIT_LOGS (TABLE_NAME, RECORD_ID, ACTION, OLD_VALUES, NEW_VALUES)
    SELECT
        'TAIKHOAN',
        COALESCE(i.MATK, d.MATK),
        CASE
            WHEN i.MATK IS NULL THEN 'DELETE'
            WHEN d.MATK IS NULL THEN 'INSERT'
            ELSE 'UPDATE'
        END,
        (SELECT * FROM deleted FOR JSON PATH),
        (SELECT * FROM inserted FOR JSON PATH)
    FROM inserted i
    FULL OUTER JOIN deleted d ON i.MATK = d.MATK;
END
```

---

## 📱 CÁC CHỨC NĂNG CHÍNH

### 1. Quản lý tài khoản
| Chức năng | Mô tả | URL |
|-----------|-------|-----|
| Đăng ký | Tạo tài khoản mới với email | `/accounts/register/` |
| Đăng nhập | Xác thực email + mật khẩu | `/accounts/login/` |
| Đăng xuất | Hủy phiên đăng nhập | `/accounts/logout/` |
| Quên mật khẩu | Đặt lại mật khẩu qua email OTP | `/accounts/password/reset/` |
| Đổi mật khẩu | Thay đổi mật khẩu | `/accounts/password/change/` |
| Bật 2FA | Kích hoạt xác thực 2 yếu tố | `/accounts/2fa/setup/` |
| Hồ sơ | Xem/sửa thông tin cá nhân | `/accounts/profile/` |

### 2. Quản lý phòng trọ
| Chức năng | Mô tả | URL |
|-----------|-------|-----|
| Danh sách phòng | Xem tất cả phòng trọ | `/rooms/` |
| Chi tiết phòng | Xem thông tin chi tiết | `/rooms/<id>/` |
| Đăng phòng | Chủ trọ đăng phòng mới | `/rooms/create/` |
| Tìm kiếm | Tìm phòng theo tiêu chí | `/rooms/search/` |
| Yêu thích | Lưu phòng yêu thích | `/rooms/<id>/favorite/` |

### 3. Đặt phòng & Lịch hẹn
| Chức năng | Mô tả | URL |
|-----------|-------|-----|
| Đặt lịch xem | Đặt lịch hẹn xem phòng | `/bookings/schedule/` |
| Lịch hẹn của tôi | Xem các lịch hẹn đã đặt | `/bookings/my-bookings/` |
| Dashboard chủ trọ | Quản lý lịch hẹn cho chủ trọ | `/bookings/landlord/` |

### 4. Đánh giá & Chat
| Chức năng | Mô tả | URL |
|-----------|-------|-----|
| Đánh giá phòng | Cho điểm và nhận xét | `/reviews/<room_id>/` |
| Nhắn tin | Chat với chủ trọ | `/chat/<user_id>/` |

---

## 🖥️ GIAO DIỆN NGƯỜI DÙNG

### Các màn hình chính

| Màn hình | Mô tả | Template |
|----------|-------|----------|
| Trang chủ | Hiển thị phòng mới nhất | `templates/rooms/home.html` |
| Đăng nhập | Form đăng nhập với CAPTCHA | `templates/accounts/login.html` |
| Đăng ký | Form đăng ký tài khoản | `templates/accounts/register.html` |
| Danh sách phòng | Grid hiển thị phòng trọ | `templates/rooms/room_list.html` |
| Chi tiết phòng | Thông tin, hình ảnh, đánh giá | `templates/rooms/room_detail.html` |
| Hồ sơ cá nhân | Thông tin user, 2FA settings | `templates/accounts/profile.html` |
| Admin | Quản trị hệ thống | `/admin/` |

### Công nghệ Frontend
- **Bootstrap 5.3** - Framework CSS responsive
- **Font Awesome** - Icon library
- **JavaScript** - Xử lý form validation, AJAX

---

## 📋 HƯỚNG DẪN TRIỂN KHAI

### 1. Yêu cầu hệ thống
- Python 3.10+
- SQL Server 2019
- Git

### 2. Cài đặt môi trường
```bash
# Clone repository
git clone https://github.com/phuonglatoi/phongtro-attt.git
cd phongtro-attt

# Tạo virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cấu hình database
```bash
# Tạo database trong SQL Server
sqlcmd -S localhost -U sa -i scripts/database_setup.sql

# Cấu hình .env
DATABASE_URL=mssql://sa:password@localhost/phongtro_db
```

### 4. Chạy ứng dụng
```bash
# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy server
python manage.py runserver
```

### 5. Triển khai với ngrok
```bash
# Cài đặt ngrok
ngrok http 8000

# URL public sẽ được tạo, ví dụ:
# https://abc123.ngrok.io
```

---

## 🔍 KIỂM THỬ BẢO MẬT

### Các test case đã thực hiện

| STT | Test Case | Kết quả |
|-----|-----------|---------|
| 1 | SQL Injection trong form login | ✅ Chặn thành công |
| 2 | XSS trong input tìm kiếm | ✅ Escape HTML |
| 3 | CSRF attack | ✅ Yêu cầu token |
| 4 | Brute force password | ✅ Khóa sau 5 lần |
| 5 | Session hijacking | ✅ HttpOnly + Secure |
| 6 | Path traversal | ✅ WAF chặn |
| 7 | 2FA bypass | ✅ Yêu cầu OTP |

---

## 📊 OWASP TOP 10 COVERAGE

| ID | Lỗ hổng | Trạng thái | Giải pháp |
|----|---------|------------|-----------|
| A01 | Broken Access Control | ✅ | Session + Role-based |
| A02 | Cryptographic Failures | ✅ | SHA256+Salt, HTTPS |
| A03 | Injection | ✅ | Django ORM, WAF |
| A04 | Insecure Design | ✅ | Defense in Depth |
| A05 | Security Misconfiguration | ✅ | Secure defaults |
| A06 | Vulnerable Components | ✅ | Updated packages |
| A07 | Auth Failures | ✅ | 2FA, Rate Limit |
| A08 | Software Integrity | ✅ | CSRF, Audit |
| A09 | Logging Failures | ✅ | Audit Logs |
| A10 | SSRF | ✅ | Input validation |

---

## 📚 TÀI LIỆU THAM KHẢO

1. Django Documentation - https://docs.djangoproject.com/
2. OWASP Top 10 - https://owasp.org/Top10/
3. pyOTP Documentation - https://pyotp.readthedocs.io/
4. SQL Server Security Best Practices - Microsoft Docs
5. django-ratelimit - https://django-ratelimit.readthedocs.io/

---

## 👥 THÔNG TIN NHÓM

| Thành viên | MSSV | Vai trò |
|------------|------|---------|
| [Tên sinh viên] | [MSSV] | [Phân công] |

---

**📅 Ngày hoàn thành:** 2025-12-22
**🔐 Phiên bản:** 1.0
**📧 Liên hệ:** [Email liên hệ]

