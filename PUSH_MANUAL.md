# 🚀 HƯỚNG DẪN PUSH THỦ CÔNG

## Bước 1: Tạo Personal Access Token

1. Vào: https://github.com/settings/tokens/new
2. **Note:** PhongTroATTT
3. **Expiration:** 30 days
4. **Select scopes:** 
   - ✅ repo (chọn tất cả)
5. Click "Generate token"
6. **COPY TOKEN** (chỉ hiện 1 lần!)

---

## Bước 2: Mở PowerShell trong thư mục dự án

1. Mở File Explorer
2. Vào: `C:\Users\Admin\Documents\PhongTroATTT`
3. Shift + Right-click → "Open PowerShell window here"

---

## Bước 3: Chạy lệnh sau (thay YOUR_TOKEN)

```powershell
# Cấu hình Git
git config --global user.name "phuonglatoi"
git config --global user.email "phuonglatoi@github.com"

# Khởi tạo Git (nếu chưa có)
git init

# Add files
git add .

# Commit
git commit -m "feat: PhongTroATTT - Hệ thống quản lý phòng trọ với bảo mật nâng cao"

# Đổi branch
git branch -M main

# Add remote
git remote remove origin
git remote add origin https://github.com/phuonglatoi/phongtro-attt.git

# Push (THAY YOUR_TOKEN bằng token vừa tạo)
git push https://YOUR_TOKEN@github.com/phuonglatoi/phongtro-attt.git main --force
```

---

## Bước 4: Kiểm tra

Vào: https://github.com/phuonglatoi/phongtro-attt

Nếu thấy code đã lên → THÀNH CÔNG! 🎉

---

## ⚠️ LƯU Ý:

- Token giống như password, KHÔNG chia sẻ công khai
- Sau khi push xong, lưu token vào nơi an toàn
- Nếu token bị lộ, xóa và tạo token mới ngay

---

## 🆘 Nếu gặp lỗi:

### Lỗi 403 (Forbidden):
- Token không đúng hoặc hết hạn
- Tạo token mới với đầy đủ quyền `repo`

### Lỗi 404 (Not Found):
- Repository chưa được tạo
- Tạo tại: https://github.com/new

### Lỗi "fatal: not a git repository":
- Chạy: `git init`

---

**Hoặc gửi token mới cho tôi, tôi sẽ push tự động cho bạn!** 🚀

