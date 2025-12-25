# 🚀 HƯỚNG DẪN TẠO TÀI KHOẢN ADMIN

## ⚡ CÁCH NHANH NHẤT (KHUYẾN NGHỊ)

### Bước 1: Mở Django Shell
```bash
python manage.py shell
```

### Bước 2: Copy và paste đoạn code sau:

```python
from apps.accounts.models import Khachhang, Vaitro, Taikhoan
from django.utils import timezone
import hashlib
import secrets

# Hàm tạo password hash
def create_password_hash(password):
    salt = secrets.token_hex(16)
    password_with_salt = password + salt
    password_hash = hashlib.sha256(password_with_salt.encode()).hexdigest()
    return password_hash, salt

# 1. Tạo vai trò Admin
admin_role, created = Vaitro.objects.get_or_create(
    tenvt='Admin',
    defaults={'mota': 'Quản trị viên hệ thống'}
)
print(f"Vai trò Admin: {'Tạo mới' if created else 'Đã có'}")

# 2. Kiểm tra tài khoản admin
admin_email = 'admin@phongtro.vn'
admin = Khachhang.objects.filter(email=admin_email).first()

if admin:
    print(f"Tài khoản {admin_email} đã tồn tại")
    print(f"Họ tên: {admin.hoten}")
    print(f"Vai trò: {admin.mavt.tenvt if admin.mavt else 'Chưa có'}")
    
    # Cập nhật vai trò
    if not admin.mavt or admin.mavt.tenvt != 'Admin':
        admin.mavt = admin_role
        admin.save()
        print("✓ Đã cập nhật vai trò thành Admin")
    
    # Reset mật khẩu
    if admin.matk:
        password_hash, salt = create_password_hash('admin123')
        admin.matk.password_hash = password_hash
        admin.matk.password_salt = salt
        admin.matk.failed_login_count = 0
        admin.matk.is_locked = False
        admin.matk.save()
        print("✓ Đã reset mật khẩu thành 'admin123'")
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
        print("✓ Đã tạo tài khoản đăng nhập mới")
else:
    print(f"Tạo tài khoản mới: {admin_email}")
    
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
    print(f"✓ Đã tạo tài khoản admin thành công!")

print("\n" + "="*60)
print("✅ HOÀN THÀNH!")
print("="*60)
print(f"Email:     {admin_email}")
print(f"Mật khẩu:  admin123")
print(f"Dashboard: http://localhost:8000/dashboard/admin/")
print("="*60)
```

### Bước 3: Thoát Django Shell
```python
exit()
```

---

## 📊 THÔNG TIN ĐĂNG NHẬP

```
Email:     admin@phongtro.vn
Mật khẩu:  admin123
Dashboard: http://localhost:8000/dashboard/admin/
```

**Đăng nhập tại:** http://localhost:8000/accounts/login/

---

## 🎯 SAU KHI ĐĂNG NHẬP

Khi đăng nhập thành công với tài khoản Admin, hệ thống sẽ **TỰ ĐỘNG** redirect đến:

```
http://localhost:8000/dashboard/admin/
```

**Không cần nhớ link!** Chỉ cần đăng nhập và hệ thống tự động đưa bạn đến dashboard Admin! 🚀

---

## 🔧 TROUBLESHOOTING

### ❌ Lỗi: "Email hoặc mật khẩu không đúng"

**Nguyên nhân:**
- Tài khoản chưa được tạo
- Mật khẩu không đúng
- Tài khoản bị khóa

**Giải pháp:**
1. Chạy lại script tạo tài khoản ở trên
2. Script sẽ tự động reset mật khẩu về `admin123`
3. Thử đăng nhập lại

---

### ❌ Lỗi: "Tài khoản đã bị khóa"

**Giải pháp:**
Chạy trong Django shell:
```python
from apps.accounts.models import Khachhang
admin = Khachhang.objects.get(email='admin@phongtro.vn')
if admin.matk:
    admin.matk.is_locked = False
    admin.matk.failed_login_count = 0
    admin.matk.save()
    print("✓ Đã mở khóa tài khoản")
```

---

### ❌ Lỗi: "Không có vai trò Admin"

**Giải pháp:**
Chạy trong Django shell:
```python
from apps.accounts.models import Khachhang, Vaitro
admin_role = Vaitro.objects.get(tenvt='Admin')
admin = Khachhang.objects.get(email='admin@phongtro.vn')
admin.mavt = admin_role
admin.save()
print("✓ Đã cập nhật vai trò Admin")
```

---

## 📝 LƯU Ý

1. ⚠️ **Đổi mật khẩu** sau khi đăng nhập lần đầu
2. ⚠️ Tài khoản **Admin** khác với **Django superuser**
3. ⚠️ Mật khẩu demo chỉ dùng để test, không dùng trong production
4. ✅ Script có thể chạy nhiều lần, sẽ tự động reset mật khẩu nếu tài khoản đã tồn tại

---

**Chúc bạn thành công! 🎉**

