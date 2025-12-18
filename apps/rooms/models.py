# ============================================
# apps/rooms/models.py
# ============================================

from django.db import models
from apps.accounts.models import Khachhang


class Nhatro(models.Model):
    """Nhà trọ - Bảng NHATRO"""
    mant = models.AutoField(db_column='MANT', primary_key=True)
    tennt = models.CharField(db_column='TENNT', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', verbose_name='Tên nhà trọ')
    diachi = models.CharField(db_column='DIACHI', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', verbose_name='Địa chỉ')
    giadien = models.DecimalField(db_column='GIADIEN', max_digits=18, decimal_places=0, blank=True, null=True, verbose_name='Giá điện')
    gianuoc = models.DecimalField(db_column='GIANUOC', max_digits=18, decimal_places=0, blank=True, null=True, verbose_name='Giá nước')
    makh = models.ForeignKey(Khachhang, models.DO_NOTHING, db_column='MAKH', verbose_name='Chủ nhà')
    trangthai = models.BooleanField(db_column='TRANGTHAI', blank=True, null=True, verbose_name='Hoạt động')
    tg_tao = models.DateTimeField(db_column='TG_TAO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NHATRO'
        verbose_name = 'Nhà trọ'
        verbose_name_plural = 'Nhà trọ'

    def __str__(self):
        return self.tennt


class Phongtro(models.Model):
    """Phòng trọ - Bảng PHONGTRO"""
    mapt = models.AutoField(db_column='MAPT', primary_key=True)
    tenpt = models.CharField(db_column='TENPT', max_length=200, verbose_name='Tên phòng')
    dientich = models.FloatField(db_column='DIENTICH', blank=True, null=True, verbose_name='Diện tích')
    mota = models.TextField(db_column='MOTA', blank=True, null=True, verbose_name='Mô tả')
    giatien = models.DecimalField(db_column='GIATIEN', max_digits=18, decimal_places=2, verbose_name='Giá tiền')
    songuoio = models.IntegerField(db_column='SONGUOIO', blank=True, null=True, default=0, verbose_name='Số người ở')
    mant = models.ForeignKey(Nhatro, models.CASCADE, db_column='MANT', related_name='phongtro_set')
    trangthai = models.CharField(db_column='TRANGTHAI', max_length=50, default='Còn trống', verbose_name='Trạng thái')
    tg_tao = models.DateTimeField(db_column='TG_TAO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PHONGTRO'
        verbose_name = 'Phòng trọ'
        verbose_name_plural = 'Phòng trọ'

    def __str__(self):
        return f"{self.tenpt} - {self.mant.tennt}"


class Hinhanh(models.Model):
    """Hình ảnh phòng trọ - Bảng HINHANH"""
    maha = models.AutoField(db_column='MAHA', primary_key=True)
    duongdan = models.CharField(db_column='DUONGDAN', max_length=500, verbose_name='Đường dẫn')
    mota = models.CharField(db_column='MOTA', max_length=200, blank=True, null=True, verbose_name='Mô tả')
    mapt = models.ForeignKey(Phongtro, models.CASCADE, db_column='MAPT', related_name='hinhanh_set')
    tg_tao = models.DateTimeField(db_column='TG_TAO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HINHANH'
        verbose_name = 'Hình ảnh'
        verbose_name_plural = 'Hình ảnh'

    def __str__(self):
        return f"Ảnh {self.maha} - {self.mapt.tenpt}"
