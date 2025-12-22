# ============================================
# apps/security/admin.py
# Admin configuration for security models
# ============================================

from django.contrib import admin
from django.utils.html import format_html
from apps.accounts.models import FailedLoginAttempts, BlockedIps, SecurityLogs, AuditLogs


# ============================================
# FAILED LOGIN ATTEMPTS Admin
# ============================================
@admin.register(FailedLoginAttempts)
class FailedLoginAttemptsAdmin(admin.ModelAdmin):
    """Quản lý đăng nhập thất bại"""
    list_display = ['id', 'ip_address', 'username_or_email', 'attempt_time']
    search_fields = ['ip_address', 'username_or_email']
    ordering = ['-attempt_time']
    list_per_page = 50
    date_hierarchy = 'attempt_time'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================
# BLOCKED IPS Admin
# ============================================
@admin.register(BlockedIps)
class BlockedIpsAdmin(admin.ModelAdmin):
    """Quản lý IP bị chặn"""
    list_display = ['id', 'ip_address', 'reason', 'status_badge', 'blocked_at', 'blocked_until']
    search_fields = ['ip_address', 'reason']
    ordering = ['-blocked_at']
    list_per_page = 30
    actions = ['unblock_selected']

    def status_badge(self, obj):
        from django.utils import timezone
        if obj.blocked_until and obj.blocked_until < timezone.now():
            return format_html('<span style="color:gray;">⏱️ Hết hạn</span>')
        return format_html('<span style="color:red;">🚫 Đang chặn</span>')
    status_badge.short_description = 'Trạng thái'

    def unblock_selected(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'✅ Đã mở chặn {count} IP.')
    unblock_selected.short_description = '✅ Mở chặn IP đã chọn'


# ============================================
# SECURITY LOGS Admin
# ============================================
@admin.register(SecurityLogs)
class SecurityLogsAdmin(admin.ModelAdmin):
    """Nhật ký bảo mật"""
    list_display = ['id', 'action_badge', 'matk', 'ip_address', 'log_time']
    list_filter = ['action_type']
    search_fields = ['ip_address', 'action_type']
    ordering = ['-log_time']
    list_per_page = 50
    date_hierarchy = 'log_time'

    def action_badge(self, obj):
        action_colors = {
            'LOGIN': '#28a745',
            'LOGOUT': '#17a2b8',
            'PASSWORD_CHANGE': '#ffc107',
            'FAILED_LOGIN': '#dc3545',
            '2FA_ENABLED': '#6f42c1',
        }
        color = action_colors.get(obj.action_type, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 6px;border-radius:3px;font-size:11px;">{}</span>',
            color, obj.action_type
        )
    action_badge.short_description = 'Hành động'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================
# AUDIT LOGS Admin
# ============================================
@admin.register(AuditLogs)
class AuditLogsAdmin(admin.ModelAdmin):
    """Nhật ký kiểm toán"""
    list_display = ['id', 'table_name', 'action_badge', 'changed_by', 'changed_date']
    list_filter = ['table_name', 'action']
    search_fields = ['table_name', 'changed_by']
    ordering = ['-changed_date']
    list_per_page = 50
    date_hierarchy = 'changed_date'

    def action_badge(self, obj):
        action_colors = {
            'INSERT': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
        }
        color = action_colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 6px;border-radius:3px;">{}</span>',
            color, obj.action
        )
    action_badge.short_description = 'Hành động'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False