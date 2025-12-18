# ============================================
# apps/rooms/forms.py
# ============================================

from django import forms
from django.forms import inlineformset_factory
from .models import Phongtro, Hinhanh
import bleach


class PhongtroForm(forms.ModelForm):
    """Form tạo/sửa phòng trọ"""
    class Meta:
        model = Phongtro
        fields = ['mant', 'tenpt', 'dientich', 'mota', 'giatien', 'songuoio']
        widgets = {
            'mota': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'mant': 'Nhà trọ',
            'tenpt': 'Tên phòng',
            'dientich': 'Diện tích (m²)',
            'mota': 'Mô tả',
            'giatien': 'Giá tiền (VNĐ)',
            'songuoio': 'Số người ở tối đa',
        }

    def clean_mota(self):
        mota = self.cleaned_data.get('mota')
        if mota:
            return bleach.clean(mota, strip=True)
        return mota


class HinhanhForm(forms.ModelForm):
    """Form upload hình ảnh"""
    class Meta:
        model = Hinhanh
        fields = ['duongdan']
        labels = {
            'duongdan': 'Đường dẫn hình ảnh',
        }


HinhanhFormSet = inlineformset_factory(
    Phongtro,
    Hinhanh,
    form=HinhanhForm,
    extra=5,
    max_num=10,
    can_delete=True,
    fk_name='mapt'
)
