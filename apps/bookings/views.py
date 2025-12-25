# ============================================
# apps/bookings/views.py
# Booking management views
# ============================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django_ratelimit.decorators import ratelimit
import bleach

import re
from datetime import datetime

from .models import Henxemtro, Thuetro, Danhgia, Tinnhan, Thongbao, Yclamchutro
from apps.rooms.models import Phongtro, Nhatro
from apps.accounts.models import Khachhang
from apps.accounts.views import login_required_custom


def get_current_khachhang(request):
    """Lấy thông tin khách hàng từ session"""
    makh = request.session.get('makh')
    if makh:
        try:
            return Khachhang.objects.get(makh=makh)
        except Khachhang.DoesNotExist:
            pass
    return None


def create_notification(khachhang, tieude, noidung, loai='info'):
    """Tạo thông báo cho người dùng"""
    from django.db import connection
    try:
        # Use raw SQL to avoid OUTPUT clause issues with triggers
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO THONGBAO (MAKH, TIEUDE, NOIDUNG, LOAI, DADOC)
                VALUES (%s, %s, %s, %s, 0)
            """, [khachhang.makh, tieude, noidung, loai])
    except Exception:
        # Fallback to ORM
        try:
            Thongbao.objects.create(
                makh=khachhang,
                tieude=tieude,
                noidung=noidung,
                loai=loai
            )
        except:
            pass


# ============================================
# VIEWING APPOINTMENTS (Hẹn xem trọ)
# ============================================

@login_required_custom
@ratelimit(key='ip', rate='10/h', method='POST')
def create_henxem(request, room_id):
    """Tạo lịch hẹn xem phòng"""
    room = get_object_or_404(Phongtro, pk=room_id)
    khachhang = get_current_khachhang(request)

    if not khachhang:
        messages.error(request, 'Vui lòng đăng nhập để đặt lịch xem phòng.')
        return redirect('accounts:login')

    if room.mant.makh == khachhang:
        messages.warning(request, 'Bạn không thể đặt lịch xem phòng của chính mình.')
        return redirect('rooms:room_detail', pk=room_id)

    if request.method == 'POST':
        # 1. Lấy dữ liệu tách rời
        ngay = request.POST.get('ngay')
        gio = request.POST.get('gio')
        
        ghichu_raw = request.POST.get('ghichu', '')
        ghichu = bleach.clean(ghichu_raw, strip=True)

        # 2. Ghép ngày và giờ lại để validate và lưu DB
        # Định dạng ghép: YYYY-MM-DD + T + HH:MM (Ví dụ: 2023-10-25T14:30)
        ngayhen_full = ""
        if ngay and gio:
            ngayhen_full = f"{ngay}T{gio}"

        # 3. Gọi hàm validate (Hàm này bạn đã thêm ở bước trước)
        is_valid, error_msg = validate_henxem_data(ngayhen_full, ghichu)
        
        if not is_valid:
            messages.error(request, error_msg)
            # Trả về form cùng dữ liệu cũ để user không phải nhập lại
            # Lưu ý: Trả về old_ngay và old_gio riêng
            return render(request, 'bookings/henxem_form.html', {
                'room': room,
                'old_ngay': ngay,
                'old_gio': gio,
                'old_ghichu': ghichu
            })

        try:
            henxem = Henxemtro.objects.create(
                mapt=room,
                makh=khachhang,
                ngayhen=ngayhen_full, # Lưu chuỗi đã ghép
                ghichu=ghichu,
                trangthai='Chờ xác nhận'
            )

            # Notify landlord... (Giữ nguyên code cũ)
            landlord = room.mant.makh
            if landlord:
                create_notification(
                    landlord,
                    'Có lịch hẹn xem phòng mới',
                    f'{khachhang.hoten} muốn xem phòng "{room.tenpt}" vào {gio} ngày {ngay}',
                    'booking'
                )

            messages.success(request, 'Đã gửi yêu cầu hẹn xem phòng thành công!')
            return redirect('rooms:room_detail', pk=room_id)
            
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')

    return render(request, 'bookings/henxem_form.html', {'room': room})


@login_required_custom
def my_bookings(request):
    """Danh sách lịch hẹn xem phòng của người dùng"""
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    henxem_list = Henxemtro.objects.filter(makh=khachhang).select_related('mapt', 'mapt__mant')

    return render(request, 'bookings/my_bookings.html', {
        'henxem_list': henxem_list
    })


@login_required_custom
def cancel_henxem(request, pk):
    """Hủy lịch hẹn xem phòng"""
    khachhang = get_current_khachhang(request)
    henxem = get_object_or_404(Henxemtro, pk=pk, makh=khachhang)

    if henxem.trangthai == 'Chờ xác nhận':
        henxem.trangthai = 'Đã hủy'
        henxem.save()
        messages.success(request, 'Đã hủy lịch hẹn.')
    else:
        messages.error(request, 'Không thể hủy lịch hẹn này.')

    return redirect('bookings:my_bookings')


# ============================================
# REVIEWS (Đánh giá)
# ============================================

@login_required_custom
@ratelimit(key='ip', rate='5/h', method='POST')
def create_review(request, room_id):
    """Tạo đánh giá phòng trọ - chỉ cho phép người đã đặt lịch hẹn được chấp nhận"""
    room = get_object_or_404(Phongtro, pk=room_id)
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    # Check if user has a confirmed/completed viewing appointment for this room
    # Chỉ những ai đặt lịch hẹn đi xem phòng được chấp nhận mới được đánh giá
    has_confirmed_viewing = Henxemtro.objects.filter(
        makh=khachhang,
        mapt=room,
        trangthai__in=['Đã xác nhận', 'Đã xem']
    ).exists()

    if not has_confirmed_viewing:
        messages.error(request, 'Bạn chỉ có thể đánh giá phòng đã đặt lịch hẹn xem và được chấp nhận.')
        return redirect('rooms:room_detail', pk=room_id)

    # Check if already reviewed
    if Danhgia.objects.filter(makh=khachhang, mapt=room).exists():
        messages.warning(request, 'Bạn đã đánh giá phòng này rồi.')
        return redirect('rooms:room_detail', pk=room_id)

    if request.method == 'POST':
        sao = int(request.POST.get('sao', 5))
        binhluan = bleach.clean(request.POST.get('binhluan', ''), strip=True)

        if sao < 1 or sao > 5:
            sao = 5

        Danhgia.objects.create(
            mapt=room,
            makh=khachhang,
            sao=sao,
            binhluan=binhluan
        )

        messages.success(request, 'Cảm ơn bạn đã đánh giá!')
        return redirect('rooms:room_detail', pk=room_id)

    return render(request, 'bookings/review_form.html', {'room': room})


# ============================================
# MESSAGES (Tin nhắn)
# ============================================

@login_required_custom
def inbox(request):
    """Hộp thư đến"""
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    # Get all conversations
    received = Tinnhan.objects.filter(makh_nhan=khachhang).select_related('makh_gui')
    sent = Tinnhan.objects.filter(makh_gui=khachhang).select_related('makh_nhan')

    # Get unique conversation partners
    partners = set()
    for msg in received:
        partners.add(msg.makh_gui)
    for msg in sent:
        partners.add(msg.makh_nhan)

    # Count unread
    unread_count = received.filter(dadoc=False).count()

    return render(request, 'bookings/inbox.html', {
        'partners': partners,
        'unread_count': unread_count
    })


def validate_message_content_inline(content):
    """
    Validate nội dung tin nhắn:
    - Không cho phép ký tự đặc biệt (trừ dấu câu tiếng Việt)
    - Giới hạn 500 ký tự
    """
    import re

    if not content:
        return False, 'Vui lòng nhập nội dung tin nhắn.'

    if len(content) > 30:
        return False, 'Tin nhắn không được quá 30 ký tự.'

    if len(content) < 2:
        return False, 'Tin nhắn phải có ít nhất 2 ký tự.'

    # Không cho phép: <, >, {, }, [, ], |, \, ^, ~, `, @, #, $, %, &, *, =, +
    dangerous_chars = re.compile(r'[<>{}|\[\]\\^~`#$%&*=+]')
    if dangerous_chars.search(content):
        return False, 'Tin nhắn không được chứa ký tự đặc biệt.'

    return True, content


@login_required_custom
def conversation(request, partner_id):
    """Cuộc hội thoại với một người - chỉ cho phép nhắn tin với chủ trọ có phòng"""
    khachhang = get_current_khachhang(request)
    partner = get_object_or_404(Khachhang, pk=partner_id)

    if not khachhang:
        return redirect('accounts:login')

    # Kiểm tra partner có phải là chủ trọ có phòng không
    # Hoặc đã có cuộc hội thoại trước đó (để tiếp tục chat)
    from apps.rooms.models import Nhatro
    partner_has_rooms = Nhatro.objects.filter(makh=partner).exists()
    has_existing_conversation = Tinnhan.objects.filter(
        Q(makh_gui=khachhang, makh_nhan=partner) |
        Q(makh_gui=partner, makh_nhan=khachhang)
    ).exists()

    # Chỉ cho phép nhắn tin nếu partner là chủ trọ có phòng hoặc đã có cuộc hội thoại
    if not partner_has_rooms and not has_existing_conversation:
        messages.error(request, 'Bạn chỉ có thể nhắn tin cho chủ trọ có phòng trọ.')
        return redirect('bookings:inbox')

    # Get all messages between two people
    messages_list = Tinnhan.objects.filter(
        Q(makh_gui=khachhang, makh_nhan=partner) |
        Q(makh_gui=partner, makh_nhan=khachhang)
    ).order_by('tg_gui')

    # Mark received messages as read
    Tinnhan.objects.filter(makh_gui=partner, makh_nhan=khachhang, dadoc=False).update(dadoc=True)

    if request.method == 'POST':
        noidung_raw = request.POST.get('noidung', '')
        noidung_clean = bleach.clean(noidung_raw, strip=True)

        # Validate nội dung tin nhắn
        is_valid, result = validate_message_content_inline(noidung_clean)
        if not is_valid:
            messages.error(request, result)
            return render(request, 'bookings/conversation.html', {
                'partner': partner,
                'messages_list': messages_list,
                'noidung': noidung_raw
            })

        Tinnhan.objects.create(
            makh_gui=khachhang,
            makh_nhan=partner,
            noidung=result
        )

        # Notify partner
        create_notification(
            partner,
            'Tin nhắn mới',
            f'{khachhang.hoten} đã gửi tin nhắn cho bạn',
            'message'
        )

        return redirect('bookings:conversation', partner_id=partner_id)

    return render(request, 'bookings/conversation.html', {
        'partner': partner,
        'messages_list': messages_list
    })


def validate_message_content(content):
    """
    Validate nội dung tin nhắn:
    - Không cho phép ký tự đặc biệt (trừ dấu câu tiếng Việt)
    - Giới hạn 500 ký tự
    """
    import re

    if not content:
        return False, 'Vui lòng nhập nội dung tin nhắn.'

    if len(content) > 500:
        return False, 'Tin nhắn không được quá 500 ký tự.'

    if len(content) < 2:
        return False, 'Tin nhắn phải có ít nhất 2 ký tự.'

    # Cho phép: chữ cái (bao gồm tiếng Việt), số, khoảng trắng, dấu câu cơ bản
    # Không cho phép: <, >, {, }, [, ], |, \, ^, ~, `, @, #, $, %, &, *, =, +
    dangerous_chars = re.compile(r'[<>{}|\[\]\\^~`@#$%&*=+]')
    if dangerous_chars.search(content):
        return False, 'Tin nhắn không được chứa ký tự đặc biệt (<, >, {, }, [, ], |, \\, ^, ~, `, @, #, $, %, &, *, =, +).'

    return True, content


@login_required_custom
def send_message_to_landlord(request, room_id):
    """Gửi tin nhắn cho chủ trọ - chỉ cho phép nhắn tin cho chủ trọ có phòng"""
    room = get_object_or_404(Phongtro, pk=room_id)
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    landlord = room.mant.makh
    if not landlord:
        messages.error(request, 'Không tìm thấy thông tin chủ trọ.')
        return redirect('rooms:room_detail', pk=room_id)

    # Kiểm tra chủ trọ có phòng trọ không (đã có vì room tồn tại)
    # Kiểm tra phòng đang hoạt động (còn trống hoặc đã thuê)
    if room.trangthai not in ['Còn trống', 'Đã thuê']:
        messages.error(request, 'Phòng trọ này không còn hoạt động.')
        return redirect('rooms:room_detail', pk=room_id)

    if request.method == 'POST':
        noidung_raw = request.POST.get('noidung', '')
        noidung_clean = bleach.clean(noidung_raw, strip=True)

        # Validate nội dung tin nhắn
        is_valid, result = validate_message_content(noidung_clean)
        if not is_valid:
            messages.error(request, result)
            return render(request, 'bookings/send_message.html', {
                'room': room,
                'landlord': landlord,
                'noidung': noidung_raw
            })

        Tinnhan.objects.create(
            makh_gui=khachhang,
            makh_nhan=landlord,
            noidung=f"[Về phòng: {room.tenpt}] {result}"
        )

        create_notification(
            landlord,
            'Tin nhắn mới về phòng trọ',
            f'{khachhang.hoten} hỏi về phòng "{room.tenpt}"',
            'message'
        )

        messages.success(request, 'Đã gửi tin nhắn cho chủ trọ.')
        return redirect('rooms:room_detail', pk=room_id)

    return render(request, 'bookings/send_message.html', {
        'room': room,
        'landlord': landlord
    })


# ============================================
# NOTIFICATIONS (Thông báo)
# ============================================

@login_required_custom
def notifications(request):
    """Danh sách thông báo"""
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    # Get all notifications for user
    all_notifications = Thongbao.objects.filter(makh=khachhang)
    unread_count = all_notifications.filter(dadoc=False).count()
    thongbao_list = all_notifications[:50]

    return render(request, 'bookings/notifications.html', {
        'thongbao_list': thongbao_list,
        'unread_count': unread_count
    })


@login_required_custom
def mark_notification_read(request, pk):
    """Đánh dấu thông báo đã đọc"""
    khachhang = get_current_khachhang(request)
    thongbao = get_object_or_404(Thongbao, pk=pk, makh=khachhang)

    thongbao.dadoc = True
    thongbao.save()

    return redirect('bookings:notifications')


@login_required_custom
def mark_all_read(request):
    """Đánh dấu tất cả thông báo đã đọc"""
    khachhang = get_current_khachhang(request)

    if khachhang:
        Thongbao.objects.filter(makh=khachhang, dadoc=False).update(dadoc=True)

    return redirect('bookings:notifications')



# ============================================
# LANDLORD REQUEST (Yêu cầu làm chủ trọ)
# ============================================

@login_required_custom
def request_landlord(request):
    """Yêu cầu trở thành chủ trọ"""
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    # Check if already landlord
    if khachhang.mavt and khachhang.mavt.tenvt == 'Chủ trọ':
        messages.info(request, 'Bạn đã là chủ trọ rồi.')
        return redirect('bookings:landlord_dashboard')

    # Check if already has pending request
    pending = Yclamchutro.objects.filter(makh=khachhang, trangthai='Chờ duyệt').exists()
    if pending:
        messages.warning(request, 'Bạn đã có yêu cầu đang chờ duyệt.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        lydo = bleach.clean(request.POST.get('lydo', ''), strip=True)

        try:
            Yclamchutro.objects.create(
                makh=khachhang,
                lydo=lydo,
                trangthai='Chờ duyệt'
            )

            # Notify all admins
            from apps.accounts.models import Vaitro
            admin_role = Vaitro.objects.filter(tenvt='Admin').first()
            if admin_role:
                admin_users = Khachhang.objects.filter(mavt=admin_role)
                for admin in admin_users:
                    create_notification(
                        admin,
                        'Yêu cầu làm chủ trọ mới',
                        f'{khachhang.hoten} ({khachhang.email}) yêu cầu trở thành chủ trọ.',
                        'warning'
                    )

            messages.success(request, 'Đã gửi yêu cầu làm chủ trọ. Vui lòng chờ admin duyệt.')
            return redirect('accounts:profile')

        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'bookings/request_landlord.html')

    return render(request, 'bookings/request_landlord.html')


# ============================================
# LANDLORD DASHBOARD
# ============================================

@login_required_custom
def landlord_dashboard(request):
    """Bảng điều khiển chủ trọ"""
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    # Check if landlord
    if not khachhang.mavt or khachhang.mavt.tenvt != 'Chủ trọ':
        messages.error(request, 'Bạn cần là chủ trọ để truy cập trang này.')
        return redirect('bookings:request_landlord')

    # Get landlord's properties
    nhatro_list = Nhatro.objects.filter(makh=khachhang)

    # Get pending appointments
    pending_henxem = Henxemtro.objects.filter(
        mapt__mant__makh=khachhang,
        trangthai='Chờ xác nhận'
    ).select_related('mapt', 'makh')

    # Get confirmed appointments (thay thế active_rentals)
    confirmed_henxem = Henxemtro.objects.filter(
        mapt__mant__makh=khachhang,
        trangthai__in=['Đã xác nhận', 'Đã xem']
    ).select_related('mapt', 'makh')

    return render(request, 'bookings/landlord_dashboard.html', {
        'nhatro_list': nhatro_list,
        'pending_henxem': pending_henxem,
        'confirmed_henxem': confirmed_henxem
    })


@login_required_custom
def customer_dashboard(request):
    """Bảng điều khiển khách hàng"""
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    # Get customer's appointments
    my_appointments = Henxemtro.objects.filter(
        makh=khachhang
    ).select_related('mapt', 'mapt__mant').order_by('-ngayhen')

    # Get customer's rentals (if any)
    my_rentals = Thuetro.objects.filter(
        makh=khachhang
    ).select_related('mapt', 'mapt__mant').order_by('-ngaybatdau')

    # Get customer's reviews
    my_reviews = Danhgia.objects.filter(
        makh=khachhang
    ).select_related('mapt').order_by('-tg_tao')

    # Get favorite rooms (if implemented)
    # favorite_rooms = ...

    return render(request, 'bookings/customer_dashboard.html', {
        'my_appointments': my_appointments,
        'my_rentals': my_rentals,
        'my_reviews': my_reviews,
    })


@login_required_custom
def manage_nhatro(request):
    """Quản lý nhà trọ"""
    khachhang = get_current_khachhang(request)

    if not khachhang or not khachhang.mavt or khachhang.mavt.tenvt != 'Chủ trọ':
        return redirect('bookings:request_landlord')

    nhatro_list = Nhatro.objects.filter(makh=khachhang)

    return render(request, 'bookings/manage_nhatro.html', {
        'nhatro_list': nhatro_list
    })


@login_required_custom
@ratelimit(key='ip', rate='10/h', method='POST')
def create_nhatro(request):
    """Tạo nhà trọ mới"""
    khachhang = get_current_khachhang(request)

    if not khachhang or not khachhang.mavt or khachhang.mavt.tenvt != 'Chủ trọ':
        return redirect('bookings:request_landlord')

    if request.method == 'POST':
        tennt = bleach.clean(request.POST.get('tennt', ''), strip=True)
        diachi = bleach.clean(request.POST.get('diachi', ''), strip=True)
        giadien = request.POST.get('giadien', 0) or 0
        gianuoc = request.POST.get('gianuoc', 0) or 0

        if not tennt or not diachi:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return render(request, 'bookings/nhatro_form.html')

        try:
            Nhatro.objects.create(
                makh=khachhang,
                tennt=tennt,
                diachi=diachi,
                giadien=giadien,
                gianuoc=gianuoc,
                trangthai=True
            )
            messages.success(request, 'Đã tạo nhà trọ thành công!')
            return redirect('bookings:manage_nhatro')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'bookings/nhatro_form.html')

    return render(request, 'bookings/nhatro_form.html')


@login_required_custom
def manage_phongtro(request, nhatro_id):
    """Quản lý phòng trọ trong nhà trọ"""
    khachhang = get_current_khachhang(request)
    nhatro = get_object_or_404(Nhatro, pk=nhatro_id, makh=khachhang)

    phongtro_list = Phongtro.objects.filter(mant=nhatro)

    return render(request, 'bookings/manage_phongtro.html', {
        'nhatro': nhatro,
        'phongtro_list': phongtro_list
    })


@login_required_custom
@ratelimit(key='ip', rate='20/h', method='POST')
def create_phongtro(request, nhatro_id):
    """Tạo phòng trọ mới"""
    from apps.rooms.models import Hinhanh
    import os
    from django.conf import settings

    khachhang = get_current_khachhang(request)
    nhatro = get_object_or_404(Nhatro, pk=nhatro_id, makh=khachhang)

    if request.method == 'POST':
        tenpt = bleach.clean(request.POST.get('tenpt', ''), strip=True)
        mota = bleach.clean(request.POST.get('mota', ''), strip=True)
        dientich = request.POST.get('dientich', 0) or 0
        giatien = request.POST.get('giatien', 0) or 0
        songuoio = request.POST.get('songuoio', 0) or 0

        if not tenpt or not giatien:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return render(request, 'bookings/phongtro_form.html', {'nhatro': nhatro})

        try:
            # Create room with "Chờ duyệt" status (pending approval)
            # Use raw SQL to avoid OUTPUT clause issue with SQL Server triggers
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO PHONGTRO (MANT, TENPT, MOTA, DIENTICH, GIATIEN, SONGUOIO, TRANGTHAI)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [nhatro.mant, tenpt, mota or '', float(dientich), int(giatien), int(songuoio), 'Chờ duyệt'])

                # Get the newly created ID
                cursor.execute("SELECT IDENT_CURRENT('PHONGTRO')")
                new_id = int(cursor.fetchone()[0])

            # Get the phongtro object
            phongtro = Phongtro.objects.get(mapt=new_id)

            # Handle image uploads with strict validation
            images = request.FILES.getlist('images')
            ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

            if images:
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'rooms', str(phongtro.mapt))
                os.makedirs(upload_dir, exist_ok=True)

                uploaded_count = 0
                for i, image in enumerate(images[:5]):  # Max 5 images
                    # Validate file extension
                    ext = image.name.split('.')[-1].lower()
                    if ext not in ALLOWED_EXTENSIONS:
                        messages.warning(request, f'Bỏ qua file {image.name}: định dạng không hỗ trợ.')
                        continue

                    # Validate MIME type
                    if image.content_type not in ALLOWED_MIME_TYPES:
                        messages.warning(request, f'Bỏ qua file {image.name}: loại file không hợp lệ.')
                        continue

                    # Validate file size
                    if image.size > MAX_FILE_SIZE:
                        messages.warning(request, f'Bỏ qua file {image.name}: file quá lớn (tối đa 5MB).')
                        continue

                    # Validate magic bytes (check actual file content)
                    header = image.read(8)
                    image.seek(0)  # Reset file pointer

                    # Check magic bytes for common image formats
                    is_valid_image = (
                        header[:3] == b'\xff\xd8\xff' or  # JPEG
                        header[:8] == b'\x89PNG\r\n\x1a\n' or  # PNG
                        header[:6] in (b'GIF87a', b'GIF89a') or  # GIF
                        header[:4] == b'RIFF'  # WebP
                    )

                    if not is_valid_image:
                        messages.warning(request, f'Bỏ qua file {image.name}: nội dung không phải ảnh hợp lệ.')
                        continue

                    # Save file
                    import uuid
                    safe_filename = f'{phongtro.mapt}_{uuid.uuid4().hex[:8]}.{ext}'
                    filepath = os.path.join(upload_dir, safe_filename)

                    with open(filepath, 'wb+') as dest:
                        for chunk in image.chunks():
                            dest.write(chunk)

                    # Create database record using raw SQL to avoid trigger issues
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO HINHANH (MAPT, DUONGDAN, MOTA)
                                VALUES (%s, %s, %s)
                            """, [phongtro.mapt, f'/media/rooms/{phongtro.mapt}/{safe_filename}', f'Ảnh {uploaded_count+1}'])
                        uploaded_count += 1
                    except Exception as img_err:
                        # Fallback to ORM if raw SQL fails
                        try:
                            Hinhanh.objects.create(
                                mapt=phongtro,
                                duongdan=f'/media/rooms/{phongtro.mapt}/{safe_filename}',
                                mota=f'Ảnh {uploaded_count+1}'
                            )
                            uploaded_count += 1
                        except:
                            pass

                if uploaded_count > 0:
                    messages.info(request, f'Đã tải lên {uploaded_count} ảnh.')

            # Notify admins about new listing
            from apps.accounts.models import Vaitro
            admin_role = Vaitro.objects.filter(tenvt='Admin').first()
            if admin_role:
                admin_users = Khachhang.objects.filter(mavt=admin_role)
                for admin in admin_users:
                    create_notification(
                        admin,
                        'Phòng trọ mới chờ duyệt',
                        f'{khachhang.hoten} đã đăng phòng "{tenpt}" tại {nhatro.tennt}. Cần duyệt.',
                        'warning'
                    )

            messages.success(request, 'Đã tạo phòng trọ! Vui lòng chờ Admin duyệt.')
            return redirect('bookings:manage_phongtro', nhatro_id=nhatro_id)

        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'bookings/phongtro_form.html', {'nhatro': nhatro})

    return render(request, 'bookings/phongtro_form.html', {'nhatro': nhatro})


