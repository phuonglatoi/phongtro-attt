"""
Script tạo tài khoản demo cho 3 role: Admin, Chủ trọ, Khách hàng
Chạy trong Django shell: python manage.py shell < create_demo_accounts.py
"""

from apps.accounts.models import Khachhang, Vaitro
from django.utils import timezone

def create_demo_accounts():
    """Tạo tài khoản demo cho 3 role"""
    
    print("\n" + "="*80)
    print("🚀 BẮT ĐẦU TẠO TÀI KHOẢN DEMO CHO 3 ROLE")
    print("="*80 + "\n")
    
    # ============================================
    # 1. TẠO CÁC VAI TRÒ (NẾU CHƯA CÓ)
    # ============================================
    print("📋 Bước 1: Tạo các vai trò...")
    
    roles_data = [
        {'tenvt': 'Admin', 'mota': 'Quản trị viên hệ thống'},
        {'tenvt': 'Chủ trọ', 'mota': 'Người cho thuê phòng trọ'},
        {'tenvt': 'Khách hàng', 'mota': 'Người thuê phòng trọ'},
    ]
    
    roles = {}
    for role_data in roles_data:
        role, created = Vaitro.objects.get_or_create(
            tenvt=role_data['tenvt'],
            defaults={'mota': role_data.get('mota', '')}
        )
        roles[role_data['tenvt']] = role
        status = "✓ Đã tạo mới" if created else "✓ Đã tồn tại"
        print(f"   {status}: {role_data['tenvt']}")
    
    print()
    
    # ============================================
    # 2. TẠO TÀI KHOẢN DEMO
    # ============================================
    print("👥 Bước 2: Tạo tài khoản demo...")
    print()
    
    accounts_data = [
        {
            'email': 'admin@phongtro.vn',
            'hoten': 'Quản Trị Viên',
            'sdt': '0901234567',
            'diachi': 'Hà Nội',
            'role': 'Admin',
            'password': 'admin123'
        },
        {
            'email': 'chutro@phongtro.vn',
            'hoten': 'Nguyễn Văn Chủ',
            'sdt': '0902345678',
            'diachi': 'Quận 1, TP.HCM',
            'role': 'Chủ trọ',
            'password': 'chutro123'
        },
        {
            'email': 'khachhang@phongtro.vn',
            'hoten': 'Trần Thị Khách',
            'sdt': '0903456789',
            'diachi': 'Quận 3, TP.HCM',
            'role': 'Khách hàng',
            'password': 'khach123'
        },
    ]
    
    created_accounts = []
    
    for account_data in accounts_data:
        email = account_data['email']
        role_name = account_data['role']
        password = account_data['password']
        
        # Kiểm tra xem email đã tồn tại chưa
        existing = Khachhang.objects.filter(email=email).first()
        
        if existing:
            print(f"⚠  Tài khoản {email} đã tồn tại!")
            print(f"   Họ tên: {existing.hoten}")
            print(f"   Vai trò hiện tại: {existing.mavt.tenvt if existing.mavt else 'Chưa có'}")
            
            # Cập nhật vai trò nếu khác
            if not existing.mavt or existing.mavt.tenvt != role_name:
                existing.mavt = roles[role_name]
                existing.save()
                print(f"   ✓ Đã cập nhật vai trò thành {role_name}")
            
            created_accounts.append({
                'email': email,
                'password': password,
                'role': role_name,
                'name': existing.hoten,
                'status': 'updated'
            })
        else:
            # Tạo tài khoản mới
            user = Khachhang.objects.create(
                email=email,
                hoten=account_data['hoten'],
                sdt=account_data['sdt'],
                diachi=account_data['diachi'],
                mavt=roles[role_name],
                trangthai=True,
                tg_tao=timezone.now()
            )
            user.set_password(password)
            user.save()
            
            print(f"✓ Đã tạo tài khoản {email}")
            print(f"   Họ tên: {user.hoten}")
            print(f"   Vai trò: {role_name}")
            
            created_accounts.append({
                'email': email,
                'password': password,
                'role': role_name,
                'name': user.hoten,
                'status': 'created'
            })
        
        print()
    
    # ============================================
    # 3. HIỂN THỊ THÔNG TIN TÀI KHOẢN
    # ============================================
    print("="*80)
    print("✅ HOÀN THÀNH! THÔNG TIN TÀI KHOẢN DEMO")
    print("="*80)
    print()
    
    for account in created_accounts:
        icon = "👑" if account['role'] == 'Admin' else "🏠" if account['role'] == 'Chủ trọ' else "👤"
        print(f"{icon} {account['role'].upper()}")
        print(f"   Email:     {account['email']}")
        print(f"   Mật khẩu:  {account['password']}")
        print(f"   Họ tên:    {account['name']}")
        print()
    
    print("="*80)
    print("🔗 ĐĂNG NHẬP TẠI:")
    print("   http://localhost:8000/accounts/login/")
    print()
    print("📊 DASHBOARD:")
    print("   👑 Admin:      http://localhost:8000/dashboard/admin/")
    print("   🏠 Chủ trọ:    http://localhost:8000/landlord/")
    print("   👤 Khách hàng: http://localhost:8000/dashboard/customer/")
    print("="*80)
    print()

# Chạy script
if __name__ == '__main__':
    create_demo_accounts()

