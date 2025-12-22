# ============================================
# apps/accounts/views.py
# ============================================

import io
import base64
import logging
import hashlib
from datetime import timedelta

import pyotp
import qrcode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.db import transaction, connection
from django.contrib.auth import views as auth_views

from django_ratelimit.decorators import ratelimit

from .models import Taikhoan, Khachhang, Vaitro, LoginHistory, FailedLoginAttempts, SecurityQuestion
from .forms import (
    LoginForm,
    RegisterForm,
    PasswordChangeWithOTPForm,
    Enable2FAForm
)

from .security import (
    get_client_ip,
    check_ip_blocked,
    log_failed_login,
    log_security_event,
    check_account_locked,
    increment_failed_login,
    reset_failed_login
)

logger = logging.getLogger('apps.accounts')


# Login throttling settings
MAX_FAILED_ATTEMPTS = 10
LOCKOUT_DURATION_MINUTES = 15


def track_failed_login(ip, email, reason):
    """Theo dõi đăng nhập thất bại và kiểm tra throttling"""
    try:
        # Use raw SQL to avoid OUTPUT clause issues with triggers
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO FAILED_LOGIN_ATTEMPTS (IP_ADDRESS, USERNAME_OR_EMAIL, USER_AGENT)
                VALUES (%s, %s, %s)
            """, [ip, email, reason])
    except Exception as e:
        # Fallback to ORM
        try:
            FailedLoginAttempts.objects.create(
                ip_address=ip,
                username_or_email=email,
                user_agent=reason
            )
        except Exception as e2:
            logger.warning(f"Failed to track login attempt: {e2}")


def check_login_throttling(ip, email=None):
    """
    Kiểm tra xem IP hoặc email có bị khóa không.
    Trả về (is_locked, remaining_seconds)
    """
    lockout_time = timezone.now() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)

    # Đếm số lần thất bại trong 15 phút gần nhất
    filter_kwargs = {'ip_address': ip, 'attempt_time__gte': lockout_time}
    failed_count = FailedLoginAttempts.objects.filter(**filter_kwargs).count()

    if failed_count >= MAX_FAILED_ATTEMPTS:
        # Tìm lần thất bại gần nhất
        last_attempt = FailedLoginAttempts.objects.filter(
            ip_address=ip,
            attempt_time__gte=lockout_time
        ).order_by('-attempt_time').first()

        if last_attempt:
            unlock_time = last_attempt.attempt_time + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            remaining = (unlock_time - timezone.now()).total_seconds()
            if remaining > 0:
                return True, int(remaining)

    return False, 0


def clear_failed_attempts(ip, email=None):
    """Xóa các lần đăng nhập thất bại sau khi đăng nhập thành công"""
    try:
        FailedLoginAttempts.objects.filter(ip_address=ip).delete()
        if email:
            FailedLoginAttempts.objects.filter(username_or_email=email).delete()
    except Exception as e:
        logger.warning(f"Failed to clear login attempts: {e}")


def verify_recaptcha(token):
    """Xác thực reCAPTCHA - placeholder"""
    # TODO: Implement actual reCAPTCHA verification
    return True


def generate_device_fingerprint(request):
    """Tạo fingerprint thiết bị"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip = get_client_ip(request)
    return hashlib.md5(f"{user_agent}{ip}".encode()).hexdigest()


def send_security_alert_email(email, subject, message):
    """Gửi email cảnh báo bảo mật"""
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        full_message = f"""
Xin chào,

{message}

Nếu bạn không thực hiện hành động này, vui lòng đổi mật khẩu ngay lập tức và liên hệ hỗ trợ.

Thời gian: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

Trân trọng,
PhongTro.vn
        """

        send_mail(
            subject=f'[PhongTro.vn] {subject}',
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,  # Don't crash if email fails
        )
    except Exception as e:
        # Log error but don't crash the application
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Failed to send security email to {email}: {e}')


def verify_password(password, stored_hash, password_salt):
    """
    Xác thực mật khẩu với salt.
    Hash: SHA256(password + salt)
    """
    salted_password = f"{password}{password_salt}".encode('utf-8')
    computed_hash = hashlib.sha256(salted_password).digest()

    # SQL Server trả về memoryview cho binary field
    if isinstance(stored_hash, memoryview):
        stored_hash = stored_hash.tobytes()
    elif stored_hash and not isinstance(stored_hash, bytes):
        stored_hash = bytes(stored_hash)

    return computed_hash == stored_hash


