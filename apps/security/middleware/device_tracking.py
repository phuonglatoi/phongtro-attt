"""
📱 DEVICE TRACKING MIDDLEWARE
- Track user devices
- Detect suspicious logins
"""

from django.utils import timezone
import logging

logger = logging.getLogger('apps.security')


def get_client_ip(request):
    """Get client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class DeviceTrackingMiddleware:
    """
    Middleware theo dõi thiết bị.
    Sử dụng session-based tracking.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Kiểm tra đăng nhập qua session custom
        makh = request.session.get('makh')

        if makh:
            try:
                from apps.accounts.models import Khachhang
                # Lấy khách hàng và gắn vào request để tiện sử dụng
                khachhang = Khachhang.objects.select_related('matk', 'mavt').get(makh=makh)
                request.khachhang = khachhang

                # Cập nhật thông tin vào session
                ip_address = get_client_ip(request)
                request.session['last_ip'] = ip_address
                request.session['last_activity'] = timezone.now().isoformat()

            except Khachhang.DoesNotExist:
                # Session không hợp lệ, xóa
                request.session.flush()
                request.khachhang = None
        else:
            request.khachhang = None

        response = self.get_response(request)
        return response