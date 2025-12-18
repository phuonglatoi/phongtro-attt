# apps/accounts/models.py
"""
👤 USER MODELS - Ánh xạ với CSDL hiện có
"""

from django.db import models
from django.utils import timezone
import pyotp


class Vaitro(models.Model):
    """Vai trò - Bảng VAITRO"""
    mavt = models.AutoField(db_column='MAVT', primary_key=True)
    tenvt = models.CharField(db_column='TENVT', unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'VAITRO'
        verbose_name = 'Vai trò'
        verbose_name_plural = 'Vai trò'

    def __str__(self):
        return self.tenvt


class Taikhoan(models.Model):
    """Tài khoản - Bảng TAIKHOAN"""
    matk = models.AutoField(db_column='MATK', primary_key=True)
    username = models.CharField(db_column='USERNAME', unique=True, max_length=100, blank=True, null=True)
    password_hash = models.BinaryField(db_column='PASSWORD_HASH', blank=True, null=True)
    password_salt = models.CharField(db_column='PASSWORD_SALT', max_length=36, blank=True, null=True)

    # Security
    is_locked = models.BooleanField(db_column='IS_LOCKED', default=False, blank=True, null=True)
    lock_time = models.DateTimeField(db_column='LOCK_TIME', blank=True, null=True)
    failed_login_count = models.IntegerField(db_column='FAILED_LOGIN_COUNT', default=0, blank=True, null=True)

    # 2FA
    two_factor_enabled = models.BooleanField(db_column='TWO_FACTOR_ENABLED', default=False, blank=True, null=True)
    two_factor_secret = models.CharField(db_column='TWO_FACTOR_SECRET', max_length=100, blank=True, null=True)

    # OAuth
    oauth_provider = models.CharField(db_column='OAUTH_PROVIDER', max_length=50, blank=True, null=True)
    oauth_id = models.CharField(db_column='OAUTH_ID', max_length=200, blank=True, null=True)

    # Login tracking
    last_login_ip = models.CharField(db_column='LAST_LOGIN_IP', max_length=45, blank=True, null=True)
    last_login_time = models.DateTimeField(db_column='LAST_LOGIN_TIME', blank=True, null=True)

    tg_tao = models.DateTimeField(db_column='TG_TAO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TAIKHOAN'
        verbose_name = 'Tài khoản'
        verbose_name_plural = 'Tài khoản'

    def __str__(self):
        return self.username or f"TK_{self.matk}"


class Khachhang(models.Model):
    """Khách hàng - Bảng KHACHHANG"""
    makh = models.AutoField(db_column='MAKH', primary_key=True)
    matk = models.ForeignKey(Taikhoan, models.CASCADE, db_column='MATK', blank=True, null=True)
    mavt = models.ForeignKey(Vaitro, models.DO_NOTHING, db_column='MAVT', blank=True, null=True)
    hoten = models.CharField(db_column='HOTEN', max_length=200)
    gioitinh = models.BooleanField(db_column='GIOITINH', blank=True, null=True)
    diachi = models.CharField(db_column='DIACHI', max_length=500, blank=True, null=True)
    sdt = models.CharField(db_column='SDT', max_length=15, blank=True, null=True)
    email = models.CharField(db_column='EMAIL', unique=True, max_length=200)
    ngaysinh = models.DateField(db_column='NGAYSINH', blank=True, null=True)
    cccd = models.CharField(db_column='CCCD', max_length=20, blank=True, null=True)
    trangthai = models.BooleanField(db_column='TRANGTHAI', default=True)
    tg_tao = models.DateTimeField(db_column='TG_TAO', blank=True, null=True)

    # Security columns
    is_2fa_enabled = models.BooleanField(db_column='IS_2FA_ENABLED', default=False)
    totp_secret = models.CharField(db_column='TOTP_SECRET', max_length=32, blank=True, null=True)
    is_locked = models.BooleanField(db_column='IS_LOCKED', default=False)
    locked_until = models.DateTimeField(db_column='LOCKED_UNTIL', blank=True, null=True)
    last_password_change = models.DateTimeField(db_column='LAST_PASSWORD_CHANGE', blank=True, null=True)
    google_id = models.CharField(db_column='GOOGLE_ID', max_length=255, blank=True, null=True)
    oauth_provider = models.CharField(db_column='OAUTH_PROVIDER', max_length=50, blank=True, null=True)



    class Meta:
        managed = False
        db_table = 'KHACHHANG'
        verbose_name = 'Khách hàng'
        verbose_name_plural = 'Khách hàng'

    def __str__(self):
        return f"{self.hoten} ({self.email})"

    # =========================
    # 🔐 2FA METHODS
    # =========================

    def enable_2fa(self):
        """Bật 2FA"""
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
        self.is_2fa_enabled = True
        self.save()
        return self.get_totp_uri()

    def disable_2fa(self):
        """Tắt 2FA"""
        self.is_2fa_enabled = False
        self.totp_secret = None
        self.save()

    def get_totp_uri(self):
        """URI dùng tạo QR"""
        if not self.totp_secret:
            return None
        totp = pyotp.TOTP(self.totp_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name='PhongTro.vn'
        )

    def verify_totp(self, token, check_enabled=True):
        """Xác thực OTP"""
        import logging
        logger = logging.getLogger('apps.accounts')

        if not self.totp_secret:
            logger.warning(f"verify_totp: No TOTP secret for user {self.email}")
            return False
        if check_enabled and not self.is_2fa_enabled:
            logger.warning(f"verify_totp: 2FA not enabled for user {self.email}, check_enabled={check_enabled}")
            return False

        totp = pyotp.TOTP(self.totp_secret)
        # valid_window=2 allows for +/- 60 seconds of time drift
        result = totp.verify(token, valid_window=2)

        if not result:
            # Debug: show expected code vs provided code
            expected = totp.now()
            logger.warning(f"verify_totp: FAILED for {self.email}. Provided: {token}, Expected: {expected}")

        return result

    def is_account_locked(self):
        """Kiểm tra bị khoá login không"""
        if not self.is_locked:
            return False
        if self.locked_until and timezone.now() > self.locked_until:
            self.is_locked = False
            self.locked_until = None
            self.save()
            return False
        return True

    @property
    def role(self):
        """Get user role name"""
        return self.mavt.tenvt if self.mavt else None

class LoginHistory(models.Model):
    """Lịch sử đăng nhập - Bảng LOGIN_HISTORY"""
    id = models.AutoField(db_column='ID', primary_key=True)
    makh = models.ForeignKey(Khachhang, models.CASCADE, db_column='MAKH')
    success = models.BooleanField(db_column='SUCCESS')
    ip_address = models.CharField(db_column='IP_ADDRESS', max_length=45)
    user_agent = models.TextField(db_column='USER_AGENT', blank=True, null=True)
    device_type = models.CharField(db_column='DEVICE_TYPE', max_length=50, blank=True, null=True)
    os_family = models.CharField(db_column='OS_FAMILY', max_length=50, blank=True, null=True)
    browser_family = models.CharField(db_column='BROWSER_FAMILY', max_length=50, blank=True, null=True)
    country = models.CharField(db_column='COUNTRY', max_length=100, blank=True, null=True)
    city = models.CharField(db_column='CITY', max_length=100, blank=True, null=True)
    failure_reason = models.CharField(db_column='FAILURE_REASON', max_length=100, blank=True, null=True)
    used_2fa = models.BooleanField(db_column='USED_2FA', default=False)
    timestamp = models.DateTimeField(db_column='TIMESTAMP', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'LOGIN_HISTORY'
        verbose_name = 'Lịch sử đăng nhập'
        verbose_name_plural = 'Lịch sử đăng nhập'
        ordering = ['-timestamp']




class FailedLoginAttempts(models.Model):
    """Lần đăng nhập thất bại - Bảng FAILED_LOGIN_ATTEMPTS"""
    id = models.AutoField(db_column='ID', primary_key=True)
    ip_address = models.CharField(db_column='IP_ADDRESS', max_length=45)
    username_or_email = models.CharField(db_column='USERNAME_OR_EMAIL', max_length=200, blank=True, null=True)
    attempt_time = models.DateTimeField(db_column='ATTEMPT_TIME', auto_now_add=True)
    user_agent = models.TextField(db_column='USER_AGENT', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'FAILED_LOGIN_ATTEMPTS'
        verbose_name = 'Lần đăng nhập thất bại'
        verbose_name_plural = 'Lần đăng nhập thất bại'
        ordering = ['-attempt_time']


class BlockedIps(models.Model):
    """IP bị chặn - Bảng BLOCKED_IPS"""
    id = models.AutoField(db_column='ID', primary_key=True)
    ip_address = models.CharField(db_column='IP_ADDRESS', max_length=45, unique=True)
    reason = models.CharField(db_column='REASON', max_length=100)
    blocked_at = models.DateTimeField(db_column='BLOCKED_AT', auto_now_add=True)
    blocked_until = models.DateTimeField(db_column='BLOCKED_UNTIL', blank=True, null=True)
    blocked_by = models.ForeignKey(Khachhang, models.SET_NULL, db_column='BLOCKED_BY',
                                    blank=True, null=True, related_name='blocked_ips')

    class Meta:
        managed = False
        db_table = 'BLOCKED_IPS'
        verbose_name = 'IP bị chặn'
        verbose_name_plural = 'Danh sách IP bị chặn'


class SecurityLogs(models.Model):
    """Log bảo mật - Bảng SECURITY_LOGS"""
    id = models.AutoField(db_column='ID', primary_key=True)
    action_type = models.CharField(db_column='ACTION_TYPE', max_length=100)
    matk = models.ForeignKey(Taikhoan, models.SET_NULL, db_column='MATK', blank=True, null=True)
    ip_address = models.CharField(db_column='IP_ADDRESS', max_length=45)
    details = models.TextField(db_column='DETAILS', blank=True, null=True)
    log_time = models.DateTimeField(db_column='LOG_TIME', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'SECURITY_LOGS'
        verbose_name = 'Log bảo mật'
        verbose_name_plural = 'Log bảo mật'
        ordering = ['-log_time']


class AuditLogs(models.Model):
    """Log kiểm toán - Bảng AUDIT_LOGS"""
    id = models.AutoField(db_column='ID', primary_key=True)
    table_name = models.CharField(db_column='TABLE_NAME', max_length=100)
    action = models.CharField(db_column='ACTION', max_length=50)
    old_data = models.TextField(db_column='OLD_DATA', blank=True, null=True)
    new_data = models.TextField(db_column='NEW_DATA', blank=True, null=True)
    changed_by = models.CharField(db_column='CHANGED_BY', max_length=100, blank=True, null=True)
    changed_date = models.DateTimeField(db_column='CHANGED_DATE', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'AUDIT_LOGS'
        verbose_name = 'Log kiểm toán'
        verbose_name_plural = 'Log kiểm toán'
        ordering = ['-changed_date']


class SecurityQuestion(models.Model):
    """Câu hỏi bảo mật - Bảng SECURITY_QUESTIONS"""

    QUESTION_CHOICES = [
        ('pet', 'Tên thú cưng đầu tiên của bạn là gì?'),
        ('school', 'Bạn học trường tiểu học nào?'),
        ('city', 'Bạn sinh ra ở thành phố nào?'),
        ('mother', 'Họ tên mẹ bạn là gì?'),
        ('food', 'Món ăn yêu thích của bạn là gì?'),
        ('movie', 'Phim yêu thích của bạn là gì?'),
        ('friend', 'Tên người bạn thân nhất thời thơ ấu?'),
        ('car', 'Chiếc xe đầu tiên bạn sở hữu là gì?'),
    ]

    id = models.AutoField(primary_key=True)
    makh = models.OneToOneField(Khachhang, on_delete=models.CASCADE, db_column='MAKH', related_name='security_question_obj')
    question_key = models.CharField(max_length=50, db_column='QUESTION_KEY')
    answer_hash = models.CharField(max_length=255, db_column='ANSWER_HASH')
    created_at = models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')
    updated_at = models.DateTimeField(auto_now=True, db_column='UPDATED_AT')

    class Meta:
        managed = True  # Django will manage this table
        db_table = 'SECURITY_QUESTIONS'
        verbose_name = 'Câu hỏi bảo mật'
        verbose_name_plural = 'Câu hỏi bảo mật'

    @classmethod
    def get_question_label(cls, key):
        """Get question label from key"""
        for k, label in cls.QUESTION_CHOICES:
            if k == key:
                return label
        return key

    def set_answer(self, answer):
        """Hash and store the answer"""
        import hashlib
        clean_answer = answer.strip().lower()
        self.answer_hash = hashlib.sha256(clean_answer.encode()).hexdigest()
        self.save()

    def verify_answer(self, answer):
        """Verify the answer"""
        import hashlib
        clean_answer = answer.strip().lower()
        answer_hash = hashlib.sha256(clean_answer.encode()).hexdigest()
        return answer_hash == self.answer_hash

    def __str__(self):
        return f"Security Q for {self.makh.hoten}"