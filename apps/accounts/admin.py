# ============================================
# apps/accounts/admin.py
# Admin configuration for user management
# ============================================

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from django.utils import timezone
from django import forms
import hashlib
import uuid

from .models import Taikhoan, Khachhang, Vaitro, LoginHistory, SecurityQuestion

# Import admin customization
import config.admin  # noqa - This sets up admin site header


# ============================================
# Unregister default Django User/Group (không cần)
# ============================================
try:
    admin.site.unregister(User)
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


# ============================================
# VAITRO (Vai trò) Admin
# ============================================
@admin.register(Vaitro)
class VaitroAdmin(admin.ModelAdmin):
    """Admin cho bảng VAITRO (Vai trò)"""
    list_display = ['mavt', 'tenvt', 'user_count']
    search_fields = ['tenvt']

    def user_count(self, obj):
        count = Khachhang.objects.filter(mavt=obj).count()
        return format_html('<span class="badge bg-info">{}</span>', count)
    user_count.short_description = 'Số người dùng'


# ============================================
# Form tạo tài khoản mới
# ============================================
class TaikhoanCreationForm(forms.ModelForm):
    """Form tạo tài khoản mới với password"""
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={'class': 'vTextField'}),
        help_text='Mật khẩu phải có ít nhất 8 ký tự'
    )
    password_confirm = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={'class': 'vTextField'})
    )

    class Meta:
        model = Taikhoan
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Mật khẩu xác nhận không khớp!')
        if password and len(password) < 8:
            raise forms.ValidationError('Mật khẩu phải có ít nhất 8 ký tự!')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data['password']

        # Hash password with SHA256 + Salt
        salt = str(uuid.uuid4())
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

        instance.password_hash = password_hash
        instance.password_salt = salt

        if commit:
            instance.save()
        return instance


# ============================================
# TAIKHOAN (Tài khoản) Admin
# ============================================
@admin.register(Taikhoan)
class TaikhoanAdmin(admin.ModelAdmin):
    """Admin cho bảng TAIKHOAN (Tài khoản)"""
    list_display = ['matk', 'username', 'status_badge', 'two_factor_badge', 'last_login_time', 'tg_tao']
    list_filter = ['two_factor_enabled', 'is_locked']
    search_fields = ['username']
    ordering = ['-tg_tao']
    readonly_fields = ['tg_tao', 'last_login_time', 'password_hash', 'password_salt']
    list_per_page = 25

    fieldsets = (
        ('📋 Thông tin cơ bản', {
            'fields': ('username',),
            'classes': ('wide',),
        }),
        ('🔒 Bảo mật', {
            'fields': ('is_locked', 'lock_time', 'failed_login_count', 'two_factor_enabled'),
            'classes': ('collapse',),
        }),
        ('🔑 Mật khẩu (Chỉ xem)', {
            'fields': ('password_hash', 'password_salt'),
            'classes': ('collapse',),
        }),
        ('📅 Thời gian', {
            'fields': ('last_login_ip', 'last_login_time', 'tg_tao'),
            'classes': ('collapse',),
        }),
    )

    actions = ['unlock_accounts', 'lock_accounts', 'reset_password']

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return TaikhoanCreationForm
        return super().get_form(request, obj, **kwargs)

    def status_badge(self, obj):
        if obj.is_locked:
            return format_html('<span style="color: red; font-weight: bold;">🔒 Đã khóa</span>')
        return format_html('<span style="color: green;">✅ Hoạt động</span>')
    status_badge.short_description = 'Trạng thái'

    def two_factor_badge(self, obj):
        if obj.two_factor_enabled:
            return format_html('<span style="color: green;">🛡️ Bật</span>')
        return format_html('<span style="color: gray;">❌ Tắt</span>')
    two_factor_badge.short_description = '2FA'

    def unlock_accounts(self, request, queryset):
        count = queryset.update(is_locked=False, lock_time=None, failed_login_count=0)
        self.message_user(request, f'✅ Đã mở khóa {count} tài khoản.')
    unlock_accounts.short_description = "🔓 Mở khóa tài khoản"

    def lock_accounts(self, request, queryset):
        count = queryset.update(is_locked=True, lock_time=timezone.now())
        self.message_user(request, f'🔒 Đã khóa {count} tài khoản.')
    lock_accounts.short_description = "🔒 Khóa tài khoản"

    def reset_password(self, request, queryset):
        """Reset password về mặc định: Password@123"""
        default_password = 'Password@123'
        count = 0
        for account in queryset:
            salt = str(uuid.uuid4())
            password_hash = hashlib.sha256((default_password + salt).encode()).hexdigest()
            account.password_hash = password_hash
            account.password_salt = salt
            account.save()
            count += 1
        self.message_user(request, f'🔑 Đã reset mật khẩu {count} tài khoản về: Password@123')
    reset_password.short_description = "🔑 Reset mật khẩu (Password@123)"




