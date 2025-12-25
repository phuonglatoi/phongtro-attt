# ============================================
# apps/security/views.py
# Protected Media File Serving
# ============================================
import os
import mimetypes
import hashlib
import time
from datetime import datetime, timedelta
from urllib.parse import quote

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, Http404, FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.signing import Signer, BadSignature, TimestampSigner
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache

from apps.accounts.models import Khachhang, SecurityLogs
from apps.rooms.models import Phongtro, Hinhanh


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_client_ip(request):
    """Lấy IP address của client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_file_access(request, file_path, allowed=True):
    """Ghi log mỗi lần truy cập file"""
    try:
        SecurityLogs.objects.create(
            action_type='file_access' if allowed else 'file_access_denied',
            ip_address=get_client_ip(request),
            matk_id=request.session.get('matk'),
            details=f"file={file_path}, allowed={allowed}"
        )
    except Exception as e:
        pass  # Không để lỗi log làm gián đoạn


def check_file_permission(request, file_path):
    """
    Kiểm tra quyền truy cập file
    Returns: (allowed: bool, reason: str)
    """
    # Kiểm tra đăng nhập
    makh = request.session.get('makh')
    if not makh:
        return False, "Chưa đăng nhập"
    
    try:
        khachhang = Khachhang.objects.select_related('matk', 'mavt').get(makh=makh)
    except Khachhang.DoesNotExist:
        return False, "Tài khoản không tồn tại"
    
    # Admin có quyền truy cập tất cả
    if khachhang.mavt and khachhang.mavt.tenvt == 'Admin':
        return True, "Admin access"
    
    # Phân tích đường dẫn file
    # Format: media/rooms/{mapt}/image.jpg
    parts = file_path.split('/')
    
    if len(parts) >= 3 and parts[0] == 'rooms':
        try:
            mapt = int(parts[1])
            phongtro = Phongtro.objects.select_related('makh').get(mapt=mapt)
            
            # Chủ phòng có quyền xem
            if phongtro.makh_id == makh:
                return True, "Owner access"
            
            # Người đã đặt phòng có quyền xem
            from apps.bookings.models import Datphong
            has_booking = Datphong.objects.filter(
                makh_id=makh,
                mapt_id=mapt
            ).exists()
            
            if has_booking:
                return True, "Renter access"
            
            # File công khai (ảnh đại diện phòng) - cho phép xem
            # Nếu muốn bảo mật hơn, comment dòng này
            return True, "Public room image"
            
        except (ValueError, Phongtro.DoesNotExist):
            return False, "Phòng không tồn tại"
    
    # Mặc định từ chối
    return False, "Không có quyền truy cập"


# ============================================
# SIGNED URL GENERATOR
# ============================================

def generate_signed_url(file_path, expiry_hours=1):
    """
    Tạo signed URL có thời hạn
    Args:
        file_path: Đường dẫn file (VD: 'rooms/123/image.jpg')
        expiry_hours: Thời gian hết hạn (giờ)
    Returns:
        Signed token
    """
    signer = TimestampSigner()
    # Thêm salt để bảo mật hơn
    data = f"{file_path}:{int(time.time())}"
    signed = signer.sign(data)
    return signed


def verify_signed_url(signed_token, max_age_seconds=3600):
    """
    Xác thực signed URL
    Args:
        signed_token: Token đã ký
        max_age_seconds: Thời gian tối đa (giây)
    Returns:
        (valid: bool, file_path: str)
    """
    signer = TimestampSigner()
    try:
        data = signer.unsign(signed_token, max_age=max_age_seconds)
        file_path = data.split(':')[0]
        return True, file_path
    except (BadSignature, IndexError):
        return False, None


# ============================================
# PROTECTED FILE SERVING VIEW
# ============================================

@never_cache
@require_http_methods(["GET"])
def serve_protected_media(request, file_path):
    """
    Serve file media với kiểm tra quyền
    URL: /protected-media/{file_path}
    """
    # Kiểm tra quyền truy cập
    allowed, reason = check_file_permission(request, file_path)
    
    # Ghi log
    log_file_access(request, file_path, allowed)
    
    if not allowed:
        return HttpResponseForbidden(f"Access Denied: {reason}")
    
    # Đường dẫn file thực tế
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    if not os.path.exists(full_path):
        raise Http404("File not found")
    
    # Kiểm tra path traversal
    real_path = os.path.realpath(full_path)
    media_root = os.path.realpath(settings.MEDIA_ROOT)
    if not real_path.startswith(media_root):
        return HttpResponseForbidden("Invalid file path")
    
    # Sử dụng X-Accel-Redirect nếu có Nginx
    if getattr(settings, 'USE_X_ACCEL_REDIRECT', False):
        response = HttpResponse()
        response['X-Accel-Redirect'] = f'/protected-files/{file_path}'
        response['Content-Type'] = mimetypes.guess_type(full_path)[0] or 'application/octet-stream'
        return response
    
    # Fallback: Serve trực tiếp từ Django (chậm hơn)
    return FileResponse(open(full_path, 'rb'))

