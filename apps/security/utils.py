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


# ============================================
# SIGNED URL UTILITIES
# ============================================
import time
from django.core.signing import TimestampSigner, BadSignature
from django.urls import reverse


class SignedURLGenerator:
    """Tạo và xác thực signed URLs có thời hạn"""

    def __init__(self, salt='media-file-access'):
        self.signer = TimestampSigner(salt=salt)
        self.default_expiry = getattr(settings, 'SIGNED_URL_EXPIRY', 3600)

    def generate_url(self, file_path, expiry_seconds=None):
        """Tạo signed URL cho file"""
        if expiry_seconds is None:
            expiry_seconds = self.default_expiry

        data = f"{file_path}:{int(time.time())}"
        signed_data = self.signer.sign(data)

        base_url = reverse('security:protected_media', kwargs={'file_path': file_path})
        url = f"{base_url}?token={signed_data}&expires={expiry_seconds}"

        return url

    def verify_token(self, token, max_age_seconds=None):
        """Xác thực token"""
        if max_age_seconds is None:
            max_age_seconds = self.default_expiry

        try:
            data = self.signer.unsign(token, max_age=max_age_seconds)
            file_path = data.split(':')[0]
            return True, file_path
        except (BadSignature, IndexError, ValueError):
            return False, None

    def generate_temporary_link(self, file_path, hours=1):
        """Tạo link tạm thời"""
        return self.generate_url(file_path, expiry_seconds=hours * 3600)


def get_protected_media_url(file_path, expiry_hours=1):
    """Helper function để dùng trong template hoặc view"""
    generator = SignedURLGenerator()
    return generator.generate_temporary_link(file_path, hours=expiry_hours)


def generate_batch_urls(file_paths, expiry_hours=1):
    """Tạo nhiều signed URLs cùng lúc"""
    generator = SignedURLGenerator()
    return {
        path: generator.generate_temporary_link(path, hours=expiry_hours)
        for path in file_paths
    }