def hash_password(password, salt):
    """Hash mật khẩu với salt: SHA256(password + salt)"""
    salted_password = f"{password}{salt}".encode('utf-8')
    return hashlib.sha256(salted_password).digest()


# ============================================
# LOGIN
# ============================================

@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate=settings.RATELIMIT_LOGIN, method='POST')
def login_view(request):
    limited = getattr(request, 'limited', False)
    if limited:
        return render(request, 'security/rate_limited.html')

    ip = get_client_ip(request)

    if check_ip_blocked(ip):
        return render(request, 'security/ip_blocked.html', {'ip': ip})

    # Check login throttling (10 failed attempts = 15 min lockout)
    is_throttled, remaining_seconds = check_login_throttling(ip)
    if is_throttled:
        remaining_minutes = remaining_seconds // 60
        remaining_secs = remaining_seconds % 60
        messages.error(
            request,
            f'Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau {remaining_minutes} phút {remaining_secs} giây.'
        )
        return render(request, 'accounts/login.html', {
            'form': LoginForm(),
            'is_throttled': True,
            'remaining_seconds': remaining_seconds
        })

    if request.method == "POST":
        form = LoginForm(request.POST)

        # Check failed login attempts for captcha
        one_hour_ago = timezone.now() - timedelta(hours=1)
        failed = FailedLoginAttempts.objects.filter(
            ip_address=ip,
            attempt_time__gte=one_hour_ago
        ).count()

        require_cap = failed >= settings.MAX_LOGIN_ATTEMPTS_BEFORE_CAPTCHA

        if require_cap:
            token = request.POST.get('g-recaptcha-response')
            if not verify_recaptcha(token):
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'require_captcha': True
                })

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember_me', False)

            # Tìm khách hàng theo email
            try:
                khachhang = Khachhang.objects.select_related('matk', 'mavt').get(email=email)
            except Khachhang.DoesNotExist:
                track_failed_login(ip, email, 'user_not_found')
                messages.error(request, 'Email hoặc mật khẩu không đúng.')
                return redirect('accounts:login')

            # Kiểm tra tài khoản có bị khóa không
            if khachhang.is_account_locked():
                messages.error(request, 'Tài khoản đã bị khóa tạm thời. Vui lòng thử lại sau.')
                return redirect('accounts:login')

            # Xác thực mật khẩu với salt
            taikhoan = khachhang.matk

            if not taikhoan:
                track_failed_login(ip, email, 'no_account')
                messages.error(request, 'Email hoặc mật khẩu không đúng.')
                return redirect('accounts:login')

            # Verify password với salt
            if not verify_password(password, taikhoan.password_hash, taikhoan.password_salt):
                track_failed_login(ip, email, 'invalid_credentials')

                # Tăng failed login count
                taikhoan.failed_login_count = (taikhoan.failed_login_count or 0) + 1
                if taikhoan.failed_login_count >= settings.MAX_LOGIN_ATTEMPTS_BEFORE_TEMP_LOCK:
                    taikhoan.is_locked = True
                    taikhoan.lock_time = timezone.now() + timedelta(minutes=settings.TEMP_LOCK_DURATION_MINUTES)
                taikhoan.save()

                # Log failed login
                LoginHistory.objects.create(
                    makh=khachhang,
                    success=False,
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    failure_reason='invalid_credentials'
                )

                messages.error(request, 'Email hoặc mật khẩu không đúng.')
                return redirect('accounts:login')

            # Đăng nhập thành công - clear failed attempts
            clear_failed_attempts(ip, email)

            ua = request.META.get('HTTP_USER_AGENT', '')

            # Parse user agent for device info
            device_type = 'Unknown'
            browser_family = 'Unknown'
            os_family = 'Unknown'

            try:
                import user_agents
                user_agent = user_agents.parse(ua)
                device_type = 'Mobile' if user_agent.is_mobile else ('Tablet' if user_agent.is_tablet else 'Desktop')
                browser_family = user_agent.browser.family or 'Unknown'
                os_family = user_agent.os.family or 'Unknown'
            except:
                # Fallback parsing
                if 'Mobile' in ua or 'Android' in ua:
                    device_type = 'Mobile'
                elif 'Tablet' in ua or 'iPad' in ua:
                    device_type = 'Tablet'
                else:
                    device_type = 'Desktop'

                if 'Chrome' in ua:
                    browser_family = 'Chrome'
                elif 'Firefox' in ua:
                    browser_family = 'Firefox'
                elif 'Safari' in ua:
                    browser_family = 'Safari'
                elif 'Edge' in ua:
                    browser_family = 'Edge'

                if 'Windows' in ua:
                    os_family = 'Windows'
                elif 'Mac' in ua:
                    os_family = 'macOS'
                elif 'Linux' in ua:
                    os_family = 'Linux'
                elif 'Android' in ua:
                    os_family = 'Android'
                elif 'iOS' in ua or 'iPhone' in ua:
                    os_family = 'iOS'

            # Log successful login
            LoginHistory.objects.create(
                makh=khachhang,
                success=True,
                ip_address=ip,
                user_agent=ua,
                device_type=device_type,
                browser_family=browser_family,
                os_family=os_family,
                used_2fa=False
            )

            # Kiểm tra 2FA (2FA nằm trên bảng KHACHHANG trong schema này)
            if khachhang.is_2fa_enabled:
                request.session['pending_2fa_makh'] = khachhang.makh
                return redirect('accounts:login_2fa')

            # Reset failed login count
            taikhoan.failed_login_count = 0
            taikhoan.last_login_ip = ip
            taikhoan.last_login_time = timezone.now()
            taikhoan.save()

            # Lưu thông tin vào session
            request.session['matk'] = taikhoan.matk
            request.session['makh'] = khachhang.makh
            request.session['user_email'] = khachhang.email
            request.session['user_name'] = khachhang.hoten
            request.session['user_role'] = khachhang.mavt.tenvt if khachhang.mavt else None
            request.session['is_authenticated'] = True

            if not remember:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                request.session.set_expiry(int(timedelta(days=30).total_seconds()))

            messages.success(request, f'Chào mừng {khachhang.hoten}!')

            # Redirect to 'next' URL or home
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('rooms:home')
    else:
        form = LoginForm()

    # Check failed attempts for CAPTCHA
    one_hour_ago = timezone.now() - timedelta(hours=1)
    failed = FailedLoginAttempts.objects.filter(
        ip_address=ip,
        attempt_time__gte=one_hour_ago
    ).count()

    return render(request, 'accounts/login.html', {
        'form': form,
        'require_captcha': failed >= settings.MAX_LOGIN_ATTEMPTS_BEFORE_CAPTCHA
    })


