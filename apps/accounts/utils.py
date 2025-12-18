# ============================================
# apps/accounts/utils.py
# ============================================

import requests
import hashlib
import json
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from user_agents import parse
import logging

logger = logging.getLogger('apps.accounts')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    
    return {
        'device_type': (
            'mobile' if user_agent.is_mobile else
            'pc' if user_agent.is_pc else
            'tablet'
        ),
        'device_brand': user_agent.device.brand or '',
        'device_model': user_agent.device.model or '',
        'os_family': user_agent.os.family or '',
        'browser_family': user_agent.browser.family or '',
    }


def generate_device_fingerprint(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    
    data = f"{user_agent}|{accept_language}|{accept_encoding}"
    
    return hashlib.sha256(data.encode()).hexdigest()


def get_geolocation(ip_address):
    try:
        if hasattr(settings, 'GEOIP2_DATABASE'):
            import geoip2.database
            reader = geoip2.database.Reader(settings.GEOIP2_DATABASE)
            response = reader.city(ip_address)
            
            return {
                'country': response.country.name or '',
                'city': response.city.name or '',
                'latitude': response.location.latitude,
                'longitude': response.location.longitude,
            }
        
        response = requests.get(
            f'https://ipapi.co/{ip_address}/json/',
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'country': data.get('country_name', ''),
                'city': data.get('city', ''),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
            }
    
    except Exception as e:
        logger.error(f"Error getting geolocation for {ip_address}: {e}")
    
    return {
        'country': '',
        'city': '',
        'latitude': None,
        'longitude': None,
    }


def verify_recaptcha(token):
    """
    Verify reCAPTCHA token. Returns True if:
    - reCAPTCHA is not configured (optional feature)
    - Token is valid and score meets threshold
    """
    # If reCAPTCHA is not configured, skip verification
    secret_key = getattr(settings, 'RECAPTCHA_PRIVATE_KEY', '')
    if not secret_key:
        return True

    if not token:
        return False

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
            score = result.get('score', 0)
            required_score = getattr(settings, 'RECAPTCHA_REQUIRED_SCORE', 0.5)
            return score >= required_score

        return False

    except Exception as e:
        logger.error(f"Error verifying reCAPTCHA: {e}")
        return True  # Allow if verification fails (connection error)


def send_security_alert_email(khachhang, alert_type, context=None):
    """
    Gửi email cảnh báo bảo mật.

    Args:
        khachhang: Đối tượng Khachhang
        alert_type: Loại cảnh báo
        context: Thông tin bổ sung
    """
    security_alerts = getattr(settings, 'SECURITY_EMAIL_ALERTS', {})
    if not security_alerts.get(alert_type, True):
        return

    # Lấy email từ khachhang
    recipient_email = khachhang.email if khachhang else None
    if not recipient_email:
        logger.warning(f"Cannot send security alert: no email for khachhang")
        return

    context = context or {}
    context['khachhang'] = khachhang
    context['user_name'] = khachhang.hoten if khachhang else 'User'

    templates = {
        'new_device_login': {
            'subject': '[Cảnh báo] Đăng nhập từ thiết bị mới',
            'template': 'emails/security/new_device.html'
        },
        'password_changed': {
            'subject': '[Cảnh báo] Mật khẩu đã được thay đổi',
            'template': 'emails/security/password_changed.html'
        },
        '2fa_enabled': {
            'subject': '[Thông báo] 2FA đã được bật',
            'template': 'emails/security/2fa_enabled.html'
        },
        '2fa_disabled': {
            'subject': '[Cảnh báo] 2FA đã được tắt',
            'template': 'emails/security/2fa_disabled.html'
        },
        'account_locked': {
            'subject': '[Cảnh báo] Tài khoản bị khóa',
            'template': 'emails/security/account_locked.html'
        },
        'suspicious_activity': {
            'subject': '[Cảnh báo] Hoạt động đăng nhập đáng ngờ',
            'template': 'emails/security/suspicious.html'
        },
    }

    alert = templates.get(alert_type)
    if not alert:
        return

    try:
        html_message = render_to_string(alert['template'], context)

        send_mail(
            subject=alert['subject'],
            message='',
            html_message=html_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phongtro.vn'),
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        logger.info(f"Sent {alert_type} email to {recipient_email}")

    except Exception as e:
        logger.error(f"Error sending security alert email: {e}")


def send_otp_email(khachhang, otp_code, purpose='password_reset'):
    """
    Gửi email OTP.

    Args:
        khachhang: Đối tượng Khachhang
        otp_code: Mã OTP
        purpose: Mục đích (password_reset, verify_email, etc.)
    """
    recipient_email = khachhang.email if khachhang else None
    if not recipient_email:
        logger.warning(f"Cannot send OTP: no email for khachhang")
        return False

    context = {
        'khachhang': khachhang,
        'user_name': khachhang.hoten if khachhang else 'User',
        'otp_code': otp_code,
        'purpose': purpose,
        'valid_minutes': 10
    }

    try:
        html_message = render_to_string('emails/otp.html', context)

        send_mail(
            subject=f'[PhongTro.vn] Mã OTP: {otp_code}',
            message=f'Mã OTP: {otp_code} (hiệu lực 10 phút).',
            html_message=html_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phongtro.vn'),
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        logger.info(f"Sent OTP to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        return False
