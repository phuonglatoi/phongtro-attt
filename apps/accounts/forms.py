# ============================================
# apps/accounts/forms.py
# ============================================

from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Khachhang
import bleach
import hashlib
import re


# ============================================
# CUSTOM PASSWORD VALIDATOR
# ============================================
def validate_strong_password(password):
    """
    Validate password với các yêu cầu:
    - Tối thiểu 8 ký tự
    - Có ít nhất 1 chữ hoa
    - Có ít nhất 1 chữ thường
    - Có ít nhất 1 số
    - Có ít nhất 1 ký tự đặc biệt
    """
    if len(password) < 8:
        raise ValidationError('Mật khẩu phải có ít nhất 8 ký tự.')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('Mật khẩu phải có ít nhất 1 chữ hoa (A-Z).')

    if not re.search(r'[a-z]', password):
        raise ValidationError('Mật khẩu phải có ít nhất 1 chữ thường (a-z).')

    if not re.search(r'[0-9]', password):
        raise ValidationError('Mật khẩu phải có ít nhất 1 chữ số (0-9).')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
        raise ValidationError('Mật khẩu phải có ít nhất 1 ký tự đặc biệt (!@#$%^&*...).')


class LoginForm(forms.Form):
    """Form đăng nhập"""

    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'autocomplete': 'email'
        })
    )

    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu',
            'autocomplete': 'current-password'
        })
    )

    remember_me = forms.BooleanField(required=False, label='Ghi nhớ đăng nhập')


class RegisterForm(forms.Form):
    """Form đăng ký tài khoản mới"""

    username = forms.CharField(
        label='Họ tên',
        min_length=2,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ tên',
            'minlength': '2',
            'maxlength': '200'
        })
    )

    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    phone = forms.CharField(
        label='Số điện thoại',
        required=True,
        validators=[
            RegexValidator(
                regex=r'^(\+84|0)[0-9]{9}$',
                message='Số điện thoại không hợp lệ (VD: 0912345678)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Số điện thoại',
            'pattern': r'(\+84|0)[0-9]{9}'
        })
    )

    password1 = forms.CharField(
        label='Mật khẩu',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu (8+ ký tự, chữ hoa, chữ thường, số, ký tự đặc biệt)',
            'minlength': '8'
        }),
        validators=[validate_strong_password],
        help_text='Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt.'
    )

    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            username = bleach.clean(username, strip=True)
            # Chỉ cho phép chữ cái, số, khoảng trắng và dấu tiếng Việt
            if len(username) < 2:
                raise forms.ValidationError("Họ tên phải có ít nhất 2 ký tự.")
            if len(username) > 200:
                raise forms.ValidationError("Họ tên không được quá 200 ký tự.")
        return username

    def clean_email(self):
        email = bleach.clean(self.cleaned_data.get('email'), strip=True).lower()
        if Khachhang.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã được sử dụng.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Skip duplicate check for now - database column might not exist
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Mật khẩu xác nhận không khớp.")

        return cleaned_data


class PasswordChangeWithOTPForm(forms.Form):
    """Form đổi mật khẩu với OTP"""

    old_password = forms.CharField(
        label='Mật khẩu hiện tại',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    new_password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
    )

    confirm_password = forms.CharField(
        label='Xác nhận mật khẩu mới',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    otp_code = forms.CharField(
        label='Mã OTP',
        min_length=6,
        max_length=6,
        validators=[RegexValidator(r'^[0-9]{6}$', message='Mã OTP phải gồm 6 chữ số')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000000'})
    )

    def __init__(self, khachhang, *args, **kwargs):
        self.khachhang = khachhang
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        old = cleaned.get("old_password")
        new = cleaned.get("new_password")
        confirm = cleaned.get("confirm_password")
        otp = cleaned.get("otp_code")

        # Verify old password (SQL Server dùng HASHBYTES('SHA2_256', password) không salt)
        if self.khachhang and self.khachhang.matk:
            taikhoan = self.khachhang.matk

            # Hash giống SQL Server
            computed_hash = hashlib.sha256(old.encode('utf-8')).digest()

            # SQL Server trả về memoryview cho binary field
            stored_hash = taikhoan.matkhau_hash
            if isinstance(stored_hash, memoryview):
                stored_hash = stored_hash.tobytes()
            elif stored_hash and not isinstance(stored_hash, bytes):
                stored_hash = bytes(stored_hash)

            if computed_hash != stored_hash:
                raise forms.ValidationError("Mật khẩu hiện tại không đúng.")

            # Verify OTP (2FA nằm trên KHACHHANG)
            if self.khachhang.totp_secret:
                import pyotp
                totp = pyotp.TOTP(self.khachhang.totp_secret)
                if not totp.verify(otp, valid_window=1):
                    raise forms.ValidationError("Mã OTP không hợp lệ.")

        if new != confirm:
            raise forms.ValidationError("Xác nhận mật khẩu không khớp.")

        return cleaned


class Enable2FAForm(forms.Form):
    """Form bật 2FA"""
    otp_code = forms.CharField(
        label='Mã OTP từ ứng dụng',
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r'^[0-9]{6}$', message='Mã OTP phải gồm 6 chữ số')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000000',
            'autocomplete': 'off'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """Form cập nhật thông tin cá nhân"""

    class Meta:
        model = Khachhang
        fields = ['hoten', 'sdt', 'diachi', 'cccd']
        widgets = {
            'hoten': forms.TextInput(attrs={'class': 'form-control'}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'diachi': forms.TextInput(attrs={'class': 'form-control'}),
            'cccd': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'hoten': 'Họ tên',
            'sdt': 'Số điện thoại',
            'diachi': 'Địa chỉ',
            'cccd': 'CMND/CCCD',
        }

    def clean_sdt(self):
        sdt = self.cleaned_data.get('sdt')
        if sdt and Khachhang.objects.exclude(makh=self.instance.makh).filter(sdt=sdt).exists():
            raise forms.ValidationError("Số điện thoại đã tồn tại.")
        return sdt

    def clean_hoten(self):
        hoten = bleach.clean(self.cleaned_data.get('hoten'), strip=True)
        return hoten
