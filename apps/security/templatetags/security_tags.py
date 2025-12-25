# ============================================
# apps/security/templatetags/security_tags.py
# Template tags for protected media URLs
# ============================================
from django import template
from apps.security.utils import get_protected_media_url

register = template.Library()


@register.simple_tag
def protected_media_url(file_path, expiry_hours=1):
    """
    Template tag để tạo signed URL cho file media
    
    Usage:
        {% load security_tags %}
        <img src="{% protected_media_url 'rooms/123/image.jpg' 2 %}">
    
    Args:
        file_path: Đường dẫn file (VD: 'rooms/123/image.jpg')
        expiry_hours: Thời gian hết hạn (giờ), mặc định 1 giờ
    
    Returns:
        Signed URL string
    """
    return get_protected_media_url(file_path, expiry_hours=expiry_hours)


@register.filter
def protected_url(file_path, expiry_hours=1):
    """
    Filter để tạo signed URL
    
    Usage:
        {% load security_tags %}
        <img src="{{ image.duongdan|protected_url:2 }}">
    """
    return get_protected_media_url(file_path, expiry_hours=expiry_hours)

