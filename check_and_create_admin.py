"""
Script kiểm tra và tạo tài khoản Admin
Chạy: python manage.py shell < check_and_create_admin.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import Khachhang, Vaitro, Taikhoan
from django.utils import timezone
import hashlib
import secrets

def create_password_hash(password):
    """Tạo password hash với salt"""
    salt = secrets.token_hex(16)
    password_with_salt = password + salt
    password_hash = hashlib.sha256(password_with_salt.encode()).hexdigest()
    return password_hash, salt

def main():
    print("\n" + "="*80)
    print("🔍 KIỂM TRA VÀ TẠO TÀI KHOẢN ADMIN")
    print("="*80 + "\n")
    
    # 1. Tạo vai trò Admin nếu chưa có
    print("📋 Bước 1: Kiểm tra vai trò Admin...")
    admin_role, created = Vaitro.objects.get_or_create(
        tenvt='Admin',
        defaults={'mota': 'Quản trị viên hệ thống'}
    )
    if created:
        print("   ✓ Đã tạo vai trò Admin")
    else:
        print(f"   ✓ Vai trò Admin đã tồn tại (ID: {admin_role.mavt})")
    print()
    
    # 2. Kiểm tra tài khoản admin
    print("👤 Bước 2: Kiểm tra tài khoản admin@phongtro.vn...")
    admin_email = 'admin@phongtro.vn'
    
    try:
        admin = Khachhang.objects.select_related('matk', 'mavt').get(email=admin_email)
        print(f"   ⚠  Tài khoản đã tồn tại!")
        print(f"   - ID: {admin.makh}")
        print(f"   - Họ tên: {admin.hoten}")
        print(f"   - Vai trò: {admin.mavt.tenvt if admin.mavt else 'Chưa có'}")
        print(f"   - Trạng thái: {'Hoạt động' if admin.trangthai else 'Bị khóa'}")
        print(f"   - Có tài khoản: {'Có' if admin.matk else 'Không'}")
        
        # Cập nhật vai trò nếu chưa đúng
        if not admin.mavt or admin.mavt.tenvt != 'Admin':
            admin.mavt = admin_role
            admin.save()
            print(f"   ✓ Đã cập nhật vai trò thành Admin")
        
        # Reset mật khẩu
        print("\n   🔄 Reset mật khẩu về 'admin123'...")
        if admin.matk:
            password_hash, salt = create_password_hash('admin123')
            admin.matk.password_hash = password_hash
            admin.matk.password_salt = salt
            admin.matk.failed_login_count = 0
            admin.matk.is_locked = False
            admin.matk.save()
            print("   ✓ Đã reset mật khẩu thành công!")
        else:
            # Tạo tài khoản mới
            password_hash, salt = create_password_hash('admin123')
            taikhoan = Taikhoan.objects.create(
                password_hash=password_hash,
                password_salt=salt,
                failed_login_count=0,
                is_locked=False
            )
            admin.matk = taikhoan
            admin.save()
            print("   ✓ Đã tạo tài khoản đăng nhập mới!")
        
    except Khachhang.DoesNotExist:
        print("   ℹ  Tài khoản chưa tồn tại. Đang tạo mới...")
        
        # Tạo tài khoản đăng nhập
        password_hash, salt = create_password_hash('admin123')
        taikhoan = Taikhoan.objects.create(
            password_hash=password_hash,
            password_salt=salt,
            failed_login_count=0,
            is_locked=False
        )
        
        # Tạo khách hàng
        admin = Khachhang.objects.create(
            email=admin_email,
            hoten='Quản Trị Viên',
            sdt='0901234567',
            diachi='Hà Nội',
            mavt=admin_role,
            matk=taikhoan,
            trangthai=True,
            tg_tao=timezone.now()
        )
        
        print(f"   ✓ Đã tạo tài khoản admin thành công!")
        print(f"   - ID: {admin.makh}")
        print(f"   - Email: {admin.email}")
        print(f"   - Họ tên: {admin.hoten}")
    
    print()
    print("="*80)
    print("✅ HOÀN THÀNH!")
    print("="*80)
    print()
    print("📊 THÔNG TIN ĐĂNG NHẬP:")
    print(f"   Email:     {admin_email}")
    print(f"   Mật khẩu:  admin123")
    print(f"   Dashboard: http://localhost:8000/dashboard/admin/")
    print()
    print("🔗 ĐĂNG NHẬP TẠI:")
    print("   http://localhost:8000/accounts/login/")
    print()
    print("="*80)

if __name__ == '__main__':
    main()

