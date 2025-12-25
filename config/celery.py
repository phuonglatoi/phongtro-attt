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
    # Database backup - Hàng ngày lúc 2:00 AM
    'backup-database-daily': {
        'task': 'backup_database_task',
        'schedule': crontab(hour=2, minute=0),
    },

    # Cleanup old logs - Hàng ngày lúc 3:00 AM
    'cleanup-old-logs-daily': {
        'task': 'cleanup_old_logs_task',
        'schedule': crontab(hour=3, minute=0),
    },

    # Database health check - Mỗi giờ
    'check-database-health': {
        'task': 'check_database_health_task',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },

    # Check suspicious IPs - Mỗi 30 phút
    'check-ip-reputation': {
        'task': 'apps.security.tasks.check_suspicious_ips',
        'schedule': crontab(minute='*/30'),
    },
}