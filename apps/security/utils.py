# ============================================
# apps/security/utils.py
# ============================================

import requests
from django.conf import settings
import logging

logger = logging.getLogger('apps.security')


def get_client_ip(request):
    """
    Lấy địa chỉ IP của người dùng từ Request.
    Hỗ trợ proxy (X-Forwarded-For header).
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def verify_recaptcha(token):
    """
    Xác thực reCAPTCHA token với Google API.
    """
    if not token:
        return False

    secret_key = getattr(settings, 'RECAPTCHA_PRIVATE_KEY', None)
    if not secret_key:
        # Nếu không có secret key, bỏ qua kiểm tra
        return True

    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': token
            },
            timeout=5
        )

        result = response.json()

        if result.get('success'):
            required_score = getattr(settings, 'RECAPTCHA_REQUIRED_SCORE', 0.5)
            score = result.get('score', 1.0)
            return score >= required_score

        return False

    except Exception as e:
        logger.error(f"Error verifying reCAPTCHA: {e}")
        return True  # Cho phép nếu có lỗi kết nối