# ============================================
# apps/security/admin.py
# NOTE: Security admin has been moved to apps/accounts/admin.py
# Yclamchutro admin has been moved to apps/bookings/admin.py
# ============================================

from django.contrib import admin
from apps.accounts.models import FailedLoginAttempts, BlockedIps, SecurityLogs, AuditLogs


@admin.register(FailedLoginAttempts)
class FailedLoginAttemptsAdmin(admin.ModelAdmin):
    """Admin cho bảng FAILED_LOGIN_ATTEMPTS"""
    list_display = ['id', 'ip_address', 'username_or_email', 'attempt_time']
    search_fields = ['ip_address', 'username_or_email']
    ordering = ['-attempt_time']


@admin.register(BlockedIps)
class BlockedIpsAdmin(admin.ModelAdmin):
    """Admin cho bảng BLOCKED_IPS"""
    list_display = ['id', 'ip_address', 'reason', 'blocked_at', 'blocked_until']
    search_fields = ['ip_address', 'reason']
    ordering = ['-blocked_at']
    actions = ['unblock_selected']

    def unblock_selected(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Đã mở chặn {count} IP.')
    unblock_selected.short_description = 'Mở chặn IP đã chọn'


@admin.register(SecurityLogs)
class SecurityLogsAdmin(admin.ModelAdmin):
    """Admin cho bảng SECURITY_LOGS"""
    list_display = ['id', 'action_type', 'matk', 'ip_address', 'log_time']
    list_filter = ['action_type']
    search_fields = ['ip_address', 'action_type']
    ordering = ['-log_time']


@admin.register(AuditLogs)
class AuditLogsAdmin(admin.ModelAdmin):
    """Admin cho bảng AUDIT_LOGS"""
    list_display = ['id', 'table_name', 'action', 'changed_by', 'changed_date']
    list_filter = ['table_name', 'action']
    search_fields = ['table_name', 'changed_by']
    ordering = ['-changed_date']