@login_required_custom
def edit_phongtro(request, pk):
    """Chỉnh sửa phòng trọ"""
    from apps.rooms.models import Hinhanh
    import os
    from django.conf import settings

    khachhang = get_current_khachhang(request)
    phongtro = get_object_or_404(Phongtro, pk=pk)

    # Check ownership
    if phongtro.mant.makh != khachhang:
        messages.error(request, 'Bạn không có quyền chỉnh sửa phòng trọ này.')
        return redirect('bookings:landlord_dashboard')

    if request.method == 'POST':
        phongtro.tenpt = bleach.clean(request.POST.get('tenpt', ''), strip=True)
        phongtro.mota = bleach.clean(request.POST.get('mota', ''), strip=True)
        phongtro.dientich = request.POST.get('dientich', 0) or 0
        phongtro.giatien = request.POST.get('giatien', 0) or 0
        phongtro.songuoio = request.POST.get('songuoio', 0) or 0

        if not phongtro.tenpt or not phongtro.giatien:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return render(request, 'bookings/phongtro_form.html', {
                'nhatro': phongtro.mant,
                'phongtro': phongtro,
                'action': 'edit'
            })

        try:
            # If room was approved, set back to pending after edit
            if phongtro.trangthai in ['Còn trống', 'Đã thuê']:
                phongtro.trangthai = 'Chờ duyệt'

            phongtro.save()

            # Handle new image uploads
            images = request.FILES.getlist('images')
            ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

            if images:
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'rooms', str(phongtro.mapt))
                os.makedirs(upload_dir, exist_ok=True)

                uploaded_count = 0
                for image in images[:5]:
                    ext = image.name.split('.')[-1].lower()
                    if ext not in ALLOWED_EXTENSIONS:
                        continue

                    if image.content_type not in ALLOWED_MIME_TYPES:
                        continue

                    if image.size > MAX_FILE_SIZE:
                        continue

                    # Validate magic bytes
                    header = image.read(8)
                    image.seek(0)

                    is_valid_image = (
                        header[:3] == b'\xff\xd8\xff' or
                        header[:8] == b'\x89PNG\r\n\x1a\n' or
                        header[:6] in (b'GIF87a', b'GIF89a') or
                        header[:4] == b'RIFF'
                    )

                    if not is_valid_image:
                        continue

                    import uuid
                    safe_filename = f'{phongtro.mapt}_{uuid.uuid4().hex[:8]}.{ext}'
                    filepath = os.path.join(upload_dir, safe_filename)

                    with open(filepath, 'wb+') as dest:
                        for chunk in image.chunks():
                            dest.write(chunk)

                    try:
                        Hinhanh.objects.create(
                            mapt=phongtro,
                            duongdan=f'/media/rooms/{phongtro.mapt}/{safe_filename}',
                            mota=f'Ảnh {uploaded_count+1}'
                        )
                        uploaded_count += 1
                    except:
                        pass

                if uploaded_count > 0:
                    messages.info(request, f'Đã tải lên {uploaded_count} ảnh mới.')

            messages.success(request, 'Đã cập nhật phòng trọ! Vui lòng chờ Admin duyệt lại.')
            return redirect('bookings:manage_phongtro', nhatro_id=phongtro.mant.mant)

        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')

    return render(request, 'bookings/phongtro_form.html', {
        'nhatro': phongtro.mant,
        'phongtro': phongtro,
        'action': 'edit'
    })


