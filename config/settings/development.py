# config/settings/development.py
from .base import *

DEBUG = True

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'mssql',  # ✅ ĐÚNG nếu đã cài mssql-django
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '1433'),  # Thêm default port
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;',
        },
    }
}