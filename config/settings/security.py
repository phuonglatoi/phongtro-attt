"""
🔐 CẤU HÌNH BẢO MẬT TOÀN DIỆN
Bao gồm: CAPTCHA, 2FA, OAuth, Rate Limiting, IP Blocking, WAF
"""

import os
from datetime import timedelta
from decouple import config

# ============================================
# 🔑 DJANGO SECRET & DEBUG
# ============================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# ============================================
# 🔐 PASSWORD HASHING (Argon2)
# ============================================
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Mạnh nhất
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# ============================================
# 🔒 PASSWORD VALIDATION
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}  # ✨ Tăng từ 8 lên 12
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# 🍪 SESSION & COOKIE SECURITY
# ============================================
SESSION_COOKIE_SECURE = True          # Chỉ qua HTTPS
SESSION_COOKIE_HTTPONLY = True        # Không cho JS đọc
SESSION_COOKIE_SAMESITE = 'Strict'    # Chống CSRF
SESSION_COOKIE_AGE = 900              # 15 phút timeout
SESSION_SAVE_EVERY_REQUEST = True     # Làm mới session
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Redis session backend (nhanh hơn DB)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_FAILURE_VIEW = 'apps.core.views.csrf_failure'

# ============================================
# 🔐 HTTPS & SECURITY HEADERS
# ============================================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 năm
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ============================================
# 🛡️ CONTENT SECURITY POLICY (CSP)
# ============================================
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Cần cho reCAPTCHA
    "https://www.google.com/recaptcha/",
    "https://www.gstatic.com/recaptcha/",
    "https://accounts.google.com/gsi/",  # Google OAuth
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https:",  # Cho ảnh từ Google avatar
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
)
CSP_FRAME_SRC = (
    "https://www.google.com/recaptcha/",
    "https://accounts.google.com/",
)
CSP_CONNECT_SRC = ("'self'", "https://www.google-analytics.com")

# ============================================
# 🤖 GOOGLE reCAPTCHA v3 (Optional)
# ============================================
RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY', default='')
RECAPTCHA_REQUIRED_SCORE = 0.5  # Điểm ngưỡng (0.0 - 1.0)

# Flag to check if reCAPTCHA is configured
RECAPTCHA_ENABLED = bool(RECAPTCHA_PUBLIC_KEY and RECAPTCHA_PRIVATE_KEY)

# Khi nào bắt buộc CAPTCHA
CAPTCHA_REQUIRED_FOR = [
    'login',          # Luôn luôn
    'register',       # Luôn luôn
    'password_reset', # Luôn luôn
]

# ============================================
# 🔐 TWO-FACTOR AUTHENTICATION (2FA)
# ============================================
OTP_TOTP_ISSUER = 'PhongTro.vn'
OTP_TOTP_TOKEN_VALIDITY = 30 # 30 giây

# 2FA bắt buộc cho
MANDATORY_2FA_ROLES = ['admin', 'moderator']

# Số backup codes
BACKUP_CODES_COUNT = 10

# ============================================
# 🌐 GOOGLE OAUTH 2.0 (Optional)
# ============================================
GOOGLE_OAUTH_CLIENT_ID = config('GOOGLE_OAUTH_CLIENT_ID', default='')
GOOGLE_OAUTH_CLIENT_SECRET = config('GOOGLE_OAUTH_CLIENT_SECRET', default='')

# Only configure OAuth if credentials are provided
if GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': [
                'profile',
                'email',
            ],
            'AUTH_PARAMS': {
                'access_type': 'online',
            },
            'APP': {
                'client_id': GOOGLE_OAUTH_CLIENT_ID,
                'secret': GOOGLE_OAUTH_CLIENT_SECRET,
                'key': ''
            }
        }
    }
else:
    SOCIALACCOUNT_PROVIDERS = {}

# Django-allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Google đã verify

# ============================================
# ⏱️ RATE LIMITING
# ============================================
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Giới hạn cụ thể cho từng action
RATELIMIT_LOGIN = '5/m'        # 5 lần/phút
RATELIMIT_REGISTER = '3/10m'   # 3 lần/10 phút
RATELIMIT_API = '60/m'         # 60 request/phút
RATELIMIT_UPLOAD = '10/h'      # 10 file/giờ
RATELIMIT_COMMENT = '10/h'     # 10 comment/giờ
RATELIMIT_REPORT = '5/d'       # 5 report/ngày