@login_required_custom
def update_phongtro_status(request, pk):
    """Cập nhật trạng thái phòng trọ"""
    khachhang = get_current_khachhang(request)
    phongtro = get_object_or_404(Phongtro, pk=pk)

    # Check ownership
    if phongtro.mant.makh != khachhang:
        messages.error(request, 'Bạn không có quyền thao tác.')
        return redirect('bookings:landlord_dashboard')

    if request.method == 'POST':
        trangthai = request.POST.get('trangthai', 'Còn trống')
        if trangthai in ['Còn trống', 'Đã thuê', 'Đang sửa chữa']:
            phongtro.trangthai = trangthai
            phongtro.save()
            messages.success(request, 'Đã cập nhật trạng thái phòng.')

    return redirect('bookings:manage_phongtro', nhatro_id=phongtro.mant.mant)


@login_required_custom
def confirm_henxem(request, pk):
    """Xác nhận lịch hẹn xem phòng"""
    khachhang = get_current_khachhang(request)
    henxem = get_object_or_404(Henxemtro, pk=pk)

    # Check if landlord owns this room
    if henxem.mapt.mant.makh != khachhang:
        messages.error(request, 'Bạn không có quyền thao tác.')
        return redirect('bookings:landlord_dashboard')

    if henxem.trangthai == 'Chờ xác nhận':
        henxem.trangthai = 'Đã xác nhận'
        henxem.save()

        # Notify customer
        create_notification(
            henxem.makh,
            'Lịch hẹn đã được xác nhận',
            f'Lịch hẹn xem phòng "{henxem.mapt.tenpt}" đã được chủ trọ xác nhận.',
            'booking'
        )

        messages.success(request, 'Đã xác nhận lịch hẹn.')

    return redirect('bookings:landlord_dashboard')


