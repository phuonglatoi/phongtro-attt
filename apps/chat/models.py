from django.db import models
from apps.accounts.models import Khachhang

class TinNhan(models.Model):
    """Tin nhắn giữa hai người dùng - Bảng TINNHAN"""

    matn = models.AutoField(db_column='MATN', primary_key=True)
    nguoigui = models.ForeignKey(Khachhang, models.DO_NOTHING, db_column='NGUOIGUI', related_name='tinnhan_gui_set', verbose_name='Người gửi')
    nguoinhan = models.ForeignKey(Khachhang, models.DO_NOTHING, db_column='NGUOINHAN', related_name='tinnhan_nhan_set', verbose_name='Người nhận')
    tinnhan = models.TextField(db_column='TINNHAN', verbose_name='Nội dung tin nhắn')
    trangthai = models.BooleanField(db_column='TRANGTHAI', default=False, verbose_name='Đã đọc')
    tg_tao = models.DateTimeField(db_column='TG_TAO', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'TINNHAN'
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
        ordering = ['-tg_tao']

    def __str__(self):
        return f"Từ {self.nguoigui.hoten} đến {self.nguoinhan.hoten}"