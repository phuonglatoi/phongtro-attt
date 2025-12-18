# ============================================
# apps/accounts/security.py
# Security utilities for the accounts app
# ============================================

from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import FailedLoginAttempts, BlockedIps, SecurityLogs, Taikhoan
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Lấy IP của client từ request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def check_ip_blocked(ip_address):
    """Kiểm tra IP có bị chặn không"""
    try:
        blocked = BlockedIps.objects.filter(
            ip_address=ip_address
        ).first()
        
        if blocked:
            # Check if block has expired
            if blocked.blocked_until and blocked.blocked_until < timezone.now():
                blocked.delete()
                return False
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking blocked IP: {e}")
        return False


def log_failed_login(ip_address, email, user_agent=None):
    """Ghi log đăng nhập thất bại và tự động chặn IP nếu cần"""
    try:
        # Log the failed attempt
        FailedLoginAttempts.objects.create(
            ip_address=ip_address,
            username_or_email=email,
            user_agent=user_agent
        )
        
        # Count failed attempts in the last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        fail_count = FailedLoginAttempts.objects.filter(
            ip_address=ip_address,
            attempt_time__gte=one_hour_ago
        ).count()
        
        # Auto-block IP if 10+ failures in 1 hour
        if fail_count >= 10:
            if not BlockedIps.objects.filter(ip_address=ip_address).exists():
                BlockedIps.objects.create(
                    ip_address=ip_address,
                    reason='Too many failed login attempts',
                    blocked_until=timezone.now() + timedelta(minutes=30)
                )
                log_security_event('IP_AUTO_BLOCKED', None, ip_address, 
                                  f'IP blocked after {fail_count} failed attempts')
                
    except Exception as e:
        logger.error(f"Error logging failed login: {e}")


def log_security_event(action_type, taikhoan, ip_address, details=None):
    """Ghi log sự kiện bảo mật"""
    try:
        SecurityLogs.objects.create(
            action_type=action_type,
            matk=taikhoan,
            ip_address=ip_address,
            details=details
        )
    except Exception as e:
        logger.error(f"Error logging security event: {e}")


def lock_account(taikhoan, minutes=15):
    """Khóa tài khoản"""
    taikhoan.is_locked = True
    taikhoan.lock_time = timezone.now() + timedelta(minutes=minutes)
    taikhoan.save()


def unlock_account(taikhoan):
    """Mở khóa tài khoản"""
    taikhoan.is_locked = False
    taikhoan.lock_time = None
    taikhoan.failed_login_count = 0
    taikhoan.save()


def check_account_locked(taikhoan):
    """Kiểm tra tài khoản có bị khóa không"""
    if not taikhoan.is_locked:
        return False
    
    # Check if lock has expired
    if taikhoan.lock_time and taikhoan.lock_time < timezone.now():
        unlock_account(taikhoan)
        return False
    
    return True


def increment_failed_login(taikhoan, ip_address):
    """Tăng số lần đăng nhập thất bại và khóa nếu vượt ngưỡng"""
    taikhoan.failed_login_count = (taikhoan.failed_login_count or 0) + 1
    taikhoan.save()
    
    # Lock account after 5 failed attempts
    if taikhoan.failed_login_count >= 5:
        lock_account(taikhoan, minutes=15)
        log_security_event('ACCOUNT_LOCKED', taikhoan, ip_address,
                          f'Account locked after {taikhoan.failed_login_count} failed attempts')
        return True
    return False


def reset_failed_login(taikhoan):
    """Reset số lần đăng nhập thất bại"""
    taikhoan.failed_login_count = 0
    taikhoan.save()


def cleanup_old_security_data():
    """Xóa dữ liệu bảo mật cũ"""
    try:
        # Delete failed attempts older than 7 days
        cutoff = timezone.now() - timedelta(days=7)
        FailedLoginAttempts.objects.filter(attempt_time__lt=cutoff).delete()
        
        # Delete expired blocked IPs
        BlockedIps.objects.filter(blocked_until__lt=timezone.now()).delete()
        
        # Delete security logs older than 180 days
        cutoff = timezone.now() - timedelta(days=180)
        SecurityLogs.objects.filter(log_time__lt=cutoff).delete()
        
    except Exception as e:
        logger.error(f"Error cleaning up security data: {e}")