# ============================================
# Form tạo khách hàng mới
# ============================================
class KhachhangCreationForm(forms.ModelForm):
    """Form tạo khách hàng mới kèm tài khoản"""
    username = forms.CharField(
        label='Tên đăng nhập',
        max_length=100,
        help_text='Tên đăng nhập cho tài khoản'
    )
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput,
        help_text='Mật khẩu tối thiểu 8 ký tự'
    )

    class Meta:
        model = Khachhang
        fields = ['hoten', 'email', 'sdt', 'gioitinh', 'ngaysinh', 'cccd', 'diachi', 'mavt']

    def save(self, commit=True):
        # Create Taikhoan first
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        salt = str(uuid.uuid4())
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

        taikhoan = Taikhoan.objects.create(
            username=username,
            password_hash=password_hash,
            password_salt=salt
        )

        # Create Khachhang
        instance = super().save(commit=False)
        instance.matk = taikhoan
        instance.trangthai = True

        if commit:
            instance.save()
        return instance


# ============================================
# KHACHHANG (Khách hàng) Admin
# ============================================
@admin.register(Khachhang)
class KhachhangAdmin(admin.ModelAdmin):
    """Admin cho bảng KHACHHANG (Khách hàng) - Quản lý người dùng"""
    list_display = [
        'makh', 'hoten', 'email', 'sdt',
        'role_badge', 'status_badge', 'lock_badge', 'twofa_badge'
    ]
    list_filter = ['mavt', 'trangthai', 'is_locked', 'is_2fa_enabled']
    search_fields = ['hoten', 'email', 'sdt', 'cccd']
    raw_id_fields = ['matk']
    list_per_page = 25
    list_editable = []
    date_hierarchy = None

    fieldsets = (
        ('👤 Thông tin cá nhân', {
            'fields': ('hoten', 'gioitinh', 'ngaysinh', 'cccd', 'diachi'),
            'classes': ('wide',),
        }),
        ('📧 Liên hệ', {
            'fields': ('email', 'sdt'),
        }),
        ('🔐 Tài khoản', {
            'fields': ('matk', 'mavt', 'trangthai'),
        }),
        ('🛡️ Bảo mật', {
            'fields': ('is_locked', 'locked_until', 'is_2fa_enabled'),
            'classes': ('collapse',),
        }),
    )

    actions = ['unlock_accounts', 'lock_accounts', 'set_role_tenant', 'set_role_landlord']

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return KhachhangCreationForm
        return super().get_form(request, obj, **kwargs)

    def role_badge(self, obj):
        if obj.mavt:
            if obj.mavt.tenvt == 'Admin':
                return format_html('<span style="background:#dc3545;color:white;padding:3px 8px;border-radius:4px;">👑 Admin</span>')
            elif obj.mavt.tenvt == 'Chủ trọ':
                return format_html('<span style="background:#28a745;color:white;padding:3px 8px;border-radius:4px;">🏠 Chủ trọ</span>')
            else:
                return format_html('<span style="background:#17a2b8;color:white;padding:3px 8px;border-radius:4px;">👤 {}</span>', obj.mavt.tenvt)
        return format_html('<span style="color:gray;">-</span>')
    role_badge.short_description = 'Vai trò'

    def status_badge(self, obj):
        if obj.trangthai:
            return format_html('<span style="color:green;">✅ Hoạt động</span>')
        return format_html('<span style="color:red;">❌ Vô hiệu</span>')
    status_badge.short_description = 'Trạng thái'

    def lock_badge(self, obj):
        if obj.is_locked:
            return format_html('<span style="color:red;">🔒 Khóa</span>')
        return format_html('<span style="color:green;">🔓</span>')
    lock_badge.short_description = 'Khóa'

    def twofa_badge(self, obj):
        if obj.is_2fa_enabled:
            return format_html('<span style="color:green;">🛡️</span>')
        return format_html('<span style="color:gray;">-</span>')
    twofa_badge.short_description = '2FA'

    def unlock_accounts(self, request, queryset):
        count = queryset.update(is_locked=False, locked_until=None)
        self.message_user(request, f'✅ Đã mở khóa {count} tài khoản.')
    unlock_accounts.short_description = "🔓 Mở khóa tài khoản"

    def lock_accounts(self, request, queryset):
        count = queryset.update(is_locked=True, locked_until=timezone.now() + timezone.timedelta(days=365))
        self.message_user(request, f'🔒 Đã khóa {count} tài khoản.')
    lock_accounts.short_description = "🔒 Khóa tài khoản"

    def set_role_tenant(self, request, queryset):
        tenant_role = Vaitro.objects.filter(tenvt='Khách thuê').first()
        if tenant_role:
            count = queryset.update(mavt=tenant_role)
            self.message_user(request, f'👤 Đã đổi {count} người dùng thành Khách thuê.')
        else:
            self.message_user(request, 'Không tìm thấy vai trò Khách thuê!', level='error')
    set_role_tenant.short_description = "👤 Đổi thành Khách thuê"

    def set_role_landlord(self, request, queryset):
        landlord_role = Vaitro.objects.filter(tenvt='Chủ trọ').first()
        if landlord_role:
            count = queryset.update(mavt=landlord_role)
            self.message_user(request, f'🏠 Đã đổi {count} người dùng thành Chủ trọ.')
        else:
            self.message_user(request, 'Không tìm thấy vai trò Chủ trọ!', level='error')
    set_role_landlord.short_description = "🏠 Đổi thành Chủ trọ"


