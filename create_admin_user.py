"""
Script tạo tài khoản Admin cho Dashboard
Chạy: python create_admin_user.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import Khachhang, Vaitro
from django.utils import timezone

def create_admin_user():
    """Tạo tài khoản Admin cho Dashboard"""
    
    # Kiểm tra xem vai trò Admin đã tồn tại chưa
    admin_role, created = Vaitro.objects.get_or_create(
        tenvt='Admin',
        defaults={'mota': 'Quản trị viên hệ thống'}
    )
    
    if created:
        print("✓ Đã tạo vai trò Admin")
    else:
        print("✓ Vai trò Admin đã tồn tại")
    
    # Thông tin tài khoản admin mới
    admin_data = {
        'email': 'admin@phongtro.vn',
        'hoten': 'Quản Trị Viên',
        'sdt': '0123456789',
        'diachi': 'Hà Nội',
        'mavt': admin_role,
        'trangthai': True,
        'tg_tao': timezone.now()
    }
    
    # Kiểm tra xem email đã tồn tại chưa
    existing_admin = Khachhang.objects.filter(email=admin_data['email']).first()
    
    if existing_admin:
        print(f"\n⚠ Tài khoản {admin_data['email']} đã tồn tại!")
        print(f"   Họ tên: {existing_admin.hoten}")
        print(f"   Vai trò: {existing_admin.mavt.tenvt if existing_admin.mavt else 'Chưa có'}")
        
        # Cập nhật vai trò nếu chưa phải Admin
        if not existing_admin.mavt or existing_admin.mavt.tenvt != 'Admin':
            existing_admin.mavt = admin_role
            existing_admin.save()
            print("   ✓ Đã cập nhật vai trò thành Admin")
        
        return existing_admin
    
    # Tạo tài khoản mới
    admin_user = Khachhang.objects.create(**admin_data)
    
    # Set password
    admin_user.set_password('admin123')  # Mật khẩu mặc định
    admin_user.save()
    
    print("\n" + "="*60)
    print("✓ ĐÃ TẠO TÀI KHOẢN ADMIN THÀNH CÔNG!")
    print("="*60)
    print(f"Email:     {admin_user.email}")
    print(f"Mật khẩu:  admin123")
    print(f"Họ tên:    {admin_user.hoten}")
    print(f"Vai trò:   {admin_user.mavt.tenvt}")
    print(f"Trạng thái: {'Hoạt động' if admin_user.trangthai else 'Khóa'}")
    print("="*60)
    print("\n🔗 Đăng nhập tại:")
    print("   http://localhost:8000/accounts/login/")
    print("\n📊 Truy cập Admin Dashboard:")
    print("   http://localhost:8000/dashboard/admin/")
    print("\n⚠ LƯU Ý: Hãy đổi mật khẩu sau khi đăng nhập lần đầu!")
    print("="*60 + "\n")
    
    return admin_user

if __name__ == '__main__':
    try:
        admin_user = create_admin_user()
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()

