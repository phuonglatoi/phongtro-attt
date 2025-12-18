from django.db import models
from apps.accounts.models import Khachhang
from apps.rooms.models import Phongtro


class Henxemtro(models.Model):
    """Lịch hẹn xem trọ - Bảng HENXEMTRO"""

    STATUS_CHOICES = [
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Đã xác nhận', 'Đã xác nhận'),
        ('Đã hủy', 'Đã hủy'),
        ('Đã xem', 'Đã xem'),
    ]

    mahxt = models.AutoField(db_column='MAHXT', primary_key=True)
    mapt = models.ForeignKey(Phongtro, models.CASCADE, db_column='MAPT', related_name='henxemtro_set')
    makh = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH', related_name='henxemtro_set')
    ngayhen = models.DateTimeField(db_column='NGAYHEN', verbose_name='Ngày hẹn')
    ghichu = models.CharField(db_column='GHICHU', max_length=500, blank=True, null=True)
    trangthai = models.CharField(db_column='TRANGTHAI', max_length=50, choices=STATUS_CHOICES, default='Chờ xác nhận')
    tg_tao = models.DateTimeField(db_column='TG_TAO', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'HENXEMTRO'
        verbose_name = 'Hẹn xem trọ'
        verbose_name_plural = 'Danh sách hẹn xem trọ'
        ordering = ['-ngayhen']

    def __str__(self):
        return f"Hẹn: {self.makh.hoten} - {self.mapt.tenpt} ({self.ngayhen})"


class Thuetro(models.Model):
    """Hợp đồng thuê trọ - Bảng THUETRO"""

    STATUS_CHOICES = [
        ('Đang thuê', 'Đang thuê'),
        ('Đã kết thúc', 'Đã kết thúc'),
        ('Đã hủy', 'Đã hủy'),
    ]

    matt = models.AutoField(db_column='MATT', primary_key=True)
    mapt = models.ForeignKey(Phongtro, models.CASCADE, db_column='MAPT', related_name='thuetro_set')
    makh = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH', related_name='thuetro_set')
    ngaybatdau = models.DateField(db_column='NGAYBATDAU', verbose_name='Ngày bắt đầu')
    ngayketthuc = models.DateField(db_column='NGAYKETTHUC', blank=True, null=True, verbose_name='Ngày kết thúc')
    tiencoc = models.DecimalField(db_column='TIENCOC', max_digits=18, decimal_places=2, default=0)
    trangthai = models.CharField(db_column='TRANGTHAI', max_length=50, choices=STATUS_CHOICES, default='Đang thuê')
    tg_tao = models.DateTimeField(db_column='TG_TAO', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'THUETRO'
        verbose_name = 'Thuê trọ'
        verbose_name_plural = 'Danh sách thuê trọ'
        ordering = ['-ngaybatdau']

    def __str__(self):
        return f"Thuê: {self.makh.hoten} - {self.mapt.tenpt}"



class Danhgia(models.Model):
    """Đánh giá phòng trọ - Bảng DANHGIA"""

    madg = models.AutoField(db_column='MADG', primary_key=True)
    mapt = models.ForeignKey(Phongtro, models.CASCADE, db_column='MAPT', related_name='danhgia_set')
    makh = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH', related_name='danhgia_set')
    sao = models.IntegerField(db_column='SAO', verbose_name='Số sao (1-5)')
    binhluan = models.TextField(db_column='BINHLUAN', blank=True, null=True, verbose_name='Bình luận')
    tg_tao = models.DateTimeField(db_column='TG_TAO', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'DANHGIA'
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Danh sách đánh giá'
        ordering = ['-tg_tao']

    def __str__(self):
        return f"Đánh giá {self.sao}★ - {self.mapt.tenpt}"


class Tinnhan(models.Model):
    """Tin nhắn - Bảng TINNHAN"""

    matn = models.AutoField(db_column='MATN', primary_key=True)
    makh_gui = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH_GUI', related_name='tinnhan_gui')
    makh_nhan = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH_NHAN', related_name='tinnhan_nhan')
    noidung = models.TextField(db_column='NOIDUNG', verbose_name='Nội dung')
    dadoc = models.BooleanField(db_column='DADOC', default=False, verbose_name='Đã đọc')
    tg_gui = models.DateTimeField(db_column='TG_GUI', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'TINNHAN'
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Danh sách tin nhắn'
        ordering = ['-tg_gui']

    def __str__(self):
        return f"Tin từ {self.makh_gui.hoten} đến {self.makh_nhan.hoten}"


class Thongbao(models.Model):
    """Thông báo - Bảng THONGBAO"""

    LOAI_CHOICES = [
        ('info', 'Thông tin'),
        ('success', 'Thành công'),
        ('warning', 'Cảnh báo'),
        ('error', 'Lỗi'),
        ('booking', 'Đặt phòng'),
        ('message', 'Tin nhắn'),
        ('system', 'Hệ thống'),
    ]

    matb = models.AutoField(db_column='MATB', primary_key=True)
    makh = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH', related_name='thongbao_set')
    tieude = models.CharField(db_column='TIEUDE', max_length=200, verbose_name='Tiêu đề')
    noidung = models.TextField(db_column='NOIDUNG', blank=True, null=True, verbose_name='Nội dung')
    loai = models.CharField(db_column='LOAI', max_length=50, choices=LOAI_CHOICES, default='info')
    dadoc = models.BooleanField(db_column='DADOC', default=False, verbose_name='Đã đọc')
    tg_tao = models.DateTimeField(db_column='TG_TAO', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'THONGBAO'
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Danh sách thông báo'
        ordering = ['-tg_tao']

    def __str__(self):
        return f"{self.tieude} - {self.makh.hoten}"


class Yclamchutro(models.Model):
    """Yêu cầu làm chủ trọ - Bảng YCLAMCHUTRO"""

    STATUS_CHOICES = [
        ('Chờ duyệt', 'Chờ duyệt'),
        ('Đã duyệt', 'Đã duyệt'),
        ('Từ chối', 'Từ chối'),
    ]

    mayc = models.AutoField(db_column='MAYC', primary_key=True)
    makh = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH', related_name='yclamchutro_set')
    lydo = models.TextField(db_column='LYDO', blank=True, null=True, verbose_name='Lý do')
    trangthai = models.CharField(db_column='TRANGTHAI', max_length=50, choices=STATUS_CHOICES, default='Chờ duyệt')
    tg_tao = models.DateTimeField(db_column='TG_TAO', auto_now_add=True)
    tg_duyet = models.DateTimeField(db_column='TG_DUYET', blank=True, null=True)
    nguoiduyet = models.ForeignKey(Khachhang, models.SET_NULL, db_column='NGUOIDUYET',
                                    related_name='yclamchutro_duyet', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'YCLAMCHUTRO'
        verbose_name = 'Yêu cầu làm chủ trọ'
        verbose_name_plural = 'Danh sách yêu cầu làm chủ trọ'
        ordering = ['-tg_tao']

    def __str__(self):
        return f"Yêu cầu: {self.makh.hoten} - {self.trangthai}"