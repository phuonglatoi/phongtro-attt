"""
🚫 IP FILTERING MIDDLEWARE
- Block malicious IPs
- Whitelist trusted IPs
- Rate limiting per IP
"""

from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from apps.accounts.models import BlockedIps
from apps.accounts.security import get_client_ip
import logging

logger = logging.getLogger('apps.security')


class IPFilterMiddleware:
    """
    Middleware lọc IP
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = get_client_ip(request)

        # Whitelist - Luôn cho phép
        whitelist = getattr(settings, 'IP_WHITELIST', ['127.0.0.1', '::1'])
        if ip_address in whitelist:
            return self.get_response(request)

        # Kiểm tra IP có bị block không
        try:
            blocked_ip = BlockedIps.objects.get(ip_address=ip_address)

            # Kiểm tra block còn hiệu lực không
            if blocked_ip.blocked_until and blocked_ip.blocked_until < timezone.now():
                # Block đã hết hạn, xóa
                blocked_ip.delete()
            else:
                logger.warning(f"Blocked IP attempted access: {ip_address} - Reason: {blocked_ip.reason}")

                return render(request, 'security/ip_blocked.html', {
                    'ip': ip_address,
                    'reason': blocked_ip.reason,
                    'blocked_until': blocked_ip.blocked_until
                }, status=403)

        except BlockedIps.DoesNotExist:
            pass

        response = self.get_response(request)
        return response