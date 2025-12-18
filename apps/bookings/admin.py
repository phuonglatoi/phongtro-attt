# ============================================
# apps/bookings/admin.py
# Admin configuration for booking models
# ============================================

from django.contrib import admin
from django.utils import timezone
from .models import Henxemtro, Thuetro, Danhgia, Tinnhan, Thongbao, Yclamchutro
from apps.accounts.models import Vaitro


@admin.register(Henxemtro)
class HenxemtroAdmin(admin.ModelAdmin):
    list_display = ['mahxt', 'makh', 'mapt', 'ngayhen', 'trangthai', 'tg_tao']
    list_filter = ['trangthai', 'ngayhen']
    search_fields = ['makh__hoten', 'mapt__tenpt']
    raw_id_fields = ['makh', 'mapt']
    list_editable = ['trangthai']
    date_hierarchy = 'ngayhen'


@admin.register(Thuetro)
class ThuetroAdmin(admin.ModelAdmin):
    list_display = ['matt', 'makh', 'mapt', 'ngaybatdau', 'ngayketthuc', 'tiencoc', 'trangthai']
    list_filter = ['trangthai', 'ngaybatdau']
    search_fields = ['makh__hoten', 'mapt__tenpt']
    raw_id_fields = ['makh', 'mapt']
    date_hierarchy = 'ngaybatdau'


@admin.register(Danhgia)
class DanhgiaAdmin(admin.ModelAdmin):
    list_display = ['madg', 'makh', 'mapt', 'sao', 'tg_tao']
    list_filter = ['sao', 'tg_tao']
    search_fields = ['makh__hoten', 'mapt__tenpt', 'binhluan']
    raw_id_fields = ['makh', 'mapt']


@admin.register(Tinnhan)
class TinnhanAdmin(admin.ModelAdmin):
    list_display = ['matn', 'makh_gui', 'makh_nhan', 'noidung_short', 'dadoc', 'tg_gui']
    list_filter = ['dadoc', 'tg_gui']
    search_fields = ['makh_gui__hoten', 'makh_nhan__hoten', 'noidung']
    raw_id_fields = ['makh_gui', 'makh_nhan']
    
    def noidung_short(self, obj):
        return obj.noidung[:50] + '...' if len(obj.noidung) > 50 else obj.noidung
    noidung_short.short_description = 'Nội dung'


@admin.register(Thongbao)
class ThongbaoAdmin(admin.ModelAdmin):
    list_display = ['matb', 'makh', 'tieude', 'loai', 'dadoc', 'tg_tao']
    list_filter = ['loai', 'dadoc', 'tg_tao']
    search_fields = ['makh__hoten', 'tieude', 'noidung']
    raw_id_fields = ['makh']


@admin.register(Yclamchutro)
class YclamchutroAdmin(admin.ModelAdmin):
    list_display = ['mayc', 'makh', 'trangthai', 'tg_tao', 'tg_duyet', 'nguoiduyet']
    list_filter = ['trangthai', 'tg_tao']
    search_fields = ['makh__hoten', 'makh__email', 'lydo']
    raw_id_fields = ['makh', 'nguoiduyet']
    readonly_fields = ['tg_tao']
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Duyệt yêu cầu làm chủ trọ"""
        # Get landlord role
        chutro_role = Vaitro.objects.filter(tenvt='Chủ trọ').first()
        if not chutro_role:
            self.message_user(request, 'Không tìm thấy vai trò Chủ trọ trong hệ thống.', level='error')
            return
        
        # Get admin khachhang
        admin_makh = request.session.get('makh')
        
        count = 0
        for yc in queryset.filter(trangthai='Chờ duyệt'):
            # Update request
            yc.trangthai = 'Đã duyệt'
            yc.tg_duyet = timezone.now()
            if admin_makh:
                from apps.accounts.models import Khachhang
                try:
                    yc.nguoiduyet = Khachhang.objects.get(makh=admin_makh)
                except:
                    pass
            yc.save()
            
            # Update user role to landlord
            yc.makh.mavt = chutro_role
            yc.makh.save()
            
            # Create notification
            Thongbao.objects.create(
                makh=yc.makh,
                tieude='Yêu cầu làm chủ trọ đã được duyệt',
                noidung='Chúc mừng! Bạn đã trở thành chủ trọ. Bây giờ bạn có thể đăng tin cho thuê phòng.',
                loai='success'
            )
            count += 1
        
        self.message_user(request, f'Đã duyệt {count} yêu cầu.')
    approve_requests.short_description = 'Duyệt yêu cầu làm chủ trọ'
    
    def reject_requests(self, request, queryset):
        """Từ chối yêu cầu làm chủ trọ"""
        count = 0
        for yc in queryset.filter(trangthai='Chờ duyệt'):
            yc.trangthai = 'Từ chối'
            yc.tg_duyet = timezone.now()
            yc.save()
            
            # Create notification
            Thongbao.objects.create(
                makh=yc.makh,
                tieude='Yêu cầu làm chủ trọ bị từ chối',
                noidung='Rất tiếc, yêu cầu làm chủ trọ của bạn đã bị từ chối. Vui lòng liên hệ hỗ trợ để biết thêm chi tiết.',
                loai='warning'
            )
            count += 1
        
        self.message_user(request, f'Đã từ chối {count} yêu cầu.')
    reject_requests.short_description = 'Từ chối yêu cầu làm chủ trọ'

