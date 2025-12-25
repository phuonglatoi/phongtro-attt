# config/settings/development.py
from .base import *

DEBUG = True

# Debug Toolbar - Đã tắt để không hiển thị sidebar
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

INTERNAL_IPS = ['127.0.0.1']

# Tắt Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# ============================================
# 🔓 DEVELOPMENT SECURITY OVERRIDES
# ============================================
# Tắt HTTPS requirement cho development (localhost)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Session timeout dài hơn cho development (1 giờ)
SESSION_COOKIE_AGE = 3600

# Database configuration
db_user = os.getenv('DB_USER', '')
db_password = os.getenv('DB_PASSWORD', '')

# Use Windows Auth if no user/password provided
if db_user and db_password:
    extra_params = 'TrustServerCertificate=yes;'
else:
    extra_params = 'TrustServerCertificate=yes;Trusted_Connection=yes;'

if db_user and db_password:
    base_params = 'TrustServerCertificate=yes;'
else:
    base_params = 'TrustServerCertificate=yes;Trusted_Connection=yes;'

full_extra_params = base_params + 'ColumnEncryption=Enabled;'

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': db_user if db_user else None,
        'PASSWORD': db_password if db_password else None,
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': full_extra_params, # Dùng chuỗi tổng hợp ở đây
        },
    }
}