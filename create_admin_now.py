import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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

print("\n" + "="*80)
print("🚀 TẠO TÀI KHOẢN ADMIN")
print("="*80 + "\n")

try:
    # 1. Tạo vai trò Admin
    print("📋 Bước 1: Tạo vai trò Admin...")
    admin_role, created = Vaitro.objects.get_or_create(
        tenvt='Admin',
        defaults={'mota': 'Quản trị viên hệ thống'}
    )
    if created:
        print(f"   ✓ Đã tạo vai trò Admin (ID: {admin_role.mavt})")
    else:
        print(f"   ✓ Vai trò Admin đã tồn tại (ID: {admin_role.mavt})")
    
    # 2. Tạo vai trò Chủ trọ
    print("\n📋 Bước 2: Tạo vai trò Chủ trọ...")
    landlord_role, created = Vaitro.objects.get_or_create(
        tenvt='Chủ trọ',
        defaults={'mota': 'Người cho thuê phòng trọ'}
    )
    if created:
        print(f"   ✓ Đã tạo vai trò Chủ trọ (ID: {landlord_role.mavt})")
    else:
        print(f"   ✓ Vai trò Chủ trọ đã tồn tại (ID: {landlord_role.mavt})")
    
    # 3. Tạo vai trò Khách hàng
    print("\n📋 Bước 3: Tạo vai trò Khách hàng...")
    customer_role, created = Vaitro.objects.get_or_create(
        tenvt='Khách hàng',
        defaults={'mota': 'Người thuê phòng trọ'}
    )
    if created:
        print(f"   ✓ Đã tạo vai trò Khách hàng (ID: {customer_role.mavt})")
    else:
        print(f"   ✓ Vai trò Khách hàng đã tồn tại (ID: {customer_role.mavt})")
    
    # 4. Tạo tài khoản Admin
    print("\n👤 Bước 4: Tạo tài khoản Admin...")
    admin_email = 'admin@phongtro.vn'
    admin = Khachhang.objects.filter(email=admin_email).first()
    
    if admin:
        print(f"   ⚠  Tài khoản {admin_email} đã tồn tại")
        print(f"   - ID: {admin.makh}")
        print(f"   - Họ tên: {admin.hoten}")
        print(f"   - Vai trò: {admin.mavt.tenvt if admin.mavt else 'Chưa có'}")
        
        # Cập nhật vai trò
        admin.mavt = admin_role
        admin.trangthai = True
        admin.save()
        print(f"   ✓ Đã cập nhật vai trò thành Admin")
        
        # Reset mật khẩu
        if admin.matk:
            password_hash, salt = create_password_hash('admin123')
            admin.matk.password_hash = password_hash
            admin.matk.password_salt = salt
            admin.matk.failed_login_count = 0
            admin.matk.is_locked = False
            admin.matk.save()
            print(f"   ✓ Đã reset mật khẩu thành 'admin123'")
        else:
            password_hash, salt = create_password_hash('admin123')
            taikhoan = Taikhoan.objects.create(
                password_hash=password_hash,
                password_salt=salt,
                failed_login_count=0,
                is_locked=False
            )
            admin.matk = taikhoan
            admin.save()
            print(f"   ✓ Đã tạo tài khoản đăng nhập mới")
    else:
        print(f"   ℹ  Tạo tài khoản mới: {admin_email}")
        
        # Tạo tài khoản đăng nhập
        password_hash, salt = create_password_hash('admin123')
        taikhoan = Taikhoan.objects.create(
            password_hash=password_hash,
            password_salt=salt,
            failed_login_count=0,
            is_locked=False
        )
        print(f"   ✓ Đã tạo Taikhoan (ID: {taikhoan.matk})")
        
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
        print(f"   ✓ Đã tạo Khachhang (ID: {admin.makh})")
    
    print("\n" + "="*80)
    print("✅ HOÀN THÀNH!")
    print("="*80)
    print("\n📊 THÔNG TIN ĐĂNG NHẬP:")
    print(f"   Email:     {admin_email}")
    print(f"   Mật khẩu:  admin123")
    print(f"   Dashboard: http://localhost:8000/dashboard/admin/")
    print("\n🔗 ĐĂNG NHẬP TẠI:")
    print("   http://localhost:8000/accounts/login/")
    print("\n" + "="*80 + "\n")

except Exception as e:
    print(f"\n❌ LỖI: {e}")
    import traceback
    traceback.print_exc()

