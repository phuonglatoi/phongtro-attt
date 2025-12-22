# ============================================
# config/admin.py
# Custom Admin Site Configuration
# ============================================

from django.contrib import admin
from django.contrib.admin import AdminSite


class PhongTroAdminSite(AdminSite):
    """Custom Admin Site cho PhongTro.vn"""

    # Tiêu đề và header
    site_header = '🏠 PhongTro.vn - Quản trị hệ thống'
    site_title = 'PhongTro.vn Admin'
    index_title = 'Bảng điều khiển quản trị'

    # Enable view on site link
    enable_nav_sidebar = True


# Tạo instance của custom admin site
phongtro_admin_site = PhongTroAdminSite(name='phongtro_admin')


# ============================================
# Customize default admin site
# ============================================
admin.site.site_header = '🏠 PhongTro.vn - Quản trị hệ thống'
admin.site.site_title = 'PhongTro.vn Admin'
admin.site.index_title = 'Bảng điều khiển quản trị'