# ============================================
# LOGIN HISTORY Admin
# ============================================
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin cho bảng LOGIN_HISTORY (Lịch sử đăng nhập)"""
    list_display = ['id', 'makh', 'success_badge', 'ip_address', 'user_agent_short', 'timestamp']
    list_filter = ['success', 'used_2fa']
    search_fields = ['ip_address', 'makh__hoten']
    readonly_fields = ['id', 'makh', 'ip_address', 'user_agent', 'success', 'used_2fa', 'timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50

    def success_badge(self, obj):
        if obj.success:
            return format_html('<span style="color:green;">✅ Thành công</span>')
        return format_html('<span style="color:red;">❌ Thất bại</span>')
    success_badge.short_description = 'Kết quả'

    def user_agent_short(self, obj):
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    user_agent_short.short_description = 'Trình duyệt'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================
# SECURITY QUESTION Admin
# ============================================
@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(admin.ModelAdmin):
    """Admin cho câu hỏi bảo mật"""
    list_display = ['id', 'makh', 'question_display', 'created_at']
    list_filter = ['question_key']
    search_fields = ['makh__hoten', 'makh__email']
    readonly_fields = ['answer_hash', 'created_at']
    list_per_page = 25

    def question_display(self, obj):
        return SecurityQuestion.get_question_label(obj.question_key)
    question_display.short_description = 'Câu hỏi'

    def has_add_permission(self, request):
        return False
