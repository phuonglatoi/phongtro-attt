# ============================================
# apps/security/tasks.py - Celery Tasks
# ============================================
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import FailedLoginAttempts, SecurityLogs, AuditLogs, BlockedIps
import logging
from django.db import models

logger = logging.getLogger('apps.security')


@shared_task
def cleanup_old_logs():
    """Xóa logs cũ hàng ngày"""

    # Xóa failed login > 30 ngày
    deleted_failed = FailedLoginAttempts.objects.filter(
        attempt_time__lt=timezone.now() - timedelta(days=30)
    ).delete()

    # Xóa security logs > 90 ngày
    deleted_security = SecurityLogs.objects.filter(
        log_time__lt=timezone.now() - timedelta(days=90)
    ).delete()

    # Xóa audit logs > 180 ngày
    deleted_audit = AuditLogs.objects.filter(
        changed_date__lt=timezone.now() - timedelta(days=180)
    ).delete()

    # Xóa blocked IPs đã hết hạn
    BlockedIps.objects.filter(
        blocked_until__lt=timezone.now()
    ).delete()

    logger.info(f"Cleanup completed: Failed={deleted_failed}, Security={deleted_security}, Audit={deleted_audit}")


@shared_task
def check_suspicious_ips():
    """Kiểm tra IP đáng ngờ"""
    from .ip_blocker import check_ip_reputation, block_ip

    # Lấy IPs có nhiều failed attempts trong 1 giờ qua
    one_hour_ago = timezone.now() - timedelta(hours=1)
    suspicious_ips = FailedLoginAttempts.objects.filter(
        attempt_time__gte=one_hour_ago
    ).values('ip_address').annotate(count=models.Count('ip_address')).filter(count__gte=5)

    for item in suspicious_ips:
        ip = item['ip_address']

        # Check reputation
        reputation = check_ip_reputation(ip)

        if reputation and reputation.get('abuseConfidenceScore', 0) > 50:
            # Auto-block
            block_ip(
                ip_address=ip,
                reason=f"Suspicious IP - Abuse score: {reputation['abuseConfidenceScore']}",
                duration=timedelta(hours=24)
            )