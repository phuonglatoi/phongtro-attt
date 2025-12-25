# 🎯 HƯỚNG DẪN TẠO TÀI KHOẢN DEMO

## 📋 Tổng Quan

Hệ thống có **3 role** với **3 dashboard riêng biệt**:

| Role | Dashboard | Mục đích |
|------|-----------|----------|
| 👑 **Admin** | `/dashboard/admin/` | Quản trị hệ thống, duyệt yêu cầu |
| 🏠 **Chủ trọ** | `/landlord/` | Quản lý phòng trọ, nhà trọ |
| 👤 **Khách hàng** | `/dashboard/customer/` | Xem lịch hẹn, phòng đang thuê |

---

## 🚀 CÁCH 1: SỬ DỤNG DJANGO SHELL (KHUYẾN NGHỊ)

### Bước 1: Mở Django Shell
```bash
python manage.py shell
```

### Bước 2: Copy và paste đoạn code sau:

```python
from apps.accounts.models import Khachhang, Vaitro
from django.utils import timezone

# Tạo các vai trò
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
    print(f"{'Tạo mới' if created else 'Đã có'}: {role_data['tenvt']}")

# Tạo tài khoản Admin
admin_email = 'admin@phongtro.vn'
admin = Khachhang.objects.filter(email=admin_email).first()
if not admin:
    admin = Khachhang.objects.create(
        email=admin_email,
        hoten='Quản Trị Viên',
        sdt='0901234567',
        diachi='Hà Nội',
        mavt=roles['Admin'],
        trangthai=True,
        tg_tao=timezone.now()
    )
    admin.set_password('admin123')
    admin.save()
    print(f"✓ Tạo Admin: {admin_email} / admin123")
else:
    print(f"⚠ Admin đã tồn tại: {admin_email}")

# Tạo tài khoản Chủ trọ
landlord_email = 'chutro@phongtro.vn'
landlord = Khachhang.objects.filter(email=landlord_email).first()
if not landlord:
    landlord = Khachhang.objects.create(
        email=landlord_email,
        hoten='Nguyễn Văn Chủ',
        sdt='0902345678',
        diachi='Quận 1, TP.HCM',
        mavt=roles['Chủ trọ'],
        trangthai=True,
        tg_tao=timezone.now()
    )
    landlord.set_password('chutro123')
    landlord.save()
    print(f"✓ Tạo Chủ trọ: {landlord_email} / chutro123")
else:
    print(f"⚠ Chủ trọ đã tồn tại: {landlord_email}")

# Tạo tài khoản Khách hàng
customer_email = 'khachhang@phongtro.vn'
customer = Khachhang.objects.filter(email=customer_email).first()
if not customer:
    customer = Khachhang.objects.create(
        email=customer_email,
        hoten='Trần Thị Khách',
        sdt='0903456789',
        diachi='Quận 3, TP.HCM',
        mavt=roles['Khách hàng'],
        trangthai=True,
        tg_tao=timezone.now()
    )
    customer.set_password('khach123')
    customer.save()
    print(f"✓ Tạo Khách hàng: {customer_email} / khach123")
else:
    print(f"⚠ Khách hàng đã tồn tại: {customer_email}")

print("\n" + "="*60)
print("✅ HOÀN THÀNH!")
print("="*60)
```

---

## 📊 THÔNG TIN TÀI KHOẢN DEMO

### 👑 ADMIN
```
Email:     admin@phongtro.vn
Mật khẩu:  admin123
Dashboard: http://localhost:8000/dashboard/admin/
```

**Tính năng:**
- Duyệt yêu cầu làm chủ trọ
- Duyệt/Từ chối phòng trọ
- Quản lý khách hàng
- Xem thống kê hệ thống

---

### 🏠 CHỦ TRỌ
```
Email:     chutro@phongtro.vn
Mật khẩu:  chutro123
Dashboard: http://localhost:8000/landlord/
```

**Tính năng:**
- Quản lý nhà trọ
- Quản lý phòng trọ
- Xem lịch hẹn xem phòng
- Xác nhận/Từ chối lịch hẹn

---

### 👤 KHÁCH HÀNG
```
Email:     khachhang@phongtro.vn
Mật khẩu:  khach123
Dashboard: http://localhost:8000/dashboard/customer/
```

**Tính năng:**
- Xem lịch hẹn xem phòng
- Xem phòng đang thuê
- Xem đánh giá đã viết
- Quản lý thông tin cá nhân

---

## 🔗 LINK QUAN TRỌNG

- **Đăng nhập:** http://localhost:8000/accounts/login/
- **Trang chủ:** http://localhost:8000/
- **Django Admin:** http://localhost:8000/admin/ (cho superuser)

---

## 🎯 AUTO-REDIRECT THEO ROLE

Khi đăng nhập thành công, hệ thống sẽ **TỰ ĐỘNG** redirect đến dashboard tương ứng:

| Vai trò | Redirect đến |
|---------|--------------|
| 👑 Admin | `/dashboard/admin/` |
| 🏠 Chủ trọ | `/landlord/` |
| 👤 Khách hàng | `/dashboard/customer/` |
| Khác | `/` (Trang chủ) |

**Không cần nhớ link dashboard!** Chỉ cần đăng nhập và hệ thống sẽ tự động đưa bạn đến đúng nơi! 🚀

---

## ⚠️ LƯU Ý

1. **Đổi mật khẩu** sau khi đăng nhập lần đầu
2. Tài khoản **Admin** khác với **Django superuser**
3. Mỗi role có dashboard riêng với tính năng khác nhau
4. Tài khoản demo chỉ dùng để test, không dùng trong production

---

## 🆘 TROUBLESHOOTING

### Lỗi: "Email đã tồn tại"
→ Tài khoản đã được tạo trước đó. Sử dụng email và mật khẩu ở trên để đăng nhập.

### Lỗi: "Không tìm thấy vai trò"
→ Chạy lại phần tạo vai trò trong script.

### Không thể đăng nhập
→ Kiểm tra email và mật khẩu, đảm bảo tài khoản có `trangthai=True`.

---

**Chúc bạn thành công! 🎉**

