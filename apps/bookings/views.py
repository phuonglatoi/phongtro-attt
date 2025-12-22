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

    if request.method == 'POST':
        ngayhen = request.POST.get('ngayhen')
        ghichu = bleach.clean(request.POST.get('ghichu', ''), strip=True)

        if not ngayhen:
            messages.error(request, 'Vui lòng chọn ngày hẹn.')
            return render(request, 'bookings/henxem_form.html', {'room': room})

        # Create appointment
        henxem = Henxemtro.objects.create(
            mapt=room,
            makh=khachhang,
            ngayhen=ngayhen,
            ghichu=ghichu,
            trangthai='Chờ xác nhận'
        )

        # Notify the landlord
        landlord = room.mant.makh
        if landlord:
            create_notification(
                landlord,
                'Có lịch hẹn xem phòng mới',
                f'{khachhang.hoten} muốn xem phòng "{room.tenpt}" vào {ngayhen}',
                'booking'
            )

        messages.success(request, 'Đã gửi yêu cầu hẹn xem phòng!')
        return redirect('rooms:room_detail', pk=room_id)

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

    if len(content) > 500:
        return False, 'Tin nhắn không được quá 500 ký tự.'

    if len(content) < 2:
        return False, 'Tin nhắn phải có ít nhất 2 ký tự.'

    # Không cho phép: <, >, {, }, [, ], |, \, ^, ~, `, @, #, $, %, &, *, =, +
    dangerous_chars = re.compile(r'[<>{}|\[\]\\^~`@#$%&*=+]')
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

    total_users = Khachhang.objects.count()
    total_rooms = Phongtro.objects.filter(trangthai='Còn trống').count()
    total_pending = pending_rooms.count()
    total_landlords = Khachhang.objects.filter(mavt__tenvt='Chủ trọ').count()

    # Recent activities
    recent_registrations = Khachhang.objects.order_by('-tg_tao')[:10]
    all_landlord_requests = Yclamchutro.objects.select_related('makh', 'nguoiduyet').order_by('-tg_tao')[:20]

    # Recent room submissions (all statuses)
    recent_rooms = Phongtro.objects.select_related('mant', 'mant__makh').order_by('-mapt')[:20]

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