@login_required_custom
def reject_henxem(request, pk):
    """Từ chối lịch hẹn xem phòng"""
    khachhang = get_current_khachhang(request)
    henxem = get_object_or_404(Henxemtro, pk=pk)

    if henxem.mapt.mant.makh != khachhang:
        messages.error(request, 'Bạn không có quyền thao tác.')
        return redirect('bookings:landlord_dashboard')

    if henxem.trangthai == 'Chờ xác nhận':
        henxem.trangthai = 'Đã hủy'
        henxem.save()

        create_notification(
            henxem.makh,
            'Lịch hẹn đã bị từ chối',
            f'Lịch hẹn xem phòng "{henxem.mapt.tenpt}" đã bị từ chối.',
            'warning'
        )

        messages.success(request, 'Đã từ chối lịch hẹn.')

    return redirect('bookings:landlord_dashboard')


# ============================================
# ADMIN DASHBOARD
# ============================================

def admin_required(view_func):
    """Decorator kiểm tra quyền admin"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            return redirect('accounts:login')
        if request.session.get('user_role') != 'Admin':
            messages.error(request, 'Bạn không có quyền truy cập.')
            return redirect('accounts:profile')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Bảng điều khiển Admin"""
    from apps.accounts.models import Vaitro
    from apps.rooms.models import Hinhanh

    # Get stats
    pending_landlord_requests = Yclamchutro.objects.filter(trangthai='Chờ duyệt').select_related('makh')
    pending_rooms = Phongtro.objects.filter(trangthai='Chờ duyệt').select_related('mant', 'mant__makh')
    rejected_rooms = Phongtro.objects.filter(trangthai='Từ chối').select_related('mant', 'mant__makh')

    # Get first image for each pending room
    for room in pending_rooms:
        room.first_image = Hinhanh.objects.filter(mapt=room).first()

    # Stats for dashboard
    total_nhatro = Nhatro.objects.count()
    pending_henxem_count = pending_landlord_requests.count()
    confirmed_henxem_count = Yclamchutro.objects.filter(trangthai='Đã duyệt').count()

    total_users = Khachhang.objects.count()
    total_rooms = Phongtro.objects.filter(trangthai='Còn trống').count()
    total_pending = pending_rooms.count()
    total_landlords = Khachhang.objects.filter(mavt__tenvt='Chủ trọ').count()

    # Recent activities
    recent_registrations = Khachhang.objects.order_by('-tg_tao')[:10]
    all_landlord_requests = Yclamchutro.objects.select_related('makh', 'nguoiduyet').order_by('-tg_tao')[:20]

    # Recent room submissions (all statuses)
    recent_rooms = Phongtro.objects.select_related('mant', 'mant__makh').order_by('-mapt')[:20]

    # Get pending appointments (Lịch hẹn chờ xác nhận)
    pending_appointments = Henxemtro.objects.filter(
        trangthai='Chờ xác nhận'
    ).select_related('mapt', 'makh', 'mapt__mant').order_by('-ngayhen')

    # Get confirmed appointments (Lịch hẹn đã xác nhận)
    confirmed_appointments = Henxemtro.objects.filter(
        trangthai='Đã xác nhận'
    ).select_related('mapt', 'makh', 'mapt__mant').order_by('-ngayhen')

    return render(request, 'bookings/admin_dashboard.html', {
        'pending_requests': pending_landlord_requests,
        'pending_rooms': pending_rooms,
        'rejected_rooms': rejected_rooms,
        'total_users': total_users,
        'total_rooms': total_rooms,
        'total_pending': total_pending,
        'total_landlords': total_landlords,
        'recent_registrations': recent_registrations,
        'all_requests': all_landlord_requests,
        'recent_rooms': recent_rooms,
        'total_nhatro': total_nhatro,
        'pending_henxem_count': pending_henxem_count,
        'confirmed_henxem_count': confirmed_henxem_count,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
    })