# ============================================
# LOGIN 2FA
# ============================================

@require_http_methods(['GET', 'POST'])
def login_2fa_view(request):
    makh_id = request.session.get('pending_2fa_makh')

    if not makh_id:
        return redirect('accounts:login')

    try:
        khachhang = Khachhang.objects.select_related('matk', 'mavt').get(makh=makh_id)
    except Khachhang.DoesNotExist:
        return redirect('accounts:login')

    # DEBUG: Show expected OTP for troubleshooting
    expected_otp = None
    if khachhang.totp_secret:
        import pyotp
        totp = pyotp.TOTP(khachhang.totp_secret)
        expected_otp = totp.now()

    if request.method == "POST":
        otp = request.POST.get('otp_code', '').strip()

        # Verify TOTP (2FA secret nằm trên KHACHHANG)
        if khachhang.verify_totp(otp):
            # Clear pending 2FA session
            del request.session['pending_2fa_makh']

            # Set user session
            request.session['matk'] = khachhang.matk.matk if khachhang.matk else None
            request.session['makh'] = khachhang.makh
            request.session['user_email'] = khachhang.email
            request.session['user_name'] = khachhang.hoten
            request.session['user_role'] = khachhang.mavt.tenvt if khachhang.mavt else None
            request.session['is_authenticated'] = True

            messages.success(request, f'Chào mừng {khachhang.hoten}!')

            # Redirect to 'next' URL or home
            next_url = request.session.pop('next_url', None)
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('rooms:home')

        messages.error(request, 'Mã OTP không hợp lệ.')

    return render(request, 'accounts/login_2fa.html', {
        'khachhang': khachhang,
        'debug_expected_otp': expected_otp,  # DEBUG - remove in production
        'secret': khachhang.totp_secret  # DEBUG - for QR re-scan
    })


