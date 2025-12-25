"""
Script đơn giản để tạo tài khoản Admin
Copy và paste vào Django shell: python manage.py shell
"""

print("""
# ============================================
# COPY VÀ PASTE CÁC LỆNH SAU VÀO DJANGO SHELL
# ============================================

from apps.accounts.models import Khachhang, Vaitro
from django.utils import timezone

# 1. Tạo hoặc lấy vai trò Admin
admin_role, created = Vaitro.objects.get_or_create(
    tenvt='Admin',
    defaults={'mota': 'Quản trị viên hệ thống'}
)
print(f"Vai trò Admin: {'Đã tạo mới' if created else 'Đã tồn tại'}")

# 2. Kiểm tra xem email đã tồn tại chưa
email = 'admin@phongtro.vn'
existing = Khachhang.objects.filter(email=email).first()

if existing:
    print(f"Tài khoản {email} đã tồn tại!")
    print(f"Họ tên: {existing.hoten}")
    if not existing.mavt or existing.mavt.tenvt != 'Admin':
        existing.mavt = admin_role
        existing.save()
        print("Đã cập nhật vai trò thành Admin")
    admin_user = existing
else:
    # 3. Tạo tài khoản mới
    admin_user = Khachhang.objects.create(
        email='admin@phongtro.vn',
        hoten='Quản Trị Viên',
        sdt='0123456789',
        diachi='Hà Nội',
        mavt=admin_role,
        trangthai=True,
        tg_tao=timezone.now()
    )
    admin_user.set_password('admin123')
    admin_user.save()
    print("Đã tạo tài khoản Admin mới!")

# 4. Hiển thị thông tin
print("="*60)
print("THÔNG TIN TÀI KHOẢN ADMIN")
print("="*60)
print(f"Email:     {admin_user.email}")
print(f"Mật khẩu:  admin123")
print(f"Họ tên:    {admin_user.hoten}")
print(f"Vai trò:   {admin_user.mavt.tenvt if admin_user.mavt else 'Chưa có'}")
print(f"Trạng thái: {'Hoạt động' if admin_user.trangthai else 'Khóa'}")
print("="*60)
print("Đăng nhập tại: http://localhost:8000/accounts/login/")
print("Admin Dashboard: http://localhost:8000/dashboard/admin/")
print("="*60)
""")

