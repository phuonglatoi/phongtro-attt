# ============================================
# apps/bookings/admin.py
# Admin configuration for booking models
# ============================================

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Henxemtro, Danhgia, Tinnhan, Thongbao, Yclamchutro
from apps.accounts.models import Vaitro


# ============================================
# HẸN XEM TRỌ Admin
# ============================================
@admin.register(Henxemtro)
class HenxemtroAdmin(admin.ModelAdmin):
    """Quản lý lịch hẹn xem phòng"""
    list_display = ['mahxt', 'makh', 'mapt', 'ngayhen', 'status_badge', 'tg_tao']
    list_filter = ['trangthai', 'ngayhen']
    search_fields = ['makh__hoten', 'mapt__tenpt']
    raw_id_fields = ['makh', 'mapt']
    date_hierarchy = 'ngayhen'
    list_per_page = 25

    actions = ['confirm_appointments', 'cancel_appointments']

    def status_badge(self, obj):
        status_colors = {
            'Chờ xác nhận': '#ffc107',
            'Đã xác nhận': '#28a745',
            'Đã xem': '#17a2b8',
            'Đã hủy': '#dc3545',
        }
        color = status_colors.get(obj.trangthai, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;">{}</span>',
            color, obj.trangthai
        )
    status_badge.short_description = 'Trạng thái'

    def confirm_appointments(self, request, queryset):
        count = queryset.filter(trangthai='Chờ xác nhận').update(trangthai='Đã xác nhận')
        self.message_user(request, f'✅ Đã xác nhận {count} lịch hẹn.')
    confirm_appointments.short_description = "✅ Xác nhận lịch hẹn"

    def cancel_appointments(self, request, queryset):
        count = queryset.exclude(trangthai='Đã hủy').update(trangthai='Đã hủy')
        self.message_user(request, f'❌ Đã hủy {count} lịch hẹn.')
    cancel_appointments.short_description = "❌ Hủy lịch hẹn"


# ============================================
# ĐÁNH GIÁ Admin
# ============================================
@admin.register(Danhgia)
class DanhgiaAdmin(admin.ModelAdmin):
    """Quản lý đánh giá phòng trọ"""
    list_display = ['madg', 'makh', 'mapt', 'star_display', 'binhluan_short', 'tg_tao']
    list_filter = ['sao', 'tg_tao']
    search_fields = ['makh__hoten', 'mapt__tenpt', 'binhluan']
    raw_id_fields = ['makh', 'mapt']
    list_per_page = 25

    def star_display(self, obj):
        stars = '⭐' * obj.sao
        return format_html('<span>{}</span>', stars)
    star_display.short_description = 'Đánh giá'

    def binhluan_short(self, obj):
        if obj.binhluan:
            return obj.binhluan[:50] + '...' if len(obj.binhluan) > 50 else obj.binhluan
        return '-'
    binhluan_short.short_description = 'Bình luận'


# ============================================
# TIN NHẮN Admin
# ============================================
@admin.register(Tinnhan)
class TinnhanAdmin(admin.ModelAdmin):
    """Quản lý tin nhắn"""
    list_display = ['matn', 'makh_gui', 'makh_nhan', 'noidung_short', 'read_badge', 'tg_gui']
    list_filter = ['dadoc', 'tg_gui']
    search_fields = ['makh_gui__hoten', 'makh_nhan__hoten', 'noidung']
    raw_id_fields = ['makh_gui', 'makh_nhan']
    list_per_page = 30

    def noidung_short(self, obj):
        return obj.noidung[:50] + '...' if len(obj.noidung) > 50 else obj.noidung
    noidung_short.short_description = 'Nội dung'

    def read_badge(self, obj):
        if obj.dadoc:
            return format_html('<span style="color:green;">✓ Đã đọc</span>')
        return format_html('<span style="color:orange;">📩 Chưa đọc</span>')
    read_badge.short_description = 'Trạng thái'


