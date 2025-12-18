# ============================================
# apps/accounts/admin.py
# ============================================

from django.contrib import admin
from .models import Taikhoan, Khachhang, Vaitro, LoginHistory


@admin.register(Vaitro)
class VaitroAdmin(admin.ModelAdmin):
    """Admin cho bảng VAITRO (Vai trò)"""
    list_display = ['mavt', 'tenvt']
    search_fields = ['tenvt']


@admin.register(Taikhoan)
class TaikhoanAdmin(admin.ModelAdmin):
    """Admin cho bảng TAIKHOAN (Tài khoản)"""
    list_display = ['matk', 'username', 'two_factor_enabled', 'is_locked', 'last_login_time', 'tg_tao']
    list_filter = ['two_factor_enabled', 'is_locked']
    search_fields = ['username']
    ordering = ['-tg_tao']
    readonly_fields = ['tg_tao', 'last_login_time', 'password_hash', 'password_salt']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('username', 'password_hash', 'password_salt'),
        }),
        ('Bảo mật', {
            'fields': ('is_locked', 'lock_time', 'failed_login_count', 'two_factor_enabled', 'two_factor_secret'),
        }),
        ('OAuth', {
            'fields': ('oauth_provider', 'oauth_id'),
        }),
        ('Thời gian', {
            'fields': ('last_login_ip', 'last_login_time', 'tg_tao'),
        }),
    )

    actions = ['unlock_accounts']

    def unlock_accounts(self, request, queryset):
        queryset.update(is_locked=False, lock_time=None, failed_login_count=0)
    unlock_accounts.short_description = "Mở khóa tài khoản đã chọn"


@admin.register(Khachhang)
class KhachhangAdmin(admin.ModelAdmin):
    """Admin cho bảng KHACHHANG (Khách hàng)"""
    list_display = [
        'makh', 'hoten', 'email', 'sdt',
        'mavt', 'trangthai', 'is_locked', 'is_2fa_enabled'
    ]
    list_filter = ['mavt', 'trangthai', 'is_locked', 'is_2fa_enabled']
    search_fields = ['hoten', 'email', 'sdt', 'cccd']
    raw_id_fields = ['matk']

    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('hoten', 'gioitinh', 'ngaysinh', 'cccd', 'diachi'),
        }),
        ('Liên hệ', {
            'fields': ('email', 'sdt'),
        }),
        ('Tài khoản', {
            'fields': ('matk', 'mavt', 'trangthai'),
        }),
        ('Bảo mật', {
            'fields': ('is_locked', 'locked_until', 'is_2fa_enabled', 'totp_secret'),
        }),
        ('OAuth', {
            'fields': ('google_id', 'oauth_provider'),
        }),
    )

    actions = ['unlock_accounts']

    def unlock_accounts(self, request, queryset):
        queryset.update(is_locked=False, locked_until=None)
    unlock_accounts.short_description = "Mở khóa tài khoản đã chọn"


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin cho bảng LOGIN_HISTORY (Lịch sử đăng nhập)"""
    list_display = ['id', 'makh', 'success', 'ip_address', 'timestamp']
    list_filter = ['success', 'used_2fa']
    search_fields = ['ip_address']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 30

