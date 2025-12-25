# 🔐 HƯỚNG DẪN SỬ DỤNG PROTECTED MEDIA FILES

## 📋 TỔNG QUAN

Hệ thống bảo vệ file media với 3 lớp bảo mật:
1. **Protected Media View** - Kiểm tra quyền truy cập
2. **Nginx X-Accel-Redirect** - Serve file hiệu suất cao
3. **Signed URLs** - Link tạm thời có thời hạn

---

## 🎯 CÁCH HOẠT ĐỘNG

### Luồng truy cập file:

```
[User request /media/rooms/123/image.jpg]
         ↓
[Nginx rewrite → /protected-media/rooms/123/image.jpg]
         ↓
[Django view: serve_protected_media()]
         ↓
[Kiểm tra đăng nhập + quyền sở hữu]
         ↓ (Allowed)
[Django trả về X-Accel-Redirect header]
         ↓
[Nginx serve file từ /protected-files/]
         ↓
[User nhận file]
```

---

## 💻 SỬ DỤNG TRONG CODE

### 1. Trong View (Python)

```python
from apps.security.utils import get_protected_media_url

def room_detail_view(request, pk):
    room = get_object_or_404(Phongtro, pk=pk)
    images = room.hinhanh_set.all()
    
    # Tạo signed URLs cho ảnh (hết hạn sau 2 giờ)
    image_urls = []
    for img in images:
        signed_url = get_protected_media_url(img.duongdan, expiry_hours=2)
        image_urls.append(signed_url)
    
    return render(request, 'rooms/detail.html', {
        'room': room,
        'image_urls': image_urls
    })
```

### 2. Trong Template

```django
{% load security_tags %}

<!-- Cách 1: Sử dụng template tag -->
<img src="{% protected_media_url 'rooms/123/image.jpg' 2 %}" alt="Room">

<!-- Cách 2: Sử dụng filter -->
<img src="{{ image.duongdan|protected_url:2 }}" alt="Room">

<!-- Cách 3: URL từ view -->
<img src="{{ signed_url }}" alt="Room">
```

### 3. Tạo nhiều URLs cùng lúc

```python
from apps.security.utils import generate_batch_urls

file_paths = ['rooms/1/a.jpg', 'rooms/1/b.jpg', 'rooms/1/c.jpg']
urls = generate_batch_urls(file_paths, expiry_hours=3)

# urls = {
#     'rooms/1/a.jpg': '/protected-media/rooms/1/a.jpg?token=...',
#     'rooms/1/b.jpg': '/protected-media/rooms/1/b.jpg?token=...',
#     'rooms/1/c.jpg': '/protected-media/rooms/1/c.jpg?token=...'
# }
```

---

## ⚙️ CẤU HÌNH

### File: `config/settings/security.py`

```python
# Bật X-Accel-Redirect (production)
USE_X_ACCEL_REDIRECT = True

# Thời gian hết hạn signed URL (giây)
SIGNED_URL_EXPIRY = 3600  # 1 giờ

# Cho phép truy cập công khai ảnh phòng
ALLOW_PUBLIC_ROOM_IMAGES = True  # False = phải đăng nhập
```

### File: `.env`

```bash
USE_X_ACCEL_REDIRECT=True
SIGNED_URL_EXPIRY=3600
ALLOW_PUBLIC_ROOM_IMAGES=True
```

---

## 🔒 QUYỀN TRUY CẬP

### Ai được phép xem file?

1. **Admin** - Xem tất cả file
2. **Chủ phòng** - Xem ảnh phòng của mình
3. **Người đã đặt phòng** - Xem ảnh phòng đã đặt
4. **Public** (nếu `ALLOW_PUBLIC_ROOM_IMAGES=True`) - Xem ảnh phòng công khai

### Customize quyền truy cập:

Edit file `apps/security/views.py`, function `check_file_permission()`:

```python
def check_file_permission(request, file_path):
    # Thêm logic kiểm tra quyền tùy chỉnh
    
    # VD: Chỉ cho phép xem ảnh nếu đã thanh toán
    if has_paid_booking(request.user, room_id):
        return True, "Paid access"
    
    return False, "Payment required"
```

---

## 🧪 TESTING

### Test truy cập file:

```bash
# 1. Không đăng nhập (sẽ bị từ chối)
curl http://localhost:8000/media/rooms/123/image.jpg

# 2. Đăng nhập (sẽ được phép)
curl -b cookies.txt http://localhost:8000/media/rooms/123/image.jpg

# 3. Sử dụng signed URL
curl "http://localhost:8000/protected-media/rooms/123/image.jpg?token=..."
```

---

## 📊 MONITORING

### Xem log truy cập file:

```python
from apps.accounts.models import SecurityLogs

# Xem log truy cập file
logs = SecurityLogs.objects.filter(
    action_type__in=['file_access', 'file_access_denied']
).order_by('-created_at')[:100]

for log in logs:
    print(f"{log.created_at} - {log.ip_address} - {log.details}")
```

---

## 🚀 DEPLOYMENT

### Production (với Nginx):

1. Đảm bảo `USE_X_ACCEL_REDIRECT=True` trong `.env`
2. Nginx config đã có `/protected-files/` location
3. Restart Nginx: `sudo systemctl restart nginx`

### Development (không có Nginx):

1. Set `USE_X_ACCEL_REDIRECT=False`
2. Django sẽ serve file trực tiếp (chậm hơn)

---

## ⚠️ LƯU Ý

1. **Signed URLs có thời hạn** - Sau khi hết hạn, link không còn hoạt động
2. **Cache** - Nên disable cache cho protected files
3. **Performance** - Sử dụng X-Accel-Redirect trong production
4. **Security** - Không share signed URLs công khai

---

## 🔧 TROUBLESHOOTING

### Lỗi: "Access Denied"
- Kiểm tra đã đăng nhập chưa
- Kiểm tra quyền sở hữu file
- Xem log trong `SecurityLogs`

### Lỗi: "File not found"
- Kiểm tra file có tồn tại trong `media/` không
- Kiểm tra đường dẫn file đúng format

### Lỗi: "Token expired"
- Signed URL đã hết hạn
- Tạo URL mới với `get_protected_media_url()`

---

**Ngày cập nhật:** 24/12/2025  
**Phiên bản:** 1.0