@admin_required
def approve_landlord_request(request, pk):
    """Duyệt yêu cầu làm chủ trọ"""
    from apps.accounts.models import Vaitro

    yc = get_object_or_404(Yclamchutro, pk=pk)

    if yc.trangthai != 'Chờ duyệt':
        messages.warning(request, 'Yêu cầu này đã được xử lý.')
        return redirect('bookings:admin_dashboard')

    # Get landlord role
    chutro_role = Vaitro.objects.filter(tenvt='Chủ trọ').first()
    if not chutro_role:
        messages.error(request, 'Không tìm thấy vai trò Chủ trọ trong hệ thống.')
        return redirect('bookings:admin_dashboard')

    # Get current admin
    admin_kh = get_current_khachhang(request)

    # Update request
    yc.trangthai = 'Đã duyệt'
    yc.tg_duyet = timezone.now()
    yc.nguoiduyet = admin_kh
    yc.save()

    # Update user role
    yc.makh.mavt = chutro_role
    yc.makh.save()

    # Notify user
    create_notification(
        yc.makh,
        'Yêu cầu làm chủ trọ đã được duyệt',
        'Chúc mừng! Bạn đã trở thành chủ trọ. Bây giờ bạn có thể đăng tin cho thuê phòng.',
        'success'
    )

    messages.success(request, f'Đã duyệt yêu cầu của {yc.makh.hoten}.')
    return redirect('bookings:admin_dashboard')


