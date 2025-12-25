# 🚀 HƯỚNG DẪN ĐẨY CODE LÊN GITHUB

## 📋 CHUẨN BỊ

### 1. Tạo file `.gitignore` (nếu chưa có)
```bash
# Tạo file .gitignore
notepad .gitignore
```

**Nội dung `.gitignore`:**
```
# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/media
/staticfiles
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backup files
*.bak
*.backup
```

---

## 🔧 BƯỚC 1: CẤU HÌNH GIT (Lần đầu tiên)

```bash
# Cấu hình tên và email
git config --global user.name "Tên của bạn"
git config --global user.email "email@example.com"

# Kiểm tra cấu hình
git config --global --list
```

---

## 📦 BƯỚC 2: KHỞI TẠO GIT REPOSITORY

```bash
# Di chuyển vào thư mục dự án
cd C:\Users\Admin\Documents\PhongTroATTT

# Khởi tạo Git (nếu chưa có)
git init

# Kiểm tra trạng thái
git status
```

---

## ➕ BƯỚC 3: THÊM FILES VÀO GIT

```bash
# Thêm tất cả files
git add .

# Hoặc thêm từng file/folder cụ thể
git add apps/
git add templates/
git add static/
git add config/
git add manage.py
git add requirements.txt
git add README.md

# Kiểm tra files đã add
git status
```

---

## 💾 BƯỚC 4: COMMIT CODE

```bash
# Commit với message
git commit -m "Initial commit: PhongTroATTT - Hệ thống quản lý phòng trọ với bảo mật nâng cao"

# Hoặc commit chi tiết hơn
git commit -m "feat: Complete PhongTroATTT system

- ✅ Authentication & Authorization (2FA, RBAC)
- ✅ Room management (CRUD, Search, Filter)
- ✅ Booking system
- ✅ Admin dashboard
- ✅ Security features (WAF, Rate limiting, Audit logs)
- ✅ Database backup automation
- ✅ 18 security features, 100% OWASP Top 10 compliance"
```

---

## 🌐 BƯỚC 5: TẠO REPOSITORY TRÊN GITHUB

### Cách 1: Qua Web Browser
1. Truy cập: https://github.com/new
2. **Repository name:** `phongtro-attt`
3. **Description:** `Hệ thống Quản lý Phòng trọ với Bảo mật nâng cao - Django + SQL Server`
4. **Public** hoặc **Private** (tùy chọn)
5. **KHÔNG** chọn "Initialize with README" (vì đã có code)
6. Click **Create repository**

### Cách 2: Qua GitHub CLI (nếu đã cài)
```bash
gh repo create phongtro-attt --public --source=. --remote=origin
```

---

## 🔗 BƯỚC 6: KẾT NỐI VỚI GITHUB

```bash
# Thêm remote repository (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/phongtro-attt.git

# Kiểm tra remote
git remote -v

# Đổi tên branch thành main (nếu đang là master)
git branch -M main
```

---

## 🚀 BƯỚC 7: PUSH CODE LÊN GITHUB

```bash
# Push lần đầu
git push -u origin main

# Nếu bị lỗi authentication, dùng Personal Access Token:
# 1. Vào GitHub Settings > Developer settings > Personal access tokens
# 2. Generate new token (classic)
# 3. Chọn scopes: repo (full control)
# 4. Copy token
# 5. Khi push, nhập:
#    Username: YOUR_USERNAME
#    Password: PASTE_TOKEN_HERE
```

---

## 🔄 CẬP NHẬT SAU NÀY

```bash
# Khi có thay đổi mới
git add .
git commit -m "feat: Thêm tính năng XYZ"
git push

# Hoặc push cụ thể
git push origin main
```

---

## 📝 TẠO README.md ĐẸP

```bash
# Tạo file README.md
notepad README.md
```

**Nội dung mẫu:**
```markdown
# 🏠 PhongTroATTT - Hệ thống Quản lý Phòng trọ

## 📌 Giới thiệu
Hệ thống quản lý cho thuê phòng trọ với **18 tính năng bảo mật nâng cao**, tuân thủ 100% OWASP Top 10.

## ✨ Tính năng chính
- 🔐 Authentication & Authorization (2FA, RBAC)
- 🏠 Quản lý phòng trọ (CRUD, Search, Filter)
- 📅 Đặt lịch xem phòng
- 👥 Admin Dashboard
- 🛡️ Bảo mật: WAF, Rate Limiting, Audit Logs
- 💾 Database Backup tự động

## 🛠️ Công nghệ
- **Backend:** Django 4.2, Python 3.12
- **Database:** SQL Server 2019
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Security:** pyotp, django-ratelimit, hashlib

## 📦 Cài đặt
\`\`\`bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/phongtro-attt.git
cd phongtro-attt

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Chạy server
python manage.py runserver
\`\`\`

## 🔒 Bảo mật
- ✅ Password Hashing (SHA256 + Salt)
- ✅ 2FA (TOTP)
- ✅ Account Lockout
- ✅ Rate Limiting
- ✅ CSRF Protection
- ✅ XSS Prevention
- ✅ SQL Injection Prevention
- ✅ WAF (Web Application Firewall)

## 📊 Demo
- **URL:** http://localhost:8000
- **Admin:** admin@phongtro.vn / admin123
- **Landlord:** chutro@phongtro.vn / chutro123
- **Customer:** khach@phongtro.vn / khach123

## 📄 License
MIT License

## 👥 Nhóm phát triển
- Người 1: Module Accounts
- Người 2: Module Rooms
- Người 3: Module Bookings + Admin
```

---

## ✅ CHECKLIST TRƯỚC KHI PUSH

- [ ] Đã tạo `.gitignore`
- [ ] Đã xóa sensitive data (.env, passwords...)
- [ ] Đã test code chạy OK
- [ ] Đã viết README.md
- [ ] Đã commit với message rõ ràng
- [ ] Đã tạo repository trên GitHub
- [ ] Đã add remote origin

---

## 🆘 XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi: "fatal: not a git repository"
```bash
git init
```

### Lỗi: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/phongtro-attt.git
```

### Lỗi: "failed to push some refs"
```bash
git pull origin main --rebase
git push origin main
```

### Lỗi: Authentication failed
- Dùng Personal Access Token thay vì password
- Hoặc dùng SSH key

---

**🎉 Hoàn thành! Code của bạn đã lên GitHub!**

**Link repository:** `https://github.com/YOUR_USERNAME/phongtro-attt`

