# ============================================
# apps/rooms/admin.py
# Admin configuration for room models
# ============================================

from django.contrib import admin
from django.utils.html import format_html
from .models import Nhatro, Phongtro, Hinhanh


# ============================================
# NHÀ TRỌ Admin
# ============================================
@admin.register(Nhatro)
class NhatroAdmin(admin.ModelAdmin):
    """Quản lý nhà trọ"""
    list_display = ['mant', 'tennt', 'makh', 'diachi', 'price_display', 'status_badge', 'room_count']
    list_filter = ['trangthai']
    search_fields = ['tennt', 'diachi', 'makh__hoten']
    raw_id_fields = ['makh']
    list_per_page = 25

    def price_display(self, obj):
        dien = f"{obj.giadien:,.0f}" if obj.giadien else "0"
        nuoc = f"{obj.gianuoc:,.0f}" if obj.gianuoc else "0"
        return format_html('⚡{} / 💧{}', dien, nuoc)
    price_display.short_description = 'Giá điện/nước'

    def status_badge(self, obj):
        if obj.trangthai:
            return format_html('<span style="color:green;">✅ Hoạt động</span>')
        return format_html('<span style="color:red;">❌ Ngừng</span>')
    status_badge.short_description = 'Trạng thái'

    def room_count(self, obj):
        count = Phongtro.objects.filter(mant=obj).count()
        return format_html('<span class="badge bg-info">{} phòng</span>', count)
    room_count.short_description = 'Số phòng'


# ============================================
# HÌNH ẢNH Inline
# ============================================
class HinhanhInline(admin.TabularInline):
    model = Hinhanh
    extra = 1
    max_num = 5
    fk_name = 'mapt'
    fields = ['duongdan', 'mota', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.duongdan:
            return format_html('<img src="{}" style="max-height:50px;"/>', obj.duongdan)
        return '-'
    image_preview.short_description = 'Xem trước'


# ============================================
# PHÒNG TRỌ Admin
# ============================================
@admin.register(Phongtro)
class PhongtroAdmin(admin.ModelAdmin):
    """Quản lý phòng trọ"""
    list_display = ['mapt', 'tenpt', 'mant', 'price_display', 'dientich', 'songuoio', 'status_badge', 'image_count']
    list_filter = ['trangthai', 'mant']
    search_fields = ['tenpt', 'mota', 'mant__tennt']
    inlines = [HinhanhInline]
    raw_id_fields = ['mant']
    list_per_page = 25

    fieldsets = (
        ('📋 Thông tin cơ bản', {
            'fields': ('tenpt', 'mant', 'mota'),
        }),
        ('📐 Chi tiết', {
            'fields': ('dientich', 'giatien', 'songuoio', 'trangthai'),
        }),
    )

    def price_display(self, obj):
        return format_html('<strong>{:,.0f} ₫</strong>', obj.giatien)
    price_display.short_description = 'Giá tiền'

    def status_badge(self, obj):
        status_colors = {
            'Còn trống': '#28a745',
            'Đã thuê': '#dc3545',
            'Đang sửa': '#ffc107',
        }
        color = status_colors.get(obj.trangthai, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;">{}</span>',
            color, obj.trangthai
        )
    status_badge.short_description = 'Trạng thái'

    def image_count(self, obj):
        count = Hinhanh.objects.filter(mapt=obj).count()
        if count > 0:
            return format_html('<span style="color:green;">📷 {}</span>', count)
        return format_html('<span style="color:gray;">-</span>')
    image_count.short_description = 'Ảnh'

    actions = ['set_available', 'set_rented']

    def set_available(self, request, queryset):
        count = queryset.update(trangthai='Còn trống')
        self.message_user(request, f'✅ Đã đặt {count} phòng về trạng thái "Còn trống".')
    set_available.short_description = "✅ Đặt trạng thái: Còn trống"

    def set_rented(self, request, queryset):
        count = queryset.update(trangthai='Đã thuê')
        self.message_user(request, f'🏠 Đã đặt {count} phòng về trạng thái "Đã thuê".')
    set_rented.short_description = "🏠 Đặt trạng thái: Đã thuê"


# ============================================
# HÌNH ẢNH Admin
# ============================================
@admin.register(Hinhanh)
class HinhanhAdmin(admin.ModelAdmin):
    """Quản lý hình ảnh phòng trọ"""
    list_display = ['maha', 'mapt', 'image_preview', 'duongdan_short']
    search_fields = ['mapt__tenpt']
    raw_id_fields = ['mapt']
    list_per_page = 30

    def image_preview(self, obj):
        if obj.duongdan:
            return format_html('<img src="{}" style="max-height:40px;border-radius:4px;"/>', obj.duongdan)
        return '-'
    image_preview.short_description = 'Ảnh'

    def duongdan_short(self, obj):
        if obj.duongdan:
            return obj.duongdan[-40:] if len(obj.duongdan) > 40 else obj.duongdan
        return '-'
    duongdan_short.short_description = 'Đường dẫn'
