# ============================================
# scripts/security_check.py
# ============================================
#!/usr/bin/env python
"""
Security Check Script
Kiểm tra các cấu hình bảo mật
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from apps.security.models import BlockedIP

User = get_user_model()


def check_debug():
    """Kiểm tra DEBUG mode"""
    if settings.DEBUG:
        print("⚠️  DEBUG=True (Không an toàn cho production)")
        return False
    print("✅ DEBUG=False")
    return True


def check_secret_key():
    """Kiểm tra SECRET_KEY"""
    if len(settings.SECRET_KEY) < 50:
        print("⚠️  SECRET_KEY quá ngắn (nên >= 50 ký tự)")
        return False
    if 'django-insecure' in settings.SECRET_KEY:
        print("⚠️  SECRET_KEY chưa được thay đổi")
        return False
    print("✅ SECRET_KEY đủ mạnh")
    return True


def check_allowed_hosts():
    """Kiểm tra ALLOWED_HOSTS"""
    if '*' in settings.ALLOWED_HOSTS:
        print("⚠️  ALLOWED_HOSTS='*' (Không an toàn)")
        return False
    if not settings.ALLOWED_HOSTS:
        print("⚠️  ALLOWED_HOSTS trống")
        return False
    print(f"✅ ALLOWED_HOSTS={settings.ALLOWED_HOSTS}")
    return True


def check_https():
    """Kiểm tra HTTPS"""
    if not settings.SECURE_SSL_REDIRECT:
        print("⚠️  SECURE_SSL_REDIRECT=False")
        return False
    if not settings.SESSION_COOKIE_SECURE:
        print("⚠️  SESSION_COOKIE_SECURE=False")
        return False
    print("✅ HTTPS được bật")
    return True


def check_password_hashers():
    """Kiểm tra password hashers"""
    first_hasher = settings.PASSWORD_HASHERS[0]
    if 'Argon2' not in first_hasher:
        print(f"⚠️  Password hasher không phải Argon2: {first_hasher}")
        return False
    print("✅ Password hashing: Argon2")
    return True


def check_2fa_users():
    """Kiểm tra số user đã bật 2FA"""
    total_users = User.objects.count()
    users_with_2fa = User.objects.filter(is_2fa_enabled=True).count()
    
    if total_users > 0:
        percentage = (users_with_2fa / total_users) * 100
        print(f"ℹ️  Users với 2FA: {users_with_2fa}/{total_users} ({percentage:.1f}%)")
        
        # Kiểm tra admin có bật 2FA không
        admins_without_2fa = User.objects.filter(
            role='admin',
            is_2fa_enabled=False
        ).count()
        
        if admins_without_2fa > 0:
            print(f"⚠️  {admins_without_2fa} admin chưa bật 2FA")
            return False
    
    print("✅ Tất cả admin đã bật 2FA")
    return True


def check_blocked_ips():
    """Kiểm tra số IP bị block"""
    blocked_count = BlockedIP.objects.filter(is_active=True).count()
    print(f"ℹ️  Số IP đang bị block: {blocked_count}")
    return True


def main():
    print("=" * 50)
    print("🔒 SECURITY CHECK")
    print("=" * 50)
    print()
    
    checks = [
        check_debug,
        check_secret_key,
        check_allowed_hosts,
        check_https,
        check_password_hashers,
        check_2fa_users,
        check_blocked_ips,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Lỗi khi chạy {check.__name__}: {e}")
            results.append(False)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"KẾT QUẢ: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ Tất cả checks đều PASS!")
        return 0
    else:
        print("⚠️  Có một số vấn đề cần khắc phục")
        return 1


if __name__ == '__main__':
    sys.exit(main())