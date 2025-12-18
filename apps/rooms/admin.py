# ============================================
# apps/rooms/admin.py
# ============================================

from django.contrib import admin
from .models import Nhatro, Phongtro, Hinhanh


@admin.register(Nhatro)
class NhatroAdmin(admin.ModelAdmin):
    """Admin cho bảng NHATRO (Nhà trọ)"""
    list_display = ['mant', 'tennt', 'makh', 'diachi', 'giadien', 'gianuoc', 'trangthai']
    list_filter = ['trangthai']
    search_fields = ['tennt', 'diachi']
    raw_id_fields = ['makh']


class HinhanhInline(admin.TabularInline):
    model = Hinhanh
    extra = 3
    fk_name = 'mapt'


@admin.register(Phongtro)
class PhongtroAdmin(admin.ModelAdmin):
    """Admin cho bảng PHONGTRO (Phòng trọ)"""
    list_display = ['mapt', 'tenpt', 'mant', 'giatien', 'dientich', 'songuoio', 'trangthai']
    list_filter = ['trangthai', 'mant']
    search_fields = ['tenpt', 'mota']
    inlines = [HinhanhInline]
    raw_id_fields = ['mant']


@admin.register(Hinhanh)
class HinhanhAdmin(admin.ModelAdmin):
    """Admin cho bảng HINHANH (Hình ảnh)"""
    list_display = ['maha', 'mapt', 'duongdan']
    search_fields = ['mapt__tenpt']
    raw_id_fields = ['mapt']