# ============================================
# REGISTER
# ============================================

@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate=settings.RATELIMIT_REGISTER, method='POST')
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                import uuid

                email = form.cleaned_data['email']
                password = form.cleaned_data['password1']
                username = form.cleaned_data['username']
                phone = form.cleaned_data.get('phone', '')

                # Tạo salt và hash password
                salt = str(uuid.uuid4())
                password_hash = hash_password(password, salt)

                taikhoan = Taikhoan.objects.create(
                    username=email,  # Dùng email làm username
                    password_hash=password_hash,
                    password_salt=salt,
                    tg_tao=timezone.now()
                )

                # Lấy vai trò mặc định (Khách hàng)
                try:
                    vaitro_khach = Vaitro.objects.get(tenvt='Khách hàng')
                except Vaitro.DoesNotExist:
                    vaitro_khach = Vaitro.objects.first()

                # Tạo khách hàng
                Khachhang.objects.create(
                    hoten=username,
                    email=email,
                    matk=taikhoan,
                    mavt=vaitro_khach,
                    trangthai=True
                )

                messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
                return redirect('accounts:login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# ============================================
# HELPER: Get current khachhang from session
# ============================================

def get_current_khachhang(request):
    """Lấy khách hàng hiện tại từ session"""
    makh = request.session.get('makh')
    if makh:
        try:
            return Khachhang.objects.select_related('matk', 'mavt').get(makh=makh)
        except Khachhang.DoesNotExist:
            pass
    return None


def login_required_custom(view_func):
    """Decorator kiểm tra đăng nhập theo session custom"""
    from functools import wraps
    from urllib.parse import urlencode

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('makh') or not request.session.get('is_authenticated'):
            messages.warning(request, 'Vui lòng đăng nhập để tiếp tục.')
            login_url = '/accounts/login/'
            # Add 'next' parameter for redirect after login
            if request.path != login_url:
                login_url = f"{login_url}?next={request.path}"
            return redirect(login_url)
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================
# CHANGE PASSWORD
# ============================================

@login_required_custom
@require_http_methods(['GET', 'POST'])
def password_change_view(request):
    """Đổi mật khẩu - sử dụng SHA256 + Salt"""
    import re
    import uuid

    khachhang = get_current_khachhang(request)
    if not khachhang or not khachhang.matk:
        return redirect('accounts:login')

    taikhoan = khachhang.matk
    requires_2fa = khachhang.is_2fa_enabled

    if request.method == "POST":
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        otp_code = request.POST.get('otp_code', '')

        # Validate old password using verify_password function
        if not verify_password(old_password, taikhoan.password_hash, taikhoan.password_salt):
            messages.error(request, 'Mật khẩu hiện tại không đúng.')
            return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        # Validate new passwords match
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới không khớp.')
            return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        # Validate password strength - 8+ chars, uppercase, lowercase, number, special char
        if len(new_password) < 8:
            messages.error(request, 'Mật khẩu mới phải có ít nhất 8 ký tự.')
            return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 chữ hoa (A-Z).')
            return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        if not re.search(r'[a-z]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 chữ thường (a-z).')
            return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        if not re.search(r'[0-9]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 chữ số (0-9).')
            return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 ký tự đặc biệt (!@#$%^&*...).')
            return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        # Validate 2FA if enabled
        if requires_2fa:
            if not otp_code:
                messages.error(request, 'Vui lòng nhập mã xác thực.')
                return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})
            totp = pyotp.TOTP(khachhang.totp_secret)
            if not totp.verify(otp_code):
                messages.error(request, 'Mã xác thực không đúng.')
                return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})

        # Update password with new salt
        new_salt = str(uuid.uuid4())
        new_hash = hash_password(new_password, new_salt)

        taikhoan.password_hash = new_hash
        taikhoan.password_salt = new_salt
        taikhoan.save()

        # Update last password change time
        khachhang.last_password_change = timezone.now()
        khachhang.save()

        messages.success(request, 'Đổi mật khẩu thành công!')
        return redirect('accounts:profile')

    return render(request, 'accounts/password_change.html', {'requires_2fa': requires_2fa})


# ============================================
# SECURITY QUESTIONS
# ============================================

