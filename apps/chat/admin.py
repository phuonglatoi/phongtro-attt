from django.contrib import admin
from .models import TinNhan

@admin.register(TinNhan)
class TinNhanAdmin(admin.ModelAdmin):
    list_display = ('matn', 'nguoigui', 'nguoinhan', 'trangthai', 'tg_tao')
    list_filter = ('trangthai', 'tg_tao')
    search_fields = ('tinnhan', 'nguoigui__hoten', 'nguoinhan__hoten')