@admin_required
def reject_landlord_request(request, pk):
    """Từ chối yêu cầu làm chủ trọ"""
    yc = get_object_or_404(Yclamchutro, pk=pk)

    if yc.trangthai != 'Chờ duyệt':
        messages.warning(request, 'Yêu cầu này đã được xử lý.')
        return redirect('bookings:admin_dashboard')

    # Get current admin
    admin_kh = get_current_khachhang(request)

    # Update request
    yc.trangthai = 'Từ chối'
    yc.tg_duyet = timezone.now()
    yc.nguoiduyet = admin_kh
    yc.save()

    # Notify user
    create_notification(
        yc.makh,
        'Yêu cầu làm chủ trọ bị từ chối',
        'Rất tiếc, yêu cầu làm chủ trọ của bạn đã bị từ chối. Vui lòng liên hệ hỗ trợ để biết thêm chi tiết.',
        'warning'
    )

    messages.success(request, f'Đã từ chối yêu cầu của {yc.makh.hoten}.')
    return redirect('bookings:admin_dashboard')


@admin_required
def approve_room(request, pk):
    """Duyệt phòng trọ"""
    phongtro = get_object_or_404(Phongtro, pk=pk)

    if phongtro.trangthai != 'Chờ duyệt':
        messages.warning(request, 'Phòng này đã được xử lý.')
        return redirect('bookings:admin_dashboard')

    phongtro.trangthai = 'Còn trống'
    phongtro.save()

    landlord = phongtro.mant.makh

    # Create in-app notification
    create_notification(
        landlord,
        'Phòng trọ đã được duyệt ✓',
        f'Chúc mừng! Phòng "{phongtro.tenpt}" tại {phongtro.mant.tennt} đã được duyệt và hiển thị công khai trên trang chủ.',
        'success'
    )

    # Send email notification
    send_listing_status_email(
        landlord.email,
        phongtro.tenpt,
        'approved',
        f'Phòng "{phongtro.tenpt}" tại {phongtro.mant.tennt} đã được duyệt và hiển thị công khai.'
    )

    messages.success(request, f'Đã duyệt phòng "{phongtro.tenpt}".')
    return redirect('bookings:admin_dashboard')


