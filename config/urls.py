# ============================================
# config/urls.py (Đã chỉnh sửa)
# ============================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Health check endpoint for monitoring and load balancers."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    status = "healthy" if db_status == "ok" else "unhealthy"
    status_code = 200 if db_status == "ok" else 503

    return JsonResponse({
        "status": status,
        "database": db_status,
    }, status=status_code)

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls), # Admin mặc định của Django

    # --- 1. Custom Accounts ---
    path('accounts/', include('apps.accounts.urls')),

    # --- 2. Django-allauth ---
    path('accounts/social/', include('allauth.urls')),

    # --- 3. Các App chức năng chính ---
    path('', include('apps.rooms.urls')), # Trang chủ
    
    # CHỈNH TẠI ĐÂY: Bỏ prefix 'bookings/' để có thể định nghĩa '/quan_tri/' bên trong app
    path('', include('apps.bookings.urls')), 
    
    path('reviews/', include('apps.reviews.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('chat/', include('apps.chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)