@login_required_custom
@require_http_methods(['GET', 'POST'])
def setup_security_question_view(request):
    """Thiết lập câu hỏi bảo mật"""
    khachhang = get_current_khachhang(request)
    if not khachhang:
        return redirect('accounts:login')

    # Get existing security question if any
    try:
        existing_sq = SecurityQuestion.objects.get(makh=khachhang)
        current_question = existing_sq.question_key
    except SecurityQuestion.DoesNotExist:
        existing_sq = None
        current_question = None

    if request.method == 'POST':
        question = request.POST.get('security_question', '')
        answer = request.POST.get('security_answer', '')

        if not question or not answer:
            messages.error(request, 'Vui lòng chọn câu hỏi và nhập câu trả lời.')
            return render(request, 'accounts/security_question.html', {
                'questions': SecurityQuestion.QUESTION_CHOICES,
                'current_question': current_question
            })

        if len(answer.strip()) < 2:
            messages.error(request, 'Câu trả lời phải có ít nhất 2 ký tự.')
            return render(request, 'accounts/security_question.html', {
                'questions': SecurityQuestion.QUESTION_CHOICES,
                'current_question': current_question
            })

        # Create or update security question
        import hashlib
        clean_answer = answer.strip().lower()
        answer_hash = hashlib.sha256(clean_answer.encode()).hexdigest()

        if existing_sq:
            existing_sq.question_key = question
            existing_sq.answer_hash = answer_hash
            existing_sq.save()
        else:
            SecurityQuestion.objects.create(
                makh=khachhang,
                question_key=question,
                answer_hash=answer_hash
            )

        messages.success(request, 'Đã thiết lập câu hỏi bảo mật thành công!')
        return redirect('accounts:profile')

    return render(request, 'accounts/security_question.html', {
        'questions': SecurityQuestion.QUESTION_CHOICES,
        'current_question': current_question
    })


# ============================================
# SETUP 2FA
# ============================================

