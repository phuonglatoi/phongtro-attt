# 🌐 HƯỚNG DẪN DEPLOY VỚI NGROK

## 📋 Yêu cầu:
- ✅ Ngrok đã được cài đặt (version 3.24.0-msix)
- ✅ Django server đang chạy
- ✅ File `.env` đã cấu hình đúng

## 🚀 Cách 1: Sử dụng script tự động (Khuyến nghị)

### Bước 1: Chạy script
```powershell
.\start_ngrok.ps1
```

Script sẽ tự động:
1. Kích hoạt virtual environment
2. Chạy Django server trên port 8000
3. Chạy ngrok tunnel

### Bước 2: Lấy URL công khai
Sau khi ngrok chạy, bạn sẽ thấy:
```
Forwarding    https://abc-xyz-123.ngrok-free.app -> http://localhost:8000
```

Copy URL `https://abc-xyz-123.ngrok-free.app` và chia sẻ với người khác!

---

## 🔧 Cách 2: Chạy thủ công

### Bước 1: Chạy Django server
Mở terminal 1:
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run Django server
python manage.py runserver 0.0.0.0:8000
```

### Bước 2: Chạy ngrok
Mở terminal 2:
```powershell
ngrok http 8000
```

### Bước 3: Lấy URL công khai
Trong giao diện ngrok, tìm dòng:
```
Forwarding    https://abc-xyz-123.ngrok-free.app -> http://localhost:8000
```

Copy URL và chia sẻ!

---

## ⚙️ Cấu hình đã có sẵn

### File `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,.ngrok-free.app,.ngrok.io,.ngrok-free.dev
```

### File `config/settings/base.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

✅ Tất cả đã được cấu hình sẵn, không cần sửa gì thêm!

---

## 🧪 Test deployment

### 1. Truy cập trang chủ:
```
https://your-ngrok-url.ngrok-free.app/
```

### 2. Đăng nhập Admin:
```
https://your-ngrok-url.ngrok-free.app/login/
Email: admin@phongtro.vn
Password: admin123
```

### 3. Admin Dashboard:
```
https://your-ngrok-url.ngrok-free.app/dashboard/admin/
```

---

## 📝 Lưu ý quan trọng

### 1. **Ngrok Free Plan:**
- ✅ URL sẽ thay đổi mỗi khi restart ngrok
- ✅ Giới hạn 40 connections/phút
- ✅ Session timeout sau 2 giờ

### 2. **Bảo mật:**
- ⚠️ Không chia sẻ URL công khai với người lạ
- ⚠️ Đổi mật khẩu admin trước khi deploy
- ⚠️ Tắt DEBUG mode trong production

### 3. **Performance:**
- Ngrok có thể chậm hơn so với hosting thật
- Phù hợp cho demo, test, không phù hợp cho production

---

## 🔒 Nâng cấp lên Ngrok Pro (Tùy chọn)

### Lợi ích:
- ✅ Custom domain (ví dụ: `phongtro.ngrok.io`)
- ✅ URL cố định, không đổi khi restart
- ✅ Không giới hạn connections
- ✅ Không có trang cảnh báo ngrok

### Cách nâng cấp:
1. Đăng ký tài khoản tại: https://ngrok.com/
2. Lấy authtoken
3. Chạy: `ngrok config add-authtoken YOUR_TOKEN`
4. Chạy với custom domain: `ngrok http 8000 --domain=your-custom-domain.ngrok.io`

---

## 🛠️ Troubleshooting

### Lỗi: "Invalid Host header"
**Nguyên nhân:** ALLOWED_HOSTS chưa có ngrok domain

**Giải pháp:** Thêm domain vào `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,.ngrok-free.app,your-specific-domain.ngrok-free.app
```

### Lỗi: "CSRF verification failed"
**Nguyên nhân:** CSRF_TRUSTED_ORIGINS chưa có ngrok domain

**Giải pháp:** Đã được cấu hình sẵn trong `config/settings/base.py`

### Ngrok không chạy
**Nguyên nhân:** Chưa cài đặt hoặc chưa authenticate

**Giải pháp:**
```powershell
# Kiểm tra version
ngrok version

# Nếu chưa cài, tải tại: https://ngrok.com/download
```

---

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Django server có đang chạy không? (http://localhost:8000)
2. Ngrok có đang chạy không?
3. File `.env` có đúng cấu hình không?

---

**Ngày tạo:** 24/12/2025  
**Phiên bản:** 1.0  
**Trạng thái:** ✅ Sẵn sàng deploy