# ============================================
# THÔNG BÁO Admin
# ============================================
@admin.register(Thongbao)
class ThongbaoAdmin(admin.ModelAdmin):
    """Quản lý thông báo hệ thống"""
    list_display = ['matb', 'makh', 'tieude', 'type_badge', 'read_badge', 'tg_tao']
    list_filter = ['loai', 'dadoc', 'tg_tao']
    search_fields = ['makh__hoten', 'tieude', 'noidung']
    raw_id_fields = ['makh']
    list_per_page = 30

    def type_badge(self, obj):
        type_colors = {
            'info': '#17a2b8',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
        }
        color = type_colors.get(obj.loai, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 6px;border-radius:3px;">{}</span>',
            color, obj.loai
        )
    type_badge.short_description = 'Loại'

    def read_badge(self, obj):
        if obj.dadoc:
            return format_html('<span style="color:green;">✓</span>')
        return format_html('<span style="color:orange;">●</span>')
    read_badge.short_description = 'Đọc'


# ============================================
# YÊU CẦU LÀM CHỦ TRỌ Admin
# ============================================
@admin.register(Yclamchutro)
class YclamchutroAdmin(admin.ModelAdmin):
    """Quản lý yêu cầu làm chủ trọ"""
    list_display = ['mayc', 'makh', 'status_badge', 'tg_tao', 'tg_duyet', 'nguoiduyet']
    list_filter = ['trangthai', 'tg_tao']
    search_fields = ['makh__hoten', 'makh__email', 'lydo']
    raw_id_fields = ['makh', 'nguoiduyet']
    readonly_fields = ['tg_tao']
    list_per_page = 25

    actions = ['approve_requests', 'reject_requests']

    def status_badge(self, obj):
        status_colors = {
            'Chờ duyệt': '#ffc107',
            'Đã duyệt': '#28a745',
            'Từ chối': '#dc3545',
        }
        color = status_colors.get(obj.trangthai, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;">{}</span>',
            color, obj.trangthai
        )
    status_badge.short_description = 'Trạng thái'

    def approve_requests(self, request, queryset):
        """Duyệt yêu cầu làm chủ trọ"""
        chutro_role = Vaitro.objects.filter(tenvt='Chủ trọ').first()
        if not chutro_role:
            self.message_user(request, '❌ Không tìm thấy vai trò Chủ trọ trong hệ thống.', level='error')
            return

        admin_makh = request.session.get('makh')

        count = 0
        for yc in queryset.filter(trangthai='Chờ duyệt'):
            yc.trangthai = 'Đã duyệt'
            yc.tg_duyet = timezone.now()
            if admin_makh:
                from apps.accounts.models import Khachhang
                try:
                    yc.nguoiduyet = Khachhang.objects.get(makh=admin_makh)
                except:
                    pass
            yc.save()

            yc.makh.mavt = chutro_role
            yc.makh.save()

            Thongbao.objects.create(
                makh=yc.makh,
                tieude='🎉 Yêu cầu làm chủ trọ đã được duyệt',
                noidung='Chúc mừng! Bạn đã trở thành chủ trọ. Bây giờ bạn có thể đăng tin cho thuê phòng.',
                loai='success'
            )
            count += 1

        self.message_user(request, f'✅ Đã duyệt {count} yêu cầu.')
    approve_requests.short_description = '✅ Duyệt yêu cầu làm chủ trọ'

    def reject_requests(self, request, queryset):
        """Từ chối yêu cầu làm chủ trọ"""
        count = 0
        for yc in queryset.filter(trangthai='Chờ duyệt'):
            yc.trangthai = 'Từ chối'
            yc.tg_duyet = timezone.now()
            yc.save()

            Thongbao.objects.create(
                makh=yc.makh,
                tieude='❌ Yêu cầu làm chủ trọ bị từ chối',
                noidung='Rất tiếc, yêu cầu làm chủ trọ của bạn đã bị từ chối. Vui lòng liên hệ hỗ trợ để biết thêm chi tiết.',
                loai='warning'
            )
            count += 1

        self.message_user(request, f'❌ Đã từ chối {count} yêu cầu.')
    reject_requests.short_description = '❌ Từ chối yêu cầu làm chủ trọ'