@login_required_custom
@require_http_methods(['GET', 'POST'])
def setup_2fa_view(request):
    khachhang = get_current_khachhang(request)
    if not khachhang:
        return redirect('accounts:login')

    if request.method == "POST":
        form = Enable2FAForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp_code']

            # Verify TOTP during setup (check_enabled=False since not enabled yet)
            if khachhang.verify_totp(otp, check_enabled=False):
                khachhang.is_2fa_enabled = True
                khachhang.save()

                # Send security alert email
                send_security_alert_email(
                    khachhang.email,
                    'Xác thực 2 yếu tố đã được bật',
                    'Xác thực 2 yếu tố (2FA) đã được bật cho tài khoản của bạn trên PhongTro.vn.'
                )
                messages.success(request, '2FA đã được bật thành công!')
                return redirect('accounts:profile')

            messages.error(request, 'Mã OTP không hợp lệ.')
    else:
        # Tạo secret nếu chưa có
        if not khachhang.totp_secret:
            khachhang.totp_secret = pyotp.random_base32()
            khachhang.save()

        # Tạo QR code
        totp = pyotp.TOTP(khachhang.totp_secret)
        totp_uri = totp.provisioning_uri(
            name=khachhang.email,
            issuer_name='PhongTro.vn'
        )

        qr = qrcode.QRCode(box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        img = qr.make_image()

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_code = base64.b64encode(buf.getvalue()).decode()

        form = Enable2FAForm()

        return render(request, 'accounts/setup_2fa.html', {
            'form': form,
            'qr_code': qr_code,
            'secret': khachhang.totp_secret
        })

    return render(request, 'accounts/setup_2fa.html', {'form': form})


# ============================================
# DISABLE 2FA
# ============================================

@login_required_custom
@require_http_methods(['POST'])
def disable_2fa_view(request):
    khachhang = get_current_khachhang(request)
    if not khachhang:
        return redirect('accounts:login')

    otp = request.POST.get('otp_code')

    if khachhang.verify_totp(otp):
        khachhang.is_2fa_enabled = False
        khachhang.totp_secret = None
        khachhang.save()

        # Send security alert email
        send_security_alert_email(
            khachhang.email,
            'Xác thực 2 yếu tố đã được tắt',
            'Xác thực 2 yếu tố (2FA) đã được tắt cho tài khoản của bạn trên PhongTro.vn.'
        )
        messages.success(request, '2FA đã được tắt.')

    return redirect('accounts:profile')


# ============================================
# DEVICES + LOGOUT
# ============================================

@login_required_custom
def manage_devices_view(request):
    khachhang = get_current_khachhang(request)
    if not khachhang:
        return redirect('accounts:login')

    # Lấy lịch sử đăng nhập - LoginHistory uses 'makh' not 'matk', and 'timestamp' not 'login_time'
    try:
        login_history = LoginHistory.objects.filter(makh=khachhang).order_by('-timestamp')[:20]
    except Exception as e:
        login_history = []
        messages.warning(request, f'Không thể tải lịch sử đăng nhập: {str(e)}')

    return render(request, 'accounts/devices.html', {
        'login_history': login_history,
        'khachhang': khachhang
    })


def logout_view(request):
    """Đăng xuất"""
    request.session.flush()
    messages.success(request, 'Đã đăng xuất thành công.')
    return redirect('accounts:login')


@login_required_custom
def logout_all_devices_view(request):
    """Đăng xuất khỏi tất cả thiết bị"""
    # Với hệ thống session-based này, chỉ có thể đăng xuất session hiện tại
    # Để logout tất cả thiết bị cần implement session store riêng
    request.session.flush()
    messages.success(request, 'Đã đăng xuất khỏi tất cả thiết bị.')
    return redirect('accounts:login')


@login_required_custom
def revoke_device_view(request, device_id):
    """Thu hồi quyền truy cập của thiết bị"""
    # Chức năng này cần bảng TrustedDevice trong database
    # Hiện tại chỉ redirect về trang quản lý thiết bị
    messages.info(request, 'Chức năng đang được phát triển.')
    return redirect('accounts:manage_devices')


@login_required_custom
def profile_view(request):
    """Trang thông tin cá nhân"""
    khachhang = get_current_khachhang(request)

    # Get login history
    login_history = []
    if khachhang:
        login_history = LoginHistory.objects.filter(makh=khachhang).order_by('-timestamp')[:10]

    return render(request, 'accounts/profile.html', {
        'khachhang': khachhang,
        'login_history': login_history
    })


# ============================================
# EDIT PROFILE
# ============================================

@login_required_custom
@require_http_methods(['GET', 'POST'])
def edit_profile_view(request):
    """Chỉnh sửa thông tin cá nhân"""
    khachhang = get_current_khachhang(request)

    if not khachhang:
        return redirect('accounts:login')

    if request.method == 'POST':
        # Get form data
        hoten = request.POST.get('hoten', '').strip()
        sdt = request.POST.get('sdt', '').strip()
        diachi = request.POST.get('diachi', '').strip()
        cccd = request.POST.get('cccd', '').strip()

        # Validate
        if not hoten:
            messages.error(request, 'Họ tên không được để trống.')
            return render(request, 'accounts/edit_profile.html', {'khachhang': khachhang})

        # Update
        khachhang.hoten = hoten
        khachhang.sdt = sdt if sdt else None
        khachhang.diachi = diachi if diachi else None
        khachhang.cccd = cccd if cccd else None
        khachhang.save()

        # Update session
        request.session['user_name'] = hoten

        messages.success(request, 'Đã cập nhật thông tin thành công!')
        return redirect('accounts:profile')

    return render(request, 'accounts/edit_profile.html', {'khachhang': khachhang})


# ============================================
# PASSWORD RESET (Email OTP Verification)
# ============================================
import random
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    """Tạo mã OTP 6 số"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate='5/h', method='POST')
def password_reset_view(request):
    """Bước 1: Nhập email để lấy lại mật khẩu - Gửi mã OTP qua email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Vui lòng nhập email.')
            return render(request, 'accounts/password_reset.html')

        # Tìm khách hàng theo email
        try:
            khachhang = Khachhang.objects.get(email=email)
        except Khachhang.DoesNotExist:
            # Không tiết lộ email có tồn tại hay không (bảo mật)
            messages.info(request, 'Nếu email tồn tại trong hệ thống, bạn sẽ nhận được mã xác nhận.')
            return render(request, 'accounts/password_reset.html')

        # Tạo mã OTP 6 số
        otp_code = generate_otp()
        otp_expiry = timezone.now() + timezone.timedelta(minutes=10)

        # Lưu vào session
        request.session['password_reset_email'] = email
        request.session['password_reset_otp'] = otp_code
        request.session['password_reset_otp_expiry'] = otp_expiry.isoformat()
        request.session['password_reset_attempts'] = 0

        # Gửi email
        try:
            subject = '🔐 Mã xác nhận đặt lại mật khẩu - PhongTro.vn'
            message = f'''Xin chào {khachhang.hoten},

Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản PhongTro.vn.

🔑 Mã xác nhận của bạn là: {otp_code}

⏰ Mã này có hiệu lực trong 10 phút.

⚠️ Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

---
PhongTro.vn - Nền tảng tìm phòng trọ an toàn
'''
            html_message = f'''
            <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: #0d6efd;">🏠 PhongTro.vn</h2>
                </div>
                <p>Xin chào <strong>{khachhang.hoten}</strong>,</p>
                <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản PhongTro.vn.</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0 0 10px 0; color: #6c757d;">Mã xác nhận của bạn:</p>
                    <h1 style="letter-spacing: 8px; color: #0d6efd; margin: 0; font-size: 36px;">{otp_code}</h1>
                </div>
                <p style="color: #dc3545;">⏰ Mã này có hiệu lực trong <strong>10 phút</strong>.</p>
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
                <p style="color: #6c757d; font-size: 12px;">
                    ⚠️ Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
                </p>
            </div>
            '''

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, f'Mã xác nhận đã được gửi đến {email}')
            return redirect('accounts:password_reset_verify_otp')

        except Exception as e:
            print(f"Email error: {e}")
            messages.error(request, 'Không thể gửi email. Vui lòng thử lại sau.')
            return render(request, 'accounts/password_reset.html')

    return render(request, 'accounts/password_reset.html')


