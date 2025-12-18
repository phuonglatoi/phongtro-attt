# ============================================
# config/celery.py
# ============================================
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('phongtro')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'cleanup-old-logs': {
        'task': 'apps.security.tasks.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    },
    'check-ip-reputation': {
        'task': 'apps.security.tasks.check_suspicious_ips',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}