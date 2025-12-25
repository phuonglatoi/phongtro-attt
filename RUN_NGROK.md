# 🚀 CHẠY NGROK - HƯỚNG DẪN NHANH

## Bước 1: Mở Terminal 1 - Chạy Django Server

```powershell
# Activate virtual environment (nếu chưa activate)
.\venv\Scripts\Activate.ps1

# Chạy Django server
python manage.py runserver 0.0.0.0:8000
```

**Kết quả:** Bạn sẽ thấy:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

✅ **Giữ terminal này mở, KHÔNG tắt!**

---

## Bước 2: Mở Terminal 2 - Chạy Ngrok

Mở terminal mới (PowerShell hoặc CMD), sau đó chạy:

```powershell
ngrok http 8000
```

**Kết quả:** Bạn sẽ thấy giao diện ngrok:
```
ngrok

Session Status                online
Account                       Free (Limit: 40 connections/minute)
Version                       3.24.0
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc-xyz-123.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

---

## Bước 3: Lấy URL Công Khai

Tìm dòng **Forwarding** trong giao diện ngrok:
```
Forwarding    https://abc-xyz-123.ngrok-free.app -> http://localhost:8000
```

✅ **Copy URL:** `https://abc-xyz-123.ngrok-free.app`

---

## Bước 4: Chia Sẻ URL

Gửi URL cho người khác, họ có thể truy cập:

- **Trang chủ:** `https://abc-xyz-123.ngrok-free.app/`
- **Đăng nhập:** `https://abc-xyz-123.ngrok-free.app/login/`
- **Admin Dashboard:** `https://abc-xyz-123.ngrok-free.app/dashboard/admin/`

**Tài khoản Admin:**
- Email: `admin@phongtro.vn`
- Password: `admin123`

---

## 🛑 Dừng Ngrok

Để dừng ngrok:
1. Vào terminal đang chạy ngrok
2. Nhấn `Ctrl + C`

Để dừng Django server:
1. Vào terminal đang chạy Django
2. Nhấn `Ctrl + C`

---

## 📝 Lưu Ý

1. **URL sẽ thay đổi** mỗi khi bạn restart ngrok (Free plan)
2. **Giới hạn:** 40 connections/phút (Free plan)
3. **Trang cảnh báo:** Lần đầu truy cập sẽ có trang cảnh báo ngrok, click "Visit Site" để tiếp tục
4. **Bảo mật:** Không chia sẻ URL với người lạ

---

## ✅ Checklist

- [ ] Terminal 1: Django server đang chạy
- [ ] Terminal 2: Ngrok đang chạy
- [ ] Đã copy URL ngrok
- [ ] Đã test truy cập URL

---

**Ngày tạo:** 24/12/2025  
**Trạng thái:** ✅ Sẵn sàng

