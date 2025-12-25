"""
Django management command để tạo tài khoản Admin
Chạy: python manage.py create_admin
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import Khachhang, Vaitro, Taikhoan
import hashlib
import secrets


class Command(BaseCommand):
    help = 'Tạo tài khoản demo cho 3 role: Admin, Chủ trọ, Khách hàng'

    def create_password_hash(self, password):
        """Tạo password hash với salt"""
        salt = secrets.token_hex(16)
        password_with_salt = password + salt
        password_hash = hashlib.sha256(password_with_salt.encode()).digest()  # digest() thay vì hexdigest()
        return password_hash, salt

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("🚀 TẠO TÀI KHOẢN ADMIN"))
        self.stdout.write("="*80 + "\n")

        try:
            # 1. Tạo vai trò Admin
            self.stdout.write("📋 Bước 1: Tạo vai trò Admin...")
            admin_role, created = Vaitro.objects.get_or_create(
                tenvt='Admin',
                defaults={'mota': 'Quản trị viên hệ thống'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo vai trò Admin (ID: {admin_role.mavt})"))
            else:
                self.stdout.write(f"   ✓ Vai trò Admin đã tồn tại (ID: {admin_role.mavt})")

            # 2. Tạo vai trò Chủ trọ
            self.stdout.write("\n📋 Bước 2: Tạo vai trò Chủ trọ...")
            landlord_role, created = Vaitro.objects.get_or_create(
                tenvt='Chủ trọ',
                defaults={'mota': 'Người cho thuê phòng trọ'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo vai trò Chủ trọ (ID: {landlord_role.mavt})"))
            else:
                self.stdout.write(f"   ✓ Vai trò Chủ trọ đã tồn tại (ID: {landlord_role.mavt})")

            # 3. Tạo vai trò Khách hàng
            self.stdout.write("\n📋 Bước 3: Tạo vai trò Khách hàng...")
            customer_role, created = Vaitro.objects.get_or_create(
                tenvt='Khách hàng',
                defaults={'mota': 'Người thuê phòng trọ'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo vai trò Khách hàng (ID: {customer_role.mavt})"))
            else:
                self.stdout.write(f"   ✓ Vai trò Khách hàng đã tồn tại (ID: {customer_role.mavt})")

            # 4. Tạo tài khoản Admin
            self.stdout.write("\n👤 Bước 4: Tạo tài khoản Admin...")
            admin_email = 'admin@phongtro.vn'
            admin = Khachhang.objects.filter(email=admin_email).first()

            if admin:
                self.stdout.write(self.style.WARNING(f"   ⚠  Tài khoản {admin_email} đã tồn tại"))
                self.stdout.write(f"   - ID: {admin.makh}")
                self.stdout.write(f"   - Họ tên: {admin.hoten}")
                self.stdout.write(f"   - Vai trò: {admin.mavt.tenvt if admin.mavt else 'Chưa có'}")

                # Cập nhật vai trò
                admin.mavt = admin_role
                admin.trangthai = True
                admin.save()
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã cập nhật vai trò thành Admin"))

                # Reset mật khẩu
                if admin.matk:
                    password_hash, salt = self.create_password_hash('admin123')
                    admin.matk.password_hash = password_hash
                    admin.matk.password_salt = salt
                    admin.matk.failed_login_count = 0
                    admin.matk.is_locked = False
                    admin.matk.save()
                    self.stdout.write(self.style.SUCCESS(f"   ✓ Đã reset mật khẩu thành 'admin123'"))
                else:
                    password_hash, salt = self.create_password_hash('admin123')
                    taikhoan = Taikhoan.objects.create(
                        password_hash=password_hash,
                        password_salt=salt,
                        failed_login_count=0,
                        is_locked=False
                    )
                    admin.matk = taikhoan
                    admin.save()
                    self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo tài khoản đăng nhập mới"))
            else:
                self.stdout.write(f"   ℹ  Tạo tài khoản mới: {admin_email}")

                # Tạo tài khoản đăng nhập
                password_hash, salt = self.create_password_hash('admin123')
                taikhoan = Taikhoan.objects.create(
                    password_hash=password_hash,
                    password_salt=salt,
                    failed_login_count=0,
                    is_locked=False
                )
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo Taikhoan (ID: {taikhoan.matk})"))

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
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo Khachhang (ID: {admin.makh})"))

            # 5. Tạo tài khoản Chủ trọ
            self.stdout.write("\n👤 Bước 5: Tạo tài khoản Chủ trọ...")
            landlord_email = 'chutro@phongtro.vn'
            landlord = Khachhang.objects.filter(email=landlord_email).first()

            if not landlord:
                password_hash, salt = self.create_password_hash('chutro123')
                taikhoan = Taikhoan.objects.create(
                    username='chutro',
                    password_hash=password_hash,
                    password_salt=salt,
                    failed_login_count=0,
                    is_locked=False,
                    tg_tao=timezone.now()
                )
                landlord = Khachhang.objects.create(
                    email=landlord_email,
                    hoten='Nguyễn Văn Chủ',
                    sdt='0902345678',
                    diachi='Quận 1, TP.HCM',
                    mavt=landlord_role,
                    matk=taikhoan,
                    trangthai=True,
                    tg_tao=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo tài khoản Chủ trọ"))
            else:
                self.stdout.write(f"   ✓ Tài khoản Chủ trọ đã tồn tại")

            # 6. Tạo tài khoản Khách hàng
            self.stdout.write("\n👤 Bước 6: Tạo tài khoản Khách hàng...")
            customer_email = 'khachhang@phongtro.vn'
            customer = Khachhang.objects.filter(email=customer_email).first()

            if not customer:
                password_hash, salt = self.create_password_hash('khach123')
                taikhoan = Taikhoan.objects.create(
                    username='khachhang',
                    password_hash=password_hash,
                    password_salt=salt,
                    failed_login_count=0,
                    is_locked=False,
                    tg_tao=timezone.now()
                )
                customer = Khachhang.objects.create(
                    email=customer_email,
                    hoten='Trần Thị Khách',
                    sdt='0903456789',
                    diachi='Quận 3, TP.HCM',
                    mavt=customer_role,
                    matk=taikhoan,
                    trangthai=True,
                    tg_tao=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f"   ✓ Đã tạo tài khoản Khách hàng"))
            else:
                self.stdout.write(f"   ✓ Tài khoản Khách hàng đã tồn tại")

            self.stdout.write("\n" + "="*80)
            self.stdout.write(self.style.SUCCESS("✅ HOÀN THÀNH!"))
            self.stdout.write("="*80)
            self.stdout.write("\n📊 THÔNG TIN ĐĂNG NHẬP:")
            self.stdout.write("\n👑 ADMIN:")
            self.stdout.write(f"   Email:     {admin_email}")
            self.stdout.write(f"   Mật khẩu:  admin123")
            self.stdout.write(f"   Dashboard: http://localhost:8000/dashboard/admin/")
            self.stdout.write("\n🏠 CHỦ TRỌ:")
            self.stdout.write(f"   Email:     {landlord_email}")
            self.stdout.write(f"   Mật khẩu:  chutro123")
            self.stdout.write(f"   Dashboard: http://localhost:8000/landlord/")
            self.stdout.write("\n👤 KHÁCH HÀNG:")
            self.stdout.write(f"   Email:     {customer_email}")
            self.stdout.write(f"   Mật khẩu:  khach123")
            self.stdout.write(f"   Dashboard: http://localhost:8000/dashboard/customer/")
            self.stdout.write("\n🔗 ĐĂNG NHẬP TẠI:")
            self.stdout.write("   http://localhost:8000/accounts/login/")
            self.stdout.write("\n" + "="*80 + "\n")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ LỖI: {e}"))
            import traceback
            traceback.print_exc()