@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate='10/h', method='POST')
def password_reset_verify_otp_view(request):
    """Bước 2: Xác nhận mã OTP từ email"""
    email = request.session.get('password_reset_email')
    otp_expiry_str = request.session.get('password_reset_otp_expiry')

    if not email or not otp_expiry_str:
        messages.error(request, 'Phiên làm việc đã hết hạn. Vui lòng thử lại.')
        return redirect('accounts:password_reset')

    # Kiểm tra hết hạn
    otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)
    if timezone.now() > otp_expiry:
        messages.error(request, 'Mã xác nhận đã hết hạn. Vui lòng yêu cầu mã mới.')
        # Xóa session
        for key in ['password_reset_email', 'password_reset_otp', 'password_reset_otp_expiry']:
            request.session.pop(key, None)
        return redirect('accounts:password_reset')

    # Tính thời gian còn lại
    remaining_seconds = int((otp_expiry - timezone.now()).total_seconds())

    # Ẩn email (chỉ hiện 3 ký tự đầu)
    email_parts = email.split('@')
    masked_email = email_parts[0][:3] + '***@' + email_parts[1]

    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code', '').strip()
        stored_otp = request.session.get('password_reset_otp')
        attempts = request.session.get('password_reset_attempts', 0)

        if not entered_otp:
            messages.error(request, 'Vui lòng nhập mã xác nhận.')
            return render(request, 'accounts/password_reset_verify_otp.html', {
                'masked_email': masked_email,
                'remaining_seconds': remaining_seconds
            })

        if attempts >= 5:
            messages.error(request, 'Bạn đã nhập sai quá nhiều lần. Vui lòng yêu cầu mã mới.')
            for key in ['password_reset_email', 'password_reset_otp', 'password_reset_otp_expiry']:
                request.session.pop(key, None)
            return redirect('accounts:password_reset')

        if entered_otp == stored_otp:
            # Đúng OTP - cho phép đặt mật khẩu mới
            request.session['password_reset_verified'] = True
            messages.success(request, 'Xác nhận thành công! Vui lòng đặt mật khẩu mới.')
            return redirect('accounts:password_reset_confirm')
        else:
            request.session['password_reset_attempts'] = attempts + 1
            remaining_attempts = 5 - (attempts + 1)
            messages.error(request, f'Mã xác nhận không đúng. Còn {remaining_attempts} lần thử.')
            return render(request, 'accounts/password_reset_verify_otp.html', {
                'masked_email': masked_email,
                'remaining_seconds': remaining_seconds
            })

    return render(request, 'accounts/password_reset_verify_otp.html', {
        'masked_email': masked_email,
        'remaining_seconds': remaining_seconds
    })