# ============================================
# 🚫 LOGIN ATTEMPT TRACKING
# ============================================
# Sau X lần sai
MAX_LOGIN_ATTEMPTS_BEFORE_CAPTCHA = 3   # Hiện CAPTCHA
MAX_LOGIN_ATTEMPTS_BEFORE_TEMP_LOCK = 5 # Khóa tạm 15 phút
MAX_LOGIN_ATTEMPTS_BEFORE_LOCK = 10     # Khóa tài khoản

# Thời gian khóa
TEMP_LOCK_DURATION = timedelta(minutes=15)
FAILED_LOGIN_RESET_TIME = timedelta(hours=1)

# ============================================
# 🌍 IP TRACKING & BLOCKING
# ============================================
# IP Geolocation
# BASE_DIR cần được import từ settings.base nếu file này được import vào đó
# Giả sử GEOIP_PATH đã được định nghĩa hoặc hardcode tạm
GEOIP_PATH = 'geoip' 
GEOIP2_DATABASE = os.path.join(GEOIP_PATH, 'GeoLite2-City.mmdb')

# IP Reputation Check
ABUSEIPDB_API_KEY = config('ABUSEIPDB_API_KEY', default='')
CHECK_IP_REPUTATION = True

# Auto-block IP nếu
AUTO_BLOCK_IP_CONDITIONS = {
    'failed_logins': 10,         # 10 lần login sai
    'spam_posts': 20,            # 20 bài đăng trong 1 giờ
    'suspicious_requests': 100,  # 100 request bất thường/phút
}

# Whitelist IPs (không bao giờ block)
IP_WHITELIST = config('IP_WHITELIST', default='127.0.0.1').split(',')

# Blacklist IPs (luôn block)
IP_BLACKLIST = []  # Sẽ load từ DB

# ============================================
# 📊 AUDIT LOGGING
# ============================================
AUDIT_LOG_ENABLED = True
AUDIT_LOG_ACTIONS = [
    'login', 'logout', 'login_failed',
    'password_change', 'password_reset',
    '2fa_enabled', '2fa_disabled',
    'profile_update',
    'post_create', 'post_update', 'post_delete',
    'file_upload', 'file_delete',
    'admin_access',
    'suspicious_activity',
]

# ============================================
# 🔍 DEVICE FINGERPRINTING
# ============================================
TRACK_USER_DEVICES = True
MAX_CONCURRENT_SESSIONS = 3 # Tối đa 3 thiết bị cùng lúc
ALERT_ON_NEW_DEVICE = True  # Email cảnh báo khi đăng nhập từ thiết bị mới

# ============================================
# 📧 EMAIL SECURITY ALERTS
# ============================================
SECURITY_EMAIL_ALERTS = {
    'new_device_login': True,
    'password_changed': True,
    '2fa_disabled': True,
    'account_locked': True,
    'suspicious_activity': True,
}

# ============================================
# 📁 FILE UPLOAD SECURITY
# ============================================
# Max upload size
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Allowed extensions
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
ALLOWED_DOCUMENT_EXTENSIONS = ['pdf']

# Scan files for malware (nếu có ClamAV)
SCAN_UPLOADED_FILES = config('SCAN_UPLOADED_FILES', default=False, cast=bool)

# Không cho execute trong media/
MEDIA_ROOT_PERMISSIONS = 0o755  # rwxr-xr-x (no execute for files)

# ============================================
# 🛡️ WEB APPLICATION FIREWALL (WAF)
# ============================================
WAF_ENABLED = True

# Patterns to block
WAF_BLOCK_PATTERNS = {
    'sql_injection': [
        r"(\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/|;)",
        r"(\bOR\b.*=.*|AND\b.*=.*)",
    ],
    'xss': [
        r"(<script|<iframe|<object|<embed|javascript:)",
        r"(onerror|onload|onclick|onmouseover)=",
    ],
    'path_traversal': [
        r"(\.\./|\.\.\\)",
        r"(/etc/passwd|/etc/shadow|C:\\Windows)",
    ],
    'command_injection': [
        r"(;|\||&|`|\$\(|\${)",
        r"(\bcat\b|\bls\b|\bwhoami\b|\bpwd\b)",
    ],
}