@admin_required
def reject_room(request, pk):
    """Từ chối phòng trọ"""
    phongtro = get_object_or_404(Phongtro, pk=pk)

    if phongtro.trangthai != 'Chờ duyệt':
        messages.warning(request, 'Phòng này đã được xử lý.')
        return redirect('bookings:admin_dashboard')

    room_name = phongtro.tenpt
    nhatro_name = phongtro.mant.tennt
    landlord = phongtro.mant.makh

    # Get rejection reason from POST if provided
    reason = request.GET.get('reason', 'Thông tin không hợp lệ hoặc vi phạm quy định.')

    # Mark as rejected (don't delete - keep for records)
    phongtro.trangthai = 'Từ chối'
    phongtro.save()

    # Create in-app notification
    create_notification(
        landlord,
        'Phòng trọ bị từ chối ✗',
        f'Phòng "{room_name}" đã bị từ chối. Lý do: {reason}. Vui lòng chỉnh sửa và gửi lại.',
        'warning'
    )

    # Send email notification
    send_listing_status_email(
        landlord.email,
        room_name,
        'rejected',
        f'Phòng "{room_name}" tại {nhatro_name} đã bị từ chối. Lý do: {reason}'
    )

    messages.success(request, f'Đã từ chối phòng "{room_name}".')
    return redirect('bookings:admin_dashboard')


