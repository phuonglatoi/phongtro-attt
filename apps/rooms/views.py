# ============================================
# apps/rooms/views.py
# ============================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from .models import Phongtro, Nhatro, Hinhanh
from .forms import PhongtroForm, HinhanhFormSet
from apps.accounts.views import login_required_custom
import bleach


def home_view(request):
    """Trang chủ"""
    # Sử dụng trangthai là string 'Còn trống' thay vì True
    featured_rooms = Phongtro.objects.filter(trangthai='Còn trống').select_related('mant')[:6]

    # Attach first image to each room
    for room in featured_rooms:
        room.first_image = Hinhanh.objects.filter(mapt=room).first()

    return render(request, 'rooms/home.html', {
        'featured_rooms': featured_rooms
    })


def room_list_view(request):
    """Danh sách phòng trọ"""
    rooms = Phongtro.objects.filter(trangthai='Còn trống').select_related('mant')

    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        rooms = rooms.filter(giatien__gte=min_price)
    if max_price:
        rooms = rooms.filter(giatien__lte=max_price)

    # Attach first image to each room
    rooms = list(rooms)
    for room in rooms:
        room.first_image = Hinhanh.objects.filter(mapt=room).first()

    return render(request, 'rooms/room_list.html', {'rooms': rooms})


def room_detail_view(request, pk):
    """Chi tiết phòng trọ"""
    room = get_object_or_404(Phongtro, pk=pk)
    return render(request, 'rooms/room_detail.html', {'room': room})


@login_required_custom
@ratelimit(key='ip', rate='10/h', method='POST')
def room_create_view(request):
    """Tạo phòng trọ mới"""

    # Check if user is owner (chủ trọ)
    khachhang = getattr(request, 'khachhang', None)
    if not khachhang or not khachhang.mavt or khachhang.mavt.tenvt != 'Chủ trọ':
        messages.error(request, 'Bạn phải là chủ trọ để đăng tin.')
        return redirect('rooms:home')

    if request.method == 'POST':
        form = PhongtroForm(request.POST, request.FILES)
        formset = HinhanhFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            room = form.save(commit=False)
            if room.mota:
                room.mota = bleach.clean(room.mota, strip=True)
            room.save()

            formset.instance = room
            formset.save()

            messages.success(request, 'Đăng tin thành công!')
            return redirect('rooms:room_detail', pk=room.pk)
    else:
        form = PhongtroForm()
        formset = HinhanhFormSet()

    return render(request, 'rooms/room_form.html', {
        'form': form,
        'formset': formset
    })


@login_required_custom
def room_update_view(request, pk):
    """Cập nhật phòng trọ"""
    room = get_object_or_404(Phongtro, pk=pk)

    # Check if user owns this room
    khachhang = getattr(request, 'khachhang', None)
    if not khachhang or room.mant.makh != khachhang:
        messages.error(request, 'Bạn không có quyền sửa phòng trọ này.')
        return redirect('rooms:room_detail', pk=pk)

    if request.method == 'POST':
        form = PhongtroForm(request.POST, request.FILES, instance=room)
        formset = HinhanhFormSet(request.POST, request.FILES, instance=room)

        if form.is_valid() and formset.is_valid():
            room = form.save(commit=False)
            if room.mota:
                room.mota = bleach.clean(room.mota, strip=True)
            room.save()
            formset.save()

            messages.success(request, 'Cập nhật phòng trọ thành công!')
            return redirect('rooms:room_detail', pk=room.pk)
    else:
        form = PhongtroForm(instance=room)
        formset = HinhanhFormSet(instance=room)

    return render(request, 'rooms/room_form.html', {
        'form': form,
        'formset': formset
    })


@login_required_custom
def room_delete_view(request, pk):
    """Xóa phòng trọ"""
    room = get_object_or_404(Phongtro, pk=pk)

    # Check if user owns this room
    khachhang = getattr(request, 'khachhang', None)
    if not khachhang or room.mant.makh != khachhang:
        messages.error(request, 'Bạn không có quyền xóa phòng trọ này.')
        return redirect('rooms:room_detail', pk=pk)

    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Đã xóa phòng trọ thành công!')
        return redirect('rooms:room_list')

    return render(request, 'rooms/room_confirm_delete.html', {'room': room})


@ratelimit(key='ip', rate='30/m', method='GET')
def search_view(request):
    """Tìm kiếm phòng trọ"""
    query = request.GET.get('q', '')
    query = bleach.clean(query, strip=True)

    rooms = Phongtro.objects.filter(trangthai='Còn trống', tenpt__icontains=query) | \
            Phongtro.objects.filter(trangthai='Còn trống', mota__icontains=query)

    return render(request, 'rooms/search_results.html', {
        'rooms': rooms,
        'query': query
    })


# ============================================
# Policy Pages
# ============================================

def terms_view(request):
    """Điều khoản sử dụng"""
    return render(request, 'rooms/terms.html')


def privacy_view(request):
    """Chính sách bảo mật"""
    return render(request, 'rooms/privacy.html')


def policies_view(request):
    """Quy định đăng tin"""
    return render(request, 'rooms/policies.html')


def contact_view(request):
    """Liên hệ & Hỗ trợ"""
    return render(request, 'rooms/contact.html')
