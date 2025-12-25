# ============================================
# apps/security/urls.py
# ============================================
from django.urls import path, re_path
from . import views

app_name = 'security'

urlpatterns = [
    # Protected media file serving
    re_path(r'^protected-media/(?P<file_path>.+)$', views.serve_protected_media, name='protected_media'),
]