def send_listing_status_email(email, room_name, status, message):
    """Gửi email thông báo trạng thái phòng trọ"""
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        if status == 'approved':
            subject = f'✓ Phòng "{room_name}" đã được duyệt'
            status_text = 'ĐÃ ĐƯỢC DUYỆT'
        else:
            subject = f'✗ Phòng "{room_name}" bị từ chối'
            status_text = 'BỊ TỪ CHỐI'

        full_message = f"""
Xin chào,

Trạng thái phòng trọ của bạn: {status_text}

{message}

{'Phòng của bạn hiện đã hiển thị công khai trên PhongTro.vn.' if status == 'approved' else 'Vui lòng chỉnh sửa thông tin và gửi lại để được duyệt.'}

Thời gian: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

Trân trọng,
PhongTro.vn
        """

        send_mail(
            subject=f'[PhongTro.vn] {subject}',
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Failed to send listing status email to {email}: {e}')

@admin_required
def admin_manage_rooms(request):
    """Admin quản lý tất cả phòng trọ đã đăng"""
    from apps.rooms.models import Hinhanh

    # Lấy tất cả phòng trọ đã được duyệt (đã đăng)
    all_rooms = Phongtro.objects.filter(
        trangthai='Đã duyệt'
    ).select_related('mant', 'mant__makh').order_by('-mapt')

    # Lấy ảnh đầu tiên cho mỗi phòng
    for room in all_rooms:
        room.first_image = Hinhanh.objects.filter(mapt=room).first()

    return render(request, 'quan_tri/admin_manage_rooms.html', {
        'all_rooms': all_rooms,
        'total_rooms': all_rooms.count()
    })

@admin_required
def manage_customers(request):
    """Quản lý danh sách khách hàng"""
    from apps.accounts.models import Khachhang
    ds_khach_hang = Khachhang.objects.all().order_by('-tg_tao')
    return render(request, 'quan_tri/manage_customers.html', {'ds_khach_hang': ds_khach_hang})

@admin_required
def toggle_user_status(request, pk):
    """Khóa/Mở khóa tài khoản khách hàng"""
    from apps.accounts.models import Khachhang
    kh = get_object_or_404(Khachhang, pk=pk)
    # Dựa theo script.sql, cột trạng thái là BIT (True/False)
    kh.trangthai = not kh.trangthai
    kh.save()
    status_text = "kích hoạt" if kh.trangthai else "vô hiệu hóa"
    messages.success(request, f"Đã {status_text} tài khoản {kh.hoten}")
    return redirect('bookings:manage_customers')

@admin_required
def add_user(request):
    """Thêm người dùng mới"""
    from apps.accounts.models import Khachhang, Vaitro
    import hashlib

    if request.method == 'POST':
        hoten = bleach.clean(request.POST.get('hoten', ''), strip=True)
        email = bleach.clean(request.POST.get('email', ''), strip=True)
        sdt = bleach.clean(request.POST.get('sdt', ''), strip=True)
        matkhau = request.POST.get('matkhau', '')
        mavt_id = request.POST.get('mavt')

        # Validate
        if not all([hoten, email, matkhau]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc.')
            return redirect('bookings:add_user')

        # Check email exists
        if Khachhang.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại trong hệ thống.')
            return redirect('bookings:add_user')

        try:
            # Hash password
            hashed_password = hashlib.sha256(matkhau.encode()).hexdigest()

            # Get role
            mavt = Vaitro.objects.get(pk=mavt_id) if mavt_id else None

            # Create user
            Khachhang.objects.create(
                hoten=hoten,
                email=email,
                sdt=sdt,
                matkhau=hashed_password,
                mavt=mavt,
                trangthai=True
            )

            messages.success(request, f'Đã thêm người dùng {hoten} thành công!')
            return redirect('bookings:manage_customers')

        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return redirect('bookings:add_user')

    # GET request
    vaitro_list = Vaitro.objects.all()
    return render(request, 'quan_tri/user_form.html', {
        'vaitro_list': vaitro_list,
        'action': 'add'
    })

@admin_required
def edit_user(request, pk):
    """Chỉnh sửa thông tin người dùng"""
    from apps.accounts.models import Khachhang, Vaitro
    import hashlib

    kh = get_object_or_404(Khachhang, pk=pk)

    if request.method == 'POST':
        kh.hoten = bleach.clean(request.POST.get('hoten', ''), strip=True)
        kh.email = bleach.clean(request.POST.get('email', ''), strip=True)
        kh.sdt = bleach.clean(request.POST.get('sdt', ''), strip=True)

        # Update password if provided
        new_password = request.POST.get('matkhau', '')
        if new_password:
            kh.matkhau = hashlib.sha256(new_password.encode()).hexdigest()

        # Update role
        mavt_id = request.POST.get('mavt')
        if mavt_id:
            kh.mavt = Vaitro.objects.get(pk=mavt_id)

        try:
            kh.save()
            messages.success(request, f'Đã cập nhật thông tin {kh.hoten}!')
            return redirect('bookings:manage_customers')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')

    vaitro_list = Vaitro.objects.all()
    return render(request, 'quan_tri/user_form.html', {
        'user': kh,
        'vaitro_list': vaitro_list,
        'action': 'edit'
    })

@admin_required
def delete_user(request, pk):
    """Xóa người dùng"""
    from apps.accounts.models import Khachhang

    kh = get_object_or_404(Khachhang, pk=pk)

    # Prevent deleting admin
    if kh.mavt and kh.mavt.tenvt == 'Admin':
        messages.error(request, 'Không thể xóa tài khoản Admin!')
        return redirect('bookings:manage_customers')

    if request.method == 'POST':
        hoten = kh.hoten
        kh.delete()
        messages.success(request, f'Đã xóa người dùng {hoten}!')
        return redirect('bookings:manage_customers')

    return render(request, 'quan_tri/user_confirm_delete.html', {'user': kh})

@admin_required
def admin_delete_room(request, pk):
    """Admin xóa phòng trọ"""
    room = get_object_or_404(Phongtro, pk=pk)

    if request.method == 'POST':
        room_name = f"Phòng {room.mapt}"
        room.delete()
        messages.success(request, f'Đã xóa {room_name}!')
        return redirect('bookings:admin_manage_rooms')

    return render(request, 'quan_tri/room_confirm_delete.html', {'room': room})

@admin_required
def manage_active_rooms(request):
    """Quản lý các phòng trọ đang hiển thị"""
    active_rooms = Phongtro.objects.filter(trangthai__in=['Còn trống', 'Đã thuê']).select_related('mant', 'mant__makh')
    return render(request, 'quan_tri/manage_rooms.html', {'active_rooms': active_rooms})

@admin_required
def admin_history(request):
    """Lịch sử hệ thống (Lấy từ AUDIT_LOGS trong database)"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 50 * FROM AUDIT_LOGS ORDER BY CHANGED_DATE DESC")
        logs = cursor.fetchall()
    return render(request, 'quan_tri/history.html', {'logs': logs})

def validate_henxem_data(ngayhen_str, ghichu):
    """
    Hàm validate riêng cho chức năng hẹn xem:
    1. Ngày hẹn không được ở quá khứ.
    2. Ghi chú: 2-30 ký tự, không ký tự đặc biệt.
    """
    # --- 1. Validate Ngày hẹn ---
    if not ngayhen_str:
        return False, 'Vui lòng chọn ngày giờ hẹn.'
    
    try:
        # Input từ datetime-local có dạng: YYYY-MM-DDTHH:MM
        hen_time = datetime.strptime(ngayhen_str, '%Y-%m-%dT%H:%M')
        # Gán timezone hiện tại cho giờ hẹn (để so sánh được với timezone.now())
        hen_time = timezone.make_aware(hen_time)
        
        if hen_time < timezone.now():
            return False, 'Thời gian hẹn không được nằm trong quá khứ.'
            
    except ValueError:
        return False, 'Định dạng ngày giờ không hợp lệ.'

    # --- 2. Validate Ghi chú ---
    # Nếu có ghi chú thì mới check (hoặc bắt buộc nhập tùy bạn, code dưới đây giả định là BẮT BUỘC nhập vì có rule 2-30 ký tự)
    if not ghichu:
        return False, 'Vui lòng nhập ghi chú.'

    ghichu = ghichu.strip()
    
    # Check độ dài 2 - 30 ký tự
    if len(ghichu) < 2 or len(ghichu) > 30:
        return False, 'Ghi chú phải từ 2 đến 30 ký tự.'
    
    # Check ký tự đặc biệt (Chỉ cho phép: Chữ, Số, Khoảng trắng, dấu chấm, dấu phẩy, gạch ngang)
    # Regex chặn các ký tự đặc biệt như: @ # $ % ^ & * ( ) _ + = { } [ ] | \ : ; " ' < > ? / ~ `
    special_chars = re.compile(r'[<>{}|\[\]\\^~`@#$%&*=+/;:_()!?"\']')
    if special_chars.search(ghichu):
        return False, 'Ghi chú không được chứa ký tự đặc biệt.'

    return True, ''