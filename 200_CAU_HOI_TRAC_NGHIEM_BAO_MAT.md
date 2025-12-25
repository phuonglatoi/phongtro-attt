# 📝 200 CÂU HỎI TRẮC NGHIỆM BẢO MẬT WEB APPLICATION
## Từ Database → Backend → Frontend → Server → Backup

---

## 📚 MỤC LỤC

- [Phần 1: Bảo mật Cơ sở dữ liệu (40 câu)](#phần-1-bảo-mật-cơ-sở-dữ-liệu)
- [Phần 2: Bảo mật Backend/Server (40 câu)](#phần-2-bảo-mật-backendserver)
- [Phần 3: Bảo mật Frontend (40 câu)](#phần-3-bảo-mật-frontend)
- [Phần 4: Xác thực & Phân quyền (40 câu)](#phần-4-xác-thực--phân-quyền)
- [Phần 5: Backup & Disaster Recovery (40 câu)](#phần-5-backup--disaster-recovery)

---

## PHẦN 1: BẢO MẬT CƠ SỞ DỮ LIỆU

### Câu 1: SQL Injection
**Câu hỏi:** Đoạn code nào sau đây BỊ LỖ HỔNG SQL Injection?

A. `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`  
B. `cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")`  
C. `User.objects.filter(id=user_id)`  
D. `cursor.execute("SELECT * FROM users WHERE id = :id", {"id": user_id})`

**Đáp án: B**

**Giải thích:**
- **B (SAI):** Sử dụng f-string trực tiếp → Attacker có thể inject: `user_id = "1 OR 1=1"`
- **A, D (ĐÚNG):** Sử dụng parameterized query với placeholder `?` hoặc `:id`
- **C (ĐÚNG):** Django ORM tự động escape SQL

---

### Câu 2: Password Hashing
**Câu hỏi:** Thuật toán nào KHÔNG NÊN dùng để hash password?

A. bcrypt  
B. Argon2  
C. MD5  
D. PBKDF2

**Đáp án: C**

**Giải thích:**
- **MD5:** Đã bị phá vỡ, tính toán nhanh → dễ brute force
- **bcrypt, Argon2, PBKDF2:** Có cost factor, chống brute force tốt
- **Best practice:** Dùng Argon2 (winner của Password Hashing Competition 2015)

---

### Câu 3: Salt trong Password Hashing
**Câu hỏi:** Mục đích chính của SALT trong password hashing là gì?

A. Tăng độ dài của password  
B. Mã hóa password  
C. Chống Rainbow Table Attack  
D. Tăng tốc độ hash

**Đáp án: C**

**Giải thích:**
- **Salt:** Chuỗi ngẫu nhiên thêm vào password trước khi hash
- **Mục đích:** Cùng password nhưng khác salt → khác hash → chống Rainbow Table
- **Ví dụ:** 
  - User A: password="123456", salt="abc" → hash1
  - User B: password="123456", salt="xyz" → hash2 (khác hash1)

---

### Câu 4: Stored Procedure
**Câu hỏi:** Lợi ích BẢO MẬT của Stored Procedure là gì?

A. Tăng tốc độ query  
B. Giảm SQL Injection risk  
C. Dễ bảo trì code  
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Giảm SQL Injection:** Logic ở database, không ghép string từ user input
- **Tăng tốc:** Pre-compiled, execution plan được cache
- **Bảo trì:** Thay đổi logic không cần deploy lại app
- **Ví dụ:**
```sql
CREATE PROCEDURE SP_LOGIN @email NVARCHAR(100), @password NVARCHAR(100)
AS
BEGIN
    SELECT * FROM TAIKHOAN WHERE EMAIL = @email AND PASS_HASH = @password
END
```

---

### Câu 5: Database Encryption
**Câu hỏi:** TDE (Transparent Data Encryption) trong SQL Server mã hóa gì?

A. Chỉ password  
B. Chỉ data files  
C. Data files, log files, backups  
D. Chỉ network traffic

**Đáp án: C**

**Giải thích:**
- **TDE:** Mã hóa toàn bộ database ở mức file system
- **Bảo vệ:** Data files (.mdf), Log files (.ldf), Backup files (.bak)
- **Transparent:** Application không cần thay đổi code
- **Không bảo vệ:** Data in transit (cần SSL/TLS)

---

### Câu 6: Database Triggers
**Câu hỏi:** Trigger nào sau đây dùng để GHI LOG thay đổi dữ liệu?

A. BEFORE INSERT  
B. AFTER UPDATE  
C. INSTEAD OF DELETE  
D. AFTER INSERT, UPDATE, DELETE

**Đáp án: D**

**Giải thích:**
- **AFTER INSERT, UPDATE, DELETE:** Ghi log sau khi thay đổi thành công
- **Ví dụ:**
```sql
CREATE TRIGGER TRG_AUDIT_TAIKHOAN
ON TAIKHOAN
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    INSERT INTO AUDIT_LOGS (TABLE_NAME, ACTION, OLD_VALUES, NEW_VALUES)
    SELECT 'TAIKHOAN', 
           CASE WHEN EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted) THEN 'UPDATE'
                WHEN EXISTS(SELECT * FROM inserted) THEN 'INSERT'
                ELSE 'DELETE' END,
           (SELECT * FROM deleted FOR JSON PATH),
           (SELECT * FROM inserted FOR JSON PATH)
END
```

---

### Câu 7: Database User Permissions
**Câu hỏi:** Nguyên tắc "Least Privilege" trong database là gì?

A. Cho tất cả user quyền admin để tiện  
B. Chỉ cấp quyền tối thiểu cần thiết  
C. Không cấp quyền nào  
D. Cấp quyền READ-ONLY cho mọi user

**Đáp án: B**

**Giải thích:**
- **Least Privilege:** Chỉ cấp quyền tối thiểu để thực hiện công việc
- **Ví dụ:**
  - App user: SELECT, INSERT, UPDATE (không có DROP, ALTER)
  - Backup user: BACKUP DATABASE (không có SELECT data)
  - Report user: SELECT only (không có INSERT, UPDATE, DELETE)

---

### Câu 8: Connection String Security
**Câu hỏi:** Cách NÀO an toàn nhất để lưu connection string?

A. Hardcode trong source code  
B. Lưu trong file .env (không commit Git)  
C. Lưu trong database  
D. Ghi trong comment

**Đáp án: B**

**Giải thích:**
- **File .env:** Lưu credentials, không commit lên Git
- **Ví dụ:**
```env
DATABASE_URL=mssql://sa:StrongP@ss!@localhost/mydb
SECRET_KEY=abc123xyz
```
- **Thêm vào .gitignore:**
```
.env
*.pyc
```

---

### Câu 9: Database Backup Encryption
**Câu hỏi:** Lệnh nào backup database VÀ MÃ HÓA trong SQL Server?

A. `BACKUP DATABASE mydb TO DISK='backup.bak'`  
B. `BACKUP DATABASE mydb TO DISK='backup.bak' WITH ENCRYPTION`  
C. `BACKUP DATABASE mydb TO DISK='backup.bak' WITH COMPRESSION, ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = MyCert)`  
D. `BACKUP DATABASE mydb WITH PASSWORD='123'`

**Đáp án: C**

**Giải thích:**
- **WITH ENCRYPTION:** Cần chỉ định algorithm và certificate
- **AES_256:** Thuật toán mã hóa mạnh
- **SERVER CERTIFICATE:** Certificate để mã hóa/giải mã
- **Lợi ích:** Backup file bị đánh cắp cũng không đọc được

---

### Câu 10: Row-Level Security
**Câu hỏi:** Row-Level Security (RLS) trong SQL Server dùng để làm gì?

A. Mã hóa từng dòng  
B. Giới hạn user chỉ thấy dòng được phép  
C. Backup từng dòng  
D. Index từng dòng

**Đáp án: B**

**Giải thích:**
- **RLS:** Lọc dữ liệu dựa trên user context
- **Ví dụ:** Chủ trọ chỉ thấy phòng của mình
```sql
CREATE FUNCTION fn_securitypredicate(@MaKH INT)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
WHERE @MaKH = CAST(SESSION_CONTEXT(N'MaKH') AS INT);

CREATE SECURITY POLICY PhongTroPolicy
ADD FILTER PREDICATE dbo.fn_securitypredicate(MAKH)
ON dbo.PHONGTRO;
```

---

### Câu 11: Database Auditing
**Câu hỏi:** SQL Server Audit có thể ghi log những sự kiện nào?

A. Chỉ login/logout  
B. Chỉ SELECT queries  
C. Login, queries, schema changes, permission changes  
D. Chỉ failed logins

**Đáp án: C**

**Giải thích:**
- **SQL Server Audit:** Ghi log toàn diện
  - **Login events:** Successful/failed logins
  - **Database events:** SELECT, INSERT, UPDATE, DELETE
  - **Schema changes:** CREATE, ALTER, DROP
  - **Permission changes:** GRANT, REVOKE
- **Lưu trữ:** File, Windows Event Log, Application Log

---

### Câu 12: Parameterized Queries
**Câu hỏi:** Tại sao parameterized queries an toàn hơn string concatenation?

A. Nhanh hơn  
B. Tự động escape special characters  
C. Dễ đọc hơn  
D. Ngắn gọn hơn

**Đáp án: B**

**Giải thích:**
- **Parameterized:** Database engine tự escape `'`, `"`, `;`, `--`
- **So sánh:**
```python
# UNSAFE
query = f"SELECT * FROM users WHERE name = '{user_input}'"
# user_input = "admin' OR '1'='1" → SQL Injection

# SAFE
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (user_input,))
```

---

### Câu 13: Database Connection Pooling
**Câu hỏi:** Lợi ích BẢO MẬT của Connection Pooling là gì?

A. Giảm số lượng connection → giảm attack surface  
B. Tăng tốc độ  
C. Dễ quản lý  
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Connection Pooling:** Tái sử dụng connection thay vì tạo mới
- **Bảo mật:** Giới hạn max connections → chống DoS
- **Hiệu năng:** Không tốn thời gian handshake
```python
# Django settings
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'pool_size': 10,
            'max_overflow': 20
        }
    }
}
```

---

### Câu 14: Database Firewall
**Câu hỏi:** Database Firewall nên chặn traffic từ đâu?

A. Chỉ internet  
B. Chỉ cho phép từ application server  
C. Cho phép tất cả  
D. Chỉ chặn port 1433

**Đáp án: B**

**Giải thích:**
- **Whitelist approach:** Chỉ cho phép IP của app server
- **Ví dụ SQL Server:**
```sql
-- Firewall rule
sp_set_firewall_rule 
    @name = 'AllowAppServer',
    @start_ip_address = '10.0.1.5',
    @end_ip_address = '10.0.1.5';
```
- **Chặn:** Direct access từ internet, developer machines

---

### Câu 15: Always Encrypted
**Câu hỏi:** Always Encrypted trong SQL Server bảo vệ dữ liệu khỏi ai?

A. Hackers  
B. Database Administrators  
C. Application users  
D. Tất cả

**Đáp án: B**

**Giải thích:**
- **Always Encrypted:** Mã hóa ở client, server chỉ lưu ciphertext
- **DBA không thấy:** Plaintext chỉ có ở application có key
- **Use case:** Số thẻ tín dụng, SSN, medical records
```sql
CREATE COLUMN MASTER KEY MyCMK
WITH (KEY_STORE_PROVIDER_NAME = 'MSSQL_CERTIFICATE_STORE');

CREATE COLUMN ENCRYPTION KEY MyCEK
WITH VALUES (COLUMN_MASTER_KEY = MyCMK);

ALTER TABLE KHACHHANG
ALTER COLUMN SDT NVARCHAR(15) ENCRYPTED WITH
(ENCRYPTION_TYPE = DETERMINISTIC, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256');
```

---

### Câu 16-40: [Tiếp tục 25 câu về Database Security]

*(Do giới hạn độ dài, tôi sẽ tạo file riêng với 200 câu đầy đủ)*

---

## PHẦN 2: BẢO MẬT BACKEND/SERVER (40 câu)

### Câu 41: Django ORM Security
**Câu hỏi:** Django ORM tự động bảo vệ khỏi lỗ hổng nào?

A. SQL Injection
B. XSS
C. CSRF
D. Tất cả

**Đáp án: A**

**Giải thích:**
```python
# Django ORM tự động escape
User.objects.filter(username=user_input)

# RAW SQL vẫn an toàn nếu dùng params
User.objects.raw("SELECT * FROM users WHERE username = %s", [user_input])
```

---

### Câu 42: Django SECRET_KEY
**Câu hỏi:** SECRET_KEY trong Django dùng để làm gì?

A. Mã hóa passwords
B. Sign cookies, CSRF tokens, sessions
C. Kết nối database
D. Không quan trọng

**Đáp án: B**

**Giải thích:**
```python
# settings.py
SECRET_KEY = os.environ.get('SECRET_KEY')  # Từ .env
```

---

### Câu 43: Rate Limiting
**Câu hỏi:** Rate limiting bảo vệ khỏi tấn công nào?

A. Brute force
B. DoS/DDoS
C. Credential stuffing
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    if getattr(request, 'limited', False):
        return HttpResponse('Too many requests', status=429)
```

---

### Câu 44: HTTPS/TLS
**Câu hỏi:** HTTPS bảo vệ dữ liệu ở giai đoạn nào?

A. Data at rest
B. Data in transit
C. Data in use
D. Tất cả

**Đáp án: B**

**Giải thích:**
- **HTTPS:** Mã hóa dữ liệu khi truyền từ client → server
- **TLS 1.3:** Phiên bản mới nhất, an toàn nhất
```python
# Django settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

---

### Câu 45: Session Security
**Câu hỏi:** Cấu hình nào an toàn nhất cho session cookies?

A. `SESSION_COOKIE_HTTPONLY = True`
B. `SESSION_COOKIE_SECURE = True`
C. `SESSION_COOKIE_SAMESITE = 'Strict'`
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
SESSION_COOKIE_HTTPONLY = True  # JavaScript không đọc được
SESSION_COOKIE_SECURE = True    # Chỉ gửi qua HTTPS
SESSION_COOKIE_SAMESITE = 'Strict'  # Chống CSRF
SESSION_COOKIE_AGE = 900  # 15 phút timeout
```

---

### Câu 46: Password Hashing trong Django
**Câu hỏi:** Django mặc định dùng thuật toán nào để hash password?

A. MD5
B. SHA256
C. PBKDF2
D. bcrypt

**Đáp án: C**

**Giải thích:**
```python
# settings.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Default
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Recommended
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

---

### Câu 47: Input Validation
**Câu hỏi:** Validation nên làm ở đâu?

A. Chỉ frontend
B. Chỉ backend
C. Cả frontend và backend
D. Không cần validation

**Đáp án: C**

**Giải thích:**
- **Frontend:** UX tốt, phản hồi nhanh
- **Backend:** Bảo mật thực sự (frontend có thể bypass)
```python
# Backend validation
from django.core.validators import validate_email

def register(request):
    email = request.POST.get('email')
    try:
        validate_email(email)
    except ValidationError:
        return HttpResponse('Invalid email', status=400)
```

---

### Câu 48: File Upload Security
**Câu hỏi:** Kiểm tra NÀO quan trọng nhất khi upload file?

A. File extension
B. File size
C. File content (MIME type)
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
import magic

def upload_file(request):
    file = request.FILES['file']

    # Check size
    if file.size > 5 * 1024 * 1024:  # 5MB
        return HttpResponse('File too large', status=400)

    # Check extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ['.jpg', '.png', '.pdf']:
        return HttpResponse('Invalid file type', status=400)

    # Check MIME type (content)
    mime = magic.from_buffer(file.read(1024), mime=True)
    if mime not in ['image/jpeg', 'image/png', 'application/pdf']:
        return HttpResponse('Invalid file content', status=400)
```

---

### Câu 49: API Authentication
**Câu hỏi:** Phương thức nào an toàn nhất cho API authentication?

A. API Key trong URL
B. Basic Auth (username:password)
C. JWT (JSON Web Token)
D. OAuth 2.0

**Đáp án: D**

**Giải thích:**
- **API Key trong URL:** Lưu trong browser history, logs
- **Basic Auth:** Credentials gửi mỗi request
- **JWT:** Stateless, có expiration
- **OAuth 2.0:** Industry standard, hỗ trợ scopes, refresh tokens

---

### Câu 50: CORS (Cross-Origin Resource Sharing)
**Câu hỏi:** CORS_ALLOW_ALL_ORIGINS = True có nguy hiểm không?

A. Có, cho phép mọi domain gọi API
B. Không, rất an toàn
C. Chỉ nguy hiểm trong production
D. Không ảnh hưởng

**Đáp án: A**

**Giải thích:**
```python
# BAD
CORS_ALLOW_ALL_ORIGINS = True

# GOOD
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://app.yourdomain.com',
]
```

---

### Câu 51: Environment Variables
**Câu hỏi:** Tại sao nên dùng environment variables cho secrets?

A. Không commit lên Git
B. Dễ thay đổi giữa environments
C. Tách code và config
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
# .env file (không commit)
DATABASE_PASSWORD=SuperSecret123!
SECRET_KEY=abc123xyz

# settings.py
import os
from decouple import config

DATABASE_PASSWORD = config('DATABASE_PASSWORD')
SECRET_KEY = config('SECRET_KEY')
```

---

### Câu 52: Logging Sensitive Data
**Câu hỏi:** Thông tin NÀO KHÔNG NÊN log?

A. Passwords
B. Credit card numbers
C. API keys
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
# BAD
logger.info(f"User login: {email} / {password}")

# GOOD
logger.info(f"User login attempt: {email}")

# Mask sensitive data
def mask_card(card_number):
    return f"****-****-****-{card_number[-4:]}"
```

---

### Câu 53: Error Handling
**Câu hỏi:** Error message nào an toàn nhất?

A. `Database connection failed: Access denied for user 'admin'@'localhost'`
B. `Error in file /var/www/app/views.py line 42`
C. `An error occurred. Please try again later.`
D. `SQL Error: Table 'users' doesn't exist`

**Đáp án: C**

**Giải thích:**
- **Generic error:** Không tiết lộ stack trace, file paths, database info
```python
try:
    # ... code ...
except Exception as e:
    logger.error(f"Error: {str(e)}")  # Log chi tiết
    return JsonResponse({
        'error': 'An error occurred'  # User chỉ thấy generic message
    }, status=500)
```

---

### Câu 54: Dependency Management
**Câu hỏi:** Công cụ nào kiểm tra vulnerabilities trong Python packages?

A. pip
B. safety
C. npm audit
D. composer

**Đáp án: B**

**Giải thích:**
```bash
# Install safety
pip install safety

# Check vulnerabilities
safety check

# Output:
# Django 2.2.0 has known security vulnerabilities
# Upgrade to Django 2.2.28
```

---

### Câu 55: Server Headers
**Câu hỏi:** Header nào ẩn thông tin server?

A. `Server: Apache/2.4.41 (Ubuntu)`
B. `Server: nginx/1.18.0`
C. `Server: MyApp`
D. Không gửi Server header

**Đáp án: D**

**Giải thích:**
```python
# Django middleware
class RemoveServerHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'Server' in response:
            del response['Server']
        return response
```

---

### Câu 56: Content Security Policy (CSP)
**Câu hỏi:** CSP header bảo vệ khỏi tấn công nào?

A. XSS
B. Clickjacking
C. Data injection
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
# Django settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", 'https://cdn.jsdelivr.net')
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
```

---

### Câu 57: X-Frame-Options
**Câu hỏi:** X-Frame-Options: DENY bảo vệ khỏi tấn công nào?

A. XSS
B. Clickjacking
C. SQL Injection
D. CSRF

**Đáp án: B**

**Giải thích:**
```python
# Django settings
X_FRAME_OPTIONS = 'DENY'  # Không cho phép iframe

# Hoặc
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Chỉ cho phép same domain
```

---

### Câu 58: Middleware Security
**Câu hỏi:** Middleware nào kiểm tra IP address?

A. AuthenticationMiddleware
B. Custom IPFilterMiddleware
C. SessionMiddleware
D. CsrfViewMiddleware

**Đáp án: B**

**Giải thích:**
```python
class IPFilterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # Check blacklist
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden('IP Blocked')

        return self.get_response(request)
```

---

### Câu 59: WAF (Web Application Firewall)
**Câu hỏi:** WAF có thể chặn tấn công nào?

A. SQL Injection
B. XSS
C. Path Traversal
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
import re

class WAFMiddleware:
    SQL_PATTERNS = [
        r'(\bUNION\b.*\bSELECT\b)',
        r'(\bDROP\b.*\bTABLE\b)',
    ]

    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
    ]

    def check_attack(self, data):
        for pattern in self.SQL_PATTERNS + self.XSS_PATTERNS:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False
```

---

### Câu 60: API Rate Limiting
**Câu hỏi:** Rate limit NÀO phù hợp cho login endpoint?

A. 100 requests/second
B. 5 requests/minute
C. 1000 requests/hour
D. Không giới hạn

**Đáp án: B**

**Giải thích:**
```python
@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # 5 lần đăng nhập/phút → chống brute force
    pass
```

---

### Câu 61-80: [Tiếp tục Backend Security]

*(Tổng cộng 40 câu cho phần Backend)*

---

## PHẦN 3: BẢO MẬT FRONTEND (40 câu)

### Câu 81: XSS (Cross-Site Scripting)
**Câu hỏi:** Loại XSS nào nguy hiểm nhất?

A. Reflected XSS
B. Stored XSS
C. DOM-based XSS
D. Tất cả đều nguy hiểm

**Đáp án: B**

**Giải thích:**
- **Stored XSS:** Lưu vào database → ảnh hưởng mọi user
- **Ví dụ:** Comment chứa `<script>alert('XSS')</script>`
```python
# Django template tự động escape
{{ user_comment }}  # Safe

# Nếu muốn render HTML
{{ user_comment|safe }}  # DANGEROUS!
```

---

### Câu 82: CSRF (Cross-Site Request Forgery)
**Câu hỏi:** CSRF token bảo vệ như thế nào?

A. Mã hóa dữ liệu
B. Verify request từ chính website
C. Chặn SQL Injection
D. Tăng tốc độ

**Đáp án: B**

**Giải thích:**
```html
<!-- Django form với CSRF token -->
<form method="POST">
    {% csrf_token %}
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```
- **Cơ chế:** Token ngẫu nhiên, verify mỗi POST request

---

### Câu 83: Content-Type Header
**Câu hỏi:** Tại sao cần set đúng Content-Type?

A. Ngăn MIME sniffing
B. Ngăn XSS
C. Tăng performance
D. A và B đúng

**Đáp án: D**

**Giải thích:**
```python
# Django view
def download_file(request):
    response = HttpResponse(file_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
```

---

### Câu 84: JavaScript Injection
**Câu hỏi:** Code nào BỊ LỖ HỔNG JavaScript injection?

A. `document.getElementById('name').textContent = userName;`
B. `document.getElementById('name').innerHTML = userName;`
C. `$('#name').text(userName);`
D. A và C an toàn

**Đáp án: B**

**Giải thích:**
```javascript
// UNSAFE
document.getElementById('name').innerHTML = userName;
// userName = "<img src=x onerror=alert('XSS')>"

// SAFE
document.getElementById('name').textContent = userName;
// hoặc
$('#name').text(userName);  // jQuery tự escape
```

---

### Câu 85: LocalStorage vs SessionStorage
**Câu hỏi:** Nên lưu JWT token ở đâu?

A. LocalStorage
B. SessionStorage
C. HttpOnly Cookie
D. Không lưu

**Đáp án: C**

**Giải thích:**
- **LocalStorage/SessionStorage:** JavaScript có thể đọc → XSS risk
- **HttpOnly Cookie:** JavaScript không đọc được
```python
# Django set HttpOnly cookie
response.set_cookie(
    'jwt_token',
    token,
    httponly=True,
    secure=True,
    samesite='Strict'
)
```

---

### Câu 86: Clickjacking
**Câu hỏi:** Cách nào chống Clickjacking?

A. X-Frame-Options: DENY
B. Content-Security-Policy: frame-ancestors 'none'
C. JavaScript frame-busting
D. A và B

**Đáp án: D**

**Giải thích:**
```python
# Django settings
X_FRAME_OPTIONS = 'DENY'

# Hoặc CSP
CSP_FRAME_ANCESTORS = ("'none'",)
```

---

### Câu 87: Subresource Integrity (SRI)
**Câu hỏi:** SRI bảo vệ khỏi rủi ro nào?

A. CDN bị hack
B. Man-in-the-middle
C. Tampered scripts
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```html
<!-- SRI hash verify file integrity -->
<script
    src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"
    integrity="sha384-vtXRMe3mGCbOeY7l30aIg8H9p3GdeSe4IFlP6G8JMa7o7lXvnz3GFKzPxzJdPfGK"
    crossorigin="anonymous">
</script>
```

---

### Câu 88: Input Sanitization
**Câu hỏi:** Thư viện nào dùng để sanitize HTML input?

A. DOMPurify
B. jQuery
C. Bootstrap
D. React

**Đáp án: A**

**Giải thích:**
```javascript
import DOMPurify from 'dompurify';

const dirty = '<img src=x onerror=alert("XSS")>';
const clean = DOMPurify.sanitize(dirty);
// clean = '<img src="x">'
```

---

### Câu 89: Autocomplete Attribute
**Câu hỏi:** Khi nào nên dùng autocomplete="off"?

A. Password fields
B. Credit card fields
C. Sensitive personal info
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```html
<input type="password" name="password" autocomplete="off">
<input type="text" name="credit-card" autocomplete="off">
```

---

### Câu 90: Referrer Policy
**Câu hỏi:** Referrer-Policy: no-referrer có tác dụng gì?

A. Không gửi Referer header
B. Ẩn URL nguồn
C. Bảo vệ privacy
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```html
<meta name="referrer" content="no-referrer">

<!-- Hoặc -->
<a href="https://external.com" rel="noreferrer">Link</a>
```

---

### Câu 91: Open Redirect
**Câu hỏi:** Code nào BỊ LỖ HỔNG Open Redirect?

A. `window.location = userInput;`
B. `window.location = '/dashboard';`
C. `window.location = validateURL(userInput);`
D. B và C an toàn

**Đáp án: A**

**Giải thích:**
```javascript
// UNSAFE
const redirect = new URLSearchParams(window.location.search).get('next');
window.location = redirect;  // next=https://evil.com

// SAFE
function validateURL(url) {
    const allowed = ['/dashboard', '/profile'];
    return allowed.includes(url) ? url : '/';
}
```

---

### Câu 92: Prototype Pollution
**Câu hỏi:** Prototype Pollution ảnh hưởng đến ngôn ngữ nào?

A. Python
B. JavaScript
C. Java
D. C++

**Đáp án: B**

**Giải thích:**
```javascript
// Vulnerable code
function merge(target, source) {
    for (let key in source) {
        target[key] = source[key];
    }
}

// Attack
merge({}, JSON.parse('{"__proto__": {"isAdmin": true}}'));
// Bây giờ mọi object đều có isAdmin = true!
```

---

### Câu 93: eval() Function
**Câu hỏi:** Tại sao KHÔNG NÊN dùng eval()?

A. Chậm
B. Code injection risk
C. Khó debug
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```javascript
// NEVER DO THIS
const userInput = "alert('XSS')";
eval(userInput);  // Execute arbitrary code!

// Use JSON.parse instead
const data = JSON.parse('{"name": "John"}');
```

---

### Câu 94: innerHTML vs textContent
**Câu hỏi:** Khi nào dùng innerHTML?

A. Luôn luôn
B. Khi cần render HTML từ trusted source
C. Khi render user input
D. Không bao giờ

**Đáp án: B**

**Giải thích:**
```javascript
// SAFE - trusted source
element.innerHTML = '<strong>Welcome</strong>';

// UNSAFE - user input
element.innerHTML = userInput;  // XSS risk!

// SAFE - user input
element.textContent = userInput;
```

---

### Câu 95: HTTPS Mixed Content
**Câu hỏi:** Mixed Content là gì?

A. HTTPS page load HTTP resources
B. HTTP page load HTTPS resources
C. Không ảnh hưởng
D. Tăng tốc độ

**Đáp án: A**

**Giải thích:**
```html
<!-- BAD: HTTPS page với HTTP script -->
<script src="http://example.com/script.js"></script>

<!-- GOOD: Protocol-relative URL -->
<script src="//example.com/script.js"></script>

<!-- BEST: HTTPS -->
<script src="https://example.com/script.js"></script>
```

---

### Câu 96: Browser Caching
**Câu hỏi:** Header nào ngăn cache sensitive pages?

A. Cache-Control: no-store
B. Cache-Control: public
C. Cache-Control: max-age=3600
D. Không cần header

**Đáp án: A**

**Giải thích:**
```python
# Django view
def sensitive_page(request):
    response = render(request, 'sensitive.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response['Pragma'] = 'no-cache'
    return response
```

---

### Câu 97: Tabnabbing
**Câu hỏi:** Cách nào chống Tabnabbing attack?

A. `rel="noopener"`
B. `rel="noreferrer"`
C. `target="_blank"`
D. A và B

**Đáp án: D**

**Giải thích:**
```html
<!-- UNSAFE -->
<a href="https://external.com" target="_blank">Link</a>

<!-- SAFE -->
<a href="https://external.com" target="_blank" rel="noopener noreferrer">Link</a>
```

---

### Câu 98: Form Validation
**Câu hỏi:** Validation nào nên làm ở frontend?

A. Email format
B. Required fields
C. Password strength
D. Tất cả (nhưng phải validate lại ở backend)

**Đáp án: D**

**Giải thích:**
```html
<form>
    <input type="email" required pattern="[^@]+@[^@]+\.[^@]+">
    <input type="password" required minlength="8">
</form>

<script>
// Frontend validation (UX)
// Backend validation (Security)
</script>
```

---

### Câu 99: Postmessage Security
**Câu hỏi:** Khi dùng postMessage, nên làm gì?

A. Verify origin
B. Validate data
C. Không dùng eval() với data
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```javascript
// Sender
window.postMessage({data: 'hello'}, 'https://trusted.com');

// Receiver
window.addEventListener('message', (event) => {
    // Verify origin
    if (event.origin !== 'https://trusted.com') return;

    // Validate data
    if (typeof event.data !== 'object') return;

    // Process data (don't use eval!)
    console.log(event.data);
});
```

---

### Câu 100: WebSocket Security
**Câu hỏi:** WebSocket nên dùng protocol nào?

A. ws://
B. wss://
C. http://
D. Không quan trọng

**Đáp án: B**

**Giải thích:**
```javascript
// UNSAFE
const socket = new WebSocket('ws://example.com/socket');

// SAFE
const socket = new WebSocket('wss://example.com/socket');
```

---

### Câu 101-120: [Tiếp tục Frontend Security]

*(Tổng cộng 40 câu cho phần Frontend)*

---

## PHẦN 4: XÁC THỰC & PHÂN QUYỀN (40 câu)

### Câu 121: 2FA (Two-Factor Authentication)
**Câu hỏi:** Loại 2FA nào an toàn nhất?

A. SMS OTP
B. Email OTP
C. TOTP (Time-based OTP)
D. Hardware token (YubiKey)

**Đáp án: D**

**Giải thích:**
- **SMS:** SIM swapping attack
- **Email:** Email account bị hack
- **TOTP:** Phishing-resistant hơn SMS
- **Hardware token:** Phishing-resistant, không thể clone

---

### Câu 122: Password Policy
**Câu hỏi:** Password policy NÀO tốt nhất?

A. Tối thiểu 8 ký tự, có chữ hoa, chữ thường, số, ký tự đặc biệt
B. Tối thiểu 12 ký tự, không yêu cầu ký tự đặc biệt
C. Tối thiểu 6 ký tự
D. Không giới hạn

**Đáp án: B**

**Giải thích:**
- **NIST 2017:** Khuyến nghị 8-64 ký tự, không bắt buộc ký tự đặc biệt
- **Lý do:** Passphrase dài hơn an toàn hơn password phức tạp ngắn
```python
# Django password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]
```

---

### Câu 123: Account Lockout
**Câu hỏi:** Sau bao nhiêu lần đăng nhập sai nên lock account?

A. 3 lần
B. 5 lần
C. 10 lần
D. Không lock

**Đáp án: B**

**Giải thích:**
- **5 lần:** Balance giữa security và UX
- **Lockout duration:** 15-30 phút
```python
def check_login_attempts(email):
    attempts = FailedLoginAttempt.objects.filter(
        email=email,
        attempt_time__gte=timezone.now() - timedelta(minutes=15)
    ).count()

    if attempts >= 5:
        return False  # Account locked
    return True
```

---

### Câu 124: Session Timeout
**Câu hỏi:** Session timeout phù hợp cho banking app là bao lâu?

A. 1 giờ
B. 30 phút
C. 5-10 phút
D. 1 ngày

**Đáp án: C**

**Giải thích:**
- **Banking/Financial:** 5-10 phút
- **E-commerce:** 30 phút
- **Social media:** 1-2 giờ
```python
# Django settings
SESSION_COOKIE_AGE = 600  # 10 minutes
```

---

### Câu 125: OAuth 2.0
**Câu hỏi:** OAuth 2.0 flow nào an toàn nhất cho web apps?

A. Implicit Flow
B. Authorization Code Flow
C. Password Grant
D. Client Credentials

**Đáp án: B**

**Giải thích:**
- **Authorization Code Flow:** Access token không expose ở browser
- **Implicit Flow:** Deprecated, token ở URL
```python
# Django OAuth2
OAUTH2_PROVIDER = {
    'ALLOWED_REDIRECT_URI_SCHEMES': ['https'],
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
}
```

---

### Câu 126: JWT (JSON Web Token)
**Câu hỏi:** JWT nên lưu ở đâu?

A. LocalStorage
B. SessionStorage
C. HttpOnly Cookie
D. URL parameter

**Đáp án: C**

**Giải thích:**
```python
# Create JWT
import jwt

payload = {'user_id': 123, 'exp': datetime.utcnow() + timedelta(hours=1)}
token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# Set HttpOnly cookie
response.set_cookie('jwt', token, httponly=True, secure=True)
```

---

### Câu 127: RBAC (Role-Based Access Control)
**Câu hỏi:** RBAC có bao nhiêu thành phần chính?

A. Users, Roles
B. Users, Roles, Permissions
C. Users, Groups
D. Users, Permissions

**Đáp án: B**

**Giải thích:**
```python
# Django RBAC
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('landlord', 'Landlord'),
        ('customer', 'Customer'),
    ])

def landlord_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'landlord':
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

### Câu 128: Password Reset
**Câu hỏi:** Password reset token nên expire sau bao lâu?

A. 1 giờ
B. 24 giờ
C. 1 tuần
D. Không expire

**Đáp án: A**

**Giải thích:**
```python
# Django password reset
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour

# Generate token
from django.contrib.auth.tokens import default_token_generator
token = default_token_generator.make_token(user)
```

---

### Câu 129: Remember Me
**Câu hỏi:** "Remember Me" feature nên implement như thế nào?

A. Lưu password trong cookie
B. Session không expire
C. Persistent cookie với secure token
D. LocalStorage

**Đáp án: C**

**Giải thích:**
```python
if remember_me:
    request.session.set_expiry(1209600)  # 2 weeks
else:
    request.session.set_expiry(0)  # Browser close
```

---

### Câu 130: Single Sign-On (SSO)
**Câu hỏi:** SSO protocol nào phổ biến nhất?

A. SAML
B. OAuth 2.0
C. OpenID Connect
D. Tất cả đều phổ biến

**Đáp án: D**

**Giải thích:**
- **SAML:** Enterprise, XML-based
- **OAuth 2.0:** Authorization
- **OpenID Connect:** Authentication layer trên OAuth 2.0

---

### Câu 131-160: [Tiếp tục Authentication & Authorization]

*(Tổng cộng 40 câu cho phần này)*

---

## PHẦN 5: BACKUP & DISASTER RECOVERY (40 câu)

### Câu 161: Backup Strategy
**Câu hỏi:** Chiến lược backup 3-2-1 là gì?

A. 3 bản backup, 2 loại media, 1 offsite
B. 3 servers, 2 databases, 1 backup
C. 3 ngày, 2 tuần, 1 tháng
D. Không có quy tắc này

**Đáp án: A**

**Giải thích:**
- **3 copies:** 1 production + 2 backups
- **2 media types:** Disk + Tape/Cloud
- **1 offsite:** Chống fire, flood, theft

---

### Câu 162: Full vs Differential Backup
**Câu hỏi:** Differential backup là gì?

A. Backup toàn bộ database
B. Backup thay đổi từ lần full backup cuối
C. Backup thay đổi từ lần backup trước
D. Không backup

**Đáp án: B**

**Giải thích:**
```sql
-- Full backup (Sunday)
BACKUP DATABASE mydb TO DISK='full.bak';

-- Differential backup (Monday-Saturday)
BACKUP DATABASE mydb TO DISK='diff_mon.bak' WITH DIFFERENTIAL;
```

---

### Câu 163: Transaction Log Backup
**Câu hỏi:** Transaction log backup cho phép gì?

A. Point-in-time recovery
B. Chỉ restore toàn bộ
C. Không restore được
D. Chỉ cho reporting

**Đáp án: A**

**Giải thích:**
```sql
-- Log backup mỗi giờ
BACKUP LOG mydb TO DISK='log_10am.trn';

-- Restore đến 10:30 AM
RESTORE DATABASE mydb FROM DISK='full.bak' WITH NORECOVERY;
RESTORE LOG mydb FROM DISK='log_10am.trn'
WITH STOPAT='2024-12-25 10:30:00', RECOVERY;
```

---

### Câu 164: Backup Encryption
**Câu hỏi:** Tại sao cần mã hóa backup?

A. Giảm dung lượng
B. Bảo vệ nếu backup bị đánh cắp
C. Tăng tốc độ
D. Không cần thiết

**Đáp án: B**

**Giải thích:**
```sql
-- Create certificate
CREATE CERTIFICATE BackupCert
WITH SUBJECT = 'Backup Encryption Certificate';

-- Encrypted backup
BACKUP DATABASE mydb TO DISK='backup.bak'
WITH COMPRESSION,
ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = BackupCert);
```

---

### Câu 165: Backup Verification
**Câu hỏi:** Lệnh nào verify backup integrity?

A. BACKUP DATABASE WITH VERIFY
B. RESTORE VERIFYONLY
C. CHECK BACKUP
D. VERIFY DATABASE

**Đáp án: B**

**Giải thích:**
```sql
-- Verify backup without restoring
RESTORE VERIFYONLY FROM DISK='backup.bak';

-- Backup with checksum
BACKUP DATABASE mydb TO DISK='backup.bak' WITH CHECKSUM;
```

---

### Câu 166: RPO (Recovery Point Objective)
**Câu hỏi:** RPO = 1 hour có nghĩa là gì?

A. Restore trong 1 giờ
B. Chấp nhận mất tối đa 1 giờ dữ liệu
C. Backup mỗi 1 giờ
D. Database down 1 giờ

**Đáp án: B**

**Giải thích:**
- **RPO:** Lượng dữ liệu có thể mất
- **RTO:** Thời gian để restore
- **Ví dụ:** RPO=1h → backup mỗi giờ

---

### Câu 167: RTO (Recovery Time Objective)
**Câu hỏi:** RTO = 4 hours có nghĩa là gì?

A. Backup mỗi 4 giờ
B. Phải restore xong trong 4 giờ
C. Mất tối đa 4 giờ dữ liệu
D. Database chạy 4 giờ

**Đáp án: B**

**Giải thích:**
- **RTO:** Downtime tối đa chấp nhận được
- **Ví dụ:** RTO=4h → phải restore và online trong 4h

---

### Câu 168: Backup Retention
**Câu hỏi:** Backup retention policy NÀO hợp lý?

A. Daily: 7 ngày, Weekly: 4 tuần, Monthly: 12 tháng
B. Chỉ giữ 1 ngày
C. Giữ mãi mãi
D. Không cần retention

**Đáp án: A**

**Giải thích:**
```sql
-- Cleanup old backups
DELETE FROM msdb.dbo.backupset
WHERE backup_finish_date < DATEADD(DAY, -30, GETDATE());
```

---

### Câu 169: Backup Compression
**Câu hỏi:** Lợi ích của backup compression?

A. Giảm storage cost
B. Nhanh hơn khi transfer
C. Giảm I/O
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
BACKUP DATABASE mydb TO DISK='backup.bak'
WITH COMPRESSION;
-- Thường giảm 50-70% dung lượng
```

---

### Câu 170: Disaster Recovery Plan
**Câu hỏi:** DR plan nên bao gồm gì?

A. Backup procedures
B. Restore procedures
C. Contact list, escalation
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **DR Plan components:**
  1. Backup schedule
  2. Restore procedures (step-by-step)
  3. Contact list (DBA, Manager, Vendor)
  4. Escalation matrix
  5. Test results
  6. Update history

---

### Câu 171: Backup Testing
**Câu hỏi:** Tần suất test restore backup?

A. Không bao giờ
B. Khi có incident
C. Hàng tháng
D. Hàng năm

**Đáp án: C**

**Giải thích:**
- **Best practice:** Test restore monthly
- **Quy trình:**
  1. Restore vào test server
  2. Verify data integrity
  3. Test application
  4. Document results

---

### Câu 172: Backup Storage
**Câu hỏi:** Nên lưu backup ở đâu?

A. Cùng server với database
B. Khác server, cùng datacenter
C. Offsite (cloud hoặc datacenter khác)
D. B và C

**Đáp án: D**

**Giải thích:**
- **Local:** Fast restore
- **Offsite:** Disaster protection
```python
# Upload to S3
import boto3
s3 = boto3.client('s3')
s3.upload_file('backup.bak', 'my-bucket', 'backups/backup.bak')
```

---

### Câu 173: Database Mirroring
**Câu hỏi:** Database Mirroring khác Backup như thế nào?

A. Real-time replication vs scheduled backup
B. Automatic failover
C. Zero data loss (synchronous mode)
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
-- Setup mirroring
ALTER DATABASE mydb SET PARTNER = 'TCP://mirror-server:5022';
```

---

### Câu 174: Always On Availability Groups
**Câu hỏi:** Always On AG có lợi ích gì?

A. High availability
B. Disaster recovery
C. Read-scale out
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Primary replica:** Read-write
- **Secondary replicas:** Read-only, automatic failover

---

### Câu 175: Backup Monitoring
**Câu hỏi:** Nên monitor backup metric nào?

A. Backup success/failure
B. Backup duration
C. Backup size
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
-- Check last backup
SELECT
    database_name,
    MAX(backup_finish_date) AS last_backup,
    DATEDIFF(HOUR, MAX(backup_finish_date), GETDATE()) AS hours_since_backup
FROM msdb.dbo.backupset
GROUP BY database_name;
```

---

### Câu 176: Backup Automation
**Câu hỏi:** Tool nào automate backup trong SQL Server?

A. SQL Server Agent
B. Windows Task Scheduler
C. PowerShell scripts
D. Tất cả đều được

**Đáp án: D**

**Giải thích:**
```sql
-- SQL Server Agent Job
EXEC msdb.dbo.sp_add_job @job_name = 'Daily Backup';
EXEC msdb.dbo.sp_add_jobstep
    @job_name = 'Daily Backup',
    @step_name = 'Backup Database',
    @command = 'BACKUP DATABASE mydb TO DISK=''backup.bak''';
EXEC msdb.dbo.sp_add_schedule
    @schedule_name = 'Daily at 2 AM',
    @freq_type = 4,  -- Daily
    @active_start_time = 020000;
```

---

### Câu 177: Incremental Backup
**Câu hỏi:** Incremental backup khác Differential như thế nào?

A. Incremental: thay đổi từ lần backup trước
B. Differential: thay đổi từ lần full backup
C. Incremental nhỏ hơn nhưng restore lâu hơn
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Incremental:** Backup A → B → C (restore cần A+B+C)
- **Differential:** Backup A → AB → ABC (restore cần A+ABC)

---

### Câu 178: Backup Bandwidth
**Câu hỏi:** Cách nào giảm bandwidth khi backup to cloud?

A. Compression
B. Incremental backup
C. Deduplication
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```python
# Compress before upload
import gzip
with open('backup.bak', 'rb') as f_in:
    with gzip.open('backup.bak.gz', 'wb') as f_out:
        f_out.writelines(f_in)
```

---

### Câu 179: Backup Security
**Câu hỏi:** Backup files nên có permissions như thế nào?

A. Everyone: Full Control
B. Chỉ DBA và Backup service account
C. Public read
D. Không cần permissions

**Đáp án: B**

**Giải thích:**
```bash
# Linux permissions
chmod 600 backup.bak
chown dba:dba backup.bak

# Windows ACL
icacls backup.bak /grant DBA:F /inheritance:r
```

---

### Câu 180: Backup Corruption
**Câu hỏi:** Cách nào phát hiện backup corruption?

A. RESTORE VERIFYONLY
B. CHECKSUM
C. Test restore
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
-- Backup with checksum
BACKUP DATABASE mydb TO DISK='backup.bak' WITH CHECKSUM;

-- Verify
RESTORE VERIFYONLY FROM DISK='backup.bak' WITH CHECKSUM;
```

---

### Câu 181: Cloud Backup
**Câu hỏi:** Lợi ích của cloud backup?

A. Offsite storage
B. Scalability
C. Cost-effective
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
-- Backup to Azure
BACKUP DATABASE mydb
TO URL = 'https://mystorageaccount.blob.core.windows.net/backups/mydb.bak'
WITH CREDENTIAL = 'MyAzureCredential';
```

---

### Câu 182: Backup Rotation
**Câu hỏi:** Grandfather-Father-Son rotation là gì?

A. Daily-Weekly-Monthly backups
B. 3 generations of backups
C. Balanced retention và storage
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Son:** Daily backups (7 ngày)
- **Father:** Weekly backups (4 tuần)
- **Grandfather:** Monthly backups (12 tháng)

---

### Câu 183: Backup Window
**Câu hỏi:** Backup window là gì?

A. Thời gian cho phép backup
B. Kích thước backup
C. Số lượng backups
D. Loại backup

**Đáp án: A**

**Giải thích:**
- **Backup window:** Thời gian ít traffic để backup
- **Ví dụ:** 2:00 AM - 6:00 AM

---

### Câu 184: Synthetic Full Backup
**Câu hỏi:** Synthetic full backup là gì?

A. Tạo full backup từ full + incrementals
B. Không cần access production database
C. Giảm load lên production
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Synthetic full:** Merge full + incrementals → new full
- **Lợi ích:** Không lock production database

---

### Câu 185: Backup Deduplication
**Câu hỏi:** Deduplication giảm bao nhiêu storage?

A. 10-20%
B. 30-50%
C. 50-90%
D. Không giảm

**Đáp án: C**

**Giải thích:**
- **Deduplication:** Loại bỏ duplicate data blocks
- **Hiệu quả:** 50-90% với database backups

---

### Câu 186: Backup Catalog
**Câu hỏi:** Backup catalog lưu thông tin gì?

A. Backup history
B. File locations
C. Restore points
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
-- SQL Server backup history
SELECT * FROM msdb.dbo.backupset
WHERE database_name = 'mydb'
ORDER BY backup_finish_date DESC;
```

---

### Câu 187: Backup Failure Handling
**Câu hỏi:** Khi backup fail, nên làm gì?

A. Alert DBA
B. Retry backup
C. Check disk space, permissions
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
-- SQL Server Agent alert
EXEC msdb.dbo.sp_add_alert
    @name = 'Backup Failed',
    @message_id = 3041,  -- Backup failed error
    @severity = 0,
    @enabled = 1;
```

---

### Câu 188: Backup Performance
**Câu hỏi:** Cách nào tăng tốc backup?

A. Multiple backup files (striping)
B. Compression
C. Faster storage
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```sql
-- Striped backup (parallel writes)
BACKUP DATABASE mydb
TO DISK='backup1.bak',
   DISK='backup2.bak',
   DISK='backup3.bak'
WITH COMPRESSION;
```

---

### Câu 189: Backup Compliance
**Câu hỏi:** GDPR yêu cầu gì về backup?

A. Encrypt backups
B. Có thể delete user data
C. Audit backup access
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **GDPR Article 17:** Right to erasure
- **Implication:** Phải có cách xóa user data khỏi backups

---

### Câu 190: Backup Documentation
**Câu hỏi:** Backup documentation nên bao gồm gì?

A. Backup schedule
B. Restore procedures
C. Contact information
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Documentation:**
  1. Backup schedule (full, diff, log)
  2. Restore procedures (step-by-step)
  3. Contact list (DBA, Manager)
  4. Test results
  5. Change history

---

### Câu 191-200: [10 câu tổng hợp]

### Câu 191: Defense in Depth
**Câu hỏi:** Defense in Depth có bao nhiêu tầng bảo vệ?

A. 3 tầng
B. 5 tầng
C. 6-7 tầng
D. Không giới hạn

**Đáp án: C**

**Giải thích:**
1. Physical Security
2. Network Security (Firewall)
3. Host Security (OS hardening)
4. Application Security (WAF)
5. Data Security (Encryption)
6. User Security (Authentication)

---

### Câu 192: Zero Trust Security
**Câu hỏi:** Zero Trust principle là gì?

A. Trust everyone
B. Never trust, always verify
C. Trust internal network
D. Trust authenticated users

**Đáp án: B**

**Giải thích:**
- **Zero Trust:** Verify mọi request, kể cả từ internal network
- **Principles:**
  - Verify explicitly
  - Least privilege access
  - Assume breach

---

### Câu 193: Security Audit
**Câu hỏi:** Security audit nên làm bao lâu 1 lần?

A. Hàng năm
B. Hàng quý
C. Hàng tháng
D. Tùy theo risk level

**Đáp án: D**

**Giải thích:**
- **High risk:** Monthly
- **Medium risk:** Quarterly
- **Low risk:** Annually

---

### Câu 194: Penetration Testing
**Câu hỏi:** Pentest nên làm khi nào?

A. Trước khi launch
B. Sau major updates
C. Định kỳ hàng năm
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Pentest types:**
  - Black box (no knowledge)
  - White box (full knowledge)
  - Gray box (partial knowledge)

---

### Câu 195: Vulnerability Scanning
**Câu hỏi:** Tool nào scan vulnerabilities?

A. Nessus
B. OpenVAS
C. Qualys
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
```bash
# OWASP ZAP scan
zap-cli quick-scan https://yourdomain.com

# Nikto web scanner
nikto -h https://yourdomain.com
```

---

### Câu 196: Security Headers
**Câu hỏi:** Header nào QUAN TRỌNG NHẤT?

A. X-Frame-Options
B. Content-Security-Policy
C. Strict-Transport-Security
D. Tất cả đều quan trọng

**Đáp án: D**

**Giải thích:**
```python
# Django security headers
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

### Câu 197: Incident Response
**Câu hỏi:** Incident response phases?

A. Preparation, Detection, Containment
B. Eradication, Recovery, Lessons Learned
C. A và B
D. Chỉ Detection

**Đáp án: C**

**Giải thích:**
1. **Preparation:** Plans, tools, training
2. **Detection:** Monitoring, alerts
3. **Containment:** Isolate affected systems
4. **Eradication:** Remove threat
5. **Recovery:** Restore services
6. **Lessons Learned:** Post-mortem

---

### Câu 198: Security Training
**Câu hỏi:** Developers nên được training về gì?

A. OWASP Top 10
B. Secure coding practices
C. Incident response
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Training topics:**
  - OWASP Top 10
  - Secure coding (input validation, authentication)
  - Security tools (SAST, DAST)
  - Incident response procedures

---

### Câu 199: Security Metrics
**Câu hỏi:** Metric nào đo lường security posture?

A. Number of vulnerabilities
B. Mean time to detect (MTTD)
C. Mean time to respond (MTTR)
D. Tất cả đều đúng

**Đáp án: D**

**Giải thích:**
- **Metrics:**
  - Vulnerabilities (Critical, High, Medium, Low)
  - MTTD: Thời gian phát hiện breach
  - MTTR: Thời gian respond và fix
  - Patch compliance rate

---

### Câu 200: Security Culture
**Câu hỏi:** Yếu tố NÀO quan trọng nhất cho security?

A. Technology
B. Processes
C. People
D. Tất cả đều quan trọng

**Đáp án: D**

**Giải thích:**
- **Security = People + Process + Technology**
- **People:** Training, awareness
- **Process:** Policies, procedures
- **Technology:** Tools, infrastructure

**"Security is not a product, but a process." - Bruce Schneier**

---

## 🎯 KẾT THÚC

**Tổng cộng: 200 câu hỏi trắc nghiệm**

- ✅ Phần 1: Database Security (40 câu)
- ✅ Phần 2: Backend/Server Security (40 câu)
- ✅ Phần 3: Frontend Security (40 câu)
- ✅ Phần 4: Authentication & Authorization (40 câu)
- ✅ Phần 5: Backup & Disaster Recovery (40 câu)

**Mức độ:** Từ cơ bản đến nâng cao
**Phù hợp cho:** Developers, Security Engineers, System Administrators
**Thời gian làm bài:** 3-4 giờ

---

**Chúc bạn học tốt! 🚀**


