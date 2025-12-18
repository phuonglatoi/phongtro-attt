# ============================================
# apps/security/middleware/audit.py
# ============================================

from django.utils import timezone
from apps.accounts.models import AuditLogs
from apps.accounts.security import get_client_ip
import logging

logger = logging.getLogger('apps.security')


class AuditMiddleware:
    """
    Middleware ghi log các hành động quan trọng
    """

    AUDITABLE_PATHS = [
        '/admin/',
        '/accounts/password-change/',
        '/accounts/2fa/',
        '/rooms/create/',
        '/rooms/delete/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = timezone.now()

        response = self.get_response(request)

        # Chỉ log nếu user đã đăng nhập và path cần audit
        makh = request.session.get('makh')
        if makh and any(request.path.startswith(path) for path in self.AUDITABLE_PATHS):
            try:
                duration_ms = round((timezone.now() - start_time).total_seconds() * 1000, 2)

                AuditLogs.objects.create(
                    table_name='REQUEST',
                    action=request.method,
                    changed_by=request.session.get('user_email', str(makh)),
                    old_data=request.path,
                    new_data=f"status={response.status_code}, duration={duration_ms}ms"
                )
            except Exception as e:
                logger.error(f"Error creating audit log: {e}")

        return response
