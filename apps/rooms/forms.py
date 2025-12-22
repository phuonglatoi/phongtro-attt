# ============================================
# apps/rooms/forms.py
# ============================================

from django import forms
from django.forms import inlineformset_factory
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Phongtro, Hinhanh
import bleach
import re


class PhongtroForm(forms.ModelForm):
    """Form tạo/sửa phòng trọ"""

    # Giới hạn diện tích: 5m² - 500m²
    dientich = forms.DecimalField(
        label='Diện tích (m²)',
        min_value=5,
        max_value=500,
        decimal_places=1,
        validators=[
            MinValueValidator(5, message='Diện tích tối thiểu là 5m²'),
            MaxValueValidator(500, message='Diện tích tối đa là 500m²')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: 20',
            'min': '5',
            'max': '500',
            'step': '0.1'
        })
    )

    # Giới hạn giá tiền: 500,000 - 50,000,000 VNĐ
    giatien = forms.DecimalField(
        label='Giá tiền (VNĐ/tháng)',
        min_value=500000,
        max_value=50000000,
        decimal_places=0,
        validators=[
            MinValueValidator(500000, message='Giá tiền tối thiểu là 500,000 VNĐ'),
            MaxValueValidator(50000000, message='Giá tiền tối đa là 50,000,000 VNĐ')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: 3000000',
            'min': '500000',
            'max': '50000000',
            'step': '100000'
        })
    )

    # Số người ở: 1-20 người
    songuoio = forms.IntegerField(
        label='Số người ở tối đa',
        min_value=1,
        max_value=20,
        validators=[
            MinValueValidator(1, message='Số người ở tối thiểu là 1'),
            MaxValueValidator(20, message='Số người ở tối đa là 20')
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: 2',
            'min': '1',
            'max': '20'
        })
    )

    class Meta:
        model = Phongtro
        fields = ['mant', 'tenpt', 'dientich', 'mota', 'giatien', 'songuoio']
        widgets = {
            'mota': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'tenpt': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'mant': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'mant': 'Nhà trọ',
            'tenpt': 'Tên phòng',
            'dientich': 'Diện tích (m²)',
            'mota': 'Mô tả',
            'giatien': 'Giá tiền (VNĐ)',
            'songuoio': 'Số người ở tối đa',
        }

    def clean_tenpt(self):
        """Validate tên phòng - chỉ cho phép chữ, số, khoảng trắng, dấu câu cơ bản"""
        tenpt = self.cleaned_data.get('tenpt')
        if tenpt:
            tenpt = bleach.clean(tenpt, strip=True)
            # Chỉ cho phép chữ cái, số, khoảng trắng, dấu câu tiếng Việt
            if len(tenpt) < 3:
                raise forms.ValidationError('Tên phòng phải có ít nhất 3 ký tự.')
            if len(tenpt) > 200:
                raise forms.ValidationError('Tên phòng không được quá 200 ký tự.')
        return tenpt

    def clean_mota(self):
        """Validate mô tả - loại bỏ HTML, giới hạn ký tự"""
        mota = self.cleaned_data.get('mota')
        if mota:
            mota = bleach.clean(mota, strip=True)
            if len(mota) > 2000:
                raise forms.ValidationError('Mô tả không được quá 2000 ký tự.')
        return mota


# ============================================
# IMAGE UPLOAD VALIDATION
# ============================================

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
ALLOWED_IMAGE_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGES_PER_ROOM = 5


def validate_image_file(image_file):
    """
    Validate uploaded image file.
    Returns (is_valid, error_message)
    """
    if not image_file:
        return True, None

    # Check file extension
    filename = image_file.name.lower()
    ext = filename.split('.')[-1] if '.' in filename else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f'Định dạng file không hỗ trợ. Chỉ chấp nhận: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'

    # Check MIME type
    if hasattr(image_file, 'content_type') and image_file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        return False, f'Loại file không hợp lệ. Chỉ chấp nhận: {", ".join(ALLOWED_IMAGE_MIME_TYPES)}'

    # Check file size
    if image_file.size > MAX_IMAGE_SIZE:
        return False, f'File quá lớn. Kích thước tối đa: {MAX_IMAGE_SIZE // (1024*1024)}MB'

    # Check magic bytes (actual file content)
    try:
        header = image_file.read(8)
        image_file.seek(0)  # Reset file pointer

        is_valid_image = (
            header[:3] == b'\xff\xd8\xff' or  # JPEG
            header[:8] == b'\x89PNG\r\n\x1a\n' or  # PNG
            header[:6] in (b'GIF87a', b'GIF89a') or  # GIF
            header[:4] == b'RIFF'  # WebP
        )

        if not is_valid_image:
            return False, 'Nội dung file không phải ảnh hợp lệ.'
    except Exception:
        return False, 'Không thể đọc file ảnh.'

    return True, None


class HinhanhForm(forms.ModelForm):
    """Form upload hình ảnh với validation"""

    image_file = forms.ImageField(
        required=False,
        label='Tải ảnh lên',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png,.gif,.webp'
        })
    )

    class Meta:
        model = Hinhanh
        fields = ['duongdan', 'mota']
        labels = {
            'duongdan': 'Đường dẫn hình ảnh',
            'mota': 'Mô tả ảnh',
        }
        widgets = {
            'duongdan': forms.HiddenInput(),
            'mota': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
        }

    def clean_image_file(self):
        """Validate uploaded image"""
        image_file = self.cleaned_data.get('image_file')
        if image_file:
            is_valid, error_msg = validate_image_file(image_file)
            if not is_valid:
                raise forms.ValidationError(error_msg)
        return image_file

    def clean_mota(self):
        """Validate mô tả ảnh"""
        mota = self.cleaned_data.get('mota')
        if mota:
            mota = bleach.clean(mota, strip=True)
            if len(mota) > 200:
                raise forms.ValidationError('Mô tả ảnh không được quá 200 ký tự.')
        return mota


HinhanhFormSet = inlineformset_factory(
    Phongtro,
    Hinhanh,
    form=HinhanhForm,
    extra=5,
    max_num=MAX_IMAGES_PER_ROOM,
    can_delete=True,
    fk_name='mapt'
)