@require_http_methods(['POST'])
@ratelimit(key='ip', rate='3/h', method='POST')
def password_reset_resend_otp_view(request):
    """Gửi lại mã OTP"""
    email = request.session.get('password_reset_email')

    if not email:
        messages.error(request, 'Phiên làm việc đã hết hạn.')
        return redirect('accounts:password_reset')

    try:
        khachhang = Khachhang.objects.get(email=email)
    except Khachhang.DoesNotExist:
        return redirect('accounts:password_reset')

    # Tạo mã OTP mới
    otp_code = generate_otp()
    otp_expiry = timezone.now() + timezone.timedelta(minutes=10)

    request.session['password_reset_otp'] = otp_code
    request.session['password_reset_otp_expiry'] = otp_expiry.isoformat()
    request.session['password_reset_attempts'] = 0

    # Gửi email
    try:
        subject = '🔐 Mã xác nhận mới - PhongTro.vn'
        html_message = f'''
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #0d6efd;">🏠 PhongTro.vn</h2>
            </div>
            <p>Xin chào <strong>{khachhang.hoten}</strong>,</p>
            <p>Đây là mã xác nhận mới của bạn:</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                <h1 style="letter-spacing: 8px; color: #0d6efd; margin: 0; font-size: 36px;">{otp_code}</h1>
            </div>
            <p style="color: #dc3545;">⏰ Mã này có hiệu lực trong <strong>10 phút</strong>.</p>
        </div>
        '''

        send_mail(
            subject=subject,
            message=f'Mã xác nhận mới của bạn là: {otp_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        messages.success(request, 'Đã gửi mã xác nhận mới!')

    except Exception as e:
        print(f"Email error: {e}")
        messages.error(request, 'Không thể gửi email. Vui lòng thử lại.')

    return redirect('accounts:password_reset_verify_otp')


@require_http_methods(['GET', 'POST'])
@ratelimit(key='ip', rate='5/h', method='POST')
def password_reset_confirm_view(request, uidb64=None, token=None):
    """Bước 3: Đặt mật khẩu mới"""
    import re
    import uuid

    email = request.session.get('password_reset_email')
    verified = request.session.get('password_reset_verified')

    if not email or not verified:
        return redirect('accounts:password_reset')

    try:
        khachhang = Khachhang.objects.get(email=email)
        taikhoan = khachhang.matk
    except (Khachhang.DoesNotExist, AttributeError):
        messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
        return redirect('accounts:password_reset')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validate passwords match
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp.')
            return render(request, 'accounts/password_reset_confirm.html')

        # Validate password strength
        if len(new_password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự.')
            return render(request, 'accounts/password_reset_confirm.html')

        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 chữ hoa (A-Z).')
            return render(request, 'accounts/password_reset_confirm.html')

        if not re.search(r'[a-z]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 chữ thường (a-z).')
            return render(request, 'accounts/password_reset_confirm.html')

        if not re.search(r'[0-9]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 chữ số (0-9).')
            return render(request, 'accounts/password_reset_confirm.html')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', new_password):
            messages.error(request, 'Mật khẩu phải có ít nhất 1 ký tự đặc biệt.')
            return render(request, 'accounts/password_reset_confirm.html')

        # Update password
        new_salt = str(uuid.uuid4())
        new_hash = hash_password(new_password, new_salt)

        taikhoan.password_hash = new_hash
        taikhoan.password_salt = new_salt
        taikhoan.failed_login_count = 0
        taikhoan.is_locked = False
        taikhoan.lock_time = None
        taikhoan.save()

        # Update last password change
        khachhang.last_password_change = timezone.now()
        khachhang.save()

        # Clear session
        if 'password_reset_email' in request.session:
            del request.session['password_reset_email']
        if 'password_reset_verified' in request.session:
            del request.session['password_reset_verified']

        messages.success(request, 'Đặt lại mật khẩu thành công! Vui lòng đăng nhập.')
        return redirect('accounts:login')

    return render(request, 'accounts/password_reset_confirm.html')


def password_reset_done_view(request):
    """Thông báo đã gửi email (không dùng nữa)"""
    return redirect('accounts:password_reset')


def password_reset_complete_view(request):
    """Hoàn thành reset password (không dùng nữa)"""
    return redirect('accounts:login')
