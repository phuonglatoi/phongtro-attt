# ============================================
# config/settings/base.py
# ============================================

import os
from pathlib import Path
from decouple import config
from django.contrib.messages import constants as messages

# Base dir
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ======================================================
# SECURITY
# ======================================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# CSRF Trusted Origins (cho ngrok và production)
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]


# ======================================================
# APPLICATIONS
# ======================================================

INSTALLED_APPS = [
    # Local apps (để trước tránh lỗi import)
    'apps.accounts',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third party
    'rest_framework',
    'django_ratelimit',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_recaptcha',

    # Local apps
    'apps.rooms',
    'apps.bookings',
    'apps.reviews',
    'apps.notifications',
    'apps.chat',
    'apps.security',
    'apps.core',

    'django.contrib.humanize',
]

# ⭐ khai báo đúng 1 lần duy nhất
AUTH_USER_MODEL = 'auth.User'


# ======================================================
# MIDDLEWARE
# ======================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # custom middleware
    'apps.security.middleware.ip_filter.IPFilterMiddleware',
    # 'apps.security.middleware.waf.WAFMiddleware',
    'apps.security.middleware.audit.AuditMiddleware',
    'apps.security.middleware.device_tracking.DeviceTrackingMiddleware',
]

ROOT_URLCONF = 'config.urls'


# ======================================================
# TEMPLATE ENGINE
# ======================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'

SITE_ID = 1


# ======================================================
# LANGUAGE + TIMEZONE
# ======================================================

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True


# ======================================================
# STATIC & MEDIA FILES
# ======================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================================
# CRISPY FORMS
# ======================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ======================================================
# DRF SETTINGS
# ======================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '100/minute',
    }
}


# ======================================================
# RATE LIMIT
# ======================================================

RATELIMIT_LOGIN = '5/m'
RATELIMIT_REGISTER = '5/m'
RATELIMIT_ENABLE = True

SILENCED_SYSTEM_CHECKS = [
    'django_ratelimit.E003',
    'django_ratelimit.W001',
]


# ======================================================
# WAF CONFIG
# ======================================================

WAF_ENABLED = True

# WAF_BLOCK_PATTERNS = {
#     'sql_injection': [
#         r"union.*select",
#         r"xp_cmdshell",
#         r"DROP TABLE",
#         r"INSERT INTO",
#     ],
#     'xss': [
#         r"<script>",
#         r"javascript:",
#         r"alert\(",
#         r"onload=",
#     ],
#     'path_traversal': [
#         r"\.\./",
#         r"etc/passwd",
#         r"win\.ini",
#     ],
#     'cmd_injection': [
#         r"cmd\.exe",
#         r"bash -i",
#     ]
# }


# ======================================================
# IP FILTER
# ======================================================

IP_FILTER_ENABLED = True

IP_WHITELIST = [
    '127.0.0.1',
    '::1',
]

IP_BLACKLIST = []


MAX_LOGIN_ATTEMPTS_BEFORE_CAPTCHA = 5

SECURITY_EMAIL_ALERTS = {
    'new_device': True,
    'failed_login': True,
    'password_change': True,
    'suspicious_activity': True,
}


# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', 'noreply@phongtro.vn')


MAX_LOGIN_ATTEMPTS_BEFORE_TEMP_LOCK = 5
TEMP_LOCK_DURATION_MINUTES = 15


# ======================================================
# RECAPTCHA TEST KEYS
# ======================================================

RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']


# Thêm các mã lỗi này vào list đã có của bạn
SILENCED_SYSTEM_CHECKS = [
    'django_recaptcha.recaptcha_test_key_error',
    'models.W043',
    'django_ratelimit.E003',  # Ẩn lỗi Cache không dùng chung
    'django_ratelimit.W001',  # Ẩn cảnh báo Cache không hỗ trợ
]

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}