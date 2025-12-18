# ============================================
# config/settings/production.py
# Production settings with maximum security
# ============================================
from .base import *
from .security import *
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# ============================================
# CORE SETTINGS
# ============================================
DEBUG = False

# ============================================
# DATABASE (SQL Server)
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=no;Encrypt=yes;',
        },
        'CONN_MAX_AGE': 60,  # Connection pooling
    }
}

# ============================================
# REDIS CACHE
# ============================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

# ============================================
# STATIC & MEDIA FILES
# ============================================
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# ============================================
# SENTRY ERROR MONITORING
# ============================================
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        send_default_pii=False,  # Don't send user data
        environment='production',
    )

# ============================================
# LOGGING (Console-based for Azure App Service)
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console_security': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'django.security': {
            'handlers': ['console_security'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.security': {
            'handlers': ['console_security'],
            'level': 'INFO',
        },
    },
}

# ============================================
# EMAIL (Production SMTP)
# ============================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'PhongTro.vn <noreply@phongtro.vn>')

# ============================================
# AZURE APPLICATION INSIGHTS
# ============================================
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

if APPLICATIONINSIGHTS_CONNECTION_STRING:
    # Add OpenCensus middleware for request tracking
    MIDDLEWARE.insert(0, 'opencensus.ext.django.middleware.OpencensusMiddleware')

    OPENCENSUS = {
        'TRACE': {
            'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=1.0)',
            'EXPORTER': '''opencensus.ext.azure.trace_exporter.AzureExporter(
                connection_string="{}"
            )'''.format(APPLICATIONINSIGHTS_CONNECTION_STRING),
        }
    }

    # Add Azure handler to logging
    LOGGING['handlers']['azure'] = {
        'level': 'INFO',
        'class': 'opencensus.ext.azure.log_exporter.AzureLogHandler',
        'connection_string': APPLICATIONINSIGHTS_CONNECTION_STRING,
    }
    LOGGING['loggers']['django']['handlers'].append('azure')
    LOGGING['loggers']['apps.security']['handlers'].append('azure')
    LOGGING['loggers']['django.security']['handlers'].append('azure')