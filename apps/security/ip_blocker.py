"""
🚫 IP BLOCKING LOGIC
"""

from .models import BlockedIps, FailedLoginAttempts, SecurityLogs
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('apps.security')


def check_ip_blocked(ip_address):
    """Kiểm tra IP có bị block không"""

    # Whitelist
    if ip_address in settings.IP_WHITELIST:
        return False

    try:
        blocked_ip = BlockedIps.objects.get(ip_address=ip_address)
        # Check if block has expired
        if blocked_ip.blocked_until and blocked_ip.blocked_until < timezone.now():
            return False
        return True
    except BlockedIps.DoesNotExist:
        return False


def track_failed_login(ip_address, username_or_email, reason):
    """Theo dõi đăng nhập thất bại"""

    # Save failed attempt
    FailedLoginAttempts.objects.create(
        ip_address=ip_address,
        username_or_email=username_or_email,
        attempt_time=timezone.now()
    )

    # Kiểm tra số lần thất bại trong 1 giờ
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_failures = FailedLoginAttempts.objects.filter(
        ip_address=ip_address,
        attempt_time__gte=one_hour_ago
    ).count()

    # Auto-block nếu quá nhiều lần thất bại
    if recent_failures >= settings.MAX_LOGIN_ATTEMPTS_BEFORE_TEMP_LOCK:
        block_ip(
            ip_address=ip_address,
            reason=f'{recent_failures} failed login attempts in 1 hour',
            duration=timedelta(minutes=15)
        )


def block_ip(ip_address, reason, duration=None):
    """Chặn IP"""

    # Không chặn whitelist
    if ip_address in settings.IP_WHITELIST:
        return False

    blocked_until = None
    if duration:
        blocked_until = timezone.now() + duration

    blocked_ip, created = BlockedIps.objects.update_or_create(
        ip_address=ip_address,
        defaults={
            'reason': reason,
            'blocked_at': timezone.now(),
            'blocked_until': blocked_until,
        }
    )

    # Log
    SecurityLogs.objects.create(
        action_type='ip_blocked',
        ip_address=ip_address,
        old_value=None,
        new_value=reason,
        log_time=timezone.now()
    )

    logger.warning(f"Blocked IP: {ip_address} - Reason: {reason}")

    return True


def unblock_ip(ip_address):
    """Gỡ chặn IP"""
    try:
        BlockedIps.objects.filter(ip_address=ip_address).delete()
        logger.info(f"Unblocked IP: {ip_address}")
        return True
    except Exception as e:
        logger.error(f"Error unblocking IP {ip_address}: {e}")
        return False


def check_ip_reputation(ip_address):
    """Kiểm tra IP reputation từ AbuseIPDB"""

    api_key = getattr(settings, 'ABUSEIPDB_API_KEY', None)
    check_enabled = getattr(settings, 'CHECK_IP_REPUTATION', False)

    if not api_key or not check_enabled:
        return None

    try:
        import requests
        response = requests.get(
            'https://api.abuseipdb.com/api/v2/check',
            headers={'Key': api_key},
            params={'ipAddress': ip_address, 'maxAgeInDays': 90},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json().get('data', {})
            return data

    except Exception as e:
        logger.error(f"Error checking IP reputation: {e}")

    return None